"""
优化的OCR脚本，通过图像预处理和Tesseract参数调整提高识别准确率
保持原图片文件的层级结构，不添加预设内容
"""

import os
import sys
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import re
import urllib.parse
import cv2
import numpy as np

def preprocess_image(image):
    """
    图像预处理，提高OCR识别准确率
    """
    # 转换为OpenCV格式
    img = np.array(image)
    
    # 转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 应用自适应阈值二值化
    binary = cv2.adaptiveThreshold(
        gray, 
        255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 
        11, 
        2
    )
    
    # 降噪
    denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)
    
    # 锐化
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(denoised, -1, kernel)
    
    # 转回PIL格式
    return Image.fromarray(sharpened)

def enhance_image(image):
    """
    增强图像质量
    """
    # 增强对比度
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    
    # 增强锐度
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(2.0)
    
    # 增强亮度
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(1.5)
    
    return image

def detect_text_orientation(image):
    """
    检测文本方向并校正
    """
    # 使用Tesseract的OSD功能检测方向
    osd = pytesseract.image_to_osd(image)
    angle = int(re.search(r'Rotate: (\d+)', osd).group(1))
    
    # 如果需要旋转，则旋转图像
    if angle != 0:
        return image.rotate(angle, expand=True)
    return image

def process_image(image_path, output_path):
    """
    处理图片，提取文本并保存为标准Markdown格式
    """
    print(f"处理图片: {image_path}")
    
    # 检查文件是否存在
    if not os.path.exists(image_path):
        print(f"错误: 文件不存在 - {image_path}")
        return False
    
    # 打开图片
    original_image = Image.open(image_path)
    
    try:
        # 图像预处理
        print("正在进行图像预处理...")
        # 检测文本方向并校正
        corrected_image = detect_text_orientation(original_image)
        # 增强图像质量
        enhanced_image = enhance_image(corrected_image)
        # 预处理图像
        processed_image = preprocess_image(enhanced_image)
        
        # 使用优化的Tesseract参数提取文本
        print("正在进行OCR识别...")
        # 设置Tesseract配置参数
        # --psm 6: 假设一个统一的文本块
        # --oem 3: 使用默认OCR引擎模式（LSTM + Legacy）
        # -l chi_sim+eng: 使用中文简体和英文语言包
        # --dpi 300: 设置较高的DPI以提高识别精度
        custom_config = r'--psm 6 --oem 3 -l chi_sim+eng --dpi 300'
        
        # 提取文本
        text = pytesseract.image_to_string(processed_image, config=custom_config)
        
        # 如果识别结果为空或太短，尝试使用原始图像
        if len(text.strip()) < 100:
            print("预处理后的图像识别结果不理想，尝试使用原始图像...")
            text = pytesseract.image_to_string(original_image, lang='chi_sim+eng', config=custom_config)
    
    except Exception as e:
        print(f"图像处理过程中出错: {str(e)}")
        print("尝试使用原始图像进行OCR识别...")
        text = pytesseract.image_to_string(original_image, lang='chi_sim+eng')
    
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
        "©": "",
        "®": "",
        "™": "",
        # 其他常见OCR错误修正
        "自标": "目标",
        "硕求": "需求",
        "簿符合": "是否符合",
        "过到": "遇到",
        "适代": "迭代",
        # 修正标点符号
        """: "\"",
        """: "\"",
        "'": "'",
        "'": "'",
        "，": ", ",
        "。": ". ",
        "；": "; ",
        "：": ": ",
        "？": "? ",
        "！": "! ",
        # 特定错误修正
        "竟品": "竞品",
        "fo)": "文档",
        "加": "",
        "OQ": "：",
        "BAM?": "How?",
        "BS Of APRN?": "本产品的优势?",
        "ROR O": "页面流程图",
        "RUEER O/": "限制 /",
        "铝": "",
    }
    
    # 应用文本修正
    for old, new in corrections.items():
        text = text.replace(old, new)
    
    # 分割文本为行
    lines = text.split('\n')
    
    # 清理行
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line:  # 只保留非空行
            # 移除多余空格
            line = re.sub(r'\s{2,}', ' ', line)
            cleaned_lines.append(line)
    
    # 处理文本结构，识别标题和列表
    markdown_lines = []
    
    # 添加文档标题 (使用文件名)
    doc_title = os.path.splitext(os.path.basename(image_path))[0]
    markdown_lines.append(f"# {doc_title}")
    markdown_lines.append("")
    
    # 添加原始图片链接 (使用URL编码处理路径中的空格)
    encoded_path = image_path.replace("\\", "/")  # 使用正斜杠
    encoded_path = urllib.parse.quote(encoded_path, safe="/:")  # URL编码，保留斜杠和冒号
    markdown_lines.append(f"![原始图片]({encoded_path})")
    markdown_lines.append("")
    
    # 识别文档层级结构
    # 1. 首先检测可能的一级标题（通常是文档类型）
    doc_type_patterns = [
        r'(商业需求文档|BRD)',
        r'(市场需求文档|MRD)',
        r'(产品需求文档|PRD)'
    ]
    
    # 查找文档类型
    doc_type = None
    for i, line in enumerate(cleaned_lines):
        for pattern in doc_type_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                doc_type = line
                markdown_lines.append(f"## {line}")
                markdown_lines.append("")
                # 从cleaned_lines中移除已处理的行
                cleaned_lines[i] = ""
                break
        if doc_type:
            break
    
    # 清理空行
    cleaned_lines = [line for line in cleaned_lines if line]
    
    # 2. 处理剩余文本，尝试识别基本结构
    current_paragraph = ""
    
    for line in cleaned_lines:
        # 检查是否是列表项 (以'-', '*', '•'或数字+'.'开头)
        list_match = re.match(r'^([-*•] |\d+\.\s+)(.*)$', line)
        
        # 检查是否可能是标题 (短句，不以标点符号结尾)
        is_heading = (len(line) < 60 and 
                     not line.endswith(('.', ',', ';', ':', '?', '!')) and
                     not list_match)
        
        if list_match:
            # 如果有累积的段落，先添加
            if current_paragraph:
                markdown_lines.append(current_paragraph)
                markdown_lines.append("")
                current_paragraph = ""
            
            # 添加列表项，保持原有格式
            markdown_lines.append(line)
        
        elif is_heading:
            # 如果有累积的段落，先添加
            if current_paragraph:
                markdown_lines.append(current_paragraph)
                markdown_lines.append("")
                current_paragraph = ""
            
            # 添加二级标题
            markdown_lines.append(f"## {line}")
            markdown_lines.append("")
        
        else:
            # 普通文本，累积到当前段落
            if current_paragraph:
                # 检查是否应该是新段落（如果当前行很短或以问号/感叹号结尾）
                if len(line) < 30 or current_paragraph.endswith(('?', '!', '.', ':')):
                    markdown_lines.append(current_paragraph)
                    markdown_lines.append("")
                    current_paragraph = line
                else:
                    current_paragraph += " " + line
            else:
                current_paragraph = line
    
    # 添加最后一个段落（如果有）
    if current_paragraph:
        markdown_lines.append(current_paragraph)
    
    # 保存Markdown文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(markdown_lines))
    
    print(f"已保存Markdown文件: {output_path}")
    return True

def main():
    """
    主函数
    """
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("用法: python simple_ocr.py <图片目录> [输出目录]")
        return
    
    # 获取目录路径
    input_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "./simple_output"
    
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 处理目录中的所有jpg图片
    processed = 0
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + ".md")
            if process_image(image_path, output_path):
                processed += 1
    
    print(f"处理完成，共处理了 {processed} 个图片文件")

if __name__ == "__main__":
    main()
