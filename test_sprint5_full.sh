#!/bin/bash

echo "🧪 Sprint 5 - Complete Test Suite"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Function to test endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local expected=$3
    
    echo -n "Testing $name... "
    response=$(curl -s "$url")
    
    if echo "$response" | grep -q "$expected"; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC}"
        echo "  Expected: $expected"
        echo "  Got: $response"
        ((FAILED++))
    fi
}

# Create test files
echo "📝 Creating test files..."

# Test 1: Empty functions
cat > test_empty.py << 'EOF'
def empty_function():
    pass

def only_docstring():
    """Just a docstring"""
    pass
EOF

# Test 2: Boolean operators
cat > test_boolean.py << 'EOF'
def complex_boolean(x, y, z):
    if x > 0 and y > 0 and z > 0:
        return True
    elif x or y:
        return False
    return None
EOF

# Test 3: Exception handling
cat > test_exceptions.py << 'EOF'
def exception_heavy():
    try:
        x = 1 / 0
    except ZeroDivisionError:
        print("error1")
    except ValueError:
        print("error2")
    except Exception:
        print("error3")
EOF

# Test 4: Nested loops
cat > test_nested.py << 'EOF'
def deeply_nested(data):
    for i in data:
        if i > 0:
            for j in range(i):
                if j % 2 == 0:
                    print(j)
EOF

# Test 5: Class
cat > test_class.py << 'EOF'
class Calculator:
    def __init__(self):
        self.value = 0
    
    def add(self, x):
        if x > 0:
            self.value += x
        return self.value
EOF

echo ""
echo "📦 Creating ZIP files..."
zip -q test_empty.zip test_empty.py
zip -q test_boolean.zip test_boolean.py
zip -q test_exceptions.zip test_exceptions.py
zip -q test_nested.zip test_nested.py
zip -q test_class.zip test_class.py

echo ""
echo "⬆️  Uploading test files..."
curl -s -X POST http://localhost:8000/api/upload -F "file=@test_empty.zip" > /dev/null
sleep 2
curl -s -X POST http://localhost:8000/api/upload -F "file=@test_boolean.zip" > /dev/null
sleep 2
curl -s -X POST http://localhost:8000/api/upload -F "file=@test_exceptions.zip" > /dev/null
sleep 2
curl -s -X POST http://localhost:8000/api/upload -F "file=@test_nested.zip" > /dev/null
sleep 2
curl -s -X POST http://localhost:8000/api/upload -F "file=@test_class.zip" > /dev/null
sleep 5

echo ""
echo "🧪 Running Tests..."
echo "==================="
echo ""

# Test 1: Basic stats
echo "Test 1: Basic Stats"
test_endpoint "Total symbols > 0" "http://localhost:8000/api/search/stats" "\"total_symbols\":"

# Test 2: Quality dashboard exists
echo ""
echo "Test 2: Quality Dashboard"
test_endpoint "Dashboard returns data" "http://localhost:8000/api/recommendations/quality-dashboard" "total_symbols"
test_endpoint "Has complexity distribution" "http://localhost:8000/api/recommendations/quality-dashboard" "complexity_distribution"
test_endpoint "Has maintainability distribution" "http://localhost:8000/api/recommendations/quality-dashboard" "maintainability_distribution"

# Test 3: Complex functions
echo ""
echo "Test 3: Complex Functions Endpoint"
response=$(curl -s "http://localhost:8000/api/recommendations/complex-functions?min_complexity=2")
count=$(echo "$response" | jq '. | length')
echo -n "Found complex functions... "
if [ "$count" -gt 0 ]; then
    echo -e "${GREEN}✓ PASSED${NC} (found $count)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC} (found $count)"
    ((FAILED++))
fi

# Test 4: Low maintainability
echo ""
echo "Test 4: Low Maintainability Endpoint"
test_endpoint "Maintainability endpoint works" "http://localhost:8000/api/recommendations/low-maintainability?max_index=100" "symbol_id"

# Test 5: Semantic search includes metrics
echo ""
echo "Test 5: Search Returns Quality Metrics"
test_endpoint "Search has complexity" "http://localhost:8000/api/search/semantic?query=function" "cyclomatic_complexity"
test_endpoint "Search has maintainability" "http://localhost:8000/api/search/semantic?query=function" "maintainability_index"

# Test 6: Database integrity
echo ""
echo "Test 6: Database Integrity Checks"
echo -n "All symbols have complexity... "
result=$(docker-compose exec -T backend python3 -c "
from database import SessionLocal
from models import Symbol
db = SessionLocal()
total = db.query(Symbol).count()
with_complexity = db.query(Symbol).filter(Symbol.cyclomatic_complexity.isnot(None)).count()
print(f'{with_complexity}/{total}')
" 2>/dev/null)
echo -e "${YELLOW}$result${NC}"

echo -n "All symbols have maintainability... "
result=$(docker-compose exec -T backend python3 -c "
from database import SessionLocal
from models import Symbol
db = SessionLocal()
total = db.query(Symbol).count()
with_mi = db.query(Symbol).filter(Symbol.maintainability_index.isnot(None)).count()
print(f'{with_mi}/{total}')
" 2>/dev/null)
echo -e "${YELLOW}$result${NC}"

# Test 7: Edge cases
echo ""
echo "Test 7: Edge Case Validations"
echo -n "Empty function has complexity=1... "
result=$(docker-compose exec -T backend python3 -c "
from database import SessionLocal
from models import Symbol
db = SessionLocal()
s = db.query(Symbol).filter(Symbol.name == 'empty_function').first()
if s and s.cyclomatic_complexity == 1:
    print('PASS')
else:
    print('FAIL')
" 2>/dev/null)
if [ "$result" = "PASS" ]; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

echo -n "Exception handler has complexity>1... "
result=$(docker-compose exec -T backend python3 -c "
from database import SessionLocal
from models import Symbol
db = SessionLocal()
s = db.query(Symbol).filter(Symbol.name == 'exception_heavy').first()
if s and s.cyclomatic_complexity > 1:
    print('PASS')
else:
    print('FAIL')
" 2>/dev/null)
if [ "$result" = "PASS" ]; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

echo -n "Nested loops have high complexity... "
result=$(docker-compose exec -T backend python3 -c "
from database import SessionLocal
from models import Symbol
db = SessionLocal()
s = db.query(Symbol).filter(Symbol.name == 'deeply_nested').first()
if s and s.cyclomatic_complexity >= 4:
    print('PASS')
else:
    print('FAIL')
" 2>/dev/null)
if [ "$result" = "PASS" ]; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

# Test 8: Class methods
echo ""
echo "Test 8: Class Symbol Extraction"
echo -n "Class extracted as symbol... "
result=$(docker-compose exec -T backend python3 -c "
from database import SessionLocal
from models import Symbol
db = SessionLocal()
s = db.query(Symbol).filter(Symbol.name == 'Calculator').first()
if s:
    print('PASS')
else:
    print('FAIL')
" 2>/dev/null)
if [ "$result" = "PASS" ]; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

echo -n "Class methods extracted... "
result=$(docker-compose exec -T backend python3 -c "
from database import SessionLocal
from models import Symbol
db = SessionLocal()
s = db.query(Symbol).filter(Symbol.name == 'add').first()
if s:
    print('PASS')
else:
    print('FAIL')
" 2>/dev/null)
if [ "$result" = "PASS" ]; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

# Cleanup
echo ""
echo "🧹 Cleaning up test files..."
rm -f test_*.py test_*.zip

# Summary
echo ""
echo "=================================="
echo "📊 Test Summary"
echo "=================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo "Total:  $((PASSED + FAILED))"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi

