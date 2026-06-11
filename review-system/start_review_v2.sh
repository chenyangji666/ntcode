#!/bin/bash
# NTCode 综述写作系统 v2 - 整合 Skill 版本
# 用法: ./start_review_v2.sh "综述主题" [期刊风格]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOPIC="$1"
JOURNAL="${2:-nature_reviews}"  # 默认 Nature Reviews

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查参数
if [ -z "$TOPIC" ]; then
    echo "=========================================="
    echo "  NTCode 综述写作系统 v2 (Skill 整合版)"
    echo "=========================================="
    echo ""
    echo "用法: $0 '综述主题' [期刊风格]"
    echo ""
    echo "期刊风格选项:"
    echo "  nature_reviews  - Nature Reviews (默认)"
    echo "  cell            - Cell"
    echo "  science         - Science"
    echo "  nature          - Nature"
    echo ""
    echo "示例:"
    echo "  $0 '单细胞转录组在肿瘤免疫微环境中的应用进展'"
    echo "  $0 'CRISPR基因编辑技术的最新进展' cell"
    echo "  $0 '人工智能在药物发现中的应用' science"
    exit 1
fi

# 检查依赖
print_info "检查依赖..."

# 检查 Claude Code
if ! command -v claude &> /dev/null; then
    print_error "Claude Code 未安装"
    exit 1
fi

# 检查 paper-search
if [ ! -d "/home/chenyangji/paper-search-mcp" ]; then
    print_warning "paper-search 未安装，将使用基础搜索"
fi

# 检查 Python
if ! command -v python3 &> /dev/null; then
    print_error "Python3 未安装"
    exit 1
fi

print_success "依赖检查完成"

# 创建输出目录
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="$SCRIPT_DIR/output/review_${TIMESTAMP}"
mkdir -p "$OUTPUT_DIR/paper"
mkdir -p "$OUTPUT_DIR/paper_rewriting_output"
mkdir -p "$OUTPUT_DIR/materials"

print_info "输出目录: $OUTPUT_DIR"

# 复制模板
print_info "复制期刊模板..."
TEMPLATE_FILE="$SCRIPT_DIR/templates/${JOURNAL}.tex"
if [ -f "$TEMPLATE_FILE" ]; then
    cp "$TEMPLATE_FILE" "$OUTPUT_DIR/paper/review.tex"
    print_success "已复制 ${JOURNAL} 模板"
else
    print_warning "未找到 ${JOURNAL} 模板，使用默认模板"
    cp "$SCRIPT_DIR/templates/nature_reviews.tex" "$OUTPUT_DIR/paper/review.tex"
fi

# 运行综述写作系统
print_info "启动综述写作系统..."
print_info "主题: $TOPIC"
print_info "期刊: $JOURNAL"
echo ""

cd "$SCRIPT_DIR"
python3 scripts/run_review_with_skills.py "$TOPIC"

# 检查结果
if [ -f "$OUTPUT_DIR/paper/review.pdf" ]; then
    print_success "综述写作完成！"
    echo ""
    echo "输出文件:"
    echo "  - PDF: $OUTPUT_DIR/paper/review.pdf"
    echo "  - LaTeX: $OUTPUT_DIR/paper/review.tex"
    echo "  - 参考文献: $OUTPUT_DIR/paper/references.bib"
    echo "  - 报告: $OUTPUT_DIR/REPORT.md"
    echo ""
    echo "打开 PDF:"
    echo "  xdg-open $OUTPUT_DIR/paper/review.pdf"
else
    print_warning "PDF 未生成，请检查日志"
    echo ""
    echo "查看日志:"
    echo "  cat $OUTPUT_DIR/REPORT.md"
fi

echo ""
print_info "完成！"
