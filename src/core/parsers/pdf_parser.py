"""
PDF文档解析器模块
"""

import os
from typing import Dict, Any, List
from .base_parser import BaseParser
from ..utils.logger import get_logger
from ..utils.exceptions import FileParsingError

logger = get_logger(__name__)

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
            logger.error(f"不支持的文件类型传递给 PDFParser: {file_path}")
            raise FileParsingError(f"PDFParser 不支持的文件类型: {file_path}")
        
        title = self.extract_title(file_path)
        content = []
        logger.info(f"开始解析 PDF 文件: {file_path}")
        
        try:
            # 尝试使用PyPDF2
            logger.debug(f"尝试使用 PyPDF2 解析: {file_path}")
            import PyPDF2
            
            with open(file_path, 'rb') as file:
                # 创建PDF阅读器
                pdf_reader = PyPDF2.PdfReader(file)
                
                # 获取页数
                num_pages = len(pdf_reader.pages)
                logger.debug(f"PyPDF2 找到 {num_pages} 页")
                
                # 处理每一页
                for page_num in range(num_pages):
                    logger.debug(f"PyPDF2 正在处理第 {page_num + 1} 页")
                    # 添加页码标题
                    content.append({
                        "type": "heading",
                        "level": 2,
                        "content": f"第 {page_num + 1} 页"
                    })
                    
                    # 提取文本
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    if text:
                        paragraphs = text.split('\n\n')
                        for para in paragraphs:
                            para_stripped = para.strip()
                            if para_stripped:
                                content.append({
                                    "type": "text",
                                    "content": para_stripped
                                })
                    else:
                        logger.warning(f"PyPDF2 未能从第 {page_num + 1} 页提取文本: {file_path}")
            
            logger.info(f"使用 PyPDF2 成功解析 PDF 文件: {file_path}")
            return {
                "title": title,
                "content": content
            }
            
        except ImportError:
            logger.warning("未找到 PyPDF2 库，尝试使用 pdfminer.six 解析 PDF 文件。")
            try:
                # 如果PyPDF2不可用，尝试使用pdfminer.six
                logger.debug(f"尝试使用 pdfminer.six 解析: {file_path}")
                from pdfminer.high_level import extract_text
                
                # 提取文本
                text = extract_text(file_path)
                logger.debug(f"pdfminer.six 提取到 {len(text)} 字符")
                
                if text:
                    paragraphs = text.split('\n\n')
                    for para in paragraphs:
                        para_stripped = para.strip()
                        if para_stripped:
                            content.append({
                                "type": "text",
                                "content": para_stripped
                            })
                else:
                    logger.warning(f"pdfminer.six 未能从文件中提取文本: {file_path}")
                
                logger.info(f"使用 pdfminer.six 成功解析 PDF 文件: {file_path}")
                return {
                    "title": title,
                    "content": content
                }
                
            except ImportError:
                logger.error("无法解析PDF文件：PyPDF2 和 pdfminer.six 库均未安装。")
                return {
                    "title": title,
                    "content": [{
                        "type": "text",
                        "content": "无法解析PDF文件，请安装PyPDF2或pdfminer.six库: pip install PyPDF2 pdfminer.six"
                    }]
                }
            except Exception as e_pdfminer:
                logger.exception(f"使用 pdfminer.six 解析 PDF 文件时发生错误: {file_path}", exc_info=True)
                raise FileParsingError(f"使用 pdfminer.six 解析 PDF 文件时出错: {e_pdfminer}") from e_pdfminer
        except Exception as e_pypdf:
            # 在实际应用中，应该使用日志记录错误
            logger.exception(f"解析 PDF 文件时发生错误: {file_path}", exc_info=True)
            raise FileParsingError(f"解析 PDF 文件时出错: {e_pypdf}") from e_pypdf