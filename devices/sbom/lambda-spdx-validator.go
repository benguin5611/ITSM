package main

import (
	"context"
	"crypto/hmac"
	"crypto/sha256"
	"crypto/subtle"
	_ "embed"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"log/slog"
	"net/url"
	"os"
	"regexp"
	"strings"
	"time"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/aws/aws-sdk-go-v2/service/s3/types"
	"github.com/aws/aws-sdk-go-v2/service/secretsmanager"
	"github.com/google/uuid"
	"github.com/xeipuuv/gojsonschema"
)

var (
	//go:embed spdx-2.3-schema.json
	spdxSchema23 string

	s3Client *s3.Client
	smClient *secretsmanager.Client

	// Device IDs must start with "AS" prefix and contain only safe characters
	deviceIDPattern = regexp.MustCompile(`^AS[A-Za-z0-9._-]+$`)
	checksumPattern = regexp.MustCompile(`^[0-9a-fA-F]{64}$`) // SHA-256 hex
	// uuid.New() emits 36-char canonical UUIDs (8-4-4-4-12 hex).
	correlationIDPattern = regexp.MustCompile(`^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$`)
	// Control characters are stripped from attacker-influenced values before
	// they reach a log, so a crafted value cannot split or forge log entries.
	logControlChars = regexp.MustCompile(`[[:cntrl:]]`)

	presignExpiryDuration = time.Minute * 30

	// Secret values fetched from Secrets Manager during init().
	// Set once per Lambda execution environment; reused across warm
	// invocations.
	authToken     string
	presignSecret string
)

const (
	maxDeviceIDLen  = 128
	unknownDeviceID = "unknown"

	maxReasonablePackages = 50000
)

// SPDX Document structure for validation
type SPDXDocument struct {
	SPDXID            string        `json:"SPDXID"`
	SPDXVersion       string        `json:"spdxVersion"`
	CreationInfo      CreationInfo  `json:"creationInfo"`
	Name              string        `json:"name"`
	DataLicense       string        `json:"dataLicense"`
	DocumentNamespace string        `json:"documentNamespace"`
	Packages          []SPDXPackage `json:"packages,omitempty"`
}

type CreationInfo struct {
	Created  string   `json:"created"`
	Creators []string `json:"creators,omitempty"`
	Comment  string   `json:"comment,omitempty"`
}

type SPDXPackage struct {
	SPDXID           string `json:"SPDXID"`
	Name             string `json:"name"`
	VersionInfo      string `json:"versionInfo,omitempty"`
	DownloadLocation string `json:"downloadLocation"`
}

// Request for presigned URL
type PresignedURLRequest struct {
	DeviceID string `json:"device_id"`
	Checksum string `json:"checksum"`
}

type PresignedURLResponse struct {
	UploadURL     string `json:"upload_url"`
	S3Key         string `json:"s3_key"`
	ExpiresIn     int    `json:"expires_in"`
	CorrelationID string `json:"correlation_id,omitempty"`
}

func init() {
	ctx := context.Background()

	cfg, err := config.LoadDefaultConfig(ctx)
	if err != nil {
		slog.Error("failed to load AWS config", "error", err)
		os.Exit(1)
	}
	s3Client = s3.NewFromConfig(cfg)
	smClient = secretsmanager.NewFromConfig(cfg)

	// Fetch both secrets from Secrets Manager up-front. ARNs are passed
	// in as env vars at deploy time; the values themselves never appear
	// in env vars (where lambda:GetFunctionConfiguration would expose
	// them), and every fetch is recorded in CloudTrail. Lambda init runs
	// once per execution environment, so the cost is paid on cold start
	// only.
	authARN := os.Getenv("SBOM_AUTH_TOKEN_SECRET_ARN")
	presignARN := os.Getenv("SBOM_PRESIGN_SECRET_ARN")
	if authARN == "" || presignARN == "" {
		slog.Error("SBOM_AUTH_TOKEN_SECRET_ARN and SBOM_PRESIGN_SECRET_ARN must be set")
		os.Exit(1)
	}

	authVal, err := smClient.GetSecretValue(ctx, &secretsmanager.GetSecretValueInput{
		SecretId: &authARN,
	})
	if err != nil {
		slog.Error("failed to fetch auth token secret", "error", err)
		os.Exit(1)
	}
	if authVal.SecretString == nil || *authVal.SecretString == "" {
		slog.Error("auth token secret is empty")
		os.Exit(1)
	}
	authToken = *authVal.SecretString

	presignVal, err := smClient.GetSecretValue(ctx, &secretsmanager.GetSecretValueInput{
		SecretId: &presignARN,
	})
	if err != nil {
		slog.Error("failed to fetch presign secret", "error", err)
		os.Exit(1)
	}
	if presignVal.SecretString == nil || *presignVal.SecretString == "" {
		slog.Error("presign secret is empty")
		os.Exit(1)
	}
	presignSecret = *presignVal.SecretString
}

