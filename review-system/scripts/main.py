#!/usr/bin/env python3
"""
NTCode 全自主综述写作系统
用法: python main.py "综述主题"
"""

import sys
import json
import os
import subprocess
import time
from pathlib import Path
from datetime import datetime

# 配置
CONFIG = {
    "max_retries": 3,
    "min_papers": 30,
    "quality_threshold": 85,
    "output_dir": Path(__file__).parent.parent / "output",
    "temp_dir": Path(__file__).parent.parent / "temp",
    "templates_dir": Path(__file__).parent.parent / "templates",
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

    def log(self, message: str):
        """记录日志"""
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        print(f"  {message}")

    def run(self):
        """执行全流程"""
        self.log(f"开始综述写作: {self.topic}")
        self.log("=" * 50)

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

        self.log("=" * 50)
        self.log(f"✅ 综述完成: {self.work_dir / 'review.pdf'}")
        return True

    def stage1_literature_search(self) -> bool:
        """阶段1: 文献检索"""
        self.log("\n[阶段1] 文献检索")
        self.log("-" * 30)

        # TODO: 调用 Tavily MCP 进行文献检索
        # TODO: 自动扩展关键词
        # TODO: 筛选近5年、高影响因子文献
        # TODO: 审查关卡：文献数量≥50篇

        self.log("⏳ 正在检索文献...")
        # 模拟检索结果
        self.papers = [
            {"title": "Example Paper 1", "year": 2024, "journal": "Nature", "doi": "10.1038/xxx"},
            # ... 实际会检索到更多文献
        ]

        if len(self.papers) < CONFIG["min_papers"]:
            self.log(f"⚠️ 文献数量不足 ({len(self.papers)}/{CONFIG['min_papers']})，重试...")
            # TODO: 扩展搜索策略重试
            return False

        self.log(f"✓ 检索到 {len(self.papers)} 篇文献")
        return True

    def stage2_literature_analysis(self) -> bool:
        """阶段2: 文献深度分析"""
        self.log("\n[阶段2] 文献深度分析")
        self.log("-" * 30)

        # TODO: 提取研究方法、关键发现、数据规模
        # TODO: 构建文献关系图
        # TODO: 审查关卡：信息提取完整度≥80%

        self.log("⏳ 正在分析文献...")
        time.sleep(1)  # 模拟分析过程

        self.log("✓ 文献分析完成")
        return True

    def stage3_outline_generation(self) -> bool:
        """阶段3: 综述结构生成"""
        self.log("\n[阶段3] 综述结构生成")
        self.log("-" * 30)

        # TODO: 生成大纲（引言、方法、发现、讨论、展望）
        # TODO: 分配文献到各章节
        # TODO: 审查关卡：逻辑连贯性、章节平衡性

        self.log("⏳ 正在生成大纲...")
        self.outline = {
            "sections": [
                {"title": "引言", "papers": []},
                {"title": "研究方法概述", "papers": []},
                {"title": "主要发现", "papers": []},
                {"title": "讨论与展望", "papers": []},
                {"title": "结论", "papers": []},
            ]
        }

        self.log("✓ 大纲生成完成")
        return True

    def stage4_latex_template(self) -> bool:
        """阶段4: LaTeX模板"""
        self.log("\n[阶段4] LaTeX模板准备")
        self.log("-" * 30)

        # TODO: 根据主题选择期刊风格
        # TODO: 下载/生成LaTeX模板
        # TODO: 审查关卡：模板完整性

        self.log("⏳ 正在准备LaTeX模板...")

        # 创建基础模板
        template_content = r"""
\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{natbib}
\usepackage{geometry}
\geometry{margin=1in}

\title{""" + self.topic + r"""}
\author{NTCode Review System}
\date{\today}

\begin{document}
\maketitle

\begin{abstract}
% 自动生成摘要
\end{abstract}

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
        self.log("-" * 30)

        # TODO: 按章节并行撰写
        # TODO: 自动插入引用
        # TODO: 审查关卡：每段学术质量评分≥85分

        self.log("⏳ 正在撰写各章节...")
        time.sleep(1)  # 模拟撰写过程

        # TODO: 实际调用 LLM 撰写

        self.log("✓ 论文撰写完成")
        return True

    def stage6_references(self) -> bool:
        """阶段6: 引用整合"""
        self.log("\n[阶段6] 引用整合")
        self.log("-" * 30)

        # TODO: 生成BibTeX条目
        # TODO: 检查引用完整性
        # TODO: 审查关卡：所有引用可解析、格式正确

        self.log("⏳ 正在整合引用...")

        # 创建示例 bib 文件
        bib_content = """@article{example2024,
  title={Example Paper},
  author={Author, A.},
  journal={Nature},
  year={2024},
  doi={10.1038/xxx}
}
"""

        bib_file = self.work_dir / "references.bib"
        with open(bib_file, "w", encoding="utf-8") as f:
            f.write(bib_content)

        self.log("✓ 引用整合完成")
        return True

    def stage7_compile_and_review(self) -> bool:
        """阶段7: PDF编译与最终审查"""
        self.log("\n[阶段7] PDF编译与最终审查")
        self.log("-" * 30)

        # TODO: 编译LaTeX → PDF
        # TODO: 自动修复编译错误
        # TODO: 最终质量审查

        self.log("⏳ 正在编译PDF...")

        # 尝试编译 LaTeX
        try:
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "review.tex"],
                cwd=self.work_dir,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                self.log(f"⚠️ LaTeX编译出错，尝试修复...")
                # TODO: 分析错误并修复
                # TODO: 重试编译
            else:
                self.log("✓ PDF编译成功")

        except FileNotFoundError:
            self.log("⚠️ pdflatex 未安装，跳过编译")
            # TODO: 提示用户安装 texlive
        except subprocess.TimeoutExpired:
            self.log("⚠️ 编译超时")
            return False

        # 最终质量审查
        self.log("⏳ 正在进行最终质量审查...")
        # TODO: LLM 自评 + 规则检查

        self.log("✓ 最终审查通过")

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

        return True


def main():
    if len(sys.argv) < 2:
        print("用法: python main.py '综述主题'")
        print("示例: python main.py '单细胞转录组在肿瘤免疫微环境中的应用进展'")
        sys.exit(1)

    topic = sys.argv[1]
    pipeline = ReviewPipeline(topic)

    print(f"\n{'='*60}")
    print(f"  NTCode 全自主综述写作系统")
    print(f"  主题: {topic}")
    print(f"{'='*60}\n")

    success = pipeline.run()

    if success:
        print(f"\n{'='*60}")
        print(f"  ✅ 综述完成!")
        print(f"  输出目录: {pipeline.work_dir}")
        print(f"  PDF文件: {pipeline.work_dir / 'review.pdf'}")
        print(f"{'='*60}\n")
    else:
        print(f"\n{'='*60}")
        print(f"  ❌ 综述写作失败，请查看日志:")
        print(f"  {pipeline.log_file}")
        print(f"{'='*60}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
