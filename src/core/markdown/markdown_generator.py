"""
Markdown生成器模块，负责将解析结果转换为Markdown格式
"""

from typing import Dict, Any, List
import re

class MarkdownGenerator:
    """
    Markdown生成器，将解析结果转换为Markdown格式
    """
    
    def generate(self, parsed_data: Dict[str, Any]) -> str:
        """
        生成Markdown内容
        
        Args:
            parsed_data: 解析结果，包含标题和内容
            
        Returns:
            str: Markdown格式的内容
        """
        markdown_lines = []
        
        # 添加标题
        title = parsed_data.get("title", "")
        if title:
            # 清理标题中可能存在的多余#符号和空格
            title = re.sub(r'^#+\s*', '', title).strip()
            # 确保标题级别不超过6级
            level = min(6, max(1, parsed_data.get("title_level", 1)))
            markdown_lines.append(f"{'#' * level} {title}")
            markdown_lines.append("")
        
        # 处理内容
        content_items = parsed_data.get("content", [])
        
        for item in content_items:
            item_type = item.get("type", "")
            item_content = item.get("content", "")
            
            if item_type == "heading":
                level = item.get("level", 1)
                # 确保级别在1-6之间
                level = max(1, min(level, 6))
                # 清理内容中可能存在的多余#符号和空格
                clean_content = re.sub(r'^#+\s*', '', item_content).strip()
                # 确保#和内容之间有一个空格
                markdown_lines.append(f"{'#' * level} {clean_content}")
                markdown_lines.append("")
            
            elif item_type == "text":
                # 简化处理：直接输出文本内容，不尝试识别结构
                if item_content.strip():
                    markdown_lines.append(item_content)
                    markdown_lines.append("")
            
            elif item_type == "list_item":
                # 直接处理单个列表项
                if item_content.strip():
                    # 检查是否已经有列表标记
                    if re.match(r'^([-*•] |\d+\.\s+)', item_content):
                        markdown_lines.append(item_content)
                    else:
                        # 默认使用无序列表
                        markdown_lines.append(f"- {item_content}")
                    markdown_lines.append("")
            
            elif item_type == "list":
                list_items = item.get("additional_info", [])
                list_type = item.get("list_type", "unordered")
                
                if list_items:
                    for i, list_item in enumerate(list_items):
                        if list_type == "ordered":
                            markdown_lines.append(f"{i+1}. {list_item}")
                        else:
                            markdown_lines.append(f"- {list_item}")
                    markdown_lines.append("")
            
            elif item_type == "image":
                image_path = item.get("additional_info", "")
                if image_path:
                    alt_text = item_content if item_content else "原始图片"
                    markdown_lines.append(f"![{alt_text}]({image_path})")
                    markdown_lines.append("")
        
        # 合并所有行并返回
        return "\n".join(markdown_lines)