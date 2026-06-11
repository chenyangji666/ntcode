#!/usr/bin/env python3
"""
Web 搜索模块 - 使用 Tavily 进行文献检索
"""

import json
import requests
from typing import List, Dict, Any, Optional
from pathlib import Path
import time


class WebSearcher:
    def __init__(self):
        # Tavily API 配置（需要用户配置）
        self.tavily_api_key = None  # 用户需要设置
        self.tavily_base_url = "https://api.tavily.com"

    def set_tavily_api_key(self, api_key: str):
        """设置 Tavily API Key"""
        self.tavily_api_key = api_key

    def search_tavily(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """使用 Tavily 进行搜索"""
        if not self.tavily_api_key:
            print("  ⚠️ Tavily API Key 未设置")
            return []

        url = f"{self.tavily_base_url}/search"

        payload = {
            "api_key": self.tavily_api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": "advanced",
            "include_answer": False,
            "include_raw_content": False,
        }

        try:
            response = requests.post(url, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                results = result.get("results", [])

                papers = []
                for r in results:
                    paper = {
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "abstract": r.get("content", "")[:500],
                        "source": "tavily",
                    }
                    papers.append(paper)

                return papers
            else:
                print(f"  ⚠️ Tavily 搜索失败: {response.status_code}")
                return []

        except Exception as e:
            print(f"  ⚠️ Tavily 搜索异常: {e}")
            return []

    def search_pubmed_via_web(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """通过 Web 搜索 PubMed"""
        search_query = f"site:pubmed.ncbi.nlm.nih.gov {query}"
        return self.search_tavily(search_query, max_results)

    def search_scholar_via_web(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """通过 Web 搜索 Google Scholar"""
        search_query = f"site:scholar.google.com {query}"
        return self.search_tavily(search_query, max_results)

    def search_general(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """通用 Web 搜索"""
        return self.search_tavily(query, max_results)

    def search_all_sources(self, topic: str, min_papers: int = 50) -> List[Dict[str, Any]]:
        """多源并行搜索"""
        all_papers = []

        # 生成搜索关键词
        queries = [
            f"{topic} review 2024",
            f"{topic} recent advances",
            f"{topic} single cell sequencing",
            f"{topic} bioinformatics",
            f"{topic} PubMed",
            f"{topic} clinical application",
        ]

        for query in queries:
            print(f"  搜索: {query}")

            # PubMed 搜索
            pubmed_papers = self.search_pubmed_via_web(query, max_results=5)
            all_papers.extend(pubmed_papers)

            # Google Scholar 搜索
            scholar_papers = self.search_scholar_via_web(query, max_results=5)
            all_papers.extend(scholar_papers)

            # 通用搜索
            general_papers = self.search_general(query, max_results=5)
            all_papers.extend(general_papers)

            # 避免请求过快
            time.sleep(1)

        # 去重
        seen_urls = set()
        unique_papers = []
        for paper in all_papers:
            url = paper.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_papers.append(paper)

        return unique_papers

    def parse_pubmed_paper(self, url: str) -> Optional[Dict[str, Any]]:
        """解析 PubMed 论文页面"""
        # TODO: 实现 PubMed 页面解析
        # 可以使用 requests + BeautifulSoup
        pass

    def extract_paper_info(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        """提取论文信息"""
        title = paper.get("title", "")
        abstract = paper.get("abstract", "")
        url = paper.get("url", "")

        # 尝试从 URL 提取 PubMed ID
        pmid = None
        if "pubmed.ncbi.nlm.nih.gov" in url:
            try:
                pmid = url.split("/")[-1].split("?")[0]
            except:
                pass

        return {
            "title": title,
            "abstract": abstract,
            "url": url,
            "pmid": pmid,
            "year": 2024,  # 默认年份
            "journal": "Unknown",
            "authors": "Unknown",
        }


def test_web_searcher():
    """测试 Web 搜索"""
    searcher = WebSearcher()

    # 注意：需要设置 Tavily API Key
    # searcher.set_tavily_api_key("your_api_key")

    print("测试 Web 搜索（需要 Tavily API Key）...")

    # 测试搜索
    papers = searcher.search_tavily("single cell RNA sequencing tumor microenvironment", max_results=5)

    print(f"搜索到 {len(papers)} 篇文献")

    for i, paper in enumerate(papers[:3]):
        print(f"  {i+1}. {paper.get('title', 'Unknown')}")

    print("✓ Web 搜索测试完成")


if __name__ == "__main__":
    test_web_searcher()
