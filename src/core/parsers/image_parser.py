"""
图片文字识别解析器模块
"""

import os
import re
from typing import Dict, Any, List, Tuple
from .base_parser import BaseParser

class ImageParser(BaseParser):
    """
    图片文字识别解析器，用于从图片中提取文字
    """
    
    def get_supported_extensions(self) -> List[str]:
        """
        获取支持的文件扩展名列表
        
        Returns:
            List[str]: 支持的文件扩展名列表
        """
        return ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']
    
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        解析图片，提取文字
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            Dict[str, Any]: 解析结果
        """
        if not self.is_supported(file_path):
            raise ValueError(f"不支持的文件类型: {file_path}")
        
        title = self.extract_title(file_path)
        content = []
        
        try:
            # 导入必要的库
            import cv2
            import numpy as np
            from PIL import Image, ImageEnhance
            from paddleocr import PaddleOCR
            
            # 打开图片
            image = Image.open(file_path)
            
            # 图像预处理
            img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # 转灰度
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            
            # 应用自适应阈值
            binary = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # 降噪
            denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)
            
            # 可选：形态学操作以改善文本
            kernel = np.ones((1, 1), np.uint8)
            denoised = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel)
            
            # 保存预处理后的图像
            preprocessed_path = file_path + ".preprocessed.jpg"
            cv2.imwrite(preprocessed_path, denoised)
            
            # 初始化PaddleOCR
            ocr = PaddleOCR(
                use_angle_cls=True,  # 使用方向分类器
                lang="ch",           # 中文模型
                use_gpu=False,       # 不使用GPU
                show_log=False       # 不显示日志
            )
            
            # 进行OCR识别
            result = ocr.ocr(preprocessed_path, cls=True)
            
            # 删除预处理图像
            os.remove(preprocessed_path)
            
            # 提取识别文本
            text_lines = []
            for line in result[0]:
                if line:
                    text_lines.append(line[1][0])  # 获取识别的文本内容
            
            # 将识别的文本合并为一个字符串
            text = "\n".join(text_lines)
            
            # 添加原始图片引用
            content.append({
                "type": "image",
                "content": "原始图片",
                "additional_info": file_path
            })
            
            # 文本处理
            if text.strip():
                # 处理识别出的文本
                processed_content = self._process_text_structure(text)
                content.extend(processed_content)
            else:
                content.append({
                    "type": "text",
                    "content": "未能从图片中识别出文字。"
                })
            
            return {
                "title": title,
                "content": content
            }
            
        except ImportError as e:
            return {
                "title": title,
                "content": [{
                    "type": "text",
                    "content": f"无法解析图片文件，缺少必要的库: {e}"
                }]
            }
        except Exception as e:
            # 在实际应用中，应该使用日志记录错误
            print(f"解析图片文件时出错: {e}")
            return {
                "title": title,
                "content": [{
                    "type": "text",
                    "content": f"解析文件时出错: {e}"
                }]
            }
    
    def _detect_doc_type(self, text: str) -> Dict[str, Any]:
        """
        检测文档类型并返回相关信息
        
        Args:
            text: 识别出的文本
            
        Returns:
            Dict[str, Any]: 文档类型信息
        """
        doc_type_info = {
            "type": None,
            "level_keywords": [],
            "title_patterns": []
        }
        
        # 检测文档类型
        if re.search(r'(商业需求文档|BRD)', text, re.IGNORECASE):
            doc_type_info["type"] = "BRD"
            doc_type_info["level_keywords"] = [
                "商业需求文档", "产品属性", "用一句话", "产品的商业模式", 
                "宏观行业趋势", "微观细分市场", "产品的市场分析", "需要哪些人员",
                "时间安排", "收入来源和渠道", "收支平衡条件", "风险分析"
            ]
            doc_type_info["title_patterns"] = [
                r"商业需求文档", r"产品属性", r"用一句话", r"产品的商业模式", 
                r"宏观行业趋势", r"微观细分市场", r"产品的市场分析", r"需要哪些人员",
                r"时间安排", r"收入来源和渠道", r"收支平衡条件", r"风险分析"
            ]
        
        elif re.search(r'(市场需求文档|MRD)', text, re.IGNORECASE):
            doc_type_info["type"] = "MRD"
            doc_type_info["level_keywords"] = [
                "市场需求文档", "为什么要做", "怎么做", "产品、需求名称", 
                "用户问题", "目标市场分析", "用户描述", "目标用户分析", 
                "关键用户需求", "竞品分析", "竞争对手分析", "产品定位", 
                "产品核心目标", "产品进度计划", "市场未来"
            ]
            doc_type_info["title_patterns"] = [
                r"市场需求文档", r"为什么要做", r"怎么做", r"产品、需求名称", 
                r"用户问题", r"目标市场分析", r"用户描述", r"目标用户分析", 
                r"关键用户需求", r"竞品分析", r"竞争对手分析", r"产品定位", 
                r"产品核心目标", r"产品进度计划", r"市场未来"
            ]
        
        elif re.search(r'(产品需求文档|PRD)', text, re.IGNORECASE):
            doc_type_info["type"] = "PRD"
            doc_type_info["level_keywords"] = [
                "产品需求文档", "功能、产品名称", "版本历史", "功能清单及优先级", 
                "功能说明", "详细说明", "业务流程", "业务规则", "页面流程图", 
                "页面原型图", "输入输出", "限制", "数据格式", "功能要求", 
                "兼容性", "性能", "市场运营需求", "发布", "支持和培训", 
                "销售思路", "交互建议", "性能需求", "其他要求"
            ]
            doc_type_info["title_patterns"] = [
                r"产品需求文档", r"功能、产品名称", r"版本历史", r"功能清单及优先级", 
                r"功能说明", r"详细说明", r"业务流程", r"业务规则", r"页面流程图", 
                r"页面原型图", r"输入输出", r"限制", r"数据格式", r"功能要求", 
                r"兼容性", r"性能", r"市场运营需求", r"发布", r"支持和培训", 
                r"销售思路", r"交互建议", r"性能需求", r"其他要求"
            ]
        
        return doc_type_info
    
    def _estimate_heading_level(self, line: str, doc_type_info: Dict[str, Any], previous_headings: List[Tuple[int, str]]) -> int:
        """
        估计标题的层级
        
        Args:
            line: 文本行
            doc_type_info: 文档类型信息
            previous_headings: 之前的标题列表
            
        Returns:
            int: 标题层级
        """
        # 默认为二级标题
        level = 2
        
        # 如果是文档类型标题，设为一级
        if doc_type_info["type"] and (
            doc_type_info["type"] in line or 
            "需求文档" in line or 
            "Requirements Document" in line
        ):
            return 1
        
        # 检查是否匹配关键词模式
        for i, pattern in enumerate(doc_type_info["title_patterns"]):
            if re.search(pattern, line, re.IGNORECASE):
                # 根据关键词在列表中的位置估计层级
                if i < 3:  # 前几个关键词通常是高层级标题
                    return 2
                elif i < 10:
                    return 3
                else:
                    return 4
        
        # 根据文本特征估计层级
        if len(line) < 10:  # 非常短的标题可能是高层级
            level = 2
        elif len(line) < 20:  # 较短的标题可能是中层级
            level = 3
        else:  # 较长的标题可能是低层级
            level = 4
        
        # 根据前面的标题层级调整当前标题层级
        if previous_headings:
            prev_level = previous_headings[-1][0]
            # 避免层级跳跃过大
            if level > prev_level + 1:
                level = prev_level + 1
        
        return min(level, 4)  # 最大不超过4级标题
    
    def _process_text_structure(self, text: str) -> List[Dict[str, Any]]:
        """
        处理文本结构，识别标题和列表，生成结构化内容
        
        Args:
            text: 识别出的文本
            
        Returns:
            List[Dict[str, Any]]: 处理后的结构化内容
        """
        # 基本OCR错误修正
        corrections = {
            "盗源": "资源",
            "远是": "适是",
            "拒补": "填补",
            "矢间": "时间",
            "必持": "支持",
            "舍什么": "靠什么",
            "赵儿": "趋势",
            "究争": "竞争",
            "坎硬件": "软硬件",
            "汪来": "带来",
            "计机": "先机",
            # 移除特殊符号
            "": "",
            "": "",
            "": "",
            # 其他常见OCR错误修正
            "自标": "目标",
            "硕求": "需求",
            "爵求": "需求",
            "簿符合": "是否符合",
            "过到": "遇到",
            "适代": "迭代",
            # 修正标点符号
            """: "\"",
            """: "\"",
            "'": "'",
            "'": "'",
        }
        
        # 应用文本修正
        for old, new in corrections.items():
            text = text.replace(old, new)
        
        # 分割文本为行
        lines = []
        for line in text.split('\n'):
            line = line.strip()
            if line:  # 只保留非空行
                # 移除多余空格
                line = re.sub(r'\s{2,}', ' ', line)
                lines.append(line)
        
        # 如果没有内容，返回空列表
        if not lines:
            return []
        
        # 检测文档类型
        doc_type_info = self._detect_doc_type("\n".join(lines))
        
        # 处理文本结构，识别标题和列表
        structured_content = []
        
        # 跟踪已处理的标题及其层级
        headings = []
        
        # 处理文本，尝试识别基本结构
        current_paragraph = ""
        in_list = False
        
        for line in lines:
            # 检查是否是列表项 (以'-', '*', '•'或数字+'.'开头)
            list_match = re.match(r'^([-*•] |\d+\.\s+)(.*)$', line)
            
            # 检查是否可能是标题 (短句，不以标点符号结尾)
            is_heading = (len(line) < 60 and 
                         not line.endswith(('.', ',', ';', ':', '?', '!')) and
                         not list_match)
            
            # 检查是否包含关键词
            contains_keyword = False
            if doc_type_info["type"]:
                for keyword in doc_type_info["level_keywords"]:
                    if keyword in line:
                        contains_keyword = True
                        is_heading = True
                        break
            
            if list_match:
                # 如果有累积的段落，先添加
                if current_paragraph:
                    structured_content.append({
                        "type": "text",
                        "content": current_paragraph
                    })
                    current_paragraph = ""
                
                # 添加列表项
                structured_content.append({
                    "type": "list_item",
                    "content": line
                })
                in_list = True
            
            elif is_heading or contains_keyword:
                # 如果有累积的段落，先添加
                if current_paragraph:
                    structured_content.append({
                        "type": "text",
                        "content": current_paragraph
                    })
                    current_paragraph = ""
                
                # 估计标题层级
                level = self._estimate_heading_level(line, doc_type_info, headings)
                
                # 添加标题
                structured_content.append({
                    "type": "heading",
                    "level": level,
                    "content": line
                })
                
                # 记录标题及其层级
                headings.append((level, line))
                
                in_list = False
            
            else:
                # 如果前面是列表，且当前行不是标题或列表项，可能是列表项的延续
                if in_list and structured_content:
                    # 添加到前一个列表项
                    last_item = structured_content[-1]
                    if last_item["type"] == "list_item":
                        last_item["content"] += " " + line
                else:
                    # 普通文本，累积到当前段落
                    if current_paragraph:
                        # 检查是否应该是新段落（如果当前行很短或以问号/感叹号结尾）
                        if len(line) < 30 or current_paragraph.endswith(('?', '!', '.', ':')):
                            structured_content.append({
                                "type": "text",
                                "content": current_paragraph
                            })
                            current_paragraph = line
                        else:
                            current_paragraph += " " + line
                    else:
                        current_paragraph = line
                    in_list = False
        
        # 添加最后一个段落（如果有）
        if current_paragraph:
            structured_content.append({
                "type": "text",
                "content": current_paragraph
            })
        
        return structured_content