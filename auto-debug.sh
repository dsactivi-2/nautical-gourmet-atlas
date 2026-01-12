#!/bin/bash
#
# Nautical Gourmet Atlas - Auto Debug Script
# Führe dieses Script aus, um den Systemstatus zu prüfen
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASS=0
WARN=0
FAIL=0

echo "=========================================="
echo "  Nautical Gourmet Atlas - Debug Check"
echo "=========================================="
echo ""

# Helper functions
check_pass() {
    echo -e "  ${GREEN}✓ PASS${NC} $1"
    ((PASS++))
}

check_warn() {
    echo -e "  ${YELLOW}! WARN${NC} $1"
    ((WARN++))
}

check_fail() {
    echo -e "  ${RED}✗ FAIL${NC} $1"
    ((FAIL++))
}

# 1. Check Docker
echo "1. Docker Status"
echo "----------------"
if command -v docker &> /dev/null; then
    if docker info &> /dev/null; then
        check_pass "Docker is running"
    else
        check_fail "Docker is not running"
    fi
else
    check_fail "Docker is not installed"
fi

# 2. Check Docker Compose
echo ""
echo "2. Docker Compose"
echo "-----------------"
if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
    check_pass "Docker Compose available"
else
    check_fail "Docker Compose not available"
fi

# 3. Check Containers (if running)
echo ""
echo "3. Container Status"
echo "-------------------"
if docker ps --format '{{.Names}}' | grep -q "nautical-gourmet"; then
    docker ps --filter "name=nautical-gourmet" --format "  {{.Names}}: {{.Status}}"
    check_pass "Containers are running"
else
    check_warn "No nautical-gourmet containers running"
fi

# 4. Check Database Connection
echo ""
echo "4. Database Check"
echo "-----------------"
if docker ps --format '{{.Names}}' | grep -q "nautical-gourmet-db"; then
    if docker exec nautical-gourmet-db pg_isready -U postgres &> /dev/null; then
        check_pass "PostgreSQL is ready"
    else
        check_fail "PostgreSQL is not ready"
    fi
else
    check_warn "Database container not running"
fi

# 5. Check API Health
echo ""
echo "5. API Health Check"
echo "-------------------"
API_URL="${API_URL:-http://localhost:8000}"
if curl -s "${API_URL}/health" &> /dev/null; then
    HEALTH=$(curl -s "${API_URL}/health")
    if echo "$HEALTH" | grep -q '"status":"ok"'; then
        check_pass "API is healthy"
    else
        check_fail "API returned unhealthy status"
    fi
else
    check_warn "API not reachable at ${API_URL}"
fi

# 6. Check API Endpoints
echo ""
echo "6. API Endpoints"
echo "----------------"
if curl -s "${API_URL}/health" &> /dev/null; then
    # Categories
    if curl -s "${API_URL}/v1/categories" | grep -q '\['; then
        check_pass "GET /v1/categories"
    else
        check_fail "GET /v1/categories"
    fi

    # Filters
    if curl -s "${API_URL}/v1/filters" | grep -q '\['; then
        check_pass "GET /v1/filters"
    else
        check_fail "GET /v1/filters"
    fi

    # Partners
    if curl -s "${API_URL}/v1/partners" | grep -q '\['; then
        check_pass "GET /v1/partners"
    else
        check_fail "GET /v1/partners"
    fi

    # Treasures
    if curl -s "${API_URL}/v1/treasures" | grep -q '\['; then
        check_pass "GET /v1/treasures"
    else
        check_fail "GET /v1/treasures"
    fi
else
    check_warn "Skipping endpoint checks - API not reachable"
fi

# 7. Check Disk Space
echo ""
echo "7. System Resources"
echo "-------------------"
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    check_pass "Disk usage: ${DISK_USAGE}%"
elif [ "$DISK_USAGE" -lt 90 ]; then
    check_warn "Disk usage: ${DISK_USAGE}% (getting high)"
else
    check_fail "Disk usage: ${DISK_USAGE}% (critical)"
fi

# 8. Check Docker Logs for Errors
echo ""
echo "8. Recent Errors"
echo "----------------"
if docker ps --format '{{.Names}}' | grep -q "nautical-gourmet-api"; then
    ERRORS=$(docker logs nautical-gourmet-api 2>&1 | tail -50 | grep -i "error\|exception\|critical" | wc -l)
    if [ "$ERRORS" -eq 0 ]; then
        check_pass "No recent errors in API logs"
    else
        check_warn "${ERRORS} error(s) in recent API logs"
    fi
else
    check_warn "API container not running - cannot check logs"
fi

# Summary
echo ""
echo "=========================================="
echo "  Summary"
echo "=========================================="
echo -e "  ${GREEN}PASS: ${PASS}${NC}"
echo -e "  ${YELLOW}WARN: ${WARN}${NC}"
echo -e "  ${RED}FAIL: ${FAIL}${NC}"
echo ""

if [ "$FAIL" -gt 0 ]; then
    echo -e "${RED}Some checks failed. Please review above.${NC}"
    exit 1
elif [ "$WARN" -gt 0 ]; then
    echo -e "${YELLOW}Some warnings. System may need attention.${NC}"
    exit 0
else
    echo -e "${GREEN}All checks passed!${NC}"
    exit 0
fi
