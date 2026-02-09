#!/usr/bin/env bash
# ============================================================================
# FinSpeak Trader - Dev Environment Setup (macOS)
# Run: chmod +x setup.sh && ./setup.sh
# ============================================================================
set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

info()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
err()   { echo -e "${RED}[✗]${NC} $1"; }
step()  { echo -e "\n${GREEN}━━━ $1 ━━━${NC}"; }

# ============================================================================
# 1. Homebrew
# ============================================================================
step "1/7 - Homebrew"
if command -v brew &>/dev/null; then
    info "Homebrew already installed"
else
    warn "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    # Add to PATH for Apple Silicon
    if [[ -f /opt/homebrew/bin/brew ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
    fi
    info "Homebrew installed"
fi

# ============================================================================
# 2. Python 3.11+ (avoid 3.14, too new)
# ============================================================================
step "2/7 - Python"
if command -v python3 &>/dev/null; then
    PY_VERSION=$(python3 --version | awk '{print $2}')
    PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
    PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
    if [[ "$PY_MAJOR" -ge 3 && "$PY_MINOR" -ge 11 && "$PY_MINOR" -le 13 ]]; then
        info "Python $PY_VERSION OK"
    else
        warn "Python $PY_VERSION detected, installing 3.13..."
        brew install python@3.13
    fi
else
    warn "Installing Python 3.13..."
    brew install python@3.13
fi
info "Python: $(python3 --version)"

# ============================================================================
# 3. Node.js 20+ (for frontend later)
# ============================================================================
step "3/7 - Node.js"
if command -v node &>/dev/null; then
    NODE_VERSION=$(node --version | sed 's/v//' | cut -d. -f1)
    if [[ "$NODE_VERSION" -ge 20 ]]; then
        info "Node.js $(node --version) OK"
    else
        warn "Node.js too old, installing v22 LTS..."
        brew install node@22
    fi
else
    warn "Installing Node.js v22 LTS..."
    brew install node@22
fi
info "Node: $(node --version), npm: $(npm --version)"

# ============================================================================
# 4. InfluxDB 2.x
# ============================================================================
step "4/7 - InfluxDB"
if command -v influx &>/dev/null || brew list influxdb2 &>/dev/null 2>&1; then
    info "InfluxDB already installed"
else
    warn "Installing InfluxDB 2..."
    brew install influxdb2
fi

# Start InfluxDB if not running
if ! pgrep -x influxd &>/dev/null; then
    warn "Starting InfluxDB..."
    brew services start influxdb2
    sleep 3
    info "InfluxDB started on http://localhost:8086"
else
    info "InfluxDB already running"
fi

echo ""
warn "InfluxDB first-time setup:"
echo "  1. Open http://localhost:8086 in your browser"
echo "  2. Create org: 'finspeak', bucket: 'market_data'"
echo "  3. Copy the API token to your .env file"

# ============================================================================
# 5. Ollama (local LLM)
# ============================================================================
step "5/7 - Ollama"
if command -v ollama &>/dev/null; then
    info "Ollama already installed"
else
    warn "Installing Ollama..."
    brew install ollama
fi

# Start Ollama if not running
if ! pgrep -x ollama &>/dev/null; then
    warn "Starting Ollama service..."
    ollama serve &>/dev/null &
    sleep 2
fi

# Pull the model
warn "Pulling llama3.1:8b model (this may take a few minutes on first run)..."
ollama pull llama3.1:8b
info "Ollama ready with llama3.1:8b"

# ============================================================================
# 6. Project Dependencies
# ============================================================================
step "6/7 - Project Dependencies"

# Python venv + backend deps
if [[ ! -d "backend/.venv" ]]; then
    warn "Creating Python virtual environment..."
    python3 -m venv backend/.venv
fi

source backend/.venv/bin/activate
info "Activated venv: $(which python)"

warn "Installing Python dependencies..."
pip install --upgrade pip -q
pip install -r backend/requirements.txt -q
pip install pytest pytest-asyncio -q
info "Python dependencies installed"

# Node deps (root + future frontend)
warn "Installing Node dependencies..."
npm install --silent
info "Node dependencies installed"

# .env file
if [[ ! -f .env ]]; then
    cp .env.example .env
    warn "Created .env from template — FILL IN YOUR API KEYS"
else
    info ".env already exists"
fi

# ============================================================================
# 7. Claude Code
# ============================================================================
step "7/7 - Claude Code"
if command -v claude &>/dev/null; then
    info "Claude Code already installed: $(claude --version 2>/dev/null || echo 'installed')"
else
    warn "Installing Claude Code..."
    npm install -g @anthropic-ai/claude-code
    info "Claude Code installed"
fi

# Restore Claude memory from repo
CLAUDE_MEM_DIR="$HOME/.claude/projects/$(pwd | sed 's|/|--|g')/memory"
if [[ -f ".planning/MEMORY.md" && ! -f "$CLAUDE_MEM_DIR/MEMORY.md" ]]; then
    mkdir -p "$CLAUDE_MEM_DIR"
    cp .planning/MEMORY.md "$CLAUDE_MEM_DIR/MEMORY.md"
    info "Claude memory restored from .planning/MEMORY.md"
else
    info "Claude memory already in place (or no portable memory found)"
fi

# ============================================================================
# Summary
# ============================================================================
echo ""
echo -e "${GREEN}━━━ Setup Complete ━━━${NC}"
echo ""
echo "Before you start:"
echo "  1. Fill in API keys in .env"
echo "     - ALPHA_API_KEY  → https://www.alphavantage.co/support/#api-key"
echo "     - FMP_API_KEY    → https://financialmodelingprep.com/developer"
echo "     - INFLUXDB_TOKEN → from InfluxDB UI at http://localhost:8086"
echo ""
echo "  2. Populate InfluxDB (first time only):"
echo "     source backend/.venv/bin/activate"
echo "     python backend/influx-populate-script.py"
echo ""
echo "  3. Run the backend:"
echo "     source backend/.venv/bin/activate"
echo "     uvicorn backend.app.main:app --reload"
echo ""
echo "  4. Run tests:"
echo "     source backend/.venv/bin/activate"
echo "     cd backend && python -m pytest tests/ -v"
echo ""
echo "  5. Start Claude Code:"
echo "     claude"
echo ""
echo -e "${YELLOW}Current branch: $(git branch --show-current)${NC}"
echo -e "${YELLOW}Project status: Phases 1 & 2 complete, Phase 3 (RQI) next${NC}"
