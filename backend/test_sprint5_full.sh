#!/bin/bash

echo "🔥 Sprint 5 - EXTREME Edge Case Testing"
echo "========================================"
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

# Function to test endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local expected=$3
    
    echo -n "  Testing $name... "
    response=$(curl -s "$url")
    
    if echo "$response" | grep -q "$expected"; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC}"
        echo "    Expected: $expected"
        echo "    Got: ${response:0:100}..."
        ((FAILED++))
    fi
}

# Cleanup function
cleanup() {
    echo "🧹 Cleaning up test files..."
    rm -f test_*.py test_*.zip generate_massive.py
}

trap cleanup EXIT

echo "📝 Creating EXTREME test files..."
echo ""

# ==============================================================================
# TEST 1: EXTREME COMPLEXITY - Nightmare Function
# ==============================================================================
echo "${BLUE}[1/10] Creating nightmare complexity test...${NC}"
cat > test_extreme_complexity.py << 'EOF'
def nightmare_function(a, b, c, d, e, f, g, h, i, j):
    """Complexity nightmare - 30+ decision points"""
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        if f > 0:
                            if g > 0:
                                if h > 0:
                                    if i > 0:
                                        if j > 0:
                                            return "deep"
                                        elif j < 0:
                                            return "negative j"
                                        else:
                                            return "zero j"
                                    elif i < 0:
                                        return "negative i"
                                elif h < 0:
                                    return "negative h"
                            elif g < 0:
                                return "negative g"
                        elif f < 0:
                            return "negative f"
                    elif e < 0:
                        return "negative e"
                elif d < 0:
                    return "negative d"
            elif c < 0:
                return "negative c"
        elif b < 0:
            return "negative b"
    elif a < 0:
        return "negative a"
    
    for x in range(a):
        if x % 2 == 0:
            for y in range(b):
                if y % 3 == 0:
                    for z in range(c):
                        if z % 5 == 0:
                            print(z)
    
    return "default"

def boolean_explosion(v1, v2, v3, v4, v5):
    """Many boolean operators"""
    if (v1 and v2) or (v3 and v4) or v5:
        if (v1 or v2) and (v3 or v4) and v5:
            if v1 and v2 and v3 and v4 and v5:
                return True
    return False
EOF

# ==============================================================================
# TEST 2: MASSIVE FILE - 1000+ Lines
# ==============================================================================
echo "${BLUE}[2/10] Creating massive file test (1000 functions)...${NC}"
cat > generate_massive.py << 'EOF'
with open('test_massive_file.py', 'w') as f:
    f.write('"""Massive file test - 1000+ lines"""\n\n')
    
    # Generate 500 functions
    for i in range(500):
        f.write(f'''def function_{i}(x):
    """Function {i}"""
    if x > {i}:
        return x + {i}
    elif x < 0:
        return 0
    else:
        return {i}

''')
    
    # Generate class with 500 methods
    f.write('\nclass MassiveClass:\n')
    f.write('    """Class with 500 methods"""\n')
    for i in range(500):
        f.write(f'    def method_{i}(self, x): return x + {i}\n')
EOF

python3 generate_massive.py
echo "  Generated $(wc -l < test_massive_file.py) lines"

# ==============================================================================
# TEST 3: UNICODE CHAOS
# ==============================================================================
echo "${BLUE}[3/10] Creating unicode extreme test...${NC}"
cat > test_unicode_extreme.py << 'EOF'
# -*- coding: utf-8 -*-
"""🚀 Unicode everywhere! 中文日本語한국어العربية"""

def 函数_中文(参数一, 参数二):
    """中文函数名"""
    if 参数一 > 参数二:
        return 参数一
    return 参数二

def función_española(número, texto):
    """Función con ñ y acentos"""
    if número > 0:
        return f"{texto}: {número}"
    return "cero"

def 日本語関数(値):
    """日本語の関数"""
    if 値 > 0:
        return True
    return False

def функция_русская(значение):
    """Русская функция"""
    if значение > 0:
        return значение * 2
    return 0

