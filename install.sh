#!/bin/bash
# VoIPTest - Installation and Testing Script

set -e

echo "=================================================="
echo "VoIPTest Installation and Testing"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version found"
echo ""

# Check if SIPp is installed
echo "Checking for SIPp..."
if command -v sipp &> /dev/null; then
    sipp_version=$(sipp -v 2>&1 | grep -i "sipp" | head -1 || echo "SIPp found")
    echo -e "${GREEN}✓ $sipp_version${NC}"
else
    echo -e "${YELLOW}⚠ SIPp not found. Tests will fail without SIPp.${NC}"
    echo "Install with: sudo apt-get install sipp (Ubuntu/Debian)"
    echo "           or: brew install sipp (macOS)"
fi
echo ""

# Check if Docker is installed
echo "Checking for Docker..."
if command -v docker &> /dev/null; then
    docker_version=$(docker --version)
    echo -e "${GREEN}✓ $docker_version${NC}"
else
    echo -e "${YELLOW}⚠ Docker not found. Lab environment will not be available.${NC}"
fi
echo ""

# Check if Docker Compose is installed
echo "Checking for Docker Compose..."
if command -v docker-compose &> /dev/null; then
    compose_version=$(docker-compose --version)
    echo -e "${GREEN}✓ $compose_version${NC}"
else
    echo -e "${YELLOW}⚠ Docker Compose not found. Lab environment will not be available.${NC}"
fi
echo ""

# Install voiptest
echo "Installing voiptest..."
if [ -f "pyproject.toml" ]; then
    pip install -e . > /dev/null 2>&1
    echo -e "${GREEN}✓ voiptest installed${NC}"
else
    echo -e "${RED}✗ pyproject.toml not found. Are you in the project root?${NC}"
    exit 1
fi
echo ""

# Check installation
echo "Verifying installation..."
if command -v voiptest &> /dev/null; then
    echo -e "${GREEN}✓ voiptest command available${NC}"
else
    echo -e "${RED}✗ voiptest command not found${NC}"
    exit 1
fi
echo ""

# Check project structure
echo "Checking project structure..."
required_files=(
    "voiptest/__init__.py"
    "voiptest/cli.py"
    "voiptest/config.py"
    "voiptest/runner.py"
    "voiptest/engines/sipp.py"
    "voiptest/engines/sipp_scenarios/uac_basic.xml"
    "voiptest/report/junit.py"
    "examples/smoke_basic.yaml"
    "docker-compose.yml"
    "lab/asterisk/extensions.conf"
    "lab/asterisk/pjsip.conf"
)

all_files_exist=true
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo -e "  ${RED}✗ $file (missing)${NC}"
        all_files_exist=false
    fi
done
echo ""

if [ "$all_files_exist" = false ]; then
    echo -e "${RED}✗ Some required files are missing${NC}"
    exit 1
fi

echo "=================================================="
echo "Installation Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Start the Docker lab:"
echo "   ${GREEN}docker-compose up -d${NC}"
echo ""
echo "2. Run tests:"
echo "   ${GREEN}voiptest run examples/smoke_basic.yaml${NC}"
echo ""
echo "3. Run all tests with JUnit output:"
echo "   ${GREEN}voiptest run examples/ --junit --out test-results${NC}"
echo ""
echo "4. View Asterisk logs:"
echo "   ${GREEN}docker-compose logs -f asterisk${NC}"
echo ""
echo "5. Stop the lab:"
echo "   ${GREEN}docker-compose down${NC}"
echo ""
echo "See README.md for more information."
echo ""