func main() {
	lambda.Start(router)
}

// Router determines which handler to use based on event type
func router(ctx context.Context, event json.RawMessage) (interface{}, error) {
	// Try to parse as S3 event
	var s3Event events.S3Event
	if err := json.Unmarshal(event, &s3Event); err == nil && len(s3Event.Records) > 0 {
		return handleS3Event(ctx, s3Event)
	}

	// Try to parse as Function URL request
	var urlRequest events.LambdaFunctionURLRequest
	if err := json.Unmarshal(event, &urlRequest); err == nil && urlRequest.RequestContext.HTTP.Method != "" {
		return handleFunctionURL(ctx, urlRequest)
	}

	return response(400, `{"error":"unknown event type"}`), nil
}

// handleFunctionURL generates presigned S3 upload URL
func handleFunctionURL(ctx context.Context, request events.LambdaFunctionURLRequest) (events.LambdaFunctionURLResponse, error) {
	// Cap presign-path work at 10s. The function-level timeout is 120s to
	// accommodate the S3 validation path; presign is sub-second in practice,
	// so a tight per-handler budget shrinks the concurrency window a
	// slow-loris attacker can hold.
	ctx, cancel := context.WithTimeout(ctx, 10*time.Second)
	defer cancel()

	// Only accept POST requests
	if request.RequestContext.HTTP.Method != "POST" {
		return response(405, `{"error":"method not allowed"}`), nil
	}

	expectedAuth := authToken

	// Use constant-time comparison to prevent timing attacks
	if authHeader := request.Headers["authorization"]; len(authHeader) != len(expectedAuth) ||
		subtle.ConstantTimeCompare([]byte(authHeader), []byte(expectedAuth)) != 1 {
		slog.Warn("unauthorized presign attempt",
			"remote_addr", request.RequestContext.HTTP.SourceIP,
			"device_id", truncate(request.Headers["x-device-id"], maxDeviceIDLen),
			"auth_provided", authHeader != "")
		return response(401, `{"error":"unauthorized"}`), nil
	}

	// Early validation: check Content-Type
	contentType := request.Headers["content-type"]
	if contentType != "application/json" {
		return response(400, `{"error":"content-type must be application/json"}`), nil
	}

	// Handle base64-encoded body if necessary
	bodyBytes := []byte(request.Body)
	if request.IsBase64Encoded {
		decoded, err := base64.StdEncoding.DecodeString(request.Body)
		if err != nil {
			return response(400, `{"error":"invalid base64 body"}`), nil
		}
		bodyBytes = decoded
	}

	// Early validation: check body size before parsing
	if len(bodyBytes) > 10000 {
		return response(400, `{"error":"presign request body too large"}`), nil
	}

	// Parse request body for presigned URL request
	var presignReq PresignedURLRequest
	if err := json.Unmarshal(bodyBytes, &presignReq); err != nil {
		return response(400, `{"error":"invalid JSON"}`), nil
	}

	// Get and sanitize device ID from header
	var deviceID string

	// Use device ID from header if not in body
	if presignReq.DeviceID == "" {
		deviceID = sanitizeDeviceID(request.Headers["x-device-id"])
	} else {
		deviceID = sanitizeDeviceID(presignReq.DeviceID)
	}

	// Validate device ID before generating presigned URL (prevent DoS via "unknown" uploads)
	// Note: AS prefix is enforced by sanitizeDeviceID() via regex
	if deviceID == unknownDeviceID {
		return response(400, `{"error":"invalid device_id: you shall not pass"}`), nil
	}

	bucket := os.Getenv("SBOM_BUCKET")
	if bucket == "" {
		slog.Error("SBOM_BUCKET not configured")
		return response(500, `{"error":"server misconfigured"}`), nil
	}

	// Validate checksum format (must be 64 hex chars for SHA-256)
	if presignReq.Checksum == "" {
		return response(400, `{"error":"checksum is required"}`), nil
	}
	if !checksumPattern.MatchString(presignReq.Checksum) {
		return response(400, `{"error":"checksum must be 64 hex characters (sha256)"}`), nil
	}

	// Generate S3 key: uploads/{device-id}/{timestamp}-{checksum}.json
	timestamp := time.Now().UTC().Format(time.RFC3339)
	key := fmt.Sprintf("uploads/%s/%s-%s.json",
		deviceID,
		timestamp,
		presignReq.Checksum[:8])

	// Generate correlation ID for tracking presign → upload flow
	correlationID := uuid.New().String()

	// Compute HMAC signature to bind upload to this presign operation.
	// This prevents direct S3 writes from bypassing Function URL authentication.
	sig := presignSignature(presignSecret, presignReq.Checksum)

	// Create presigned PUT URL (30 minute expiry)
	// Include checksum metadata and HMAC signature for verification during validation
	presignClient := s3.NewPresignClient(s3Client)
	presignResult, err := presignClient.PresignPutObject(ctx, &s3.PutObjectInput{
		Bucket:               ptr(bucket),
		Key:                  ptr(key),
		ContentType:          ptr("application/json"),
		ServerSideEncryption: types.ServerSideEncryptionAes256,
		Metadata: map[string]string{
			"device-id":      deviceID,
			"checksum":       presignReq.Checksum,
			"correlation-id": correlationID,
			"sig":            sig,
		},
	}, s3.WithPresignExpires(presignExpiryDuration))
	if err != nil {
		slog.Error("failed to generate presigned URL",
			"error", err,
			"device_id", deviceID)
		return response(500, `{"error":"failed to generate upload URL"}`), nil
	}

	expiresAt := time.Now().Add(presignExpiryDuration).Format(time.RFC3339)

	slog.Info("presigned URL generated",
		"correlation_id", correlationID,
		"device_id", deviceID,
		"s3_key", key,
		"expires_at", expiresAt,
		"request_bytes", len(bodyBytes))

	// Return presigned URL
	resp := PresignedURLResponse{
		UploadURL:     presignResult.URL,
		S3Key:         key,
		ExpiresIn:     int(presignExpiryDuration.Seconds()),
		CorrelationID: correlationID,
	}

	respJSON, err := json.Marshal(resp)
	if err != nil {
		slog.Error("failed to marshal presign response", "error", err)
		return response(500, `{"error":"internal error"}`), nil
	}
	return response(200, string(respJSON)), nil
}

