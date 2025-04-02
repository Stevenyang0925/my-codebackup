"""
解析器模块初始化文件
"""

from .base_parser import BaseParser
from .text_parser import TextParser
from .word_parser import WordParser
from .excel_parser import ExcelParser
from .pdf_parser import PDFParser
from .image_parser import ImageParser

# 创建解析器实例
text_parser = TextParser()
word_parser = WordParser()
excel_parser = ExcelParser()
pdf_parser = PDFParser()
image_parser = ImageParser()

# 解析器列表
parsers = [
    text_parser,
    word_parser,
    excel_parser,
    pdf_parser,
    image_parser
]

def get_parser_for_file(file_path: str) -> BaseParser:
    """
    根据文件路径获取合适的解析器
    
    Args:
        file_path: 文件路径
        
    Returns:
        BaseParser: 解析器实例
        
    Raises:
        ValueError: 如果没有找到合适的解析器
    """
    for parser in parsers:
        if parser.is_supported(file_path):
            return parser
    
    raise ValueError(f"不支持的文件类型: {file_path}")