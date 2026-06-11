# NTCode 全自主综述写作系统

## 🎯 功能

自动完成综述论文的全流程，无需人工干预：

```
主题输入 → 文献检索 → 文献分析 → 大纲生成 → LaTeX模板 → 分段撰写 → 引用整合 → PDF输出
```

## 🚀 快速开始

### 基本用法
```bash
./start_review.sh "单细胞转录组在肿瘤免疫微环境中的应用进展"
```

### 带 Tavily API Key
```bash
./start_review.sh "CRISPR基因编辑技术的最新进展" tvly-xxxx
```

## 📋 系统要求

- Python 3.8+
- requests 库 (`pip install requests`)
- pdflatex (可选，用于PDF编译)
  ```bash
  sudo apt install texlive-full
  ```

## ⚙️ 配置

### 1. Tavily API Key (用于文献检索)

**方式一：编辑 config.json**
```json
{
  "api": {
    "tavily": {
      "api_key": "tvly-xxxx"
    }
  }
}
```

**方式二：环境变量**
```bash
export TAVILY_API_KEY="tvly-xxxx"
```

**获取 Tavily API Key:**
1. 访问 https://tavily.com
2. 注册账号
3. 获取免费 API Key (每月1000次搜索)

### 2. LLM API (小米 mimo-v2.5-pro)

已在 config.json 中配置，默认使用小米 API。

## 📁 输出结构

```
output/review_YYYYMMDD_HHMMSS/
├── review.pdf              # 最终论文
├── review.tex              # LaTeX源码
├── references.bib          # 参考文献
├── quality_report.md       # 质量审查报告
├── process_log.md          # 全流程日志
├── papers.json             # 检索到的文献
└── outline.json            # 综述大纲
```

## 🔄 工作流程

### 阶段1: 文献检索
- 多源并行搜索: PubMed + Google Scholar + Web
- 自动扩展关键词
- 筛选近5年、高影响因子文献
- 审查关卡: 文献数量≥30篇

### 阶段2: 文献深度分析
- 提取研究方法、关键发现
- 构建文献关系图
- 审查关卡: 信息提取完整度≥80%

### 阶段3: 综述结构生成
- 自动生成大纲 (引言、方法、发现、讨论、结论)
- 分配文献到各章节
- 审查关卡: 逻辑连贯性

### 阶段4: LaTeX模板
- 匹配期刊风格
- 生成标准模板
- 审查关卡: 模板完整性

### 阶段5: 分段撰写
- LLM自动撰写各章节
- 自动插入引用
- 审查关卡: 质量评分≥85分

### 阶段6: 引用整合
- 生成BibTeX条目
- 检查引用完整性
- 审查关卡: 引用格式正确

### 阶段7: PDF编译与审查
- 编译LaTeX → PDF
- 自动修复编译错误
- 最终质量审查
- 输出完整PDF

## 🛡️ 质量控制

- 每阶段自动审查
- 不通过自动重试 (最多3次)
- 生成详细质量报告
- 全流程日志记录

## 🔧 自愈机制

| 异常场景 | 自动处理策略 |
|----------|--------------|
| 文献检索失败 | 换搜索引擎、扩展关键词 |
| LaTeX编译错误 | 自动分析错误并修复 |
| 质量审查不通过 | 自动重写 (最多3次) |
| 网络超时 | 自动重试 (指数退避) |

## 📊 使用示例

### 示例1: 单细胞转录组
```bash
./start_review.sh "单细胞转录组在肿瘤免疫微环境中的应用进展"
```

### 示例2: CRISPR技术
```bash
./start_review.sh "CRISPR基因编辑技术的最新进展"
```

### 示例3: 人工智能+生物信息学
```bash
./start_review.sh "人工智能在生物信息学中的应用"
```

## 🐛 故障排除

### 问题: Tavily API 调用失败
**解决:**
1. 检查 API Key 是否正确
2. 检查网络连接
3. 查看 process_log.md 获取详细错误

### 问题: LaTeX 编译失败
**解决:**
1. 安装 texlive: `sudo apt install texlive-full`
2. 查看编译错误日志
3. 系统会自动尝试修复

### 问题: 质量审查不通过
**解决:**
1. 查看 quality_report.md 了解问题
2. 系统会自动重写
3. 如果多次失败，检查主题是否太宽泛

## 📝 注意事项

1. **网络连接**: 需要稳定的网络连接用于文献检索
2. **API 配额**: Tavily 免费版每月1000次搜索
3. **编译时间**: LaTeX编译可能需要几分钟
4. **主题选择**: 建议选择具体、明确的主题

## 🔗 相关链接

- Tavily API: https://tavily.com
- 小米大模型: https://xiaoai.mi.com
- LaTeX 安装: https://www.latex-project.org/get/

## 📧 反馈

如有问题或建议，请查看日志文件或联系开发者。