// handleS3Event validates SBOM uploaded to S3
func handleS3Event(ctx context.Context, event events.S3Event) (string, error) {
	expectedBucket := os.Getenv("SBOM_BUCKET")

	for _, record := range event.Records {
		bucket := record.S3.Bucket.Name
		// S3 event keys are URL-encoded (e.g. ":" → "%3A"). Decode before
		// calling GetObject, otherwise the lookup misses and S3 returns
		// 403 (masked as AccessDenied because we don't grant ListBucket).
		key, err := url.QueryUnescape(record.S3.Object.Key)
		if err != nil {
			slog.Warn("invalid S3 event key encoding",
				"raw_key", record.S3.Object.Key,
				"error", err)
			continue
		}

		// Validate bucket name matches expected bucket
		if bucket != expectedBucket {
			slog.Warn("ignoring event from unexpected bucket",
				"bucket", bucket,
				"expected", expectedBucket)
			continue
		}

		// Only process uploads/ prefix
		if !strings.HasPrefix(key, "uploads/") {
			slog.Info("ignoring non-upload object", "key", key)
			continue
		}

		slog.Info("processing S3 upload",
			"bucket", bucket,
			"key", key,
			"size", record.S3.Object.Size)

		body, metadata, err := downloadS3Object(ctx, bucket, key)
		if err != nil {
			slog.Warn("error getting object",
				"bucket", bucket,
				"key", key,
				"error", err)
			continue
		}

		// Extract device ID and correlation ID. Prefer metadata
		// (canonical, set by the presigning Lambda); fall back to
		// the key path if metadata is absent.
		var (
			deviceID      = unknownDeviceID
			correlationID = "unknown"
		)
		if metadata != nil {
			if id, ok := metadata["device-id"]; ok {
				deviceID = id
			}
			if corrID, ok := metadata["correlation-id"]; ok && correlationIDPattern.MatchString(corrID) {
				correlationID = corrID
			}
		}
		if deviceID == unknownDeviceID {
			// Fallback: parse from key uploads/{device-id}/{timestamp}-{checksum}.json
			parts := strings.Split(key, "/")
			if len(parts) >= 2 {
				deviceID = parts[1]
			}
		}

		// Re-sanitize device ID (defence against direct S3 writes bypassing presign).
		// Keep the raw value for the rejection log; after sanitisation the
		// variable only ever holds the "unknown" constant on this path.
		rawDeviceID := deviceID
		if deviceID = sanitizeDeviceID(deviceID); deviceID == unknownDeviceID {
			slog.Error("You shall not pass",
				"device_id", sanitizeForLog(truncate(rawDeviceID, maxDeviceIDLen)),
				"correlation_id", correlationID)
			continue
		}

		if err := validateS3Object(ctx, body, metadata, deviceID, correlationID); err != nil {
			slog.Error("SBOM validation failed",
				"error", err,
				"device_id", deviceID,
				"correlation_id", correlationID)

			// Delete invalid SBOM
			deleteS3Object(ctx, bucket, key)
			continue
		}

		copyMetadata := map[string]string{
			"device-id": deviceID,
			"checksum":  metadata["checksum"],
		}

		// Move from uploads/ to sboms/ (validated)
		dstKey := strings.Replace(key, "uploads/", "sboms/", 1)
		if err := moveAndDeleteS3Object(ctx, bucket, key, dstKey, copyMetadata); err != nil {
			slog.Error("unable to move and delete s3 object",
				"error", err,
				"bucket", bucket,
				"key", key,
				"dst_key", dstKey,
				"device_id", deviceID,
				"correlation_id", correlationID)

			continue
		}

		slog.Info("SBOM validated and moved",
			"device_id", deviceID,
			"correlation_id", correlationID,
			"bucket", bucket,
			"key", key,
			"dstKey", dstKey)
	}

	return "processed", nil
}

