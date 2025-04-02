import os
import re

class FileWriter:
    """
    文件写入器，负责将生成的Markdown内容写入文件
    """
    
    def write(self, content: str, output_path: str, filename: str = None) -> str:
        """
        将内容写入文件
        
        Args:
            content: 要写入的内容
            output_path: 输出目录路径
            filename: 文件名，如果为None则自动生成
            
        Returns:
            str: 写入的文件的完整路径
        """
        # 确保输出目录存在
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        # 如果没有提供文件名，则生成一个
        if not filename:
            filename = f"markdown_output_{self._get_timestamp()}.md"
        
        # 确保文件名有.md扩展名
        if not filename.endswith('.md'):
            filename += '.md'
        
        # 确保文件名合法
        filename = self._sanitize_filename(filename)
        
        # 构建完整的文件路径
        file_path = os.path.join(output_path, filename)
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        import datetime
        return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        清理文件名，移除不合法字符
        """
        # 替换不合法字符
        filename = re.sub(r'[\\/*?:"<>|]', '_', filename)
        
        # 确保文件名不超过255个字符
        if len(filename) > 255:
            base, ext = os.path.splitext(filename)
            filename = base[:255-len(ext)] + ext
        
        return filename