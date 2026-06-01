#!/usr/bin/env bash
# Harvest the full PR corpus for a repo into NDJSON (one PR per line, with every
# comment / review / inline-thread body). Two modes:
#   all     : page repository.pullRequests (team mode — everyone's PRs)
#   search  : page search() with a query (self mode — e.g. author:<me>)
#
# Usage:
#   harvest.sh all    <owner> <name> <out.ndjson>
#   harvest.sh search <owner> <name> <out.ndjson> "<extra search qualifiers>"
# e.g. harvest.sh search <OWNER> <REPO> raw/<REPO>.me.ndjson "author:<LOGIN>"
set -euo pipefail
MODE="$1"; OWNER="$2"; NAME="$3"; OUT="$4"; EXTRA="${5:-}"
> "$OUT"

PR_FIELDS='
  number title state createdAt mergedAt closedAt additions deletions changedFiles
  author{login} mergedBy{login}
  labels(first:50){nodes{name}}
  files(first:100){totalCount nodes{path additions deletions}}
  reviews(first:50){totalCount nodes{author{login} state bodyText submittedAt}}
  comments(first:100){totalCount nodes{author{login} bodyText createdAt}}
  reviewThreads(first:50){totalCount nodes{isResolved comments(first:20){nodes{author{login} path bodyText}}}}'

page=0; cursor=""
while : ; do
  page=$((page+1))
  if [ "$MODE" = "all" ]; then
    resp=$(gh api graphql -f query="
      query(\$owner:String!,\$name:String!,\$cursor:String){
        repository(owner:\$owner,name:\$name){
          pullRequests(first:25, after:\$cursor, orderBy:{field:CREATED_AT,direction:ASC}){
            pageInfo{hasNextPage endCursor}
            nodes{ $PR_FIELDS }
          }
        }
      }" -F owner="$OWNER" -F name="$NAME" $( [ -n "$cursor" ] && echo "-F cursor=$cursor" ) 2>/dev/null || true)
    echo "$resp" | jq -c '.data.repository.pullRequests.nodes[]?' >> "$OUT" 2>/dev/null || true
    hasNext=$(echo "$resp" | jq -r '.data.repository.pullRequests.pageInfo.hasNextPage // "false"')
    cursor=$(echo "$resp" | jq -r '.data.repository.pullRequests.pageInfo.endCursor // ""')
  else
    Q="repo:$OWNER/$NAME is:pr $EXTRA"
    resp=$(gh api graphql -f query="
      query(\$q:String!,\$cursor:String){
        search(query:\$q, type:ISSUE, first:25, after:\$cursor){
          pageInfo{hasNextPage endCursor}
          nodes{ ... on PullRequest { $PR_FIELDS } }
        }
      }" -F q="$Q" $( [ -n "$cursor" ] && echo "-F cursor=$cursor" ) 2>/dev/null || true)
    echo "$resp" | jq -c '.data.search.nodes[]? | select(.number)' >> "$OUT" 2>/dev/null || true
    hasNext=$(echo "$resp" | jq -r '.data.search.pageInfo.hasNextPage // "false"')
    cursor=$(echo "$resp" | jq -r '.data.search.pageInfo.endCursor // ""')
  fi
  n=$(wc -l < "$OUT" | tr -d ' ')
  echo "  [$NAME/$MODE] page $page -> $n PRs" >&2
  [ "$hasNext" = "true" ] || break
done
# de-dupe by number (search across author+reviewer can overlap)
if [ -s "$OUT" ]; then
  tmp="$OUT.dedup"; jq -c -s 'unique_by(.number)[]' "$OUT" > "$tmp" && mv "$tmp" "$OUT"
fi
echo "  [$NAME/$MODE] DONE: $(wc -l < "$OUT" | tr -d ' ') PRs" >&2
