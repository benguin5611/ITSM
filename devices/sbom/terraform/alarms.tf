variable "alert_email" {
  description = "Email address to receive CloudWatch alarm notifications. Leave empty to skip subscription."
  type        = string
  default     = ""
}

resource "aws_sns_topic" "alerts" {
  name = "device-sbom-audit-alerts"
}

resource "aws_sns_topic_subscription" "alerts_email" {
  count = var.alert_email == "" ? 0 : 1

  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "device-sbom-audit-errors"
  alarm_description   = "Lambda errors indicate validation/operational failures"
  namespace           = "AWS/Lambda"
  metric_name         = "Errors"
  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 1
  threshold           = 5
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.sbom_validator.function_name
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "lambda_throttles" {
  alarm_name          = "device-sbom-audit-throttles"
  alarm_description   = "Lambda throttles indicate reserved concurrency is too low or unusual burst"
  namespace           = "AWS/Lambda"
  metric_name         = "Throttles"
  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 1
  threshold           = 1
  comparison_operator = "GreaterThanOrEqualToThreshold"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.sbom_validator.function_name
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "lambda_high_volume" {
  alarm_name          = "device-sbom-audit-high-volume"
  alarm_description   = "Unusually high invocation volume — possible abuse or runaway client"
  namespace           = "AWS/Lambda"
  metric_name         = "Invocations"
  statistic           = "Sum"
  period              = 3600
  evaluation_periods  = 1
  threshold           = 200
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.sbom_validator.function_name
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
}

# Log-metric-filter on "unauthorized presign attempt" — slog warn line in handler.
resource "aws_cloudwatch_log_metric_filter" "unauthorized" {
  name           = "device-sbom-audit-unauthorized"
  log_group_name = aws_cloudwatch_log_group.lambda_logs.name
  pattern        = "\"unauthorized presign attempt\""

  metric_transformation {
    name          = "UnauthorizedPresignAttempts"
    namespace     = "DeviceSbomAudit"
    value         = "1"
    default_value = "0"
  }
}

resource "aws_cloudwatch_metric_alarm" "unauthorized" {
  alarm_name          = "device-sbom-audit-unauthorized-attempts"
  alarm_description   = "Multiple unauthorized presign attempts — possible token brute-force or leaked credential"
  namespace           = "DeviceSbomAudit"
  metric_name         = "UnauthorizedPresignAttempts"
  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 1
  threshold           = 3
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"

  alarm_actions = [aws_sns_topic.alerts.arn]
}
