"""
Markdown解析器，用于解析Markdown文件
"""

import re
from typing import Dict, Any, List

class MarkdownParser:
    """
    Markdown解析器，将Markdown文本解析为结构化数据
    """
    
    def parse(self, markdown_text: str) -> Dict[str, Any]:
        """
        解析Markdown文本
        
        Args:
            markdown_text: Markdown文本
            
        Returns:
            Dict[str, Any]: 解析结果，格式与BaseParser.parse返回值相同
        """
        if not markdown_text:
            return {"title": "", "content": []}
        
        lines = markdown_text.split('\n')
        result = {
            "title": "",
            "content": []
        }
        
        # 提取标题（第一个一级标题）
        for line in lines:
            if line.startswith('# '):
                result["title"] = line[2:].strip()
                break
        
        # 解析内容
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # 解析标题
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if heading_match:
                level = len(heading_match.group(1))
                content = heading_match.group(2).strip()
                result["content"].append({
                    "type": "heading",
                    "level": level,
                    "content": content
                })
                i += 1
                continue
            
            # 解析列表
            if line.strip().startswith('- ') or line.strip().startswith('* ') or re.match(r'^\d+\.\s+', line.strip()):
                list_items = []
                while i < len(lines) and (lines[i].strip().startswith('- ') or 
                                         lines[i].strip().startswith('* ') or 
                                         re.match(r'^\d+\.\s+', lines[i].strip())):
                    item_content = re.sub(r'^[-*\d.]\s+', '', lines[i].strip())
                    list_items.append(item_content)
                    i += 1
                result["content"].append({
                    "type": "list",
                    "content": "",
                    "additional_info": list_items
                })
                continue
            
            # 解析代码块
            if line.strip().startswith('```'):
                language = line.strip()[3:].strip()
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                if i < len(lines):  # 跳过结束的```
                    i += 1
                result["content"].append({
                    "type": "code",
                    "content": language,
                    "additional_info": '\n'.join(code_lines)
                })
                continue
            
            # 解析图片
            image_match = re.match(r'!\[(.*?)\]\((.*?)\)', line)
            if image_match:
                alt_text = image_match.group(1)
                image_path = image_match.group(2)
                result["content"].append({
                    "type": "image",
                    "content": alt_text,
                    "additional_info": image_path
                })
                i += 1
                continue
            
            # 解析链接
            link_match = re.match(r'\[(.*?)\]\((.*?)\)', line)
            if link_match:
                link_text = link_match.group(1)
                link_url = link_match.group(2)
                result["content"].append({
                    "type": "link",
                    "content": link_text,
                    "additional_info": link_url
                })
                i += 1
                continue
            
            # 解析表格
            if '|' in line and i + 1 < len(lines) and '|' in lines[i + 1] and '-' in lines[i + 1]:
                table_data = []
                
                # 解析表头
                header = [cell.strip() for cell in line.strip('|').split('|')]
                table_data.append(header)
                
                i += 1  # 跳过分隔行
                i += 1
                
                # 解析表格内容
                while i < len(lines) and '|' in lines[i]:
                    row = [cell.strip() for cell in lines[i].strip('|').split('|')]
                    table_data.append(row)
                    i += 1
                
                result["content"].append({
                    "type": "table",
                    "content": "",
                    "additional_info": table_data
                })
                continue
            
            # 普通文本
            if line.strip():
                result["content"].append({
                    "type": "text",
                    "content": line
                })
            
            i += 1
        
        return result