#!/bin/bash
# Quick test: Upload test_project via API and check call graph

set -e

echo "🧪 Call Graph Quick Test"
echo "========================================"
echo ""

# Check if backend is running
echo "1. Checking if backend is running..."
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Backend is not running!"
    echo "Start it with: docker-compose up -d backend"
    exit 1
fi
echo "✅ Backend is running"
echo ""

# Create ZIP of test_project
echo "2. Creating ZIP of test_project..."
cd /Users/lediodurmishaj/Desktop/Code-Intelligence/backend
if [ ! -d "test_project" ]; then
    echo "❌ test_project directory not found!"
    exit 1
fi

zip -r /tmp/test_project.zip test_project/*.py > /dev/null 2>&1
echo "✅ Created /tmp/test_project.zip"
echo ""

# Upload via API
echo "3. Uploading to backend..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/upload \
    -F "file=@/tmp/test_project.zip" \
    -w "\n%{http_code}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" != "200" ]; then
    echo "❌ Upload failed (HTTP $HTTP_CODE)"
    echo "$BODY"
    exit 1
fi

REPO_ID=$(echo "$BODY" | grep -o '"repository_id":"[^"]*' | cut -d'"' -f4)
echo "✅ Uploaded! Repository ID: $REPO_ID"
echo ""

# Wait for processing
echo "4. Waiting for processing to complete..."
echo "(Make sure Celery worker is running: docker-compose up -d celery)"
for i in {1..30}; do
    STATUS=$(curl -s "http://localhost:8000/api/repositories/$REPO_ID" | grep -o '"status":"[^"]*' | cut -d'"' -f4)
    
    if [ "$STATUS" = "completed" ]; then
        echo "✅ Processing completed!"
        break
    elif [ "$STATUS" = "failed" ]; then
        echo "❌ Processing failed!"
        exit 1
    fi
    
    echo "   Status: $STATUS... waiting..."
    sleep 2
done
echo ""

# Check call graph
echo "5. Checking call graph..."
CALL_GRAPH=$(curl -s "http://localhost:8000/api/call-graph/repositories/$REPO_ID/call-graph")

TOTAL_FUNCTIONS=$(echo "$CALL_GRAPH" | grep -o '"total_functions":[0-9]*' | cut -d':' -f2)
TOTAL_CALLS=$(echo "$CALL_GRAPH" | grep -o '"total_calls":[0-9]*' | cut -d':' -f2)

echo "   Functions: $TOTAL_FUNCTIONS"
echo "   Calls: $TOTAL_CALLS"
echo ""

if [ "$TOTAL_CALLS" -gt "0" ]; then
    echo "✅ SUCCESS! Call graph extracted!"
    echo ""
    echo "View in browser:"
    echo "  http://localhost:3000/repositories/$REPO_ID"
else
    echo "⚠️  No call relationships found!"
    echo ""
    echo "Debug steps:"
    echo "  1. Check Celery logs: docker-compose logs celery"
    echo "  2. Verify files have source: python diagnose_call_graph.py"
    echo "  3. Check call graph task ran"
fi

echo ""
echo "========================================"
echo "Test complete!"