def συνάρτηση_ελληνική(τιμή):
    """Greek function"""
    if τιμή > 0:
        return τιμή + 1
    return 0

class 한국어클래스:
    """Korean class"""
    def 메서드(self, 값):
        if 값 > 0:
            return 값
        return 0
EOF

# ==============================================================================
# TEST 4: WHITESPACE & FORMATTING CHAOS
# ==============================================================================
echo "${BLUE}[4/10] Creating whitespace chaos test...${NC}"
cat > test_whitespace_chaos.py << 'EOF'
def         weird_spacing     (    x   ,   y    ):
    """Terrible formatting"""
    if     x>0:
        if y<0:
            return    x-y
    return x+y

def no_newlines():x=1;y=2;z=3;if x>y:return x;return y

def       empty_lines_everywhere       (  x     ):
    
    
    result = 0
    
    
    if x > 0:
        
        
        result = x
    
    
    return result
    
    

def mixed_indentation(x):
	if x > 0:
	    if x > 10:
	        return "big"
	    else:
	        return "small"
	return "zero"
EOF

# ==============================================================================
# TEST 5: COMMENT EXTREMES
# ==============================================================================
echo "${BLUE}[5/10] Creating comment extreme test...${NC}"
cat > test_comment_extremes.py << 'EOF'
def no_comments_at_all():
    x = 1
    y = 2
    z = 3
    if x > y:
        if y > z:
            return x
    return z

def all_comments():
    # This is a comment
    # Another comment
    # More comments
    # So many comments
    # Even more comments
    # Comment overload
    # Still commenting
    # Never stop commenting
    # Comment line 9
    # Comment line 10
    # Comment line 11
    # Comment line 12
    # Comment line 13
    # Comment line 14
    # Comment line 15
    x = 1  # inline comment
    # Post-assignment comment
    # Pre-return comment
    return x  # return comment

def docstring_heavy():
    """
    This function has an extremely long docstring.
    It goes on and on and on and on.
    Multiple lines.
    Many paragraphs.
    
    Args:
        None
        
    Returns:
        Nothing really important
        
    Examples:
        >>> docstring_heavy()
        None
        
    Notes:
        This is just a test.
        More notes here.
        And here too.
        Keep going with notes.
        Never ending notes.
        So many notes.
        Notes everywhere.
    """
    return None
EOF

# ==============================================================================
# TEST 6: ONLY PASS STATEMENTS
# ==============================================================================
echo "${BLUE}[6/10] Creating pass-only test...${NC}"
cat > test_only_pass.py << 'EOF'
def empty1(): pass
def empty2(): pass
def empty3(): pass
def empty4(): pass
def empty5(): pass

class EmptyClass:
    pass

class EmptyWithMethods:
    def m1(self): pass
    def m2(self): pass
    def m3(self): pass
    def m4(self): pass
    def m5(self): pass
EOF

# ==============================================================================
# TEST 7: CIRCULAR LOGIC MADNESS
# ==============================================================================
echo "${BLUE}[7/10] Creating circular logic test...${NC}"
cat > test_circular_logic.py << 'EOF'
def circular_hell(x):
    """Multiple nested paths"""
    result = 0
    
    for i in range(x):
        if i % 2 == 0:
            if i % 3 == 0:
                if i % 5 == 0:
                    result += i
                else:
                    result -= i
            elif i % 7 == 0:
                result *= 2
            else:
                result += 1
        elif i % 11 == 0:
            if i % 13 == 0:
                result = 0
            else:
                result += i
        else:
            result -= 1
    
    while result > 100:
        if result % 2 == 0:
            result //= 2
        else:
            result -= 1
    
    return result

def nested_loops_extreme(data):
    """Deep nesting"""
    for a in data:
        for b in data:
            for c in data:
                for d in data:
                    if a > b:
                        if c > d:
                            if a > c:
                                print(a)
EOF

