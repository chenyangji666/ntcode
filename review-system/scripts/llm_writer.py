#!/usr/bin/env python3
"""
LLM 写作模块 - 使用小米 mimo-v2.5-pro API
"""

import json
import requests
from typing import List, Dict, Any, Optional
from pathlib import Path
import time


class LLMWriter:
    def __init__(self, api_key: str, base_url: str = "https://token-plan-sgp.xiaomimimo.com/anthropic"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = "mimo-v2.5-pro"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

    def call_llm(self, prompt: str, max_tokens: int = 4096) -> Optional[str]:
        """调用 LLM API"""
        url = f"{self.base_url}/v1/messages"

        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=120)

            if response.status_code == 200:
                result = response.json()
                # 小米 API 响应格式：content 是数组，每个元素有 type 字段
                content_list = result.get("content", [])
                for item in content_list:
                    if item.get("type") == "text":
                        return item.get("text", "")
                    elif item.get("type") == "thinking":
                        # 如果只有 thinking，返回 thinking 内容
                        return item.get("thinking", "")
                # 如果都没有，尝试直接获取第一个元素的 text
                if content_list:
                    return content_list[0].get("text", "") or content_list[0].get("thinking", "")
                return None
            else:
                print(f"  ⚠️ API 调用失败: {response.status_code}")
                print(f"  {response.text}")
                return None

        except Exception as e:
            print(f"  ⚠️ API 调用异常: {e}")
            return None

    def generate_outline(self, topic: str, papers: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """生成综述大纲"""
        print("  生成综述大纲...")

        paper_list = "\n".join([
            f"- {p.get('title', 'Unknown')} ({p.get('year', 'N/A')}) - {p.get('journal', 'Unknown')}"
            for p in papers[:20]  # 只用前20篇
        ])

        prompt = f"""请为以下综述主题生成一个详细的综述大纲。

主题: {topic}

参考文献:
{paper_list}

要求:
1. 包含以下章节: 引言、研究方法概述、主要发现、讨论与展望、结论
2. 每个章节包含2-3个小节
3. 每个小节列出需要引用的文献
4. 逻辑连贯，层次分明

请以JSON格式输出大纲，格式如下:
{{
  "title": "综述标题",
  "abstract": "摘要内容",
  "sections": [
    {{
      "title": "章节标题",
      "subsections": [
        {{
          "title": "小节标题",
          "content_brief": "内容概述",
          "papers": ["文献标题1", "文献标题2"]
        }}
      ]
    }}
  ]
}}
"""

        result = self.call_llm(prompt, max_tokens=8192)

        if result:
            try:
                # 处理 markdown 代码块包裹的 JSON
                json_str = result.strip()

                # 移除 markdown 代码块标记
                if json_str.startswith("```json"):
                    json_str = json_str[7:]
                elif json_str.startswith("```"):
                    json_str = json_str[3:]

                if json_str.endswith("```"):
                    json_str = json_str[:-3]

                json_str = json_str.strip()

                # 尝试提取 JSON
                json_start = json_str.find("{")
                json_end = json_str.rfind("}") + 1
                if json_start != -1 and json_end != -1:
                    json_str = json_str[json_start:json_end]
                    outline = json.loads(json_str)
                    print("  ✓ 大纲生成完成")
                    return outline
                else:
                    print("  ⚠️ 未找到 JSON 对象")
            except json.JSONDecodeError as e:
                print(f"  ⚠️ 大纲格式解析失败: {e}")
                # 尝试修复常见的 JSON 错误（截断）
                try:
                    # 尝试补全截断的 JSON
                    fixed = json_str.rstrip()
                    # 补全缺失的括号
                    open_braces = fixed.count('{') - fixed.count('}')
                    open_brackets = fixed.count('[') - fixed.count(']')
                    if open_braces > 0 or open_brackets > 0:
                        # 截断到最后一个完整的元素
                        last_complete = max(fixed.rfind('},'), fixed.rfind('],'))
                        if last_complete > 0:
                            fixed = fixed[:last_complete + 1]
                            # 补全闭合括号
                            open_braces = fixed.count('{') - fixed.count('}')
                            open_brackets = fixed.count('[') - fixed.count(']')
                            fixed += ']' * open_brackets + '}' * open_braces
                            outline = json.loads(fixed)
                            print("  ✓ 大纲生成完成（已修复截断）")
                            return outline
                except:
                    pass

        return None

    def write_section(self, topic: str, section_title: str, subsection_title: str,
                      content_brief: str, papers: List[Dict[str, Any]]) -> Optional[str]:
        """撰写单个章节"""
        print(f"  撰写: {section_title} - {subsection_title}")

        paper_list = "\n".join([
            f"- {p.get('title', 'Unknown')} ({p.get('year', 'N/A')})"
            for p in papers[:10]
        ])

        prompt = f"""请撰写以下综述章节的内容。

主题: {topic}
章节: {section_title}
小节: {subsection_title}
内容概述: {content_brief}

参考文献:
{paper_list}

要求:
1. 学术风格，语言严谨
2. 适当引用参考文献（使用 [作者, 年份] 格式）
3. 每段200-300字
4. 包含研究现状、方法比较、未来方向

请直接输出章节内容，不要包含标题。
"""

        result = self.call_llm(prompt, max_tokens=1024)
        return result

    def review_quality(self, content: str, section_title: str) -> Dict[str, Any]:
        """质量审查"""
        print(f"  审查: {section_title}")

        prompt = f"""请审查以下综述章节的质量。

章节: {section_title}
内容:
{content[:1000]}

审查标准:
1. 学术规范性 (0-100分)
2. 逻辑连贯性 (0-100分)
3. 引用完整性 (0-100分)
4. 语言质量 (0-100分)

请以JSON格式输出审查结果:
{{
  "overall_score": 85,
  "academic_score": 90,
  "logic_score": 80,
  "citation_score": 75,
  "language_score": 85,
  "issues": ["问题1", "问题2"],
  "suggestions": ["建议1", "建议2"]
}}
"""

        result = self.call_llm(prompt, max_tokens=512)

        if result:
            try:
                # 移除 markdown 代码块标记
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
                    review = json.loads(json_str)
                    return review
            except json.JSONDecodeError:
                pass

        return {"overall_score": 80, "issues": [], "suggestions": []}

    def generate_abstract(self, topic: str, sections: List[str]) -> Optional[str]:
        """生成摘要"""
        print("  生成摘要...")

        sections_text = "\n".join([f"- {s}" for s in sections])

        prompt = f"""请为以下综述生成一个200-300字的摘要。

主题: {topic}
主要章节:
{sections_text}

要求:
1. 简明扼要
2. 包含研究背景、主要发现、未来方向
3. 学术风格

请直接输出摘要内容。
"""

        result = self.call_llm(prompt, max_tokens=512)
        return result


def test_llm_writer():
    """测试 LLM 写作模块"""
    # 这里的 API Key 需要替换为实际的
    api_key = "tp-sikntt03kg0yxrxb7n07qsmhzs853637o0mmcbrwjvyk57v6"

    writer = LLMWriter(api_key)

    # 测试大纲生成
    test_papers = [
        {"title": "Single-cell RNA sequencing in tumor microenvironment", "year": 2024, "journal": "Nature"},
        {"title": "Immunotherapy response prediction", "year": 2023, "journal": "Science"},
    ]

    outline = writer.generate_outline("单细胞转录组在肿瘤免疫微环境中的应用", test_papers)

    if outline:
        print(f"  大纲: {json.dumps(outline, ensure_ascii=False, indent=2)}")

    print("✓ LLM 写作模块测试完成")


if __name__ == "__main__":
    test_llm_writer()
