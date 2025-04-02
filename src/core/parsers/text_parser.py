"""
文本文件解析器模块
"""

import os
from typing import Dict, Any, List
from .base_parser import BaseParser

class TextParser(BaseParser):
    """
    文本文件解析器，用于解析.txt等纯文本文件
    """
    
    def get_supported_extensions(self) -> List[str]:
        """
        获取支持的文件扩展名列表
        
        Returns:
            List[str]: 支持的文件扩展名列表
        """
        return ['.txt', '.text', '.md', '.markdown']
    
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        解析文本文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            Dict[str, Any]: 解析结果
        """
        if not self.is_supported(file_path):
            raise ValueError(f"不支持的文件类型: {file_path}")
        
        title = self.extract_title(file_path)
        content = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 处理文本内容
            current_paragraph = []
            
            for line in lines:
                line = line.rstrip()
                
                # 检测标题
                if line.startswith('#'):
                    # 先处理之前的段落
                    if current_paragraph:
                        content.append({
                            "type": "text",
                            "content": '\n'.join(current_paragraph)
                        })
                        current_paragraph = []
                    
                    # 计算标题级别
                    level = 0
                    for char in line:
                        if char == '#':
                            level += 1
                        else:
                            break
                    
                    heading_text = line[level:].strip()
                    content.append({
                        "type": "heading",
                        "level": level,
                        "content": heading_text
                    })
                
                # 检测列表
                elif line.strip().startswith(('- ', '* ', '+ ')) or line.strip().startswith(tuple(f"{i}. " for i in range(1, 10))):
                    # 先处理之前的段落
                    if current_paragraph:
                        content.append({
                            "type": "text",
                            "content": '\n'.join(current_paragraph)
                        })
                        current_paragraph = []
                    
                    # 提取列表项内容
                    list_item = line.strip()
                    if list_item.startswith(('- ', '* ', '+ ')):
                        list_item = list_item[2:]
                    else:  # 数字列表
                        list_item = list_item[list_item.find('.')+1:].strip()
                    
                    content.append({
                        "type": "list",
                        "content": "",
                        "additional_info": [list_item]
                    })
                
                # 空行表示段落结束
                elif not line:
                    if current_paragraph:
                        content.append({
                            "type": "text",
                            "content": '\n'.join(current_paragraph)
                        })
                        current_paragraph = []
                
                # 普通文本行
                else:
                    current_paragraph.append(line)
            
            # 处理最后一个段落
            if current_paragraph:
                content.append({
                    "type": "text",
                    "content": '\n'.join(current_paragraph)
                })
            
            return {
                "title": title,
                "content": content
            }
            
        except Exception as e:
            # 在实际应用中，应该使用日志记录错误
            print(f"解析文本文件时出错: {e}")
            return {
                "title": title,
                "content": [{
                    "type": "text",
                    "content": f"解析文件时出错: {e}"
                }]
            }