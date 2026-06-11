#!/bin/bash
# NTCode 综述写作系统 - 测试脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "  NTCode 综述写作系统 - 系统测试"
echo "=========================================="
echo ""

# 检查 Python
echo "1. 检查 Python 环境..."
if command -v python3 &> /dev/null; then
    echo "   ✓ Python3: $(python3 --version)"
else
    echo "   ✗ Python3 未安装"
    exit 1
fi

# 检查 requests 库
echo "2. 检查 requests 库..."
if python3 -c "import requests" 2>/dev/null; then
    echo "   ✓ requests 库已安装"
else
    echo "   ⚠️ requests 库未安装，正在安装..."
    pip3 install requests -q
    echo "   ✓ requests 库已安装"
fi

# 检查 LaTeX
echo "3. 检查 LaTeX 环境..."
if command -v pdflatex &> /dev/null; then
    echo "   ✓ pdflatex: $(pdflatex --version | head -1)"
else
    echo "   ⚠️ pdflatex 未安装"
    echo "   安装命令: sudo apt install texlive-full"
fi

# 检查配置文件
echo "4. 检查配置文件..."
if [ -f "$SCRIPT_DIR/config.json" ]; then
    echo "   ✓ config.json 存在"

    # 检查 API Key
    if python3 -c "import json; config=json.load(open('$SCRIPT_DIR/config.json')); print('LLM API Key:', '✓' if config['api']['llm']['api_key'] else '✗')" 2>/dev/null; then
        :
    fi
else
    echo "   ✗ config.json 不存在"
fi

# 检查脚本文件
echo "5. 检查脚本文件..."
for script in run_review.py literature_search.py llm_writer.py web_search.py; do
    if [ -f "$SCRIPT_DIR/scripts/$script" ]; then
        echo "   ✓ $script"
    else
        echo "   ✗ $script 不存在"
    fi
done

# 测试 LLM API 连接
echo "6. 测试 LLM API 连接..."
cd "$SCRIPT_DIR"
python3 -c "
import sys
sys.path.insert(0, 'scripts')
from llm_writer import LLMWriter
import json

config = json.load(open('config.json'))
api_key = config['api']['llm']['api_key']
base_url = config['api']['llm']['base_url']

writer = LLMWriter(api_key, base_url)
result = writer.call_llm('你好，请回复OK', max_tokens=10)

if result:
    print('   ✓ LLM API 连接正常')
else:
    print('   ✗ LLM API 连接失败')
" 2>/dev/null || echo "   ⚠️ 无法测试 LLM API"

echo ""
echo "=========================================="
echo "  测试完成"
echo "=========================================="
echo ""
echo "如果所有检查都通过，可以运行综述写作:"
echo "  ./start_review.sh '你的综述主题'"
echo ""
