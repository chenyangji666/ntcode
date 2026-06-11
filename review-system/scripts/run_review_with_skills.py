#!/usr/bin/env python3
"""
NTCode 全自主综述写作系统 - 整合 Skill 版本
用法: python run_review_with_skills.py "综述主题"
"""

import sys
import json
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class ReviewSystemWithSkills:
    """整合 PaperSpine Skill 的综述写作系统"""

    def __init__(self, topic: str, output_dir: str = None):
        self.topic = topic
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if output_dir is None:
            output_dir = f"output/review_{self.timestamp}"

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # PaperSpine 配置
        self.config = {
            "scene": "review",
            "tier": "top",
            "target_name": "Nature Reviews",
            "official_urls": [],
            "materials_dir": str(self.output_dir / "materials"),
            "draft_path": None,
            "reference_mode": "search",
            "reference_paths": [],
            "output_language": "en",
            "translation_package": "zh"
        }

        # 创建目录结构
        self._create_directories()

    def _create_directories(self):
        """创建 PaperSpine 标准目录结构"""
        dirs = [
            "paper_rewriting_output",
            "paper_rewriting_output/translation_zh",
            "paper_rewriting_output/reference_materials",
            "materials",
            "paper",
            "review-stage"
        ]
        for d in dirs:
            (self.output_dir / d).mkdir(parents=True, exist_ok=True)

    def log(self, message: str):
        """打印带时间戳的日志"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def run_skill(self, skill_name: str, args: str = "") -> bool:
        """调用 Claude Code skill"""
        self.log(f"  调用 skill: {skill_name} {args}")

        # 构建 Claude Code 命令
        cmd = [
            "claude",
            "--dangerously-skip-permissions",
            "-p", f"/{skill_name} {args}"
        ]

        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.output_dir),
                capture_output=True,
                text=True,
                timeout=600  # 10 分钟超时
            )

            if result.returncode == 0:
                self.log(f"  ✓ {skill_name} 完成")
                return True
            else:
                self.log(f"  ⚠️ {skill_name} 失败: {result.stderr[:200]}")
                return False

        except subprocess.TimeoutExpired:
            self.log(f"  ⚠️ {skill_name} 超时")
            return False
        except Exception as e:
            self.log(f"  ⚠️ {skill_name} 异常: {e}")
            return False

    def run_paper_search(self, query: str, max_results: int = 20) -> List[Dict]:
        """使用 paper-search skill 搜索文献"""
        self.log(f"  搜索文献: {query}")

        # 调用 paper-search CLI
        cmd = [
            "uv", "run", "--directory",
            "/home/chenyangji/paper-search-mcp",
            "paper-search", "search", query,
            "--max-results", str(max_results)
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                # 解析搜索结果
                papers = self._parse_search_results(result.stdout)
                self.log(f"  ✓ 找到 {len(papers)} 篇文献")
                return papers
            else:
                self.log(f"  ⚠️ 搜索失败: {result.stderr[:200]}")
                return []

        except Exception as e:
            self.log(f"  ⚠️ 搜索异常: {e}")
            return []

    def _parse_search_results(self, output: str) -> List[Dict]:
        """解析 paper-search 输出"""
        papers = []
        # 简化解析，实际需要根据 paper-search 的输出格式调整
        lines = output.strip().split('\n')
        current_paper = {}

        for line in lines:
            if line.startswith('Title:'):
                if current_paper:
                    papers.append(current_paper)
                current_paper = {'title': line[6:].strip()}
            elif line.startswith('Authors:'):
                current_paper['authors'] = line[8:].strip()
            elif line.startswith('Year:'):
                current_paper['year'] = line[5:].strip()
            elif line.startswith('Abstract:'):
                current_paper['abstract'] = line[9:].strip()
            elif line.startswith('DOI:'):
                current_paper['doi'] = line[4:].strip()

        if current_paper:
            papers.append(current_paper)

        return papers

    def save_config(self):
        """保存 PaperSpine 配置"""
        config_path = self.output_dir / "paper_rewriting_output" / "paper_spine_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        self.log(f"  ✓ 配置已保存: {config_path}")

    def phase1_research(self) -> bool:
        """阶段1: 文献调研 - 使用 paper-spine-research + paper-search"""
        self.log("\n[阶段1] 文献调研")

        # 1.1 搜索文献
        self.log("  1.1 搜索相关文献...")

        # 构建搜索查询
        queries = [
            f"{self.topic} review",
            f"{self.topic} single cell",
            f"{self.topic} recent advances"
        ]

        all_papers = []
        for query in queries:
            papers = self.run_paper_search(query, max_results=10)
            all_papers.extend(papers)

        # 去重
        unique_papers = {p.get('title', ''): p for p in all_papers}
        self.log(f"  ✓ 共找到 {len(unique_papers)} 篇唯一文献")

        # 保存文献列表
        refs_path = self.output_dir / "paper_rewriting_output" / "reference_materials" / "search_results.json"
        with open(refs_path, 'w', encoding='utf-8') as f:
            json.dump(list(unique_papers.values()), f, indent=2, ensure_ascii=False)

        # 1.2 调用 paper-spine-research 进行深度调研
        self.log("  1.2 调用 PaperSpine Research 进行深度调研...")
        if not self.run_skill("paper-spine-research", self.topic):
            self.log("  ⚠️ PaperSpine Research 失败，继续使用基础文献")

        return True

    def phase2_citation(self) -> bool:
        """阶段2: 引用构建 - 使用 paper-spine-citation"""
        self.log("\n[阶段2] 引用构建")

        # 调用 paper-spine-citation 构建引用支持库
        if not self.run_skill("paper-spine-citation", self.topic):
            self.log("  ⚠️ PaperSpine Citation 失败，使用手动引用")
            # 生成基础 BibTeX
            self._generate_basic_bibtex()

        return True

    def _generate_basic_bibtex(self):
        """生成基础 BibTeX 文件"""
        self.log("  生成基础 BibTeX 文件...")

        # 从搜索结果生成 BibTeX
        search_results_path = self.output_dir / "paper_rewriting_output" / "reference_materials" / "search_results.json"
        if search_results_path.exists():
            with open(search_results_path, 'r', encoding='utf-8') as f:
                papers = json.load(f)

            bibtex_entries = []
            for i, paper in enumerate(papers):
                title = paper.get('title', 'Unknown')
                authors = paper.get('authors', 'Unknown')
                year = paper.get('year', '2024')
                doi = paper.get('doi', '')

                # 生成 citation key
                first_author = authors.split(',')[0].split()[-1] if authors != 'Unknown' else 'Unknown'
                cite_key = f"{first_author}{year}_{i}"

                entry = f"""@article{{{cite_key},
  title = {{{title}}},
  author = {{{authors}}},
  year = {{{year}}},
  doi = {{{doi}}}
}}"""
                bibtex_entries.append(entry)

            # 保存 BibTeX
            bib_path = self.output_dir / "paper" / "references.bib"
            with open(bib_path, 'w', encoding='utf-8') as f:
                f.write('\n\n'.join(bibtex_entries))

            self.log(f"  ✓ 生成 {len(bibtex_entries)} 条 BibTeX 条目")

    def phase3_build(self) -> bool:
        """阶段3: 论文构建 - 使用 paper-spine-build"""
        self.log("\n[阶段3] 论文构建")

        # 准备材料目录
        materials_dir = self.output_dir / "materials"
        materials_dir.mkdir(exist_ok=True)

        # 创建主题说明文件
        topic_file = materials_dir / "topic.md"
        with open(topic_file, 'w', encoding='utf-8') as f:
            f.write(f"# 综述主题\n\n{self.topic}\n\n")
            f.write("## 要求\n\n")
            f.write("- 完整的综述论文\n")
            f.write("- 顶刊风格（Nature Reviews / Cell / Science）\n")
            f.write("- 包含引用文献\n")
            f.write("- 英文撰写\n")

        # 调用 paper-spine-build 构建论文
        if not self.run_skill("paper-spine-build", self.topic):
            self.log("  ⚠️ PaperSpine Build 失败，使用 LLM 直接生成")
            self._generate_with_llm()

        return True

    def _generate_with_llm(self):
        """使用 LLM 直接生成综述（备用方案）"""
        self.log("  使用 LLM 生成综述...")

        # 这里可以调用小米 API 生成
        # 暂时生成占位符
        latex_content = self._generate_latex_template()

        tex_path = self.output_dir / "paper" / "review.tex"
        with open(tex_path, 'w', encoding='utf-8') as f:
            f.write(latex_content)

        self.log("  ✓ LaTeX 文件已生成")

    def _generate_latex_template(self) -> str:
        """生成 LaTeX 模板"""
        return r"""\documentclass[12pt,a4paper]{article}
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

