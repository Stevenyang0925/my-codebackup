"""
测试 mammoth 库的 API
"""

import mammoth
import os

def test_mammoth_api():
    # 测试文件路径
    test_file = r"E:\PythonProjects\Markdown\test file\智能腕表2代.docx"
    
    if not os.path.exists(test_file):
        print(f"错误: 文件不存在: {test_file}")
        return
    
    print(f"开始测试 mammoth API: {test_file}")
    
    # 定义样式映射
    style_map = """
    p[style-name='Heading 1'] => h1:fresh
    p[style-name='Heading 2'] => h2:fresh
    p[style-name='Heading 3'] => h3:fresh
    p[style-name='Heading 4'] => h4:fresh
    p[style-name='标题 1'] => h1:fresh
    p[style-name='标题 2'] => h2:fresh
    p[style-name='标题 3'] => h3:fresh
    p[style-name='标题 4'] => h4:fresh
    p[style-name='Title'] => h1:fresh
    p[style-name='Subtitle'] => h2:fresh
    """
    
    try:
        # 尝试不同的 API 调用方式
        print("\n方法1: 使用 style_map 参数")
        with open(test_file, "rb") as docx_file:
            try:
                result = mammoth.convert_to_markdown(docx_file, style_map=style_map)
                print(f"成功! 结果前100个字符: {result.value[:100]}")
            except Exception as e:
                print(f"失败: {e}")
        
        print("\n方法2: 不使用样式映射")
        with open(test_file, "rb") as docx_file:
            try:
                result = mammoth.convert_to_markdown(docx_file)
                print(f"成功! 结果前100个字符: {result.value[:100]}")
            except Exception as e:
                print(f"失败: {e}")
        
        # 保存结果到文件
        output_file = r"E:\PythonProjects\Markdown\output\mammoth_test_output.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result.value)
        
        print(f"\n结果已保存到: {output_file}")
    
    except Exception as e:
        print(f"测试过程中发生异常: {e}")

if __name__ == "__main__":
    test_mammoth_api()
