#!/usr/bin/env bash
# Fetch a single PR by number with retry; append the node JSON to OUT.
# Used to backfill PRs that a paged harvest dropped (GraphQL complexity/timeout).
# Usage: fetch_pr.sh <owner> <name> <number> <out.ndjson>
OWNER="$1"; NAME="$2"; NUM="$3"; OUT="$4"
q='query($owner:String!,$name:String!,$num:Int!){
  repository(owner:$owner,name:$name){
    pullRequest(number:$num){
      number title state createdAt mergedAt closedAt additions deletions changedFiles
      author{login} mergedBy{login}
      labels(first:50){nodes{name}}
      files(first:100){totalCount nodes{path additions deletions}}
      reviews(first:50){totalCount nodes{author{login} state bodyText submittedAt}}
      comments(first:100){totalCount nodes{author{login} bodyText createdAt}}
      reviewThreads(first:50){totalCount nodes{isResolved comments(first:20){nodes{author{login} path bodyText}}}}
    }
  }
}'
for attempt in 1 2 3 4; do
  resp=$(gh api graphql -f query="$q" -F owner="$OWNER" -F name="$NAME" -F num="$NUM" 2>/dev/null)
  node=$(echo "$resp" | jq -c '.data.repository.pullRequest' 2>/dev/null)
  if [ -n "$node" ] && [ "$node" != "null" ]; then echo "$node" >> "$OUT"; exit 0; fi
  /bin/sleep $((attempt*2))
done
echo "FAILED:$NUM" >&2; exit 1
