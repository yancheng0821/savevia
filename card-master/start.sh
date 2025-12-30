#!/bin/bash
#
# Card Master 启动脚本
# 使用 uv 管理依赖，自动初始化环境并启动服务
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  🎴 Card Master - 信用卡返现排行工具${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 检查 uv 是否安装
check_uv() {
    if ! command -v uv &> /dev/null; then
        echo -e "${RED}❌ 未找到 uv，请先安装：${NC}"
        echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    echo -e "${GREEN}✓${NC} uv 已安装"
}

# 创建/检查虚拟环境
setup_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        echo -e "${YELLOW}→${NC} 创建虚拟环境..."
        uv venv "$VENV_DIR" --python 3.13
        echo -e "${GREEN}✓${NC} 虚拟环境创建完成"
    else
        echo -e "${GREEN}✓${NC} 虚拟环境已存在"
    fi
}

# 安装依赖
install_deps() {
    echo -e "${YELLOW}→${NC} 检查依赖..."
    uv pip install -r "$PROJECT_DIR/requirements.txt" --python "$VENV_DIR/bin/python" -q
    echo -e "${GREEN}✓${NC} 依赖安装完成"
}

# 检查 Playwright 浏览器
check_playwright() {
    # 检查 Playwright 浏览器是否已安装
    if [ ! -d "$HOME/Library/Caches/ms-playwright" ] && [ ! -d "$HOME/.cache/ms-playwright" ]; then
        echo -e "${YELLOW}→${NC} 安装 Playwright 浏览器 (首次运行需要)..."
        "$VENV_DIR/bin/playwright" install chromium
        echo -e "${GREEN}✓${NC} Playwright 浏览器安装完成"
    else
        echo -e "${GREEN}✓${NC} Playwright 浏览器已就绪"
    fi
}

# 检查 .env 文件
check_env() {
    if [ ! -f "$PROJECT_DIR/.env" ]; then
        echo -e "${YELLOW}⚠${NC}  未找到 .env 文件，创建示例..."
        cat > "$PROJECT_DIR/.env" << 'EOF'
# LLM 提供商配置 (选择一个)
# DEFAULT_LLM_PROVIDER=volces
# VOLCES_API_KEY=your-api-key
# VOLCES_BASE_URL=https://ark.cn-beijing.volces.com/api/v3

# OPENAI_API_KEY=your-openai-key
# ANTHROPIC_API_KEY=your-anthropic-key
# GOOGLE_API_KEY=your-google-key
EOF
        echo -e "${YELLOW}⚠${NC}  请编辑 .env 文件配置 API Key"
    else
        echo -e "${GREEN}✓${NC} .env 文件已存在"
    fi
}

# 启动服务器
start_server() {
    local host="${1:-0.0.0.0}"
    local port="${2:-8000}"

    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}  🚀 启动服务器${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "  📍 地址: ${BLUE}http://localhost:${port}${NC}"
    echo -e "  📚 API 文档: ${BLUE}http://localhost:${port}/docs${NC}"
    echo ""
    echo -e "  ${YELLOW}按 Ctrl+C 停止服务${NC}"
    echo ""

    cd "$PROJECT_DIR"
    # --loop asyncio: 强制使用 asyncio 而不是 uvloop，避免与 nest_asyncio 冲突
    "$VENV_DIR/bin/uvicorn" main:app --host "$host" --port "$port" --reload --loop asyncio
}

# 显示帮助
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help       显示帮助信息"
    echo "  -p, --port PORT  指定端口 (默认: 8000)"
    echo "  --host HOST      指定绑定地址 (默认: 0.0.0.0)"
    echo "  --install-only   仅安装依赖，不启动服务"
    echo ""
    echo "示例:"
    echo "  $0                    # 使用默认配置启动"
    echo "  $0 -p 3000            # 使用端口 3000 启动"
    echo "  $0 --install-only     # 仅初始化环境"
}

# 主流程
main() {
    local port=8000
    local host="0.0.0.0"
    local install_only=false

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -p|--port)
                port="$2"
                shift 2
                ;;
            --host)
                host="$2"
                shift 2
                ;;
            --install-only)
                install_only=true
                shift
                ;;
            *)
                echo -e "${RED}未知选项: $1${NC}"
                show_help
                exit 1
                ;;
        esac
    done

    # 执行初始化
    check_uv
    setup_venv
    install_deps
    check_playwright
    check_env

    if [ "$install_only" = true ]; then
        echo ""
        echo -e "${GREEN}✅ 环境初始化完成!${NC}"
        echo ""
        echo "启动服务器: $0"
        echo "激活环境:   source .venv/bin/activate"
        exit 0
    fi

    # 启动服务器
    start_server "$host" "$port"
}

main "$@"
