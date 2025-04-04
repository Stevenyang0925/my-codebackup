"""
调试 WordParser 的标题识别功能
"""

import os
import sys
from src.core.parsers.word_parser import WordParser

def main():
    # 设置测试文件路径
    test_file = r"E:\PythonProjects\Markdown\test file\智能腕表2代.docx"
    
    if not os.path.exists(test_file):
        print(f"错误: 文件不存在: {test_file}")
        return
    
    print(f"开始解析文件: {test_file}")
    
    # 创建 WordParser 实例
    parser = WordParser()
    
    # 解析文件
    parsed_data = parser.parse(test_file)
    
    # 检查解析结果
    print("\n解析结果:")
    print(f"标题: {parsed_data.get('title', '无标题')}")
    print(f"是否为原始 Markdown: {parsed_data.get('raw_markdown', False)}")
    
    # 保存结果到文件
    output_file = r"E:\PythonProjects\Markdown\output\debug_output.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(parsed_data.get("content", ""))
    
    print(f"\n结果已保存到: {output_file}")

if __name__ == "__main__":
    main()
