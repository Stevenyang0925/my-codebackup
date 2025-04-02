import docx
import re
import os

class WordParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.doc = docx.Document(file_path)
        # 专业术语词典，确保大小写一致性
        self.terminology = {
            'ppg': 'PPG',
            'adc': 'ADC',
            'imu': 'IMU',
            'ble': 'BLE',
            'ntc': 'NTC',
            'snr': 'SNR',
        }
        # 中英文标点符号映射
        self.punctuation_map = {
            '：': ':',
            '，': ',',
            '。': '.',
            '（': '(',
            '）': ')',
            '、': ',',
            '"': '"',
            '"': '"',
            ''': "'",
            ''': "'",
            '！': '!',
            '？': '?',
            '；': ';',
            '【': '[',
            '】': ']',
            '《': '<',
            '》': '>',
        }
        # 已处理的标题，用于去重
        self.processed_headings = set()
        
    def parse(self):
        """解析Word文档并返回结构化内容"""
        content = []
        current_heading_level = 0
        current_list_level = 0
        in_list = False
        
        for para in self.doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
                
            # 标准化文本（处理专业术语和标点符号）
            text = self._normalize_text(text)
            
            # 检查是否为标题
            heading_level = self._get_heading_level(para)
            if heading_level > 0:
                # 检查标题是否重复
                if text in self.processed_headings:
                    continue
                self.processed_headings.add(text)
                
                content.append({
                    'type': 'heading',
                    'level': heading_level,
                    'text': text
                })
                current_heading_level = heading_level
                in_list = False
                continue
            
            # 检查是否为列表项
            if self._is_list_item(para):
                list_text = text
                if list_text.startswith('•') or list_text.startswith('-') or list_text.startswith('*'):
                    list_text = list_text[1:].strip()
                
                content.append({
                    'type': 'list_item',
                    'level': current_list_level,
                    'text': list_text
                })
                in_list = True
                continue
            
            # 普通段落
            content.append({
                'type': 'paragraph',
                'text': text
            })
            in_list = False
        
        return content
    
    def _normalize_text(self, text):
        """标准化文本，处理专业术语和标点符号"""
        # 处理专业术语
        for term, replacement in self.terminology.items():
            # 使用正则表达式确保只替换独立的词，而不是词的一部分
            text = re.sub(r'\b' + term + r'\b', replacement, text, flags=re.IGNORECASE)
        
        # 处理标点符号
        for cn_punct, en_punct in self.punctuation_map.items():
            text = text.replace(cn_punct, en_punct)
        
        return text
    
    def _get_heading_level(self, paragraph):
        """根据段落样式确定标题级别"""
        if not paragraph.style.name:
            return 0
            
        if 'Heading 1' in paragraph.style.name or paragraph.style.name == '标题 1':
            return 1
        elif 'Heading 2' in paragraph.style.name or paragraph.style.name == '标题 2':
            return 2
        elif 'Heading 3' in paragraph.style.name or paragraph.style.name == '标题 3':
            return 3
        elif 'Heading 4' in paragraph.style.name or paragraph.style.name == '标题 4':
            return 4
        elif 'Heading 5' in paragraph.style.name or paragraph.style.name == '标题 5':
            return 5
        elif 'Heading 6' in paragraph.style.name or paragraph.style.name == '标题 6':
            return 6
        
        # 尝试通过字体大小和加粗判断是否为标题
        if hasattr(paragraph, 'runs') and paragraph.runs:
            run = paragraph.runs[0]
            if run.bold and run.font.size and run.font.size.pt > 12:
                # 根据字体大小估计标题级别
                if run.font.size.pt >= 18:
                    return 1
                elif run.font.size.pt >= 16:
                    return 2
                elif run.font.size.pt >= 14:
                    return 3
                else:
                    return 4
        
        return 0
    
    def _is_list_item(self, paragraph):
        """判断段落是否为列表项"""
        # 检查是否有列表样式
        if paragraph.style.name and ('List' in paragraph.style.name or '列表' in paragraph.style.name):
            return True
        
        # 检查文本是否以列表标记开头
        text = paragraph.text.strip()
        if text.startswith('•') or text.startswith('-') or text.startswith('*') or re.match(r'^\d+\.', text):
            return True
        
        # 检查是否有项目符号
        if hasattr(paragraph, 'paragraph_format') and paragraph.paragraph_format.first_line_indent:
            return True
            
        return False


class MarkdownGenerator:
    def __init__(self, content):
        self.content = content
        
    def generate(self):
        """生成Markdown格式的内容"""
        markdown = []
        prev_type = None
        
        for item in self.content:
            item_type = item['type']
            
            # 确保段落之间有空行
            if prev_type and prev_type != 'list_item' and item_type != 'list_item':
                markdown.append('')
            
            if item_type == 'heading':
                level = item['level']
                text = item['text']
                markdown.append('#' * level + ' ' + text)
            
            elif item_type == 'list_item':
                level = item.get('level', 0)
                text = item['text']
                indent = '  ' * level
                markdown.append(indent + '- ' + text)
            
            elif item_type == 'paragraph':
                markdown.append(item['text'])
            
            prev_type = item_type
        
        return '\n'.join(markdown)


def convert_word_to_markdown(word_file, output_file=None):
    """将Word文档转换为Markdown格式"""
    parser = WordParser(word_file)
    content = parser.parse()
    
    generator = MarkdownGenerator(content)
    markdown = generator.generate()
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown)
    
    return markdown


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python word_parser.py <word_file> [output_file]")
        sys.exit(1)
    
    word_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(word_file):
        print(f"Error: File '{word_file}' not found.")
        sys.exit(1)
    
    try:
        markdown = convert_word_to_markdown(word_file, output_file)
        if not output_file:
            print(markdown)
        else:
            print(f"Markdown content has been written to '{output_file}'.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)