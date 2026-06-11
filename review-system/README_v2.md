# NTCode 综述写作系统 v2 - Skill 整合版

## 系统特点

- **零人工干预**：用户只输入主题，系统全自动完成
- **Skill 整合**：调用 40+ 个论文相关 skill
- **顶刊模板**：支持 Nature Reviews / Cell / Science 等顶刊风格
- **完整引用**：自动搜索文献、生成 BibTeX、验证引用
- **质量保证**：多轮自动审查、去 AI 痕迹

## 使用的 Skill

| Skill | 功能 | 阶段 |
|-------|------|------|
| `paper-search` | 文献搜索 | 阶段1 |
| `paper-spine-research` | 深度调研 | 阶段1 |
| `paper-spine-citation` | 引用构建 | 阶段2 |
| `paper-spine-build` | 论文构建 | 阶段3 |
| `paper-spine-latex` | LaTeX 处理 | 阶段4 |
| `paper-compile` | PDF 编译 | 阶段5 |
| `auto-review-loop` | 质量审查 | 阶段6 |
| `humanizer` | 去 AI 痕迹 | 阶段7 |
| `paper-spine-translate` | 翻译 | 阶段8 |

## 快速开始

### 1. 测试系统

```bash
cd /mnt/c/Users/12860/Desktop/ntcode/review-system
./start_review_v2.sh "单细胞转录组在肿瘤免疫微环境中的应用进展"
```

### 2. 指定期刊风格

```bash
# Nature Reviews (默认)
./start_review_v2.sh "CRISPR基因编辑技术的最新进展" nature_reviews

# Cell
./start_review_v2.sh "人工智能在药物发现中的应用" cell

# Science
./start_review_v2.sh "单细胞多组学技术进展" science
```

### 3. 查看输出

```bash
# 查看生成的 PDF
ls output/review_*/paper/review.pdf

# 查看报告
cat output/review_*/REPORT.md
```

## 输出结构

```
output/review_20260609_120000/
├── paper/
│   ├── review.tex          # LaTeX 源码
│   ├── review.pdf          # PDF 文件
│   └── references.bib      # 参考文献
├── paper_rewriting_output/
│   ├── paper_spine_config.json
│   ├── reference_materials/
│   └── translation_zh/     # 中文翻译
├── materials/              # 原始材料
└── REPORT.md               # 总结报告
```

## 工作流程

```
[输入] 综述主题
    ↓
[阶段1] 文献调研 (paper-search + paper-spine-research)
    ├─ 多源并行搜索：PubMed / arXiv / Semantic Scholar
    ├─ 自动筛选：近5年、高影响因子
    └─ 输出：文献库 + 调研报告
    ↓
[阶段2] 引用构建 (paper-spine-citation)
    ├─ 自动生成 BibTeX 条目
    ├─ 验证引用完整性
    └─ 输出：引用支持库
    ↓
[阶段3] 论文构建 (paper-spine-build)
    ├─ 选择顶刊模板
    ├─ 自动生成大纲
    ├─ 分段撰写
    └─ 输出：完整草稿
    ↓
[阶段4] LaTeX 处理 (paper-spine-latex)
    ├─ 图表插入
    ├─ 引用格式化
    └─ 输出：编译就绪的 LaTeX
    ↓
[阶段5] 编译 PDF (paper-compile)
    ├─ 自动编译
    ├─ 错误修复
    └─ 输出：PDF 文件
    ↓
[阶段6] 质量审查 (auto-review-loop)
    ├─ 多轮审查
    ├─ 自动修复
    └─ 输出：审查报告
    ↓
[阶段7] 去 AI 痕迹 (humanizer)
    ├─ 语言润色
    ├─ 风格调整
    └─ 输出：自然语言版本
    ↓
[阶段8] 翻译 (paper-spine-translate)
    ├─ 逐段翻译
    ├─ 术语统一
    └─ 输出：中文版本
    ↓
[输出] 完整综述 + PDF + 中文翻译
```

## 质量控制

- **文献数量**：≥ 30 篇（自动扩展搜索）
- **引用完整性**：100% 可验证
- **语言质量**：通过 humanizer 去 AI 痕迹
- **格式规范**：顶刊模板 + 自动编译
- **审查轮次**：最多 4 轮自动审查

## 注意事项

1. **网络要求**：需要网络连接进行文献搜索
2. **编译环境**：需要安装 texlive-xetex（中文支持）
3. **时间消耗**：完整流程约 30-60 分钟
4. **API 限制**：小米 API 有调用频率限制

## 故障排除

### 问题：文献搜索失败
```bash
# 检查 paper-search 是否安装
ls /home/chenyangji/paper-search-mcp

# 手动测试搜索
uv run --directory /home/chenyangji/paper-search-mcp paper-search search "CRISPR"
```

### 问题：PDF 编译失败
```bash
# 安装中文支持
sudo apt install texlive-xetex texlive-lang-chinese

# 手动编译
cd output/review_*/paper
xelatex review.tex
```

### 问题：Skill 调用失败
```bash
# 检查 Claude Code
claude --version

# 手动测试 skill
claude -p "/paper-search CRISPR"
```

## 更新日志

### v2.0 (2026-06-09)
- 整合 40+ 个论文相关 skill
- 支持顶刊模板（Nature Reviews / Cell / Science）
- 自动文献搜索和引用构建
- 多轮质量审查
- 去 AI 痕迹
- 中文翻译

### v1.0 (2026-06-09)
- 初始版本
- 基础 LLM 生成
- 简单 PDF 编译
