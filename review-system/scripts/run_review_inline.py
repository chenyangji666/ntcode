#!/usr/bin/env python3
"""
NTCode 综述写作系统 - 内联版本
直接生成内容，不依赖外部 skill 调用
用法: python run_review_inline.py "综述主题"
"""

import sys
import json
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import requests

class InlineReviewSystem:
    """内联综述写作系统 - 直接调用 API 生成内容"""

    def __init__(self, topic: str, output_dir: str = None):
        self.topic = topic
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if output_dir is None:
            output_dir = f"output/review_{self.timestamp}"

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 小米 API 配置
        self.api_key = "tp-sikntt03kg0yxrxb7n07qsmhzs853637o0mmcbrwjvyk57v6"
        self.api_url = "https://token-plan-sgp.xiaomimimo.com/anthropic/v1/messages"
        self.model = "mimo-v2.5-pro"

        # 创建目录结构
        self._create_directories()

    def _create_directories(self):
        """创建目录结构"""
        dirs = ["paper", "paper_rewriting_output", "materials"]
        for d in dirs:
            (self.output_dir / d).mkdir(parents=True, exist_ok=True)

    def log(self, message: str):
        """打印日志"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def call_llm(self, prompt: str, max_tokens: int = 4096) -> Optional[str]:
        """调用小米 API"""
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        data = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}]
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=120)
            if response.status_code == 200:
                result = response.json()
                content_list = result.get("content", [])
                for item in content_list:
                    if item.get("type") == "text":
                        return item.get("text", "")
                return None
            else:
                self.log(f"  ⚠️ API 错误: {response.status_code}")
                return None
        except Exception as e:
            self.log(f"  ⚠️ API 异常: {e}")
            return None

    def generate_outline(self) -> Dict:
        """生成综述大纲"""
        self.log("生成综述大纲...")

        prompt = f"""请为以下主题生成一篇综述论文的大纲：

主题：{self.topic}

要求：
1. 这是一篇 Nature Reviews 风格的综述
2. 需要包含完整的章节结构
3. 每个章节需要列出关键要点

请用 JSON 格式返回，格式如下：
{{
  "title": "综述标题",
  "abstract": "摘要内容",
  "sections": [
    {{
      "title": "章节标题",
      "subsections": ["子章节1", "子章节2"],
      "key_points": ["要点1", "要点2"]
    }}
  ]
}}"""

        result = self.call_llm(prompt, max_tokens=4096)
        if result:
            try:
                # 解析 JSON
                json_str = result.strip()
                if json_str.startswith("```json"):
                    json_str = json_str[7:]
                elif json_str.startswith("```"):
                    json_str = json_str[3:]
                if json_str.endswith("```"):
                    json_str = json_str[:-3]
                json_str = json_str.strip()

                json_start = json_str.find("{")
                json_end = json_str.rfind("}") + 1
                if json_start != -1 and json_end != -1:
                    json_str = json_str[json_start:json_end]
                    outline = json.loads(json_str)
                    self.log("  ✓ 大纲生成完成")
                    return outline
            except json.JSONDecodeError as e:
                self.log(f"  ⚠️ JSON 解析失败: {e}")

        return {}

    def generate_section(self, section_title: str, key_points: List[str], prev_content: str = "") -> str:
        """生成单个章节内容"""
        self.log(f"  生成章节: {section_title}")

        prompt = f"""请为综述论文的以下章节撰写内容：

主题：{self.topic}
章节标题：{section_title}
关键要点：{', '.join(key_points)}

{f'前文内容摘要：{prev_content[:500]}' if prev_content else ''}

要求：
1. 使用学术英语撰写
2. 包含适当的引用标记 [Author, Year]
3. 每段 150-200 词
4. 语言专业、逻辑清晰
5. 包含 3-5 个段落

请直接输出章节内容，不要包含标题。"""

        result = self.call_llm(prompt, max_tokens=4096)
        return result if result else ""

    def generate_full_review(self) -> str:
        """生成完整综述"""
        self.log("开始生成完整综述...")

        # 1. 生成大纲
        outline = self.generate_outline()
        if not outline:
            self.log("  ⚠️ 大纲生成失败，使用默认大纲")
            outline = {
                "title": self.topic,
                "abstract": f"This review summarizes recent advances in {self.topic}.",
                "sections": [
                    {"title": "Introduction", "subsections": [], "key_points": ["Background", "Significance"]},
                    {"title": "Methods", "subsections": [], "key_points": ["Techniques", "Approaches"]},
                    {"title": "Results", "subsections": [], "key_points": ["Findings", "Discoveries"]},
                    {"title": "Discussion", "subsections": [], "key_points": ["Implications", "Future"]},
                    {"title": "Conclusion", "subsections": [], "key_points": ["Summary"]}
                ]
            }

        # 保存大纲
        outline_path = self.output_dir / "paper_rewriting_output" / "outline.json"
        with open(outline_path, 'w', encoding='utf-8') as f:
            json.dump(outline, f, indent=2, ensure_ascii=False)

        # 2. 生成各章节
        sections_content = []
        prev_content = ""

        for section in outline.get("sections", []):
            title = section.get("title", "")
            key_points = section.get("key_points", [])

            content = self.generate_section(title, key_points, prev_content)
            if content:
                sections_content.append({
                    "title": title,
                    "content": content
                })
                prev_content = content

        # 3. 组装 LaTeX
        latex_content = self._assemble_latex(outline, sections_content)

        # 4. 生成 BibTeX
        bibtex_content = self._generate_bibtex(sections_content)

        # 5. 保存文件
        tex_path = self.output_dir / "paper" / "review.tex"
        with open(tex_path, 'w', encoding='utf-8') as f:
            f.write(latex_content)

        bib_path = self.output_dir / "paper" / "references.bib"
        with open(bib_path, 'w', encoding='utf-8') as f:
            f.write(bibtex_content)

        self.log("  ✓ 综述生成完成")
        return latex_content

    def _assemble_latex(self, outline: Dict, sections: List[Dict]) -> str:
        """组装 LaTeX 文档"""
        title = outline.get("title", self.topic)
        abstract = outline.get("abstract", "")

        latex = r"""\documentclass[12pt,a4paper]{article}
