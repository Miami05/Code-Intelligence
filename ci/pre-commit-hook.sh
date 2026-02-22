#!/bin/bash

CODE_INTEL_URL="${CODE_INTEL_URL:-http://localhost:8000}"
REPO_ID="${CODE_INTEL_REPO_ID}"

if [ -z "$REPO_ID" ]; then
  echo "⚠️  CODE_INTEL_REPO_ID not set — skipping quality gate"
  exit 0
fi

echo "🔍 Running Code Intelligence quality gate..."

RESPONSE=$(curl -s -X POST \
  "$CODE_INTEL_URL/api/cicd/quality-gate/$REPO_ID/check" \
  -H "Content-Type: application/json")

PASSED=$(echo "$RESPONSE" | python3 -c \
  "import sys,json; print(json.load(sys.stdin).get('passed', True))" 2>/dev/null)
SUMMARY=$(echo "$RESPONSE" | python3 -c \
  "import sys,json; print(json.load(sys.stdin).get('summary', ''))" 2>/dev/null)

echo "$SUMMARY"

if [ "$PASSED" = "False" ]; then
  echo ""
  echo "❌ Quality gate FAILED — commit blocked"
  echo "   Set SKIP_QUALITY_GATE=1 to bypass"
  [ "$SKIP_QUALITY_GATE" = "1" ] && echo "⚠️  Bypassing..." && exit 0
  exit 1
fi

echo "✅ Quality gate passed"
exit 0

