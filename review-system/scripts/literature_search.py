#!/usr/bin/env python3
"""
文献检索模块 - 使用 Tavily Web Search
"""

import json
import subprocess
from typing import List, Dict, Any
from pathlib import Path


class LiteratureSearcher:
    def __init__(self, topic: str):
        self.topic = topic
        self.papers = []
        self.search_queries = self._generate_queries()

    def _generate_queries(self) -> List[str]:
        """生成搜索关键词"""
        queries = [
            f"{self.topic} review 2024",
            f"{self.topic} recent advances",
            f"{self.topic} single cell sequencing",
            f"{self.topic} bioinformatics methods",
            f"{self.topic} PubMed",
            f"{self.topic} clinical application",
        ]
        return queries

    def search_pubmed(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """通过 PubMed 搜索文献"""
        papers = []

        # 使用 Tavily 搜索 PubMed
        search_query = f"site:pubmed.ncbi.nlm.nih.gov {query}"

        # 这里应该调用 Tavily MCP 工具
        # 暂时使用模拟数据
        print(f"  搜索: {search_query}")

        # 模拟搜索结果
        mock_papers = [
            {
                "title": f"Research on {self.topic} - Part {i}",
                "authors": f"Author A{i}, Author B{i}",
                "journal": "Nature",
                "year": 2024,
                "doi": f"10.1038/s41586-024-0{i:04d}-1",
                "abstract": f"This study investigates {self.topic} using advanced methods...",
                "url": f"https://pubmed.ncbi.nlm.nih.gov/38{i:07d}/",
            }
            for i in range(1, max_results + 1)
        ]

        return mock_papers

    def search_google_scholar(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """通过 Google Scholar 搜索文献"""
        papers = []

        # 使用 Tavily 搜索 Google Scholar
        search_query = f"site:scholar.google.com {query}"

        # 这里应该调用 Tavily MCP 工具
        # 暂时使用模拟数据
        print(f"  搜索: {search_query}")

        # 模拟搜索结果
        mock_papers = [
            {
                "title": f"Scholar paper on {self.topic} - {i}",
                "authors": f"Scholar Author {i}",
                "journal": "Science",
                "year": 2023,
                "doi": f"10.1126/science.ab{i:04d}",
                "abstract": f"A comprehensive study of {self.topic}...",
                "url": f"https://scholar.google.com/scholar?q={self.topic}+{i}",
            }
            for i in range(1, max_results + 1)
        ]

        return mock_papers

    def search_web(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """通过 Web 搜索文献"""
        papers = []

        # 使用 Tavily 搜索 Web
        search_query = f"{query} filetype:pdf"

        # 这里应该调用 Tavily MCP 工具
        # 暂时使用模拟数据
        print(f"  搜索: {search_query}")

        # 模拟搜索结果
        mock_papers = [
            {
                "title": f"Web resource on {self.topic} - {i}",
                "authors": f"Web Author {i}",
                "journal": "Preprint",
                "year": 2024,
                "doi": None,
                "abstract": f"This preprint discusses {self.topic}...",
                "url": f"https://www.example.com/paper{i}.pdf",
            }
            for i in range(1, max_results + 1)
        ]

        return mock_papers

    def search_all(self, min_papers: int = 50) -> List[Dict[str, Any]]:
        """多源并行搜索"""
        all_papers = []

        for query in self.search_queries:
            # PubMed 搜索
            pubmed_papers = self.search_pubmed(query, max_results=10)
            all_papers.extend(pubmed_papers)

            # Google Scholar 搜索
            scholar_papers = self.search_google_scholar(query, max_results=10)
            all_papers.extend(scholar_papers)

            # Web 搜索
            web_papers = self.search_web(query, max_results=5)
            all_papers.extend(web_papers)

        # 去重（基于标题）
        seen_titles = set()
        unique_papers = []
        for paper in all_papers:
            title = paper.get("title", "").strip().lower()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_papers.append(paper)

        self.papers = unique_papers
        return unique_papers

    def filter_papers(self, min_year: int = 2019) -> List[Dict[str, Any]]:
        """筛选文献（近5年、高影响因子）"""
        filtered = []

        for paper in self.papers:
            year = paper.get("year", 0)
            journal = paper.get("journal", "").lower()

            # 年份筛选
            if year < min_year:
                continue

            # 期刊筛选（示例：优先选择高影响因子期刊）
            high_impact_journals = ["nature", "science", "cell", "lancet", "nejm", "nature methods", "nature biotechnology"]
            is_high_impact = any(j in journal for j in high_impact_journals)

            paper["is_high_impact"] = is_high_impact
            filtered.append(paper)

        # 按年份和影响因子排序
        filtered.sort(key=lambda x: (x.get("year", 0), x.get("is_high_impact", False)), reverse=True)

        self.papers = filtered
        return filtered

    def save_papers(self, output_file: Path):
        """保存文献列表"""
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.papers, f, ensure_ascii=False, indent=2)
        print(f"  ✓ 保存 {len(self.papers)} 篇文献到 {output_file}")


def test_searcher():
    """测试文献检索"""
    searcher = LiteratureSearcher("单细胞转录组在肿瘤免疫微环境中的应用")

    print("开始文献检索...")
    papers = searcher.search_all(min_papers=30)

    print(f"检索到 {len(papers)} 篇文献")

    print("筛选文献...")
    filtered = searcher.filter_papers()

    print(f"筛选后 {len(filtered)} 篇文献")

    # 保存结果
    output_file = Path("test_papers.json")
    searcher.save_papers(output_file)

    print("✓ 文献检索测试完成")


if __name__ == "__main__":
    test_searcher()
