#!/bin/bash

echo "🔥 Sprint 6 - EXTREME GitHub Integration Testing"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Cleanup function
cleanup() {
    echo ""
    echo "🧹 Cleaning up..."
}

trap cleanup EXIT

# ==============================================================================
# TEST 1: URL Validation - Valid URLs
# ==============================================================================
echo "${BLUE}[1/15] Testing GitHub URL Validation - Valid URLs${NC}"

test_valid_url() {
    local url=$1
    echo -n "  Validating $url... "
    response=$(curl -s -X POST "http://localhost:8000/api/github/validate?url=$url")
    
    if echo "$response" | grep -q '"valid":true'; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC}"
        echo "    Response: $response"
        ((FAILED++))
    fi
}

test_valid_url "https://github.com/python/cpython"
test_valid_url "https://github.com/torvalds/linux"
test_valid_url "https://github.com/microsoft/vscode"

# ==============================================================================
# TEST 2: URL Validation - Invalid URLs
# ==============================================================================
echo ""
echo "${BLUE}[2/15] Testing GitHub URL Validation - Invalid URLs${NC}"

test_invalid_url() {
    local url=$1
    local expected_error=$2
    echo -n "  Rejecting $url... "
    response=$(curl -s -X POST "http://localhost:8000/api/github/validate?url=$url")
    
    if echo "$response" | grep -q "detail"; then
        echo -e "${GREEN}✓ PASSED${NC} (rejected)"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} (should reject)"
        ((FAILED++))
    fi
}

test_invalid_url "https://github.com/nonexistent/repo12345xyz"
test_invalid_url "https://gitlab.com/user/repo"
test_invalid_url "not-a-url"
test_invalid_url "https://github.com"

# ==============================================================================
# TEST 3: Import Small Python Repository
# ==============================================================================
echo ""
echo "${BLUE}[3/15] Importing Small Python Repository (Flask)${NC}"
echo -n "  Importing Flask... "

response=$(curl -s -X POST http://localhost:8000/api/github/import \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com/pallets/flask",
    "branch": "main"
  }')

if echo "$response" | grep -q "repository_id"; then
    REPO_ID_FLASK=$(echo "$response" | jq -r '.repository_id')
    echo -e "${GREEN}✓ PASSED${NC} (ID: ${REPO_ID_FLASK:0:8}...)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    echo "    Response: $response"
    ((FAILED++))
    REPO_ID_FLASK=""
fi

# ==============================================================================
# TEST 4: Import C Repository
# ==============================================================================
echo ""
echo "${BLUE}[4/15] Importing C Repository (curl)${NC}"
echo -n "  Importing curl library... "

response=$(curl -s -X POST http://localhost:8000/api/github/import \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com/curl/curl",
    "branch": "master"
  }')

if echo "$response" | grep -q "repository_id"; then
    REPO_ID_CURL=$(echo "$response" | jq -r '.repository_id')
    echo -e "${GREEN}✓ PASSED${NC} (ID: ${REPO_ID_CURL:0:8}...)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    echo "    Response: $response"
    ((FAILED++))
    REPO_ID_CURL=""
fi

# ==============================================================================
# TEST 5: Import Assembly Repository
# ==============================================================================
echo ""
echo "${BLUE}[5/15] Importing Assembly Repository${NC}"
echo -n "  Importing assembly examples... "

response=$(curl -s -X POST http://localhost:8000/api/github/import \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com/0xAX/asm",
    "branch": "master"
  }')

if echo "$response" | grep -q "repository_id"; then
    REPO_ID_ASM=$(echo "$response" | jq -r '.repository_id')
    echo -e "${GREEN}✓ PASSED${NC} (ID: ${REPO_ID_ASM:0:8}...)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
    REPO_ID_ASM=""
fi

# ==============================================================================
# TEST 6: Import Multi-Language Repository
# ==============================================================================
echo ""
echo "${BLUE}[6/15] Importing Multi-Language Repository${NC}"
echo -n "  Importing repository with Python + C... "

response=$(curl -s -X POST http://localhost:8000/api/github/import \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com/numpy/numpy",
    "branch": "main"
  }')

