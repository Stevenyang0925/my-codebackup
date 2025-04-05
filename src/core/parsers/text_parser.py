"""
文本文件解析器模块
"""

import os
from typing import Dict, Any, List
from .base_parser import BaseParser
from ..utils.logger import get_logger
from ..utils.exceptions import FileParsingError

# 获取 logger 实例
logger = get_logger(__name__)

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
            logger.error(f"不支持的文件类型传递给 TextParser: {file_path}")
            raise FileParsingError(f"TextParser 不支持的文件类型: {file_path}")
        
        title = self.extract_title(file_path)
        content = []
        logger.info(f"开始解析文本文件: {file_path}")
        
        try:
            logger.debug(f"尝试以 UTF-8 编码读取文件: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            logger.debug(f"成功读取 {len(lines)} 行")
            
            # 处理文本内容
            current_paragraph = []
            logger.debug("开始逐行处理文本内容")
            
            for i, line in enumerate(lines):
                line = line.rstrip()
                
                # 检测标题
                if line.startswith('#'):
                    if current_paragraph:
                        content.append({
                            "type": "text",
                            "content": '\n'.join(current_paragraph)
                        })
                        current_paragraph = []
                    
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
                    if current_paragraph:
                        content.append({
                            "type": "text",
                            "content": '\n'.join(current_paragraph)
                        })
                        current_paragraph = []
                    
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
            
            logger.info(f"成功解析文本文件: {file_path}")
            return {
                "title": title,
                "content": content
            }
            
        except FileNotFoundError:
            logger.error(f"文件未找到: {file_path}")
            raise FileParsingError(f"文件未找到: {file_path}") from None
        except IOError as e_io:
            logger.error(f"读取文件时发生 IO 错误: {file_path} - {e_io}", exc_info=False)
            raise FileParsingError(f"读取文件时出错: {e_io}") from e_io
        except UnicodeDecodeError as e_decode:
            logger.error(f"文件编码错误 (尝试使用 UTF-8): {file_path} - {e_decode}", exc_info=False)
            raise FileParsingError(f"文件编码错误，请确保文件为 UTF-8 编码: {e_decode}") from e_decode
        except Exception as e:
            logger.exception(f"解析文本文件时发生未预料的错误: {file_path}", exc_info=True)
            raise FileParsingError(f"解析文本文件时出错: {e}") from e