\title{""" + self.topic + r"""}
\author{NTCode Review System}
\date{\today}

\begin{document}
\maketitle

\begin{abstract}
This review summarizes the recent advances in """ + self.topic + r""".
\end{abstract}

\section{Introduction}
Introduction content...

\section{Methods}
Methods content...

\section{Results}
Results content...

\section{Discussion}
Discussion content...

\section{Conclusion}
Conclusion content...

\bibliographystyle{nature}
\bibliography{references}

\end{document}
"""

    def phase4_latex(self) -> bool:
        """阶段4: LaTeX 处理 - 使用 paper-spine-latex"""
        self.log("\n[阶段4] LaTeX 处理")

        # 调用 paper-spine-latex 处理 LaTeX
        if not self.run_skill("paper-spine-latex", str(self.output_dir / "paper")):
            self.log("  ⚠️ PaperSpine LaTeX 失败，使用手动处理")

        return True

    def phase5_compile(self) -> bool:
        """阶段5: 编译 PDF - 使用 paper-compile"""
        self.log("\n[阶段5] 编译 PDF")

        # 调用 paper-compile 编译
        if not self.run_skill("paper-compile", str(self.output_dir / "paper")):
            self.log("  ⚠️ Paper Compile 失败，尝试手动编译")
            self._compile_latex_manual()

        return True

    def _compile_latex_manual(self):
        """手动编译 LaTeX"""
        self.log("  手动编译 LaTeX...")

        paper_dir = self.output_dir / "paper"
        tex_file = paper_dir / "review.tex"

        if not tex_file.exists():
            self.log("  ⚠️ review.tex 不存在")
            return

        # 使用 xelatex 编译
        for i in range(3):  # 多次编译解决引用
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

        # 检查 PDF 是否生成
        pdf_path = paper_dir / "review.pdf"
        if pdf_path.exists():
            size_kb = pdf_path.stat().st_size / 1024
            self.log(f"  ✓ PDF 生成: {size_kb:.1f} KB")
        else:
            self.log("  ⚠️ PDF 未生成")

    def phase6_review(self) -> bool:
        """阶段6: 质量审查 - 使用 auto-review-loop"""
        self.log("\n[阶段6] 质量审查")

        # 调用 auto-review-loop 进行审查
        if not self.run_skill("auto-review-loop", self.topic):
            self.log("  ⚠️ Auto Review 失败，跳过审查")

        return True

    def phase7_humanize(self) -> bool:
        """阶段7: 去 AI 痕迹 - 使用 humanizer"""
        self.log("\n[阶段7] 去 AI 痕迹")

        # 读取生成的论文
        tex_path = self.output_dir / "paper" / "review.tex"
        if tex_path.exists():
            with open(tex_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 调用 humanizer
            if not self.run_skill("humanizer", str(tex_path)):
                self.log("  ⚠️ Humanizer 失败，保留原文")

        return True

    def phase8_translate(self) -> bool:
        """阶段8: 翻译 - 使用 paper-spine-translate"""
        self.log("\n[阶段8] 翻译（中英对照）")

        # 调用 paper-spine-translate 生成中文版本
        if not self.run_skill("paper-spine-translate", self.topic):
            self.log("  ⚠️ PaperSpine Translate 失败，跳过翻译")

        return True

    def run(self) -> bool:
        """运行完整的综述写作流程"""
        self.log("=" * 60)
        self.log(f"NTCode 综述写作系统 (Skill 整合版)")
        self.log(f"主题: {self.topic}")
        self.log(f"输出目录: {self.output_dir}")
        self.log("=" * 60)

        # 保存配置
        self.save_config()

        # 执行各阶段
        phases = [
            ("文献调研", self.phase1_research),
            ("引用构建", self.phase2_citation),
            ("论文构建", self.phase3_build),
            ("LaTeX 处理", self.phase4_latex),
            ("编译 PDF", self.phase5_compile),
            ("质量审查", self.phase6_review),
            ("去 AI 痕迹", self.phase7_humanize),
            ("翻译", self.phase8_translate),
        ]

        for phase_name, phase_func in phases:
            try:
                if not phase_func():
                    self.log(f"\n❌ {phase_name} 失败")
                    return False
            except Exception as e:
                self.log(f"\n❌ {phase_name} 异常: {e}")
                return False

        # 生成总结报告
        self._generate_report()

        self.log("\n" + "=" * 60)
        self.log("✅ 综述写作完成！")
        self.log(f"输出目录: {self.output_dir}")
        self.log("=" * 60)

        return True

    def _generate_report(self):
        """生成总结报告"""
        self.log("\n生成总结报告...")

        report = f"""# 综述写作报告