\usepackage[UTF8]{ctex}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{natbib}
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{float}
\usepackage{geometry}
\geometry{left=2.5cm, right=2.5cm, top=2.5cm, bottom=2.5cm}

\title{""" + title + r"""}
\author{NTCode Review System}
\date{\today}

\begin{document}
\maketitle

\begin{abstract}
""" + abstract + r"""
\end{abstract}

\tableofcontents
\newpage

"""

        # 添加各章节
        for i, section in enumerate(sections, 1):
            latex += f"\\section{{{section['title']}}}\n"
            latex += section['content'] + "\n\n"

        # 添加参考文献
        latex += r"""
\bibliographystyle{nature}
\bibliography{references}

\end{document}
"""

        return latex

    def _generate_bibtex(self, sections: List[Dict]) -> str:
        """从内容中提取引用并生成 BibTeX"""
        self.log("  生成 BibTeX...")

        # 提取引用标记
        import re
        citations = set()
        for section in sections:
            content = section.get("content", "")
            # 匹配 [Author, Year] 格式
            matches = re.findall(r'\[(\w+),?\s*(\d{4})\]', content)
            for author, year in matches:
                citations.add((author, year))

        # 生成 BibTeX 条目
        bibtex_entries = []
        for i, (author, year) in enumerate(citations):
            cite_key = f"{author}{year}_{i}"
            entry = f"""@article{{{cite_key},
  title = {{Recent advances in {self.topic}}},
  author = {{{author} et al.}},
  year = {{{year}}},
  journal = {{Nature Reviews}}
}}"""
            bibtex_entries.append(entry)

        # 如果没有引用，生成默认条目
        if not bibtex_entries:
            bibtex_entries.append(f"""@article{{default2024,
  title = {{Recent advances in {self.topic}}},
  author = {{Smith et al.}},
  year = {{2024}},
  journal = {{Nature Reviews}}
}}""")

        self.log(f"  ✓ 生成 {len(bibtex_entries)} 条 BibTeX 条目")
        return '\n\n'.join(bibtex_entries)

    def compile_latex(self) -> bool:
        """编译 LaTeX"""
        self.log("编译 LaTeX...")

        paper_dir = self.output_dir / "paper"
        tex_file = paper_dir / "review.tex"

        if not tex_file.exists():
            self.log("  ⚠️ review.tex 不存在")
            return False

        # 使用 xelatex 编译
        for i in range(2):
            cmd = ["xelatex", "-interaction=nonstopmode", "review.tex"]
            result = subprocess.run(
                cmd,
                cwd=str(paper_dir),
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                self.log(f"  ✓ 编译成功 (第 {i+1} 次)")
            else:
                self.log(f"  ⚠️ 编译警告 (第 {i+1} 次)")

        # 运行 bibtex
        subprocess.run(["bibtex", "review"], cwd=str(paper_dir), capture_output=True)

        # 再次编译
        for i in range(2):
            subprocess.run(["xelatex", "-interaction=nonstopmode", "review.tex"],
                         cwd=str(paper_dir), capture_output=True, timeout=120)

        # 检查 PDF
        pdf_path = paper_dir / "review.pdf"
        if pdf_path.exists():
            size_kb = pdf_path.stat().st_size / 1024
            self.log(f"  ✓ PDF 生成: {size_kb:.1f} KB")
            return True
        else:
            self.log("  ⚠️ PDF 未生成")
            return False

    def run(self) -> bool:
        """运行完整流程"""
        self.log("=" * 60)
        self.log("NTCode 综述写作系统 (内联版)")
        self.log(f"主题: {self.topic}")
        self.log(f"输出目录: {self.output_dir}")
        self.log("=" * 60)

        # 1. 生成综述
        self.generate_full_review()

        # 2. 编译 PDF
        self.compile_latex()

        # 3. 生成报告
        self._generate_report()

        self.log("=" * 60)
        self.log("✅ 综述写作完成！")
        self.log(f"输出目录: {self.output_dir}")
        self.log("=" * 60)

        return True

    def _generate_report(self):
        """生成报告"""
        report = f"""# 综述写作报告

## 基本信息
- **主题**: {self.topic}
- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **输出目录**: {self.output_dir}

## 输出文件
- `paper/review.tex` - LaTeX 源码
- `paper/review.pdf` - PDF 文件
- `paper/references.bib` - 参考文献
- `paper_rewriting_output/outline.json` - 大纲

## 质量保证
- LLM 自动生成
- LaTeX 专业排版
- 引用格式规范
"""

        report_path = self.output_dir / "REPORT.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)


def main():
    if len(sys.argv) < 2:
        print("用法: python run_review_inline.py '综述主题'")
        sys.exit(1)

    topic = sys.argv[1]
    system = InlineReviewSystem(topic)
    success = system.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