func downloadS3Object(ctx context.Context, bucket, key string) ([]byte, map[string]string, error) {
	// Download SBOM from S3
	getCtx, getCancel := context.WithTimeout(ctx, 30*time.Second)
	defer getCancel()

	result, err := s3Client.GetObject(getCtx, &s3.GetObjectInput{
		Bucket: ptr(bucket),
		Key:    ptr(key),
	})
	if err != nil {
		return nil, nil, fmt.Errorf("unable to download: %w", err)
	}
	defer func() {
		if err := result.Body.Close(); err != nil {
			slog.Warn("failed to close S3 response body", "error", err)
		}
	}()

	// Cap the body read at 75 MB. Uploads arrive via presigned S3 PUT, so
	// the Function URL payload limit does not apply here.
	const maxBodySize = 75 * 1024 * 1024
	limitedReader := io.LimitReader(result.Body, maxBodySize+1)
	body, err := io.ReadAll(limitedReader)
	if err != nil {
		return nil, nil, fmt.Errorf("read body: %w", err)
	}

	return body, result.Metadata, nil
}

func validateS3Object(ctx context.Context, body []byte, metadata map[string]string, deviceID, correlationID string) error {

	// Calculate checksum and verify (metadata required)
	checksum := fmt.Sprintf("%x", sha256.Sum256(body))
	if metadata == nil {
		return fmt.Errorf("S3 metadata missing (upload may not have used presigned URL)")
	}
	expectedChecksum, ok := metadata["checksum"]
	if !ok || expectedChecksum == "" {
		return fmt.Errorf("checksum metadata missing (required for validation)")
	}

	// Use constant-time comparison to prevent timing attacks
	if subtle.ConstantTimeCompare([]byte(expectedChecksum), []byte(checksum)) != 1 {
		return fmt.Errorf("checksum mismatch")
	}

	// Verify HMAC signature to ensure upload came from legitimate presign operation.
	// This prevents direct S3 writes from bypassing Function URL authentication.
	expectedSig, ok := metadata["sig"]
	if !ok || expectedSig == "" {
		return fmt.Errorf("missing presign signature metadata (upload may have bypassed presign flow)")
	}

	recomputedSig := presignSignature(presignSecret, expectedChecksum)
	if subtle.ConstantTimeCompare([]byte(expectedSig), []byte(recomputedSig)) != 1 {
		return fmt.Errorf("invalid presign signature (upload did not originate from authenticated presign)")
	}

	// Validate SPDX SBOM
	var doc SPDXDocument
	if err := json.Unmarshal(body, &doc); err != nil {
		return fmt.Errorf("invalid JSON: %w", err)
	}

	// Validate against SPDX JSON schema
	// SPDX uses version string like "SPDX-2.3"
	spdxVersion := doc.SPDXVersion
	if spdxVersion == "" {
		return fmt.Errorf("spdxVersion is required")
	}

	// Extract version number (e.g., "SPDX-2.3" -> "2.3")
	versionParts := strings.Split(spdxVersion, "-")
	if len(versionParts) != 2 {
		return fmt.Errorf("invalid spdxVersion format: %s (expected SPDX-X.Y)", spdxVersion)
	}
	version := versionParts[1]

	// Only accept SPDX 2.3 (embedded schema, no external dependencies)
	if version != "2.3" {
		return fmt.Errorf("unsupported SPDX version: %s (only SPDX-2.3 is supported)", spdxVersion)
	}

	schemaLoader := gojsonschema.NewStringLoader(spdxSchema23)

	documentLoader := gojsonschema.NewBytesLoader(body)

	schemaResult, err := gojsonschema.Validate(schemaLoader, documentLoader)
	if err != nil {
		return fmt.Errorf("schema validation setup failed: %w", err)
	}
	if !schemaResult.Valid() {
		// Limit logged errors to prevent log amplification DoS
		const maxErrorsToLog = 20
		var errors []string
		for i, desc := range schemaResult.Errors() {
			if i >= maxErrorsToLog {
				break
			}
			errors = append(errors, desc.String())
		}
		if len(schemaResult.Errors()) > maxErrorsToLog {
			errors = append(errors, fmt.Sprintf("... and %d more errors",
				len(schemaResult.Errors())-maxErrorsToLog))
		}

		slog.Warn("SPDX schema validation failed",
			"device_id", deviceID,
			"correlation_id", correlationID,
			"spdx_version", spdxVersion,
			"errors", strings.Join(errors, "; "))
		return fmt.Errorf("SPDX schema validation failed: %d errors", len(schemaResult.Errors()))
	}

	// Validate SPDX spec compliance - check required fields
	if doc.SPDXID == "" {
		return fmt.Errorf("SPDXID is required")
	}
	if doc.SPDXID != "SPDXRef-DOCUMENT" {
		return fmt.Errorf("document SPDXID must be 'SPDXRef-DOCUMENT', got: %s", doc.SPDXID)
	}
	if doc.DocumentNamespace == "" {
		return fmt.Errorf("documentNamespace is required")
	}
	if doc.Name == "" {
		return fmt.Errorf("name is required")
	}

	// Cap document-level field lengths to prevent abuse
	if len(doc.Name) > 500 {
		return fmt.Errorf("document name too long: %d chars (max 500)", len(doc.Name))
	}
	if len(doc.DocumentNamespace) > 2048 {
		return fmt.Errorf("documentNamespace too long: %d chars (max 2048)", len(doc.DocumentNamespace))
	}
	if doc.DataLicense == "" {
		slog.Warn("dataLicense is empty (should be CC0-1.0)",
			"device_id", deviceID,
			"correlation_id", correlationID,
			"spdx_version", spdxVersion)
	}

	// Basic sanity checks
	if numPackages := len(doc.Packages); numPackages == 0 {
		slog.Warn("SBOM has no packages",
			"device_id", deviceID,
			"correlation_id", correlationID,
			"spdx_version", spdxVersion)
	} else if numPackages > maxReasonablePackages {
		// Reject suspiciously large package counts (likely malformed)
		return fmt.Errorf("package count %d exceeds reasonable limit %d", numPackages, maxReasonablePackages)
	}

	// Validate package field lengths to prevent abuse
	for i, pkg := range doc.Packages {
		if len(pkg.Name) > 500 {
			return fmt.Errorf("package[%d] name too long: %d chars (max 500)", i, len(pkg.Name))
		}
		if len(pkg.VersionInfo) > 100 {
			return fmt.Errorf("package[%d] versionInfo too long: %d chars (max 100)", i, len(pkg.VersionInfo))
		}
		if len(pkg.SPDXID) > 500 {
			return fmt.Errorf("package[%d] SPDXID too long: %d chars (max 500)", i, len(pkg.SPDXID))
		}
		if len(pkg.DownloadLocation) > 2048 {
			return fmt.Errorf("package[%d] downloadLocation too long: %d chars (max 2048)", i, len(pkg.DownloadLocation))
		}
	}

	slog.Info("SBOM validated",
		"device_id", deviceID,
		"checksum", checksum,
		"size_bytes", len(body),
		"package_count", len(doc.Packages),
		"correlation_id", correlationID)

	return nil
}

