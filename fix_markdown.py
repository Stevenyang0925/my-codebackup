"""
修复 Markdown 文件，添加二级标题标记
"""

import os
import sys
import re

def fix_markdown_file(input_file, output_file=None):
    """
    修复 Markdown 文件，添加二级标题标记
    
    Args:
        input_file: 输入文件路径
        output_file: 输出文件路径，如果为 None，则覆盖输入文件
    """
    # 如果没有提供输出文件，则覆盖输入文件
    if output_file is None:
        output_file = input_file
    
    # 读取输入文件
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"读取文件: {input_file}")
    print(f"原始内容前200个字符: {content[:200]}")
    
    # 处理内容
    lines = content.split('\n')
    processed_lines = []
    
    # 已知的章节标题
    known_sections = ["息屏显", "冷钱包", "5ATM防水保护", "3D弧面玻璃", "快充加持", "多功能配件", "数字身份"]
    
    for i, line in enumerate(lines):
        # 跳过空行
        if not line.strip():
            processed_lines.append(line)
            continue
        
        # 处理已有的标题行，确保格式正确
        if line.startswith('#'):
            # 确保标题格式正确（# 后有空格）
            if not re.match(r'^#+\s', line):
                line = re.sub(r'^(#+)', r'\1 ', line)
            processed_lines.append(line)
            continue
        
        # 识别特定的章节标题并添加 ## 标记
        is_section = False
        for section in known_sections:
            if section == line.strip():
                print(f"发现章节标题: {line} -> ## {line.strip()}")
                line = f"## {line.strip()}"
                processed_lines.append(line)
                is_section = True
                break
        
        if is_section:
            continue
        
        # 处理其他行
        processed_lines.append(line)
    
    # 重新组合内容
    processed_content = '\n'.join(processed_lines)
    
    # 确保段落之间有空行
    processed_content = re.sub(r'([^\n])\n([^#\n-])', r'\1\n\n\2', processed_content)
    
    # 确保标题前后有空行
    processed_content = re.sub(r'([^\n])\n(#+\s)', r'\1\n\n\2', processed_content)
    processed_content = re.sub(r'(#+\s[^\n]+)\n([^#\n])', r'\1\n\n\2', processed_content)
    
    print(f"处理后内容前200个字符: {processed_content[:200]}")
    
    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(processed_content)
    
    print(f"已保存到: {output_file}")
    return True

def main():
    # 设置固定的输入和输出目录
    input_dir = r"E:\PythonProjects\Markdown\output"
    output_dir = r"E:\PythonProjects\Markdown\output"
    
    print(f"输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 指定要处理的文件
    target_file = "智能腕表2代.md"
    input_file = os.path.join(input_dir, target_file)
    
    if os.path.exists(input_file):
        print(f"\n处理文件: {target_file}")
        output_file = os.path.join(output_dir, target_file)
        fix_markdown_file(input_file, output_file)
        print(f"处理完成: {target_file}")
    else:
        print(f"错误: 文件不存在: {input_file}")

if __name__ == "__main__":
    main()