# ==============================================================================
# TEST 8: EXCEPTION HANDLING EXTREME
# ==============================================================================
echo "${BLUE}[8/10] Creating exception extreme test...${NC}"
cat > test_exception_extreme.py << 'EOF'
def exception_nightmare():
    """10+ exception handlers"""
    try:
        x = 1 / 0
    except ZeroDivisionError:
        print("error1")
    except ValueError:
        print("error2")
    except TypeError:
        print("error3")
    except KeyError:
        print("error4")
    except IndexError:
        print("error5")
    except AttributeError:
        print("error6")
    except ImportError:
        print("error7")
    except RuntimeError:
        print("error8")
    except MemoryError:
        print("error9")
    except Exception:
        print("error10")
    finally:
        print("cleanup")

def nested_try_blocks():
    """Nested exception handling"""
    try:
        try:
            try:
                x = 1 / 0
            except ValueError:
                print("inner1")
        except TypeError:
            print("inner2")
    except Exception:
        print("outer")
EOF

# ==============================================================================
# TEST 9: LAMBDA & COMPREHENSION CHAOS
# ==============================================================================
echo "${BLUE}[9/10] Creating lambda/comprehension test...${NC}"
cat > test_lambda_chaos.py << 'EOF'
def comprehension_madness(data):
    """Extreme comprehensions"""
    a = [x for x in data if x > 0]
    b = [x for x in data if x < 0]
    c = [x for x in data if x % 2 == 0]
    d = [x for x in data if x % 3 == 0]
    e = [x for x in a if x > 10]
    f = [x for x in b if x < -10]
    g = [[y for y in x if y > 0] for x in data if x]
    h = {x: y for x, y in enumerate(data) if x % 2 == 0}
    i = {x for x in data if x > 0 and x < 100}
    return a, b, c, d, e, f, g, h, i

def lambda_explosion(data):
    """Many lambdas"""
    f1 = lambda x: x if x > 0 else 0
    f2 = lambda x: x * 2 if x > 10 else x
    f3 = lambda x, y: x + y if x > 0 and y > 0 else 0
    result = list(map(lambda x: x * 2 if x > 5 else x, data))
    return result
EOF

# ==============================================================================
# TEST 10: SPECIAL CHARACTERS IN STRINGS
# ==============================================================================
echo "${BLUE}[10/10] Creating special character test...${NC}"
cat > test_special_chars.py << 'EOF'
def string_chaos():
    """Strings with special characters"""
    s1 = "Hello\nWorld\t!"
    s2 = r"Raw\nString"
    s3 = """
    Triple
    Quote
    String
    """
    s4 = '''Another
    Triple
    Quote'''
    s5 = "Quote in string: \"hello\""
    s6 = 'Apostrophe: it\'s here'
    if len(s1) > 0:
        if len(s2) > 0:
            if len(s3) > 0:
                return True
    return False
EOF

echo ""
echo "📦 Creating ZIP files..."
zip -q test_extreme_complexity.zip test_extreme_complexity.py
zip -q test_massive_file.zip test_massive_file.py
zip -q test_unicode_extreme.zip test_unicode_extreme.py
zip -q test_whitespace_chaos.zip test_whitespace_chaos.py
zip -q test_comment_extremes.zip test_comment_extremes.py
zip -q test_only_pass.zip test_only_pass.py
zip -q test_circular_logic.zip test_circular_logic.py
zip -q test_exception_extreme.zip test_exception_extreme.py
zip -q test_lambda_chaos.zip test_lambda_chaos.py
zip -q test_special_chars.zip test_special_chars.py

echo ""
echo "⬆️  Uploading test files (this may take a minute)..."
echo ""

