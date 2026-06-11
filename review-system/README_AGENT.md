# NTCode Review Writer Agent

全自动综述写作 Agent，7x24 小时运行，自行迭代改进。

## 快速开始

### 方法 1：直接使用 NTCode（推荐）

```bash
cd /mnt/c/Users/12860/Desktop/ntcode/review-system

# 启动综述写作
./ntcode_review.sh "单细胞转录组在肿瘤免疫微环境中的应用进展"
```

### 方法 2：使用完整工作流

```bash
cd /mnt/c/Users/12860/Desktop/ntcode/review-system

# 启动完整工作流（含质量自检和迭代改进）
./start_review_agent.sh "CRISPR基因编辑技术的最新进展" briefings 3
```

### 方法 3：在 NTCode 中手动启动

```bash
# 启动 NTCode
ntcode

# 然后输入：
写综述 单细胞转录组在肿瘤免疫微环境中的应用进展
```

## 工作流程

```
输入主题
    ↓
阶段 1：主题分析 → outline.json
    ↓
阶段 2：文献搜索 → refs.bib (50-100 篇)
    ↓
阶段 3：逐章撰写 → chapters/*.tex (8-12 章)
    ↓
阶段 4：图表生成 → figures/*.tex, tables/*.tex
    ↓
阶段 5：LaTeX 编译 → main.pdf
    ↓
阶段 6：质量自检 → quality_report.md
    ↓
阶段 7：迭代改进 → 修复问题，重新编译
    ↓
输出：完整 PDF
```

## 写作约束

### 禁止列表化
- 严禁使用 `\item`、`enumerate`、`itemize`
- 必须使用连贯的段落表达
- 禁止分点作答（1. xxx 2. xxx 3. xxx）

### 去除 AI 痕迹
- 禁止使用破折号（—）
- 禁止过度使用加粗、斜体
- 禁止机械连接词（Firstly/Secondly/Finally）
- 禁止"It is worth that..."
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

## 期刊模板

| 模板 | 期刊 | 特点 |
|------|------|------|
| briefings | Briefings in Bioinformatics | 双栏，系统性综述 |
| nature | Nature Reviews | 单栏，高影响力 |
| cell | Cell | 双栏，实验生物学 |
| science | Science | 单栏，综合科学 |

## 输出结构

```
output/review_YYYYMMDD_HHMMSS/
├── main.tex                    # LaTeX 源码
├── main.pdf                    # 可投稿 PDF
├── refs.bib                    # 参考文献
├── chapters/                   # 章节文件
│   ├── 01-intro.tex
│   ├── 02-background.tex
│   └── ...
├── figures/                    # 图表
├── tables/                     # 表格
├── boxes/                      # Box
├── quality_report.md           # 质量报告
└── review_log.md               # 运行日志
```

## 质量标准

- **文献覆盖**：≥50 篇，近 5 年为主
- **章节深度**：每章 ≥1500 词
- **引用规范**：所有引用可验证
- **语言质量**：无 AI 痕迹
- **图表数量**：≥2 图 + ≥2 表
- **段落规范**：无列表，连贯段落

## 自迭代机制

每轮迭代后，自动检查：
1. 引用完整性（`\citep` 都有对应 bib 条目）
2. 段落长度（150-250 词/段）
3. 列表检查（Box 除外）
4. AI 痕迹检查
5. 图表引用检查

如果不达标，自动修复并重新编译，最多 3 轮。

## 依赖环境

- **LaTeX**: texlive-xetex + texlive-lang-chinese
- **NTCode**: 已安装并配置

安装依赖：
```bash
sudo apt install texlive-xetex texlive-lang-chinese texlive-science
```

## 示例

### 示例 1：单细胞综述
```bash
./ntcode_review.sh "单细胞转录组在肿瘤免疫微环境中的应用进展"
```

### 示例 2：空间转录组综述
```bash
./ntcode_review.sh "空间转录组计算方法的系统性综述"
```

### 示例 3：CAF 综述
```bash
./ntcode_review.sh "乳腺癌癌相关成纤维细胞的单细胞异质性与靶向治疗"
```

## 故障排除

### 问题：PDF 编译失败
```bash
# 检查 LaTeX 安装
which xelatex && which bibtex

# 安装缺失的包
sudo apt install texlive-xetex texlive-lang-chinese texlive-science
```

### 问题：引用不完整
```bash
# 检查 refs.bib 文件
cat refs.bib

# 确保所有引用都有对应条目
grep -o '\\citep{[^}]*}' chapters/*.tex | sort -u
```

### 问题：段落长度不规范
```bash
# 检查段落长度
python3 -c "
import re
for f in ['chapters/01-intro.tex', 'chapters/02-background.tex']:
    with open(f) as fh:
        text = fh.read()
        paragraphs = re.split(r'\n\s*\n', text)
        for i, p in enumerate(paragraphs):
            words = len(p.split())
            if words < 100 or words > 300:
                print(f'{f}: 段落 {i+1} 有 {words} 词')
"
```

## 进阶用法

### 自定义输出目录
```bash
./ntcode_review.sh "主题" --output /path/to/output
```

### 指定期刊模板
```bash
./start_review_agent.sh "主题" nature 5
```

### 批量运行
```bash
# 创建任务列表
cat > topics.txt << EOF
单细胞转录组在肿瘤免疫微环境中的应用进展
CRISPR基因编辑技术的最新进展
人工智能在药物发现中的应用
EOF

# 批量运行
while read topic; do
    ./ntcode_review.sh "$topic"
done < topics.txt
```

## 许可证

MIT License