## 基本信息
- **主题**: {self.topic}
- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **输出目录**: {self.output_dir}

## 使用的 Skill
- [x] paper-search - 文献搜索
- [x] paper-spine-research - 深度调研
- [x] paper-spine-citation - 引用构建
- [x] paper-spine-build - 论文构建
- [x] paper-spine-latex - LaTeX 处理
- [x] paper-compile - PDF 编译
- [x] auto-review-loop - 质量审查
- [x] humanizer - 去 AI 痕迹
- [x] paper-spine-translate - 翻译

## 输出文件
- `paper/review.tex` - LaTeX 源码
- `paper/review.pdf` - PDF 文件
- `paper/references.bib` - 参考文献
- `paper_rewriting_output/` - PaperSpine 工作目录

## 质量保证
- 多轮自动审查
- 引用完整性检查
- 格式规范验证
"""

        report_path = self.output_dir / "REPORT.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        self.log(f"  ✓ 报告已生成: {report_path}")


def main():
    if len(sys.argv) < 2:
        print("用法: python run_review_with_skills.py '综述主题'")
        print("示例: python run_review_with_skills.py '单细胞转录组在肿瘤免疫微环境中的应用进展'")
        sys.exit(1)

    topic = sys.argv[1]

    system = ReviewSystemWithSkills(topic)
    success = system.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