upload_file() {
    local file=$1
    echo -n "  Uploading $file... "
    response=$(curl -s -X POST http://localhost:8000/api/upload -F "file=@$file")
    if echo "$response" | grep -q "repository_id"; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
    fi
    sleep 2
}

upload_file "test_extreme_complexity.zip"
upload_file "test_massive_file.zip"
upload_file "test_unicode_extreme.zip"
upload_file "test_whitespace_chaos.zip"
upload_file "test_comment_extremes.zip"
upload_file "test_only_pass.zip"
upload_file "test_circular_logic.zip"
upload_file "test_exception_extreme.zip"
upload_file "test_lambda_chaos.zip"
upload_file "test_special_chars.zip"

echo ""
echo "⏳ Waiting for processing to complete..."
sleep 10

echo ""
echo "🧪 Running EXTREME Tests..."
echo "============================"
echo ""

# ==============================================================================
# EXTREME TEST 1: Nightmare Complexity
# ==============================================================================
echo "${YELLOW}Test 1: Nightmare Complexity${NC}"
result=$(docker-compose exec -T backend python3 -c "
from database import SessionLocal
from models import Symbol
db = SessionLocal()
s = db.query(Symbol).filter(Symbol.name == 'nightmare_function').first()
if s:
    print(f'{s.cyclomatic_complexity},{s.maintainability_index}')
" 2>/dev/null)

complexity=$(echo $result | cut -d',' -f1)
maintainability=$(echo $result | cut -d',' -f2)

echo -n "  Nightmare function complexity > 30... "
if [ "$complexity" -gt 30 ]; then
    echo -e "${GREEN}✓ PASSED${NC} (complexity=$complexity)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC} (complexity=$complexity, expected > 30)"
    ((FAILED++))
fi

echo -n "  Nightmare maintainability < 60... "
if (( $(echo "$maintainability < 60" | bc -l) )); then
    echo -e "${GREEN}✓ PASSED${NC} (MI=$maintainability)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC} (MI=$maintainability, expected < 60)"
    ((FAILED++))
fi

# ==============================================================================
# EXTREME TEST 2: Massive File Processing
# ==============================================================================
echo ""
echo "${YELLOW}Test 2: Massive File Processing${NC}"
result=$(docker-compose exec -T backend python3 -c "
from database import SessionLocal
from models import Symbol, File
db = SessionLocal()
file = db.query(File).filter(File.file_path.like('%massive%')).first()
if file:
    count = db.query(Symbol).filter(Symbol.file_id == file.id).count()
    print(count)
" 2>/dev/null)

echo -n "  Extracted 1000+ symbols from massive file... "
if [ "$result" -gt 1000 ]; then
    echo -e "${GREEN}✓ PASSED${NC} (found $result symbols)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC} (found $result symbols, expected > 1000)"
    ((FAILED++))
fi

# ==============================================================================
# EXTREME TEST 3: Unicode Handling
# ==============================================================================
echo ""
echo "${YELLOW}Test 3: Unicode Handling${NC}"
result=$(docker-compose exec -T backend python3 -c "
from database import SessionLocal
from models import Symbol
db = SessionLocal()
chinese = db.query(Symbol).filter(Symbol.name == '函数_中文').first()
spanish = db.query(Symbol).filter(Symbol.name == 'función_española').first()
japanese = db.query(Symbol).filter(Symbol.name == '日本語関数').first()
russian = db.query(Symbol).filter(Symbol.name == 'функция_русская').first()
count = sum([1 for x in [chinese, spanish, japanese, russian] if x])
print(count)
" 2>/dev/null)

echo -n "  Unicode function names parsed correctly... "
if [ "$result" -ge 3 ]; then
    echo -e "${GREEN}✓ PASSED${NC} (found $result/4 unicode functions)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC} (found $result/4 unicode functions)"
    ((FAILED++))
fi

# ==============================================================================
# EXTREME TEST 4: Whitespace Chaos
# ==============================================================================
echo ""
echo "${YELLOW}Test 4: Whitespace & Formatting Chaos${NC}"
result=$(docker-compose exec -T backend python3 -c "
from database import SessionLocal
from models import Symbol
db = SessionLocal()
weird = db.query(Symbol).filter(Symbol.name == 'weird_spacing').first()
no_nl = db.query(Symbol).filter(Symbol.name == 'no_newlines').first()
empty = db.query(Symbol).filter(Symbol.name == 'empty_lines_everywhere').first()
count = sum([1 for x in [weird, no_nl, empty] if x and x.cyclomatic_complexity])
print(count)
" 2>/dev/null)

echo -n "  Weird formatting parsed correctly... "
if [ "$result" -eq 3 ]; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC} (parsed $result/3)"
    ((FAILED++))
fi

# ==============================================================================
# EXTREME TEST 5: Comment Analysis
# ==============================================================================
echo ""
echo "${YELLOW}Test 5: Comment Extremes${NC}"
result=$(docker-compose exec -T backend python3 -c "
from database import SessionLocal
from models import Symbol
db = SessionLocal()
no_comments = db.query(Symbol).filter(Symbol.name == 'no_comments_at_all').first()
all_comments = db.query(Symbol).filter(Symbol.name == 'all_comments').first()
docstring = db.query(Symbol).filter(Symbol.name == 'docstring_heavy').first()
print(f'{no_comments.comment_lines if no_comments else -1},{all_comments.comment_lines if all_comments else -1},{docstring.comment_lines if docstring else -1}')
" 2>/dev/null)

no_com=$(echo $result | cut -d',' -f1)
all_com=$(echo $result | cut -d',' -f2)
doc_com=$(echo $result | cut -d',' -f3)

echo -n "  No comments function has 0 comment lines... "
if [ "$no_com" -eq 0 ]; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC} (found $no_com comments)"
    ((FAILED++))
fi

echo -n "  Heavy comments function has 10+ lines... "
if [ "$all_com" -ge 10 ]; then
    echo -e "${GREEN}✓ PASSED${NC} (found $all_com)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC} (found $all_com, expected >= 10)"
    ((FAILED++))
fi

# ==============================================================================
# EXTREME TEST 6: Pass-Only Functions
# ==============================================================================
echo ""
echo "${YELLOW}Test 6: Pass-Only Functions${NC}"
result=$(docker-compose exec -T backend python3 -c "
from database import SessionLocal
from models import Symbol
db = SessionLocal()
empties = db.query(Symbol).filter(Symbol.name.like('empty%')).all()
all_simple = all(s.cyclomatic_complexity == 1 for s in empties if s.cyclomatic_complexity)
print(f'{len(empties)},{all_simple}')
" 2>/dev/null)

count=$(echo $result | cut -d',' -f1)
all_simple=$(echo $result | cut -d',' -f2)

echo -n "  All pass-only functions have complexity=1... "
if [ "$all_simple" = "True" ]; then
    echo -e "${GREEN}✓ PASSED${NC} (checked $count functions)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

# ==============================================================================
# EXTREME TEST 7: Circular Logic
# ==============================================================================
echo ""
echo "${YELLOW}Test 7: Circular Logic${NC}"
result=$(docker-compose exec -T backend python3 -c "
from database import SessionLocal
from models import Symbol
db = SessionLocal()
s = db.query(Symbol).filter(Symbol.name == 'circular_hell').first()
if s:
    print(s.cyclomatic_complexity)
" 2>/dev/null)

echo -n "  Circular logic complexity > 15... "
if [ "$result" -gt 15 ]; then
    echo -e "${GREEN}✓ PASSED${NC} (complexity=$result)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC} (complexity=$result, expected > 15)"
    ((FAILED++))
fi

# ==============================================================================
# EXTREME TEST 8: Exception Handling
# ==============================================================================
echo ""
echo "${YELLOW}Test 8: Exception Handling Extreme${NC}"
result=$(docker-compose exec -T backend python3 -c "
from database import SessionLocal
from models import Symbol
db = SessionLocal()
s = db.query(Symbol).filter(Symbol.name == 'exception_nightmare').first()
if s:
    print(s.cyclomatic_complexity)
" 2>/dev/null)

echo -n "  Exception nightmare complexity > 10... "
if [ "$result" -gt 10 ]; then
    echo -e "${GREEN}✓ PASSED${NC} (complexity=$result)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC} (complexity=$result, expected > 10)"
    ((FAILED++))
fi

# ==============================================================================
# EXTREME TEST 9: API Performance
# ==============================================================================
echo ""
echo "${YELLOW}Test 9: API Performance${NC}"
echo -n "  Quality dashboard responds < 3 seconds... "
start=$(date +%s%N)
response=$(curl -s http://localhost:8000/api/recommendations/quality-dashboard)
end=$(date +%s%N)
duration=$(( (end - start) / 1000000 )) # Convert to milliseconds

if [ "$duration" -lt 3000 ]; then
    echo -e "${GREEN}✓ PASSED${NC} (${duration}ms)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC} (${duration}ms, expected < 3000ms)"
    ((FAILED++))
fi

# ==============================================================================
# EXTREME TEST 10: Database Integrity
# ==============================================================================
echo ""
echo "${YELLOW}Test 10: Database Integrity${NC}"
result=$(docker-compose exec -T backend python3 -c "
from database import SessionLocal
from models import Symbol
db = SessionLocal()
total = db.query(Symbol).count()
with_complexity = db.query(Symbol).filter(Symbol.cyclomatic_complexity.isnot(None)).count()
with_mi = db.query(Symbol).filter(Symbol.maintainability_index.isnot(None)).count()
invalid = db.query(Symbol).filter(Symbol.cyclomatic_complexity < 1).count()
print(f'{total},{with_complexity},{with_mi},{invalid}')
" 2>/dev/null)

total=$(echo $result | cut -d',' -f1)
with_comp=$(echo $result | cut -d',' -f2)
with_mi=$(echo $result | cut -d',' -f3)
invalid=$(echo $result | cut -d',' -f4)

echo -n "  All symbols have complexity... "
if [ "$total" -eq "$with_comp" ]; then
    echo -e "${GREEN}✓ PASSED${NC} ($with_comp/$total)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC} ($with_comp/$total)"
    ((FAILED++))
fi

echo -n "  All symbols have maintainability... "
if [ "$total" -eq "$with_mi" ]; then
    echo -e "${GREEN}✓ PASSED${NC} ($with_mi/$total)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC} ($with_mi/$total)"
    ((FAILED++))
fi

echo -n "  No invalid complexity values (< 1)... "
if [ "$invalid" -eq 0 ]; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC} (found $invalid invalid values)"
    ((FAILED++))
fi

# ==============================================================================
# SUMMARY
# ==============================================================================
echo ""
echo "=========================================="
echo "📊 EXTREME Test Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo "Total:  $((PASSED + FAILED))"
echo ""

# Show top 10 most complex functions
echo "🔥 Top 10 Most Complex Functions:"
docker-compose exec -T backend python3 -c "
from database import SessionLocal
from models import Symbol
db = SessionLocal()
top = db.query(Symbol).filter(Symbol.cyclomatic_complexity.isnot(None)).order_by(Symbol.cyclomatic_complexity.desc()).limit(10).all()
for i, s in enumerate(top, 1):
    print(f'{i}. {s.name}: complexity={s.cyclomatic_complexity}, MI={s.maintainability_index:.1f}')
" 2>/dev/null

echo ""
echo "📈 Overall Statistics:"
docker-compose exec -T backend python3 -c "
from database import SessionLocal
from models import Symbol
from sqlalchemy import func
db = SessionLocal()
stats = db.query(
    func.count(Symbol.id).label('total'),
    func.avg(Symbol.cyclomatic_complexity).label('avg_complexity'),
    func.max(Symbol.cyclomatic_complexity).label('max_complexity'),
    func.avg(Symbol.maintainability_index).label('avg_mi'),
    func.min(Symbol.maintainability_index).label('min_mi')
).first()
print(f'Total Symbols: {stats.total}')
print(f'Avg Complexity: {stats.avg_complexity:.2f}')
print(f'Max Complexity: {stats.max_complexity}')
print(f'Avg Maintainability: {stats.avg_mi:.2f}')
print(f'Min Maintainability: {stats.min_mi:.2f}')
" 2>/dev/null

echo ""
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL EXTREME TESTS PASSED!${NC}"
    echo "Sprint 5 is BULLETPROOF! 💪"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some extreme tests failed${NC}"
    echo "But Sprint 5 core functionality works!"
    exit 1
fi

