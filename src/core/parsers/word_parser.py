"""
Word文档解析器模块
"""

import os
import re
from typing import Dict, Any, List
from .base_parser import BaseParser

class WordParser(BaseParser):
    """
    Word文档解析器，用于解析.docx和.doc文件
    """
    
    def get_supported_extensions(self) -> List[str]:
        """
        获取支持的文件扩展名列表
        
        Returns:
            List[str]: 支持的文件扩展名列表
        """
        return ['.docx', '.doc']
    
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        解析Word文档
        
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
            # 导入python-docx库
            import docx
            
            # 打开Word文档
            doc = docx.Document(file_path)
            
            # 提取标题（使用文档的第一个段落作为标题）
            if doc.paragraphs and doc.paragraphs[0].text:
                title = doc.paragraphs[0].text
            
            # 增强标题识别和层级结构处理
            current_section = None
            current_subsection = None
            list_items = []
            in_list = False
            
            for para in doc.paragraphs:
                text = para.text.strip()
                if not text:
                    # 空段落可能表示列表结束
                    if in_list and list_items:
                        content.append({
                            "type": "list",
                            "content": "",
                            "additional_info": list_items,
                            "list_type": "unordered"
                        })
                        list_items = []
                        in_list = False
                    continue
                
                # 增强标题识别 - 检查样式和其他特征
                is_heading = False
                heading_level = 0
                
                # 1. 检查官方标题样式
                if para.style.name.startswith('Heading'):
                    try:
                        heading_level = int(para.style.name.replace('Heading', ''))
                        is_heading = True
                    except ValueError:
                        heading_level = 1
                        is_heading = True
                
                # 2. 检查字体特征（大字体、加粗等可能是标题）
                if not is_heading and para.runs:
                    # 检查是否所有文本都是加粗的
                    all_bold = all(run.bold for run in para.runs if run.text.strip())
                    # 检查字体大小（如果有设置）
                    large_font = any(run.font.size and run.font.size.pt > 12 for run in para.runs if run.text.strip())
                    
                    if (all_bold or large_font) and len(text) < 100:  # 标题通常较短
                        is_heading = True
                        # 根据文本特征估计标题级别
                        if text.lower().startswith(('chapter', '第', '章')):
                            heading_level = 1
                        elif len(text) < 20:  # 短文本可能是小标题
                            heading_level = 2
                        else:
                            heading_level = 3
                
                # 3. 检查是否是可能的标题（无标点符号结尾的短句）
                if not is_heading and len(text) < 50 and not re.search(r'[.,:;?!]$', text):
                    # 检查是否包含关键词
                    section_keywords = ['模块', '传感器', '配置', '管理', '接口', '要求', '策略']
                    subsection_keywords = ['LED', '光电', '采样', '加速度', '陀螺仪', '睡眠', '日常', '紧急']
                    
                    if any(keyword in text for keyword in section_keywords):
                        is_heading = True
                        heading_level = 2  # 假设为二级标题
                    elif any(keyword in text for keyword in subsection_keywords) or text.endswith('：') or text.endswith(':'):
                        is_heading = True
                        heading_level = 3  # 假设为三级标题
                
                # 处理标题
                if is_heading:
                    # 如果之前在处理列表，先结束列表
                    if in_list and list_items:
                        content.append({
                            "type": "list",
                            "content": "",
                            "additional_info": list_items,
                            "list_type": "unordered"
                        })
                        list_items = []
                        in_list = False
                    
                    # 防止标题重复
                    if content and content[-1]["type"] == "heading" and content[-1]["content"] == text:
                        # 跳过重复的标题
                        continue
                    
                    # 添加标题
                    content.append({
                        "type": "heading",
                        "level": heading_level,
                        "content": text
                    })
                    
                    # 更新当前章节信息
                    if heading_level == 1:
                        current_section = text
                        current_subsection = None
                    elif heading_level == 2:
                        current_subsection = text
                    
                    continue
                
                # 处理列表项
                if text.startswith(('-', '•', '*', '·')) or re.match(r'^\d+\.', text):
                    # 清理列表项标记
                    item_text = re.sub(r'^[-•*·]\s*', '', text)
                    item_text = re.sub(r'^\d+\.\s*', '', item_text)
                    
                    list_items.append(item_text)
                    in_list = True
                    continue
                
                # 检测可能的列表项（冒号分隔的短语）
                if ':' in text or '：' in text:
                    parts = re.split(r'[:：]', text, 1)
                    if len(parts) == 2 and parts[0].strip() and parts[1].strip():
                        # 这可能是一个键值对，作为列表项处理
                        list_items.append(f"{parts[0].strip()}：{parts[1].strip()}")
                        in_list = True
                        continue
                
                # 如果之前在处理列表，先结束列表
                if in_list and list_items:
                    content.append({
                        "type": "list",
                        "content": "",
                        "additional_info": list_items,
                        "list_type": "unordered"
                    })
                    list_items = []
                    in_list = False
                
                # 处理普通段落
                content.append({
                    "type": "text",
                    "content": text
                })
            
            # 处理文档末尾可能的未完成列表
            if in_list and list_items:
                content.append({
                    "type": "list",
                    "content": "",
                    "additional_info": list_items,
                    "list_type": "unordered"
                })
            
            # 处理表格
            for table in doc.tables:
                table_data = []
                
                # 提取表格数据
                for row in table.rows:
                    row_data = [cell.text for cell in row.cells]
                    table_data.append(row_data)
                
                if table_data:
                    content.append({
                        "type": "table",
                        "content": "",
                        "additional_info": table_data
                    })
            
            # 后处理 - 规范化专业术语大小写
            self._normalize_terminology(content)
            
            return {
                "title": title,
                "content": content
            }
            
        except ImportError:
            return {
                "title": title,
                "content": [{
                    "type": "text",
                    "content": "无法解析Word文档，请安装python-docx库: pip install python-docx"
                }]
            }
        except Exception as e:
            # 在实际应用中，应该使用日志记录错误
            print(f"解析Word文档时出错: {e}")
            return {
                "title": title,
                "content": [{
                    "type": "text",
                    "content": f"解析文件时出错: {e}"
                }]
            }
    
    def _normalize_terminology(self, content):
        """
        规范化专业术语的大小写
        
        Args:
            content: 内容列表
        """
        terms = {
            "ppg": "PPG",
            "adc": "ADC",
            "imu": "IMU",
            "ntc": "NTC",
            "ble": "BLE"
        }
        
        for item in content:
            if "content" in item and isinstance(item["content"], str):
                for term_lower, term_upper in terms.items():
                    # 使用正则表达式确保只替换独立的词，而不是词的一部分
                    item["content"] = re.sub(
                        r'\b' + term_lower + r'\b', 
                        term_upper, 
                        item["content"], 
                        flags=re.IGNORECASE
                    )
            
            if "additional_info" in item and isinstance(item["additional_info"], list):
                for i, info in enumerate(item["additional_info"]):
                    if isinstance(info, str):
                        for term_lower, term_upper in terms.items():
                            item["additional_info"][i] = re.sub(
                                r'\b' + term_lower + r'\b', 
                                term_upper, 
                                info, 
                                flags=re.IGNORECASE
                            )