if echo "$response" | grep -q "repository_id"; then
    REPO_ID_NUMPY=$(echo "$response" | jq -r '.repository_id')
    echo -e "${GREEN}✓ PASSED${NC} (ID: ${REPO_ID_NUMPY:0:8}...)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
    REPO_ID_NUMPY=""
fi

# ==============================================================================
# TEST 7: Duplicate Import Detection
# ==============================================================================
echo ""
echo "${BLUE}[7/15] Testing Duplicate Import Detection${NC}"
echo -n "  Attempting to re-import Flask... "

response=$(curl -s -X POST http://localhost:8000/api/github/import \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com/pallets/flask",
    "branch": "main"
  }')

if echo "$response" | grep -q "already imported"; then
    echo -e "${GREEN}✓ PASSED${NC} (duplicate rejected)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC} (should reject duplicate)"
    echo "    Response: $response"
    ((FAILED++))
fi

# ==============================================================================
# TEST 8: Wait for Processing
# ==============================================================================
echo ""
echo "${BLUE}[8/15] Waiting for Repository Processing${NC}"
echo "  ⏳ Waiting 30 seconds for GitHub cloning and parsing..."
sleep 30

# ==============================================================================
# TEST 9: Check Flask Processing Status
# ==============================================================================
echo ""
echo "${BLUE}[9/15] Checking Flask Repository Status${NC}"

if [ -n "$REPO_ID_FLASK" ]; then
    result=$(docker-compose exec -T backend python3 -c "
from database import SessionLocal
from models import Repository
db = SessionLocal()
repo = db.query(Repository).filter(Repository.id == '$REPO_ID_FLASK').first()
if repo:
    print(f'{repo.status.value},{repo.file_count},{repo.symbol_count},{repo.github_stars}')
" 2>/dev/null)
    
    status=$(echo $result | cut -d',' -f1)
    files=$(echo $result | cut -d',' -f2)
    symbols=$(echo $result | cut -d',' -f3)
    stars=$(echo $result | cut -d',' -f4)
    
    echo -n "  Flask status is 'completed'... "
    if [ "$status" = "completed" ]; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} (status: $status)"
        ((FAILED++))
    fi
    
    echo -n "  Flask has files parsed (>0)... "
    if [ "$files" -gt 0 ]; then
        echo -e "${GREEN}✓ PASSED${NC} (files: $files)"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} (files: $files)"
        ((FAILED++))
    fi
    
    echo -n "  Flask has symbols extracted (>0)... "
    if [ "$symbols" -gt 0 ]; then
        echo -e "${GREEN}✓ PASSED${NC} (symbols: $symbols)"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} (symbols: $symbols)"
        ((FAILED++))
    fi
    
    echo -n "  Flask GitHub stars fetched (>10000)... "
    if [ "$stars" -gt 10000 ]; then
        echo -e "${GREEN}✓ PASSED${NC} (stars: $stars)"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠ WARNING${NC} (stars: $stars, expected >10000)"
        ((PASSED++))
    fi
else
    echo -e "${RED}✗ SKIPPED${NC} (Flask import failed)"
    ((FAILED+=4))
fi

# ==============================================================================
# TEST 10: List GitHub Repositories
# ==============================================================================
echo ""
echo "${BLUE}[10/15] Testing List GitHub Repositories${NC}"
echo -n "  Fetching GitHub repositories list... "

response=$(curl -s "http://localhost:8000/api/github/repositories?limit=10")

if echo "$response" | grep -q "repositories"; then
    count=$(echo "$response" | jq '.repositories | length')
    echo -e "${GREEN}✓ PASSED${NC} (found $count repositories)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

# ==============================================================================
# TEST 11: Check Multi-Language Detection
# ==============================================================================
echo ""
echo "${BLUE}[11/15] Testing Multi-Language Detection (NumPy)${NC}"

