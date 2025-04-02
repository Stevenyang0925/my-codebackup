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
        
        # 跟踪当前的标题层级
        current_section = {"level": 1, "title": ""}
        
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
                
                # 更新当前标题层级
                current_section = {"level": level, "title": clean_content}
            
            elif item_type == "text":
                # 处理可能的段落格式，确保段落之间有空行
                if not item_content.strip():
                    continue
                
                # 检查文本是否可能是列表项
                lines = item_content.split('\n')
                processed_lines = []
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 检查是否是列表项（以冒号结尾的短语通常是列表项的标题）
                    if ':' in line and len(line) < 100:
                        parts = line.split(':', 1)
                        if len(parts) == 2 and parts[1].strip():
                            # 这看起来像是一个列表项
                            processed_lines.append(f"- {parts[0].strip()}: {parts[1].strip()}")
                        else:
                            processed_lines.append(line)
                    else:
                        processed_lines.append(line)
                
                if processed_lines:
                    # 检查是否所有行都是列表项
                    all_list_items = all(line.startswith('- ') for line in processed_lines)
                    
                    if all_list_items:
                        # 如果全是列表项，直接添加
                        for line in processed_lines:
                            markdown_lines.append(line)
                        markdown_lines.append("")
                    else:
                        # 否则作为普通段落处理
                        clean_paragraph = '\n'.join(processed_lines)
                        # 确保段落内的换行被保留为软换行
                        clean_paragraph = re.sub(r'\n', '  \n', clean_paragraph)
                        markdown_lines.append(clean_paragraph)
                        markdown_lines.append("")
            
            elif item_type == "list":
                list_items = item.get("additional_info", [])
                list_type = item.get("list_type", "unordered")
                
                for i, list_item in enumerate(list_items):
                    if list_type == "ordered":
                        markdown_lines.append(f"{i+1}. {list_item}")
                    else:
                        markdown_lines.append(f"- {list_item}")
                
                markdown_lines.append("")
            
            elif item_type == "table":
                table_data = item.get("additional_info", [])
                if table_data and len(table_data) > 0:
                    # 表头
                    if len(table_data) > 0 and len(table_data[0]) > 0:
                        header = table_data[0]
                        markdown_lines.append("| " + " | ".join(str(cell) for cell in header) + " |")
                        
                        # 分隔线 (对齐方式: 默认左对齐)
                        markdown_lines.append("| " + " | ".join(["---"] * len(header)) + " |")
                        
                        # 表格内容
                        for row in table_data[1:]:
                            # 确保行中的单元格数量与表头一致
                            while len(row) < len(header):
                                row.append("")
                            row = row[:len(header)]  # 截断多余的单元格
                            
                            # 处理单元格中可能存在的管道符号
                            escaped_row = [str(cell).replace("|", "\\|") for cell in row]
                            markdown_lines.append("| " + " | ".join(escaped_row) + " |")
                    
                    markdown_lines.append("")
            
            elif item_type == "image":
                image_path = item.get("additional_info", "")
                alt_text = item_content or "图片"
                if image_path:
                    # 确保alt文本和图片路径中的特殊字符被正确转义
                    alt_text = alt_text.replace("[", "\\[").replace("]", "\\]")
                    image_path = image_path.replace("(", "\\(").replace(")", "\\)")
                    markdown_lines.append(f"![{alt_text}]({image_path})")
                    markdown_lines.append("")
            
            elif item_type == "code":
                code_content = item.get("additional_info", "")
                language = item.get("language", "")
                
                # 确保代码块有正确的格式
                if code_content:
                    markdown_lines.append(f"```{language}")
                    # 不对代码内容做修改，保持原样
                    markdown_lines.append(code_content.rstrip())
                    markdown_lines.append("```")
                    markdown_lines.append("")
            
            elif item_type == "link":
                link_url = item.get("additional_info", "")
                link_text = item_content or link_url
                if link_url:
                    # 确保链接文本和URL中的特殊字符被正确转义
                    link_text = link_text.replace("[", "\\[").replace("]", "\\]")
                    link_url = link_url.replace("(", "\\(").replace(")", "\\)")
                    markdown_lines.append(f"[{link_text}]({link_url})")
                    markdown_lines.append("")
            
            elif item_type == "blockquote":
                quote_content = item_content
                if quote_content:
                    # 处理多行引用
                    lines = quote_content.split('\n')
                    for line in lines:
                        markdown_lines.append(f"> {line}")
                    markdown_lines.append("")
            
            elif item_type == "horizontal_rule":
                # 添加水平分割线
                markdown_lines.append("---")
                markdown_lines.append("")
        
        # 后处理：优化标题层级结构
        processed_lines = []
        current_level = 1
        section_stack = []
        
        i = 0
        while i < len(markdown_lines):
            line = markdown_lines[i]
            
            # 检测标题行
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if header_match:
                level = len(header_match.group(1))
                content = header_match.group(2)
                
                # 确保标题层级不跳级（如从h1直接到h3）
                if level > current_level + 1:
                    level = current_level + 1
                
                # 更新当前层级
                current_level = level
                
                # 添加处理后的标题
                processed_lines.append(f"{'#' * level} {content}")
            else:
                processed_lines.append(line)
            
            i += 1
        
        # 移除末尾多余的空行
        while processed_lines and not processed_lines[-1]:
            processed_lines.pop()
            
        # 确保文件末尾有一个换行符
        if processed_lines:
            processed_lines.append("")
            
        # 合并所有行并返回
        return "\n".join(processed_lines)
    
    def _detect_list_items(self, text):
        """检测文本中的列表项"""
        lines = text.split('\n')
        list_items = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 检查是否是列表项
            if re.match(r'^[-*•]\s+', line):
                # 已经是列表项格式
                list_items.append(line)
            elif ':' in line:
                # 可能是键值对形式的列表项
                parts = line.split(':', 1)
                if len(parts) == 2 and parts[1].strip():
                    list_items.append(f"- {parts[0].strip()}: {parts[1].strip()}")
                else:
                    return None  # 不是列表
            else:
                return None  # 不是列表
                
        return list_items if list_items else None