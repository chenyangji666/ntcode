#!/bin/bash
# NTCode 综述写作 Agent - 简化版
# 直接启动 NTCode，注入综述写作系统提示词

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOPIC="$1"

if [ -z "$TOPIC" ]; then
    echo "用法: $0 '综述主题'"
    echo "示例: $0 '单细胞转录组在肿瘤免疫微环境中的应用进展'"
    exit 1
fi

# 创建输出目录
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="$SCRIPT_DIR/output/review_${TIMESTAMP}"
mkdir -p "$OUTPUT_DIR"

# 构建系统提示词
SYSTEM_PROMPT="# NTCode Review Writer — 全自动综述写作 Agent

你是 NTCode Review Writer，一个专注于撰写高质量学术综述的 AI agent。

## 当前任务

撰写一篇关于「${TOPIC}」的综述论文。

## 工作流程

1. 使用 WebSearch 搜索 50-100 篇相关文献
2. 生成 BibTeX 参考文献文件
3. 设计 8-12 章节结构
4. 逐章撰写（每章 1500-2500 词，连贯段落）
5. 使用 TikZ 生成概念图和流程图
6. 生成专业表格（booktabs 格式）
7. 组装 LaTeX 并编译 PDF
8. 质量自检（检查 AI 痕迹、引用完整性）
9. 迭代改进（最多 3 轮）

## 写作约束（铁律）

### 禁止列表化
- 严禁使用 \\item、enumerate、itemize（Box 除外）
- 必须使用连贯的段落表达
- 禁止分点作答

### 去除 AI 痕迹
- 禁止使用破折号（—）
- 禁止过度使用加粗、斜体
- 禁止机械连接词（Firstly/Secondly/Finally）
- 禁止\"It is worth noting that...\"
- 使用自然过渡

### 时态规范
- 一般现在时：描述方法、机制
- 过去时：提及特定研究
- 现在完成时：描述领域进展

### 段落结构
- 每段 150-250 词
- 首句主题句
- 后续句子展开论证
- 末句过渡或总结

## 输出要求

最终交付：
- main.tex（LaTeX 源码）
- main.pdf（可投稿 PDF）
- refs.bib（参考文献）
- quality_report.md（质量报告）

## 立即开始

不要询问确认，直接开始工作。输出进度日志，最终交付 PDF。
"

# 启动 NTCode
echo "=========================================="
echo "  NTCode Review Writer"
echo "=========================================="
echo ""
echo "主题: ${TOPIC}"
echo "输出: ${OUTPUT_DIR}"
echo ""
echo "启动 NTCode..."
echo ""

# 将系统提示词写入文件
echo "$SYSTEM_PROMPT" > "$OUTPUT_DIR/system_prompt.md"

# 启动 NTCode（注入系统提示词）
cd "$OUTPUT_DIR"
ntcode --system-prompt "$SYSTEM_PROMPT"

echo ""
echo "=========================================="
echo "  综述写作完成"
echo "=========================================="
echo ""
echo "输出目录: ${OUTPUT_DIR}"
echo "PDF: ${OUTPUT_DIR}/main.pdf"
