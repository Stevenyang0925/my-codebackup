# 从原型HTML文件中提取图标资源

import os
import re
import base64
from pathlib import Path
from bs4 import BeautifulSoup
import cairosvg

def ensure_dir(directory):
    """确保目录存在，如果不存在则创建"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def extract_svg_icons():
    """从原型HTML文件中提取SVG图标并保存为PNG"""
    # 项目根目录
    project_root = Path(os.path.dirname(os.path.dirname(__file__)))
    
    # 原型文件路径
    prototype_path = project_root / "prototype.html"
    
    # 图标输出目录
    icons_dir = project_root / "resources" / "icons"
    ensure_dir(icons_dir)
    
    # 读取原型文件
    with open(prototype_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 提取内联SVG图标
    svg_patterns = [
        # 下拉菜单图标
        {
            'name': 'dropdown.svg',
            'pattern': r'url\("data:image/svg\+xml;charset=UTF-8,%3csvg[^"]+points=\'6 9 12 15 18 9\'[^"]+\)',
            'type': 'background-image'
        }
    ]
    
    # 创建基本图标集
    basic_icons = [
        {'name': 'new.png', 'color': '#007AFF', 'text': 'N'},
        {'name': 'open.png', 'color': '#007AFF', 'text': 'O'},
        {'name': 'save.png', 'color': '#007AFF', 'text': 'S'},
        {'name': 'import.png', 'color': '#FF9500', 'text': 'I'},
        {'name': 'undo.png', 'color': '#5856D6', 'text': '↩'},
        {'name': 'redo.png', 'color': '#5856D6', 'text': '↪'},
        {'name': 'convert.png', 'color': '#34C759', 'text': 'C'},
        {'name': 'preview.png', 'color': '#FF2D55', 'text': 'P'},
        {'name': 'split.png', 'color': '#AF52DE', 'text': '⊞'}
    ]
    
    # 提取SVG图标
    for pattern in svg_patterns:
        matches = re.findall(pattern['pattern'], html_content)
        if matches:
            svg_data = matches[0]
            # 提取SVG内容
            svg_content = re.sub(r'url\("data:image/svg\+xml;charset=UTF-8,', '', svg_data)
            svg_content = svg_content.rstrip(')"')
            svg_content = svg_content.replace('%3c', '<').replace('%3e', '>').replace('%3d', '=')
            
            # 保存SVG文件
            svg_path = icons_dir / pattern['name']
            with open(svg_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            
            # 转换为PNG (如果需要)
            png_path = icons_dir / pattern['name'].replace('.svg', '.png')
            cairosvg.svg2png(url=str(svg_path), write_to=str(png_path), output_width=24, output_height=24)
    
    # 生成基本图标
    from PIL import Image, ImageDraw, ImageFont
    
    for icon in basic_icons:
        # 创建一个24x24的透明图像
        img = Image.new('RGBA', (24, 24), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 绘制圆形背景
        draw.ellipse((0, 0, 24, 24), fill=icon['color'])
        
        # 添加文本
        try:
            # 尝试加载系统字体
            font = ImageFont.truetype("arial.ttf", 14)
        except IOError:
            # 如果找不到，使用默认字体
            font = ImageFont.load_default()
        
        # 计算文本位置使其居中 - 修复这里的错误
        # 使用textbbox代替已弃用的textsize
        left, top, right, bottom = draw.textbbox((0, 0), icon['text'], font=font)
        text_width = right - left
        text_height = bottom - top
        position = ((24 - text_width) / 2, (24 - text_height) / 2)
        
        # 绘制文本
        draw.text(position, icon['text'], fill='white', font=font)
        
        # 保存图标
        img.save(icons_dir / icon['name'])
    
    print(f"图标已提取并保存到 {icons_dir}")

if __name__ == "__main__":
    extract_svg_icons()