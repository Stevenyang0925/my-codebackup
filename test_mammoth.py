import mammoth
import sys

def main():
    if len(sys.argv) < 2:
        print("用法: python test_mammoth.py [word文档路径]")
        return
    
    file_path = sys.argv[1]
    
    try:
        # 设置自定义样式映射
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
        p[style-name='Normal'] => p:fresh
        p[style-name='List Paragraph'] => p:fresh
        r[style-name='Strong'] => strong
        r[style-name='Emphasis'] => em
        """
        
        # 自定义转换选项
        conversion_options = {
            "style_map": style_map
        }
        
        with open(file_path, "rb") as docx_file:
            # 使用与 word_parser.py 相同的调用方式
            result = mammoth.convert_to_markdown(docx_file, conversion_options=conversion_options)
            markdown = result.value
            
            # 打印完整的转换结果
            print("完整转换结果:")
            print("=" * 50)
            print(markdown)
            print("=" * 50)
            
            # 打印警告信息
            if result.messages:
                print("\n警告信息:")
                for message in result.messages:
                    print(f"- {message.message} ({message.type})")
    except Exception as e:
        print(f"转换失败: {e}")

if __name__ == "__main__":
    main()
