#!/bin/bash
# NTCode 全自主综述写作系统 - 启动脚本
# 用法: ./start_review.sh "综述主题" [tavily_api_key]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOPIC="$1"
TAVILY_API_KEY="$2"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查参数
if [ -z "$TOPIC" ]; then
    echo "=========================================="
    echo "  NTCode 全自主综述写作系统"
    echo "=========================================="
    echo ""
    echo "用法: $0 '综述主题' [tavily_api_key]"
    echo ""
    echo "示例:"
    echo "  $0 '单细胞转录组在肿瘤免疫微环境中的应用进展'"
    echo "  $0 'CRISPR基因编辑技术的最新进展' tvly-xxxx"
    echo ""
    echo "配置说明:"
    echo "  1. 编辑 config.json 设置 Tavily API Key"
    echo "  2. 或者通过参数传入 Tavily API Key"
    echo "  3. Tavily API Key 可从 https://tavily.com 获取"
    echo ""
    exit 1
fi

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    print_error "Python3 未安装"
    exit 1
fi

# 检查 requests 库
if ! python3 -c "import requests" 2>/dev/null; then
    print_warn "requests 库未安装，正在安装..."
    pip3 install requests -q
fi

# 检查 LaTeX 环境
if ! command -v pdflatex &> /dev/null; then
    print_warn "pdflatex 未安装，PDF编译将跳过"
    print_info "安装命令: sudo apt install texlive-full"
fi

# 设置 Tavily API Key
if [ -n "$TAVILY_API_KEY" ]; then
    export TAVILY_API_KEY="$TAVILY_API_KEY"
    print_info "已设置 Tavily API Key"
fi

# 创建输出目录
mkdir -p "$SCRIPT_DIR/output"
mkdir -p "$SCRIPT_DIR/temp"

print_info "开始综述写作"
print_info "主题: $TOPIC"
print_info "输出目录: $SCRIPT_DIR/output"
echo ""

# 运行综述写作
cd "$SCRIPT_DIR"
python3 scripts/run_review.py "$TOPIC"

# 检查结果
if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "  ✅ 综述写作完成!"
    echo "=========================================="
    echo ""
    echo "输出文件:"
    echo "  - review.pdf: 最终论文"
    echo "  - review.tex: LaTeX源码"
    echo "  - references.bib: 参考文献"
    echo "  - quality_report.md: 质量报告"
    echo "  - process_log.md: 流程日志"
    echo ""
    echo "查看输出: ls -la output/"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "  ❌ 综述写作失败"
    echo "=========================================="
    echo ""
    echo "请查看日志文件获取详细信息"
    echo ""
    exit 1
fi
