"""
异常处理模块，定义自定义异常类
"""

class MarkdownConverterError(Exception):
    """Markdown转换器基础异常类"""
    pass

class FileParsingError(MarkdownConverterError):
    """文件解析错误"""
    def __init__(self, file_path: str, message: str = None):
        self.file_path = file_path
        self.message = message or f"解析文件时出错: {file_path}"
        super().__init__(self.message)

class MarkdownGenerationError(MarkdownConverterError):
    """Markdown生成错误"""
    def __init__(self, message: str = None):
        self.message = message or "生成Markdown时出错"
        super().__init__(self.message)

class FileWritingError(MarkdownConverterError):
    """文件写入错误"""
    def __init__(self, file_path: str, message: str = None):
        self.file_path = file_path
        self.message = message or f"写入文件时出错: {file_path}"
        super().__init__(self.message)

class UnsupportedFileTypeError(MarkdownConverterError):
    """不支持的文件类型错误"""
    def __init__(self, file_path: str, message: str = None):
        self.file_path = file_path
        self.message = message or f"不支持的文件类型: {file_path}"
        super().__init__(self.message)