func moveAndDeleteS3Object(ctx context.Context, bucket, srcKey, dstKey string, metadata map[string]string) error {
	copyCtx, copyCancel := context.WithTimeout(ctx, 30*time.Second)
	defer copyCancel()

	// Request S3 compute SHA-256 on the destination so we can verify the
	// copy stored the same bytes the validator hashed. The source was
	// already verified byte-for-byte in validateS3Object; this catches
	// (very rare) silent partial-copy failures before we delete the source.
	copyResp, err := s3Client.CopyObject(copyCtx, &s3.CopyObjectInput{
		Bucket:               ptr(bucket),
		CopySource:           ptr(bucket + "/" + srcKey),
		Key:                  ptr(dstKey),
		ServerSideEncryption: types.ServerSideEncryptionAes256,
		Metadata:             metadata,
		MetadataDirective:    types.MetadataDirectiveReplace,
		ChecksumAlgorithm:    types.ChecksumAlgorithmSha256,
	})
	if err != nil {
		return fmt.Errorf("unable to copy to final location: %w", err)
	}

	// S3 returns SHA-256 base64-encoded; the metadata checksum is hex.
	expectedHex := metadata["checksum"]
	expectedBytes, decodeErr := hex.DecodeString(expectedHex)
	if decodeErr == nil && copyResp.CopyObjectResult != nil && copyResp.CopyObjectResult.ChecksumSHA256 != nil {
		expectedB64 := base64.StdEncoding.EncodeToString(expectedBytes)
		if *copyResp.CopyObjectResult.ChecksumSHA256 != expectedB64 {
			deleteS3Object(ctx, bucket, dstKey)
			return fmt.Errorf("checksum mismatch on copied object: expected %s, got %s", expectedB64, *copyResp.CopyObjectResult.ChecksumSHA256)
		}
	}

	deleteS3Object(ctx, bucket, srcKey)

	return nil
}