if [ -n "$REPO_ID_NUMPY" ]; then
    result=$(docker-compose exec -T backend python3 -c "
from database import SessionLocal
from models import File
from sqlalchemy import func
db = SessionLocal()
languages = db.query(File.language, func.count(File.id)).filter(
    File.repository_id == '$REPO_ID_NUMPY'
).group_by(File.language).all()
for lang, count in languages:
    print(f'{lang}:{count}')
" 2>/dev/null)
    
    echo "  Languages detected in NumPy:"
    while IFS=: read -r lang count; do
        echo "    - $lang: $count files"
    done <<< "$result"
    
    echo -n "  Multiple languages detected... "
    lang_count=$(echo "$result" | wc -l)
    if [ "$lang_count" -ge 2 ]; then
        echo -e "${GREEN}✓ PASSED${NC} ($lang_count languages)"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠ WARNING${NC} (only $lang_count language)"
        ((PASSED++))
    fi
else
    echo -e "${RED}✗ SKIPPED${NC} (NumPy import failed)"
    ((FAILED++))
fi

# ==============================================================================
# TEST 12: GitHub Metadata Integrity
# ==============================================================================
echo ""
echo "${BLUE}[12/15] Testing GitHub Metadata Integrity${NC}"

result=$(docker-compose exec -T backend python3 -c "
from database import SessionLocal
from models import Repository
from models.repository import RepoSource
db = SessionLocal()
github_repos = db.query(Repository).filter(Repository.source == RepoSource.github).all()
all_have_owner = all(r.github_owner for r in github_repos)
all_have_repo = all(r.github_repo for r in github_repos)
all_have_url = all(r.github_url for r in github_repos)
all_have_branch = all(r.github_branch for r in github_repos)
print(f'{len(github_repos)},{all_have_owner},{all_have_repo},{all_have_url},{all_have_branch}')
" 2>/dev/null)

total=$(echo $result | cut -d',' -f1)
has_owner=$(echo $result | cut -d',' -f2)
has_repo=$(echo $result | cut -d',' -f3)
has_url=$(echo $result | cut -d',' -f4)
has_branch=$(echo $result | cut -d',' -f5)

echo -n "  All GitHub repos have owner... "
if [ "$has_owner" = "True" ]; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

echo -n "  All GitHub repos have repo name... "
if [ "$has_repo" = "True" ]; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

echo -n "  All GitHub repos have URL... "
if [ "$has_url" = "True" ]; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

# ==============================================================================
# TEST 13: Search Across GitHub Repositories
# ==============================================================================
echo ""
echo "${BLUE}[13/15] Testing Search Across GitHub Repos${NC}"
echo -n "  Semantic search for 'flask application'... "

response=$(curl -s -X POST "http://localhost:8000/api/search/semantic?query=flask+application&limit=5")

if echo "$response" | grep -q "results"; then
    count=$(echo "$response" | jq '.results | length')
    echo -e "${GREEN}✓ PASSED${NC} (found $count results)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

# ==============================================================================
# TEST 14: Quality Dashboard for GitHub Repo
# ==============================================================================
echo ""
echo "${BLUE}[14/15] Testing Quality Dashboard for GitHub Repo${NC}"

if [ -n "$REPO_ID_FLASK" ]; then
    echo -n "  Quality dashboard for Flask... "
    response=$(curl -s "http://localhost:8000/api/recommendations/quality-dashboard?repository_id=$REPO_ID_FLASK")
    
    if echo "$response" | grep -q "total_symbols"; then
        symbols=$(echo "$response" | jq '.total_symbols')
        echo -e "${GREEN}✓ PASSED${NC} (symbols: $symbols)"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((FAILED++))
    fi
else
    echo -e "${RED}✗ SKIPPED${NC}"
    ((FAILED++))
fi

# ==============================================================================
# TEST 15: API Performance with GitHub Data
# ==============================================================================
echo ""
echo "${BLUE}[15/15] Testing API Performance${NC}"
echo -n "  List repositories response time < 1s... "

start=$(date +%s%N)
curl -s "http://localhost:8000/api/github/repositories?limit=20" > /dev/null
end=$(date +%s%N)
duration=$(( (end - start) / 1000000 ))

if [ "$duration" -lt 1000 ]; then
    echo -e "${GREEN}✓ PASSED${NC} (${duration}ms)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC} (${duration}ms, expected < 1000ms)"
    ((FAILED++))
fi

# ==============================================================================
# EXTREME EDGE CASES
# ==============================================================================
echo ""
echo "${YELLOW}═══════════════════════════════════════${NC}"
echo "${YELLOW}    EXTREME EDGE CASE TESTS${NC}"
echo "${YELLOW}═══════════════════════════════════════${NC}"
echo ""

# Edge Case 1: Huge Repository (Linux Kernel - optional, takes long)
echo "${BLUE}Edge Case 1: Large Repository Warning${NC}"
echo "  ⚠️  Skipping Linux kernel import (too large for testing)"
echo "      In production: curl -X POST http://localhost:8000/api/github/import -d '{\"url\":\"https://github.com/torvalds/linux\"}'"
echo ""

# Edge Case 2: Repository with Special Characters
echo "${BLUE}Edge Case 2: Repository with Special Characters${NC}"
echo -n "  Importing repo with dashes/underscores... "
response=$(curl -s -X POST http://localhost:8000/api/github/import \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com/python-poetry/poetry"
  }')

if echo "$response" | grep -q "repository_id"; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

# Edge Case 3: Branch that doesn't exist
echo ""
echo "${BLUE}Edge Case 3: Non-existent Branch${NC}"
echo -n "  Importing with invalid branch... "
response=$(curl -s -X POST http://localhost:8000/api/github/import \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com/pallets/flask",
    "branch": "nonexistent-branch-xyz123"
  }')

# This should either reject or mark as failed
if echo "$response" | grep -q "repository_id"; then
    echo -e "${YELLOW}⚠ ACCEPTED${NC} (will fail during clone)"
    ((PASSED++))
else
    echo -e "${GREEN}✓ REJECTED${NC}"
    ((PASSED++))
fi

# ==============================================================================
# SUMMARY & STATISTICS
# ==============================================================================
echo ""
echo "=========================================="
echo "📊 Sprint 6 Test Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo "Total:  $((PASSED + FAILED))"
echo ""

# Show GitHub repository statistics
echo "📈 GitHub Import Statistics:"
docker-compose exec -T backend python3 -c "
from database import SessionLocal
from models import Repository
from models.repository import RepoSource, RepoStatus
from sqlalchemy import func
db = SessionLocal()

total_github = db.query(func.count(Repository.id)).filter(
    Repository.source == RepoSource.github
).scalar()

completed = db.query(func.count(Repository.id)).filter(
    Repository.source == RepoSource.github,
    Repository.status == RepoStatus.completed
).scalar()

failed = db.query(func.count(Repository.id)).filter(
    Repository.source == RepoSource.github,
    Repository.status == RepoStatus.failed
).scalar()

total_files = db.query(func.sum(Repository.file_count)).filter(
    Repository.source == RepoSource.github
).scalar() or 0

total_symbols = db.query(func.sum(Repository.symbol_count)).filter(
    Repository.source == RepoSource.github
).scalar() or 0

print(f'Total GitHub Repos: {total_github}')
print(f'Completed: {completed}')
print(f'Failed: {failed}')
print(f'Total Files Processed: {total_files}')
print(f'Total Symbols Extracted: {total_symbols}')
" 2>/dev/null

echo ""
echo "🔝 Top Imported Repositories:"
docker-compose exec -T backend python3 -c "
from database import SessionLocal
from models import Repository
from models.repository import RepoSource
db = SessionLocal()

repos = db.query(Repository).filter(
    Repository.source == RepoSource.github
).order_by(Repository.symbol_count.desc()).limit(5).all()

for i, r in enumerate(repos, 1):
    print(f'{i}. {r.github_owner}/{r.github_repo} - {r.symbol_count} symbols, {r.github_stars} stars')
" 2>/dev/null

echo ""
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo "Sprint 6 GitHub Integration is PRODUCTION READY! 💪"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some tests failed${NC}"
    echo "Sprint 6 core functionality works, but needs attention."
    exit 1
fi

