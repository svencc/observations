#!/usr/bin/env bash
# Read-only demonstration client for the existing apps/knowledge API.
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage (requires an already running knowledge service):
  KNOWLEDGE_API_URL=http://127.0.0.1:8000 bash search/knowledge-query.sh count
  ... knowledge-query.sh topics
  ... knowledge-query.sh search "query" [limit: 1..100]
  ... knowledge-query.sh neighbours "chunk-id" [n: 1..10]
No indexing or service startup. Results belong to the selected service's index.
EOF
  exit 2
}

[[ $# -ge 1 ]] || usage
api_url="${KNOWLEDGE_API_URL:-}"
[[ "$api_url" == http://127.0.0.1:* || "$api_url" == http://localhost:* ]] || {
  printf '%s\n' 'Set KNOWLEDGE_API_URL explicitly to a local knowledge service.' >&2
  exit 2
}
api_url="${api_url%/}"
action="$1"
shift
curl_args=(--fail --silent --show-error --connect-timeout 3 --max-time 60 --get)

case "$action" in
  count|topics)
    [[ $# -eq 0 ]] || usage
    ;;
  search|neighbours)
    [[ $# -ge 1 && $# -le 2 && -n "$1" ]] || usage
    value="$1"
    if [[ "$action" == search ]]; then
      number="${2:-8}"
      [[ "$number" =~ ^([1-9]|[1-9][0-9]|100)$ ]] || usage
      curl_args+=(--data-urlencode "query=$value" --data-urlencode "limit=$number")
    else
      number="${2:-2}"
      [[ "$number" =~ ^([1-9]|10)$ ]] || usage
      curl_args+=(--data-urlencode "id=$value" --data-urlencode "n=$number")
    fi
    ;;
  *) usage ;;
esac

curl "${curl_args[@]}" "$api_url/$action"
printf '\n'
