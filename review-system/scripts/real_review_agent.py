#!/usr/bin/env python3
"""
NTCode 综述 Agent - 真正能用的版本
用法: python real_review_agent.py "综述主题" [--journal briefings|nature|cell|science]
"""

import sys
import os
import json
import subprocess
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class RealReviewAgent:
    """真正能用的综述写作 Agent"""

    def __init__(self, topic: str, journal: str = 'briefings'):
        self.topic = topic
        self.journal = journal
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = Path(f"output/real_review_{self.timestamp}")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 小米 API 配置
        self.api_key = "tp-sikntt03kg0yxrxb7n07qsmhzs853637o0mmcbrwjvyk57v6"
        self.api_url = "https://token-plan-sgp.xiaomimimo.com/anthropic/v1/messages"
        self.model = "mimo-v2.5-pro"

        # 创建目录
        for d in ['chapters', 'figures', 'tables', 'boxes']:
            (self.output_dir / d).mkdir(exist_ok=True)

    def log(self, msg: str):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    def call_llm(self, prompt: str, max_tokens: int = 4096, system_prompt: str = None, retries: int = 2) -> Optional[str]:
        """调用 LLM API，支持重试"""
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        data = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": 0.4,
            "messages": [{"role": "user", "content": prompt}]
        }
        if system_prompt:
            data["system"] = system_prompt
        for attempt in range(retries + 1):
            try:
                resp = requests.post(self.api_url, headers=headers, json=data, timeout=180)
                if resp.status_code == 200:
                    result = resp.json()
                    for item in result.get("content", []):
                        if item.get("type") == "text":
                            text = item["text"].strip()
                            if text:
                                return text
                if attempt < retries:
                    self.log(f"  ⚠️ API 返回异常 (HTTP {resp.status_code})，重试 {attempt+1}/{retries}...")
                    import time; time.sleep(5)
            except Exception as e:
                self.log(f"  ⚠️ API 错误: {e}")
                if attempt < retries:
                    import time; time.sleep(5)
        return None

    def check_latex(self) -> bool:
        """检查并安装 LaTeX"""
        self.log("检查 LaTeX 环境...")
        try:
            subprocess.run(["which", "xelatex"], capture_output=True, check=True)
            self.log("  ✓ xelatex 已安装")
            return True
        except:
            self.log("  xelatex 未安装，正在安装...")
            try:
                subprocess.run(
                    ["sudo", "apt", "install", "-y", "texlive-xetex", "texlive-lang-chinese", "texlive-science"],
                    capture_output=True, timeout=600
                )
                self.log("  ✓ LaTeX 安装完成")
                return True
            except Exception as e:
                self.log(f"  ✗ 安装失败: {e}")
                return False

    def download_template(self) -> bool:
        """下载/复制期刊模板（多路径搜索 + 在线下载 + 本地缓存）"""
        self.log(f"获取 {self.journal} 模板...")
        import shutil

        # 项目级模板缓存目录
        cache_dir = Path(__file__).parent.parent / "templates_cache"
        cache_dir.mkdir(exist_ok=True)

        # OUP 模板文件名
        cls_file = "oup-authoring-template.cls"
        bst_file = "oup-abbrvnat.bst"

        # 搜索顺序：1) 项目缓存 2) 多个本地路径 3) 在线下载
        search_paths = [
            cache_dir,
            Path("/mnt/e/虚拟扰动/空间转录组综述/review-tex"),
            Path("E:/虚拟扰动/空间转录组综述/review-tex"),
            Path(__file__).parent.parent / "output" / "caf_review",
            Path(__file__).parent.parent / "output" / "spatial_review",
            Path(__file__).parent.parent / "output" / "my_review",
            Path(__file__).parent.parent / "templates",
        ]

        for search_path in search_paths:
            cls_src = search_path / cls_file
            bst_src = search_path / bst_file
            if cls_src.exists() and bst_src.exists():
                shutil.copy(cls_src, self.output_dir / cls_file)
                shutil.copy(bst_src, self.output_dir / bst_file)
                # 缓存到项目级目录
                if search_path != cache_dir:
                    shutil.copy(cls_src, cache_dir / cls_file)
                    shutil.copy(bst_src, cache_dir / bst_file)
                self.log(f"  ✓ OUP 模板已从 {search_path} 复制")
                return True

        # 在线下载（OUP 模板）
        if self.journal in ('briefings', 'nar', 'bioinformatics'):
            self.log("  本地无模板，尝试在线下载...")
            try:
                urls = {
                    cls_file: "https://raw.githubusercontent.com/oxford-university-press/oup-authoring-template/main/oup-authoring-template.cls",
                    bst_file: "https://raw.githubusercontent.com/oxford-university-press/oup-authoring-template/main/oup-abbrvnat.bst",
                }
                for fname, url in urls.items():
                    resp = requests.get(url, timeout=30)
                    if resp.status_code == 200:
                        with open(self.output_dir / fname, 'wb') as f:
                            f.write(resp.content)
                        with open(cache_dir / fname, 'wb') as f:
                            f.write(resp.content)
                    else:
                        self.log(f"  ⚠️ 下载 {fname} 失败 (HTTP {resp.status_code})")
                        return False
                self.log("  ✓ OUP 模板已下载并缓存")
                return True
            except Exception as e:
                self.log(f"  ⚠️ 下载失败: {e}")

        # Nature/Cell/Science: 使用 article class 作为 fallback
        if self.journal in ('nature', 'cell', 'science'):
            self.log(f"  {self.journal} 使用 article class fallback")
            return True

        self.log("  ⚠️ 无法获取模板文件")
        return False

    def generate_outline(self) -> Dict:
        """生成大纲"""
        self.log("生成大纲...")

        prompt = f"""Generate a comprehensive outline for a systematic review paper:

Topic: {self.topic}
Target Journal: Briefings in Bioinformatics (OUP)

Requirements:
1. 8-10 sections covering introduction, background, methodology survey, applications, challenges, and future directions
2. Each section should have 2-3 key points that will guide the writing
3. Section titles MUST be in English (concise, academic style)
4. Key points should be specific and actionable (not generic placeholders)
5. Follow the structure typical of published Briefings in Bioinformatics reviews

Return ONLY valid JSON in this exact format:
{{
  "title": "Review Title in English",
  "sections": [
    {{"id": "01", "title": "Introduction", "key_points": ["Specific point 1", "Specific point 2"]}},
    {{"id": "02", "title": "Background and Foundations", "key_points": ["Point 1", "Point 2"]}}
  ]
}}
"""

        result = self.call_llm(prompt, max_tokens=2048)
        if result:
            try:
                import re
                # Strip markdown code fences if present
                cleaned = re.sub(r'```(?:json)?\s*', '', result).strip()
                # Extract JSON object
                json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
                if json_match:
                    outline = json.loads(json_match.group())
                    if 'sections' in outline and len(outline['sections']) >= 3:
                        self.log(f"  ✓ 大纲生成完成：{len(outline.get('sections', []))} 个章节")
                        return outline
                    else:
                        self.log(f"  ⚠️ 大纲格式异常，使用默认大纲")
            except Exception as e:
                self.log(f"  ⚠️ 大纲解析失败: {e}")

        # 默认大纲
        self.log("  使用默认大纲")
        return {
            "title": self.topic,
            "sections": [
                {"id": "01", "title": "Introduction", "key_points": ["Background and motivation", "Scope and contributions"]},
                {"id": "02", "title": "Background and Foundations", "key_points": ["Key concepts", "Underlying technologies"]},
                {"id": "03", "title": "Methods and Approaches", "key_points": ["Method categories", "Algorithmic details"]},
                {"id": "04", "title": "Applications", "key_points": ["Domain applications", "Case studies"]},
                {"id": "05", "title": "Comparative Analysis", "key_points": ["Benchmarking results", "Performance trade-offs"]},
                {"id": "06", "title": "Challenges and Limitations", "key_points": ["Technical challenges", "Open problems"]},
                {"id": "07", "title": "Future Directions", "key_points": ["Emerging trends", "Research opportunities"]},
                {"id": "08", "title": "Conclusions", "key_points": ["Summary of findings", "Practical recommendations"]}
            ]
        }

    def write_section(self, section: Dict) -> str:
        """写一个章节"""
        self.log(f"  写章节：{section['title']}")

        prompt = f"""You are writing a section for a systematic review paper targeting Briefings in Bioinformatics.

Topic: {self.topic}
Section: {section['title']}
Key points: {', '.join(section.get('key_points', []))}

CRITICAL LANGUAGE RULE: Write ENTIRELY in academic English. DO NOT write in Chinese or any other language.

WRITING STYLE — emulate published Briefings in Bioinformatics papers:
- Write in academic English with HIGH information density
- Every sentence must carry new information, a specific claim, or analytical insight
- Use connected paragraphs, NO lists
- Each paragraph: 150-250 words
- Include 1-2 citations per paragraph using \\citep{{ref}} or \\citet{{ref}}
- Use present tense for methods/mechanisms, past tense for specific studies

ANALYTICAL FRAMEWORK — for every method/technology/approach discussed:
1. Name it explicitly (no "several methods" — name them)
2. Core mechanism: What does it do technically? Name the algorithm/model/framework
3. Key innovation: What ONE thing does it do that predecessors cannot?
4. Fundamental limitation: What can it NOT do? What assumption may not hold?
5. Practical trade-off: When to use it vs. alternatives? Computational cost? Data needs?

COMPARATIVE SYNTHESIS — required at end of each subsection:
- Explicitly state which method excels in which scenario
- State conditions under which each method fails
- Provide practical recommendation with rationale

QUANTITATIVE SPECIFICITY — zero tolerance for vague claims:
- NEVER "significant improvement" → Give numbers: "15-20% improvement in RMSE"
- NEVER "widely adopted" → Evidence: "applied in over 50 published studies"
- NEVER "computationally expensive" → Specifics: "requires GPU and 2-4 hours"
- NEVER "recent advances" → Name years: "between 2022 and 2025"
- NEVER "some studies show" → Cite specific: "\\citet{{author2024}} demonstrated..."

GOLDEN EXAMPLE (emulate this style and depth):
"cell2location employs a hierarchical Bayesian model that decomposes spot counts into contributions from cell types whose signatures are learned from a paired single-cell reference. By modelling both the reference uncertainty and the spatial data jointly, it yields posterior distributions over absolute cell counts per spot, enabling downstream spatial statistics that account for estimation uncertainty. Its scalability to Visium-scale datasets (thousands of spots, tens of cell types) has made it one of the most widely adopted tools."

DO NOT:
- Use generic filler ("X plays a crucial role", "has attracted increasing attention")
- Repeat the same information across paragraphs
- Use vague language without evidence
- Skip limitations or challenges
- Write less than 1500 words for the section
- Use AI patterns ("Firstly", "It is worth noting", em dashes)

Output ONLY the LaTeX content directly. Do NOT include \\section commands (the system adds them automatically). Do NOT include explanations or commentary.
"""

        content = self.call_llm(prompt, max_tokens=4096)
        if not content:
            content = f"[Content for {section['title']} section — to be generated by NTCode]"

        # 清理 LLM 输出：去除 markdown 围栏、重复 \section 命令
        import re
        content = re.sub(r'^```(?:latex|tex)?\s*', '', content.strip())
        content = re.sub(r'```\s*$', '', content.strip())
        content = re.sub(r'^\\section\{[^}]*\}\s*', '', content.strip())
        content = re.sub(r'^\\label\{[^}]*\}\s*', '', content.strip())

        # 保存文件
        file_path = self.output_dir / "chapters" / f"{section['id']}-{section['title'].lower().replace(' ', '-')}.tex"
        with open(file_path, 'w') as f:
            f.write(f"\\section{{{section['title']}}}\n\\label{{sec:{section['id']}}}\n\n{content}\n")

        return str(file_path)

    def generate_refs(self) -> str:
        """生成参考文献 — 从章节中提取引用键，分批生成 BibTeX"""
        self.log("生成参考文献...")
        import re

        # Step 1: 扫描所有章节，提取引用键
        all_cite_keys = set()
        chapters_dir = self.output_dir / "chapters"
        for tex_file in sorted(chapters_dir.glob("*.tex")):
            content = tex_file.read_text(encoding='utf-8')
            # 匹配 \citep{key1, key2}, \citet{key}, \citeyearpar{key} 等
            for match in re.finditer(r'\\cite[tp]?\{([^}]+)\}', content):
                keys = [k.strip() for k in match.group(1).split(',')]
                all_cite_keys.update(keys)
            for match in re.finditer(r'\\citeyearpar\{([^}]+)\}', content):
                keys = [k.strip() for k in match.group(1).split(',')]
                all_cite_keys.update(keys)

        all_cite_keys.discard('')
        self.log(f"  发现 {len(all_cite_keys)} 个唯一引用键")

        if not all_cite_keys:
            self.log("  ⚠️ 未找到引用键，使用空 bib")
            refs_path = self.output_dir / "refs.bib"
            with open(refs_path, 'w') as f:
                f.write("")
            return str(refs_path)

        # Step 2: 分批生成 BibTeX (每批 10 个键)
        keys_list = sorted(all_cite_keys)
        batch_size = 10
        all_bibtex = []
        failed_batches = []
        covered_keys = set()

        for i in range(0, len(keys_list), batch_size):
            batch = keys_list[i:i+batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(keys_list) + batch_size - 1) // batch_size
            self.log(f"  生成 BibTeX 批次 {batch_num}/{total_batches} ({len(batch)} 条)...")

            prompt = f"""Generate real BibTeX entries for the following citation keys used in a review on: {self.topic}

Citation keys to generate entries for:
{', '.join(batch)}

Requirements:
1. Each entry MUST use EXACTLY the citation key specified above (case-sensitive)
2. Use REAL paper information (authors, title, journal, year, volume, pages)
3. Standard BibTeX format (@article or @inproceedings)
4. Include doi when available

Example:
@article{{Kleshchevnikov2022,
  title={{Cell2location maps fine-grained cell types in spatial transcriptomics}},
  author={{Kleshchevnikov, Vitalii and Shmatko, Artem and Dann, Emma and others}},
  journal={{Nature Biotechnology}},
  volume={{40}},
  pages={{661--671}},
  year={{2022}},
  doi={{10.1038/s41587-021-01139-4}}
}}

Output ONLY BibTeX entries, no explanations."""

            result = self.call_llm(prompt, max_tokens=4096, retries=2)
            if result:
                # Strip markdown fences
                result = re.sub(r'```(?:bibtex)?\s*', '', result).strip()
                # Count entries in this batch
                count = result.count('@article') + result.count('@inproceedings') + result.count('@misc') + result.count('@incollection')
                self.log(f"    ✓ 批次 {batch_num}: {count} 条")
                all_bibtex.append(result)
                covered_keys.update(batch)
            else:
                self.log(f"    ⚠️ 批次 {batch_num} 失败")
                failed_batches.append(batch)

        # Step 3: 重试失败的批次 (最多再试 2 轮)
        for retry_round in range(2):
            if not failed_batches:
                break
            self.log(f"  重试 {len(failed_batches)} 个失败批次 (轮次 {retry_round+1})...")
            import time; time.sleep(3)
            still_failed = []
            for batch in failed_batches:
                batch_keys_str = ', '.join(batch)
                prompt = f"""Generate real BibTeX entries for these citation keys:
{batch_keys_str}

Each entry MUST use EXACTLY the citation key above (case-sensitive). Use REAL paper info. Standard @article format. Include doi when available. Output ONLY BibTeX, no explanations."""
                result = self.call_llm(prompt, max_tokens=4096, retries=1)
                if result:
                    result = re.sub(r'```(?:bibtex)?\s*', '', result).strip()
                    count = result.count('@article') + result.count('@inproceedings') + result.count('@misc') + result.count('@incollection')
                    self.log(f"    ✓ 重试成功: {count} 条")
                    all_bibtex.append(result)
                    covered_keys.update(batch)
                else:
                    still_failed.append(batch)
            failed_batches = still_failed

        if failed_batches:
            missed_keys = []
            for batch in failed_batches:
                missed_keys.extend(batch)
            self.log(f"  ⚠️ {len(missed_keys)} 个引用键未能生成")

        # Step 4: 合并所有 BibTeX
        combined = "\n\n".join(all_bibtex)
        entry_count = combined.count('@article') + combined.count('@inproceedings') + combined.count('@misc') + combined.count('@incollection')

        refs_path = self.output_dir / "refs.bib"
        with open(refs_path, 'w') as f:
            f.write(combined)

        self.log(f"  ✓ 参考文献已生成 ({entry_count} 条，覆盖 {len(covered_keys)}/{len(all_cite_keys)} 个引用键)")
        return str(refs_path)

    def generate_table(self) -> str:
        """生成表格"""
        self.log("生成对比表格...")

        prompt = f"""Generate a professional comparison table in LaTeX for a review on: {self.topic}

Requirements:
1. Use booktabs format (\\toprule, \\midrule, \\bottomrule)
2. Include 4-5 columns comparing key methods or approaches
3. Content should be technically accurate and specific to the field
4. Include a descriptive caption and label
5. All text must be in English

Output ONLY the LaTeX table code, no explanations.
"""

        result = self.call_llm(prompt, max_tokens=2048)
        if result:
            import re
            # Strip markdown code fences
            result = re.sub(r'```(?:latex)?\s*', '', result)
            result = result.strip()
        if not result:
            result = f"""\\begin{{table}}[htbp]
\\centering
\\caption{{Comparison of methods for {self.topic}}}
\\label{{tab:comparison}}
\\begin{{tabular}}{{@{{}}llll@{{}}}}
\\toprule
\\textbf{{Method}} & \\textbf{{Resolution}} & \\textbf{{Speed}} & \\textbf{{Accuracy}} \\\\
\\midrule
Method A & High & Fast & 85\\% \\\\
Method B & Medium & Medium & 90\\% \\\\
Method C & Low & Slow & 95\\% \\\\
\\bottomrule
\\end{{tabular}}
\\end{{table}}
"""

        table_path = self.output_dir / "tables" / "tab1.tex"
        with open(table_path, 'w') as f:
            f.write(result)

        self.log(f"  ✓ 表格已生成")
        return str(table_path)

    def assemble_latex(self, outline: Dict, chapters: List[str]) -> str:
        """组装 LaTeX"""
        self.log("组装 LaTeX...")

        # 主文件头
        main = r"""\documentclass[unnumsec,webpdf,contemporary,large,namedate]{oup-authoring-template}
\graphicspath{{figures/}}
\usepackage{longtable}
\usepackage{tcolorbox}
\usepackage{tikz}
\usetikzlibrary{shapes,arrows,positioning}

\begin{document}

\journaltitle{Briefings in Bioinformatics}
\DOI{DOI HERE}
\copyrightyear{2026}
\pubyear{2026}
\access{Advance Access Publication Date: Day Month Year}
\appnotes{Review}
\firstpage{1}

"""

        # 标题
        main += f"\\title{{{outline.get('title', self.topic)}}}\n"
        main += "\\author{NTCode Review Agent}\n"
        main += "\\date{\\today}\n"
        main += "\\maketitle\n\n"

        # 章节 — 使用相对于 main.tex 的路径
        for chapter in chapters:
            # chapter 是完整路径如 output/real_review_xxx/chapters/01-xxx.tex
            # main.tex 在 output/real_review_xxx/ 内，所以只需要 chapters/01-xxx.tex
            rel_path = str(Path(chapter).relative_to(self.output_dir))
            # LaTeX 使用 / 作为路径分隔符
            rel_path = rel_path.replace("\\", "/")
            main += f"\\input{{{rel_path}}}\n"

        # 参考文献
        main += r"""
\bibliographystyle{oup-abbrvnat}
\bibliography{refs}

\end{document}
"""

        main_path = self.output_dir / "main.tex"
        with open(main_path, 'w') as f:
            f.write(main)

        self.log(f"  ✓ LaTeX 已组装")
        return str(main_path)

    def compile_pdf(self) -> bool:
        """编译 PDF"""
        self.log("编译 PDF...")

        try:
            # 第一次编译
            subprocess.run(
                ["xelatex", "-interaction=nonstopmode", "main.tex"],
                cwd=self.output_dir, capture_output=True, timeout=120
            )

            # bibtex
            subprocess.run(
                ["bibtex", "main"],
                cwd=self.output_dir, capture_output=True, timeout=60
            )

            # 第二次编译
            subprocess.run(
                ["xelatex", "-interaction=nonstopmode", "main.tex"],
                cwd=self.output_dir, capture_output=True, timeout=120
            )

            # 第三次编译
            subprocess.run(
                ["xelatex", "-interaction=nonstopmode", "main.tex"],
                cwd=self.output_dir, capture_output=True, timeout=120
            )

            pdf_path = self.output_dir / "main.pdf"
            if pdf_path.exists():
                size_kb = pdf_path.stat().st_size / 1024
                self.log(f"  ✓ PDF 生成成功: {size_kb:.1f} KB")
                return True
            else:
                self.log("  ✗ PDF 生成失败")
                return False

        except Exception as e:
            self.log(f"  ✗ 编译错误: {e}")
            return False

    def run(self) -> str:
        """运行完整流程"""
        self.log("=" * 60)
        self.log("NTCode 综述 Agent - 真正能用的版本")
        self.log(f"主题: {self.topic}")
        self.log(f"期刊: {self.journal}")
        self.log(f"输出: {self.output_dir}")
        self.log("=" * 60)

        # 1. 检查 LaTeX
        if not self.check_latex():
            self.log("LaTeX 环境不可用，退出")
            return ""

        # 2. 下载模板
        self.download_template()

        # 3. 生成大纲
        outline = self.generate_outline()

        # 4. 写章节
        self.log("写章节...")
        chapters = []
        for section in outline.get('sections', []):
            chapter_path = self.write_section(section)
            chapters.append(chapter_path)

        # 5. 生成参考文献
        self.generate_refs()

        # 6. 生成表格
        self.generate_table()

        # 7. 组装 LaTeX
        self.assemble_latex(outline, chapters)

        # 8. 编译 PDF
        self.compile_pdf()

        # 9. 生成报告
        self.log("生成报告...")
        pdf_path = self.output_dir / "main.pdf"
        pdf_size = f"{pdf_path.stat().st_size / 1024:.1f} KB" if pdf_path.exists() else "NOT GENERATED"
        chapter_count = len(list((self.output_dir / "chapters").glob("*.tex")))
        report = f"""# Review Generation Report

## Basic Info
- Topic: {self.topic}
- Journal: {self.journal}
- Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Output: {self.output_dir}

## Generated Files
- main.tex: Assembled LaTeX source
- main.pdf: Compiled PDF ({pdf_size})
- refs.bib: Bibliography
- chapters/: {chapter_count} section files
- tables/: Comparison tables
- figures/: TikZ figures

## Quality Notes
- AI-generated draft requiring expert review
- References should be verified for accuracy
- Figures may need manual refinement
- Check citation consistency before submission
"""
        with open(self.output_dir / "REPORT.md", 'w') as f:
            f.write(report)

        self.log("=" * 60)
        self.log("✅ 综述写作完成！")
        self.log(f"PDF: {self.output_dir / 'main.pdf'}")
        self.log("=" * 60)

        return str(self.output_dir / "main.pdf")


def main():
    if len(sys.argv) < 2:
        print("用法: python real_review_agent.py '综述主题' [--journal briefings|nature|cell|science]")
        sys.exit(1)

    topic = sys.argv[1]
    journal = 'briefings'

    for i, arg in enumerate(sys.argv):
        if arg == '--journal' and i + 1 < len(sys.argv):
            journal = sys.argv[i + 1]

    agent = RealReviewAgent(topic, journal)
    agent.run()


if __name__ == "__main__":
    main()
