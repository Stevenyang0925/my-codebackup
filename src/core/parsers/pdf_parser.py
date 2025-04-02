"""
PDF文档解析器模块
"""

import os
from typing import Dict, Any, List
from .base_parser import BaseParser

class PDFParser(BaseParser):
    """
    PDF文档解析器，用于解析.pdf文件
    """
    
    def get_supported_extensions(self) -> List[str]:
        """
        获取支持的文件扩展名列表
        
        Returns:
            List[str]: 支持的文件扩展名列表
        """
        return ['.pdf']
    
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        解析PDF文档
        
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
            # 尝试使用PyPDF2
            import PyPDF2
            
            with open(file_path, 'rb') as file:
                # 创建PDF阅读器
                pdf_reader = PyPDF2.PdfReader(file)
                
                # 获取页数
                num_pages = len(pdf_reader.pages)
                
                # 处理每一页
                for page_num in range(num_pages):
                    # 添加页码标题
                    content.append({
                        "type": "heading",
                        "level": 2,
                        "content": f"第 {page_num + 1} 页"
                    })
                    
                    # 提取文本
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    # 按段落分割文本
                    paragraphs = text.split('\n\n')
                    for para in paragraphs:
                        if para.strip():
                            content.append({
                                "type": "text",
                                "content": para.strip()
                            })
            
            return {
                "title": title,
                "content": content
            }
            
        except ImportError:
            try:
                # 如果PyPDF2不可用，尝试使用pdfminer.six
                from pdfminer.high_level import extract_text
                
                # 提取文本
                text = extract_text(file_path)
                
                # 按段落分割文本
                paragraphs = text.split('\n\n')
                for para in paragraphs:
                    if para.strip():
                        content.append({
                            "type": "text",
                            "content": para.strip()
                        })
                
                return {
                    "title": title,
                    "content": content
                }
                
            except ImportError:
                return {
                    "title": title,
                    "content": [{
                        "type": "text",
                        "content": "无法解析PDF文件，请安装PyPDF2或pdfminer.six库: pip install PyPDF2 pdfminer.six"
                    }]
                }
        except Exception as e:
            # 在实际应用中，应该使用日志记录错误
            print(f"解析PDF文件时出错: {e}")
            return {
                "title": title,
                "content": [{
                    "type": "text",
                    "content": f"解析文件时出错: {e}"
                }]
            }