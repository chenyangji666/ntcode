#!/bin/bash
# NTCode Review Agent 启动脚本
# 用法: ./start_review_agent.sh "综述主题" [期刊风格] [最大迭代次数]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOPIC="$1"
JOURNAL="${2:-briefings}"
MAX_ITERATIONS="${3:-3}"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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
    echo "  NTCode Review Agent - 全自动综述写作"
    echo "=========================================="
    echo ""
    echo "用法: $0 '综述主题' [期刊风格] [最大迭代次数]"
    echo ""
    echo "期刊风格选项:"
    echo "  briefings  - Briefings in Bioinformatics (默认)"
    echo "  nature     - Nature Reviews"
    echo "  cell       - Cell"
    echo "  science    - Science"
    echo ""
    echo "示例:"
    echo "  $0 '单细胞转录组在肿瘤免疫微环境中的应用进展'"
    echo "  $0 'CRISPR基因编辑技术的最新进展' nature"
    echo "  $0 '人工智能在药物发现中的应用' cell 5"
    exit 1
fi

# 检查依赖
print_info "检查依赖..."

# 检查 xelatex
if ! command -v xelatex &> /dev/null; then
    print_error "xelatex 未安装。请运行: sudo apt install texlive-xetex texlive-lang-chinese"
    exit 1
fi

# 检查 bibtex
if ! command -v bibtex &> /dev/null; then
    print_error "bibtex 未安装。请运行: sudo apt install texlive-base"
    exit 1
fi

print_success "依赖检查完成"

# 创建输出目录
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="$SCRIPT_DIR/output/review_${TIMESTAMP}"
mkdir -p "$OUTPUT_DIR"/{chapters,figures,tables,boxes}

print_info "输出目录: $OUTPUT_DIR"

# 复制模板
print_info "复制期刊模板..."
TEMPLATE_DIR="$SCRIPT_DIR/../.claude/skills/review-writer/templates"
if [ -d "$TEMPLATE_DIR" ]; then
    cp "$TEMPLATE_DIR/briefings-bioinformatics.cls" "$OUTPUT_DIR/" 2>/dev/null || true
    cp "$TEMPLATE_DIR/figures/"*.tex "$OUTPUT_DIR/figures/" 2>/dev/null || true
fi

# 复制 OUP 模板（如果存在）
OUP_TEMPLATE="/mnt/e/虚拟扰动/空间转录组综述/review-tex/oup-authoring-template.cls"
if [ -f "$OUP_TEMPLATE" ]; then
    cp "$OUP_TEMPLATE" "$OUTPUT_DIR/"
    cp "/mnt/e/虚拟扰动/空间转录组综述/review-tex/oup-abbrvnat.bst" "$OUTPUT_DIR/"
    print_success "OUP 模板已复制"
fi

# 启动 NTCode Review Agent
print_info "启动 NTCode Review Agent..."
print_info "主题: $TOPIC"
print_info "期刊: $JOURNAL"
print_info "最大迭代: $MAX_ITERATIONS"
echo ""

# 构建 NTCode 命令
NTCODE_CMD="cd $OUTPUT_DIR && ntcode --review-writer '$TOPIC' --journal $JOURNAL --max-iterations $MAX_ITERATIONS"

print_info "执行命令: $NTCODE_CMD"
print_info "按 Ctrl+C 可以中断（进度会保存）"
echo ""

# 运行 NTCode
eval "$NTCODE_CMD"

# 检查结果
if [ -f "$OUTPUT_DIR/main.pdf" ]; then
    print_success "综述写作完成！"
    echo ""
    echo "输出文件:"
    echo "  - PDF: $OUTPUT_DIR/main.pdf"
    echo "  - LaTeX: $OUTPUT_DIR/main.tex"
    echo "  - 参考文献: $OUTPUT_DIR/refs.bib"
    echo "  - 质量报告: $OUTPUT_DIR/quality_report.md"
    echo ""
    echo "打开 PDF:"
    echo "  xdg-open $OUTPUT_DIR/main.pdf"
else
    print_warning "PDF 未生成，请检查日志"
    echo ""
    echo "查看日志:"
    echo "  cat $OUTPUT_DIR/review_log.md"
fi

echo ""
print_info "完成！"