// truncate caps s to at most n bytes for safe logging of attacker-controlled
// header values. Returns s unchanged when within limit.
func truncate(s string, n int) string {
	if len(s) <= n {
		return s
	}
	return s[:n]
}

// sanitizeForLog strips control characters (including CR and LF) from a value
// before it is logged, so an attacker-influenced field such as a rejected
// device ID cannot inject line breaks and forge or split log entries.
func sanitizeForLog(s string) string {
	return logControlChars.ReplaceAllString(s, "")
}

// presignSignature computes HMAC-SHA256 signature for presigned URL verification
// This binds S3 uploads cryptographically to legitimate presign operations
func presignSignature(secret, checksum string) string {
	mac := hmac.New(sha256.New, []byte(secret))
	mac.Write([]byte(checksum))
	return hex.EncodeToString(mac.Sum(nil))
}

// sanitizeDeviceID ensures device ID is safe for S3 keys and metadata
func sanitizeDeviceID(raw string) string {
	if raw == "" {
		return unknownDeviceID
	}
	if len(raw) > maxDeviceIDLen {
		raw = raw[:maxDeviceIDLen]
	}

	// Ensure only safe characters (including AS prefix requirement)
	if !deviceIDPattern.MatchString(raw) {
		return unknownDeviceID
	}
	return raw
}

// deleteS3Object removes an object from S3
func deleteS3Object(ctx context.Context, bucket, key string) {
	delCtx, cancel := context.WithTimeout(ctx, 10*time.Second)
	defer cancel()

	_, err := s3Client.DeleteObject(delCtx, &s3.DeleteObjectInput{
		Bucket: ptr(bucket),
		Key:    ptr(key),
	})
	if err != nil {
		slog.Warn("failed to delete object",
			"error", err,
			"bucket", bucket,
			"key", key)
	}
}

func response(statusCode int, body string) events.LambdaFunctionURLResponse {
	return events.LambdaFunctionURLResponse{
		StatusCode: statusCode,
		Headers: map[string]string{
			"Content-Type": "application/json",
		},
		Body: body,
	}
}

func ptr[T any](v T) *T {
	return &v
}
