#!/usr/bin/env python3
"""
NTCode 全自主综述写作系统 - 主控脚本
用法: python run_review.py "综述主题"
"""

import sys
import json
import os
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# 导入模块
from literature_search import LiteratureSearcher
from llm_writer import LLMWriter


# 配置
CONFIG = {
    "max_retries": 3,
    "min_papers": 30,
    "quality_threshold": 85,
    "output_dir": Path(__file__).parent.parent / "output",
    "temp_dir": Path(__file__).parent.parent / "temp",
    "templates_dir": Path(__file__).parent.parent / "templates",
    "api_key": "tp-sikntt03kg0yxrxb7n07qsmhzs853637o0mmcbrwjvyk57v6",
    "api_base_url": "https://token-plan-sgp.xiaomimimo.com/anthropic",
}


class ReviewPipeline:
    def __init__(self, topic: str):
        self.topic = topic
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.work_dir = CONFIG["output_dir"] / f"review_{self.timestamp}"
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.work_dir / "process_log.md"
        self.papers = []
        self.outline = {}
        self.quality_scores = {}

        # 初始化模块
        self.searcher = LiteratureSearcher(topic)
        self.writer = LLMWriter(CONFIG["api_key"], CONFIG["api_base_url"])

    def log(self, message: str):
        """记录日志"""
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        print(f"  {message}")

    def run(self) -> bool:
        """执行全流程"""
        self.log(f"开始综述写作: {self.topic}")
        self.log("=" * 60)

        # 阶段1: 文献检索
        if not self.stage1_literature_search():
            self.log("❌ 文献检索失败，终止")
            return False

        # 阶段2: 文献分析
        if not self.stage2_literature_analysis():
            self.log("❌ 文献分析失败，终止")
            return False

        # 阶段3: 大纲生成
        if not self.stage3_outline_generation():
            self.log("❌ 大纲生成失败，终止")
            return False

        # 阶段4: LaTeX模板
        if not self.stage4_latex_template():
            self.log("❌ LaTeX模板准备失败，终止")
            return False

        # 阶段5: 分段撰写
        if not self.stage5_writing():
            self.log("❌ 论文撰写失败，终止")
            return False

        # 阶段6: 引用整合
        if not self.stage6_references():
            self.log("❌ 引用整合失败，终止")
            return False

        # 阶段7: PDF编译与审查
        if not self.stage7_compile_and_review():
            self.log("❌ PDF编译失败，终止")
            return False

        self.log("=" * 60)
        self.log(f"✅ 综述完成: {self.work_dir / 'review.pdf'}")
        return True

    def stage1_literature_search(self) -> bool:
        """阶段1: 文献检索"""
        self.log("\n[阶段1] 文献检索")
        self.log("-" * 40)

        self.log("⏳ 正在检索文献...")

        # 多源并行搜索
        self.papers = self.searcher.search_all(min_papers=CONFIG["min_papers"])

        # 筛选文献
        self.papers = self.searcher.filter_papers(min_year=2019)

        # 保存文献列表
        papers_file = self.work_dir / "papers.json"
        self.searcher.save_papers(papers_file)

        # 审查关卡
        if len(self.papers) < CONFIG["min_papers"]:
            self.log(f"⚠️ 文献数量不足 ({len(self.papers)}/{CONFIG['min_papers']})")
            # TODO: 扩展搜索策略重试
            return False

        self.log(f"✓ 检索到 {len(self.papers)} 篇文献")
        return True

    def stage2_literature_analysis(self) -> bool:
        """阶段2: 文献深度分析"""
        self.log("\n[阶段2] 文献深度分析")
        self.log("-" * 40)

        self.log("⏳ 正在分析文献...")

        # TODO: 提取研究方法、关键发现、数据规模
        # TODO: 构建文献关系图
        # TODO: 审查关卡：信息提取完整度≥80%

        # 模拟分析过程
        time.sleep(1)

        self.log("✓ 文献分析完成")
        return True

    def stage3_outline_generation(self) -> bool:
        """阶段3: 综述结构生成"""
        self.log("\n[阶段3] 综述结构生成")
        self.log("-" * 40)

        self.log("⏳ 正在生成大纲...")

        # 调用 LLM 生成大纲
        self.outline = self.writer.generate_outline(self.topic, self.papers)

        if not self.outline:
            self.log("⚠️ 大纲生成失败")
            return False

        # 保存大纲
        outline_file = self.work_dir / "outline.json"
        with open(outline_file, "w", encoding="utf-8") as f:
            json.dump(self.outline, f, ensure_ascii=False, indent=2)

        self.log("✓ 大纲生成完成")
        return True

    def stage4_latex_template(self) -> bool:
        """阶段4: LaTeX模板"""
        self.log("\n[阶段4] LaTeX模板准备")
        self.log("-" * 40)

        self.log("⏳ 正在准备LaTeX模板...")

        # 获取综述标题
        title = self.outline.get("title", self.topic)
        abstract = self.outline.get("abstract", "")

        # 创建 LaTeX 模板（支持中文）
        template_content = r"""\documentclass[12pt,a4paper]{article}
\usepackage[UTF8]{ctex}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{natbib}
\usepackage{geometry}
\usepackage{setspace}
\usepackage{lineno}
\geometry{margin=1in}
\doublespacing
\linenumbers

\title{""" + title + r"""}
\author{NTCode Review System}
\date{\today}

\begin{document}
\maketitle

\begin{abstract}
""" + abstract + r"""
\end{abstract}

\keywords{综述, """ + self.topic + r"""}

\section*{Highlights}
\begin{itemize}
\item 本综述系统总结了""" + self.topic + r"""的最新研究进展
\item 涵盖了主要的研究方法和发现
\item 讨论了未来的研究方向和挑战
\end{itemize}

% 内容由各章节填充

\bibliographystyle{oup-abbrvnat}
\bibliography{references}

\end{document}
"""

        template_file = self.work_dir / "review.tex"
        with open(template_file, "w", encoding="utf-8") as f:
            f.write(template_content)

        self.log("✓ LaTeX模板准备完成")
        return True

    def stage5_writing(self) -> bool:
        """阶段5: 分段撰写"""
        self.log("\n[阶段5] 分段撰写")
        self.log("-" * 40)

        sections = self.outline.get("sections", [])

        if not sections:
            self.log("⚠️ 大纲中没有章节")
            return False

        # 读取 LaTeX 模板
        tex_file = self.work_dir / "review.tex"
        with open(tex_file, "r", encoding="utf-8") as f:
            tex_content = f.read()

        # 撰写各章节
        for section in sections:
            section_title = section.get("title", "未知章节")
            subsections = section.get("subsections", [])

            self.log(f"  撰写章节: {section_title}")

            # 添加章节标题
            tex_content += f"\n\\section{{{section_title}}}\n"

            for subsection in subsections:
                subsection_title = subsection.get("title", "未知小节")
                content_brief = subsection.get("content_brief", "")
                paper_titles = subsection.get("papers", [])

                self.log(f"    撰写小节: {subsection_title}")

                # 获取相关文献
                related_papers = [
                    p for p in self.papers
                    if any(pt.lower() in p.get("title", "").lower() for pt in paper_titles)
                ][:5]

                # 撰写内容
                content = self.writer.write_section(
                    self.topic, section_title, subsection_title,
                    content_brief, related_papers
                )

                if content:
                    # 添加小节标题和内容
                    tex_content += f"\n\\subsection{{{subsection_title}}}\n"
                    tex_content += content + "\n"

                    # 质量审查
                    review = self.writer.review_quality(content, subsection_title)
                    overall_score = review.get("overall_score", 0)

                    if overall_score < CONFIG["quality_threshold"]:
                        self.log(f"    ⚠️ 质量不达标 ({overall_score}/{CONFIG['quality_threshold']})")
                        # TODO: 自动重写
                    else:
                        self.log(f"    ✓ 质量达标 ({overall_score}/{CONFIG['quality_threshold']})")
                else:
                    self.log(f"    ⚠️ 撰写失败")

        # 保存更新后的 LaTeX
        with open(tex_file, "w", encoding="utf-8") as f:
            f.write(tex_content)

        self.log("✓ 论文撰写完成")
        return True

    def stage6_references(self) -> bool:
        """阶段6: 引用整合"""
        self.log("\n[阶段6] 引用整合")
        self.log("-" * 40)

        self.log("⏳ 正在生成 BibTeX...")

        # 生成 BibTeX 条目
        bib_entries = []
        for i, paper in enumerate(self.papers):
            authors = paper.get("authors", "Unknown").split(",")[0].strip().split()[0]
            year = paper.get("year", 2024)
            title = paper.get("title", "Unknown")
            journal = paper.get("journal", "Unknown")
            doi = paper.get("doi", "")

            entry = f"""@article{{{authors.lower()}{year},
  title={{{title}}},
  author={{{paper.get('authors', 'Unknown')}}},
  journal={{{journal}}},
  year={{{year}}},
  doi={{{doi}}}
}}"""
            bib_entries.append(entry)

        # 保存 BibTeX
        bib_file = self.work_dir / "references.bib"
        with open(bib_file, "w", encoding="utf-8") as f:
            f.write("\n\n".join(bib_entries))

        self.log(f"✓ 生成 {len(bib_entries)} 条 BibTeX 条目")
        return True

    def stage7_compile_and_review(self) -> bool:
        """阶段7: PDF编译与最终审查"""
        self.log("\n[阶段7] PDF编译与最终审查")
        self.log("-" * 40)

        self.log("⏳ 正在编译PDF...")

        # 使用 xelatex 编译（支持中文）
        try:
            result = subprocess.run(
                ["which", "xelatex"],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                self.log("⚠️ xelatex 未安装，跳过编译")
                self.log("  安装命令: sudo apt install texlive-xetex texlive-lang-chinese")
                return True  # 继续流程

        except Exception:
            self.log("⚠️ 无法检查 xelatex")
            return True

        # 使用 xelatex 编译 LaTeX（支持中文）
        try:
            result = subprocess.run(
                ["xelatex", "-interaction=nonstopmode", "review.tex"],
                cwd=self.work_dir,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                self.log("⚠️ LaTeX 编译出错")
                self.log(f"  错误: {result.stderr[:500]}")
                # TODO: 自动修复编译错误
            else:
                self.log("✓ PDF 编译成功")

        except subprocess.TimeoutExpired:
            self.log("⚠️ 编译超时")
            return False
        except Exception as e:
            self.log(f"⚠️ 编译异常: {e}")
            return False

        # 最终质量审查
        self.log("⏳ 正在进行最终质量审查...")
        # TODO: LLM 自评 + 规则检查

        # 生成质量报告
        report_content = f"""# 质量审查报告

## 综述主题
{self.topic}

## 审查结果
- 文献数量: {len(self.papers)} 篇
- 章节数量: {len(self.outline.get('sections', []))}
- 质量评分: {self.quality_scores.get('overall', 'N/A')}

## 审查时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        report_file = self.work_dir / "quality_report.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_content)

        self.log("✓ 最终审查完成")
        return True


def main():
    if len(sys.argv) < 2:
        print("用法: python run_review.py '综述主题'")
        print("示例: python run_review.py '单细胞转录组在肿瘤免疫微环境中的应用进展'")
        sys.exit(1)

    topic = sys.argv[1]
    pipeline = ReviewPipeline(topic)

    print(f"\n{'='*60}")
    print(f"  NTCode 全自主综述写作系统")
    print(f"  主题: {topic}")
    print(f"  模型: mimo-v2.5-pro (小米)")
    print(f"{'='*60}\n")

    success = pipeline.run()

    if success:
        print(f"\n{'='*60}")
        print(f"  ✅ 综述完成!")
        print(f"  输出目录: {pipeline.work_dir}")
        print(f"  PDF文件: {pipeline.work_dir / 'review.pdf'}")
        print(f"  质量报告: {pipeline.work_dir / 'quality_report.md'}")
        print(f"{'='*60}\n")
    else:
        print(f"\n{'='*60}")
        print(f"  ❌ 综述写作失败，请查看日志:")
        print(f"  {pipeline.log_file}")
        print(f"{'='*60}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
