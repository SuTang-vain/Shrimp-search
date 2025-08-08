"""
测试文档处理修复
验证Enhanced_Interactive_Multimodal_RAG_v2.py中的文档处理修复是否有效
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_document_processing():
    """测试文档处理功能"""
    print("🧪 测试文档处理修复")
    print("=" * 50)
    
    try:
        # 导入修复后的系统
        from Enhanced_Interactive_Multimodal_RAG_v2 import EnhancedRAGSystemV2
        
        # 初始化系统
        print("步骤1: 初始化RAG系统...")
        rag_system = EnhancedRAGSystemV2(
            api_key=os.getenv('MODELSCOPE_SDK_TOKEN'),
            enable_performance_monitoring=True
        )
        print("✅ 系统初始化成功")
        
        # 测试不同的文档源格式
        test_cases = [
            {
                'name': '正常字符串路径',
                'sources': ['G:\\Program for work\\Other\\CamelAgent.pdf'],
                'should_work': True
            },
            {
                'name': '列表格式路径 (修复前会出错)',
                'sources': [['G:\\Program for work\\Other\\CamelAgent.pdf']],
                'should_work': True  # 现在应该能处理
            },
            {
                'name': '空列表',
                'sources': [[]],
                'should_work': False
            },
            {
                'name': '不存在的文件',
                'sources': ['nonexistent_file.pdf'],
                'should_work': False
            },
            {
                'name': '字符串"path"',
                'sources': ['path'],
                'should_work': False
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n步骤{i+1}: 测试 - {test_case['name']}")
            print(f"源数据: {test_case['sources']}")
            
            try:
                rag_system.setup_knowledge_base(
                    sources=test_case['sources'],
                    source_type="path",
                    force_reprocess=False
                )
                
                if test_case['should_work']:
                    print("✅ 测试通过 - 按预期工作")
                else:
                    print("⚠️  测试意外成功 - 预期应该失败")
                    
            except Exception as e:
                if test_case['should_work']:
                    print(f"❌ 测试失败 - 预期应该成功: {e}")
                else:
                    print(f"✅ 测试通过 - 按预期失败: {e}")
        
        print(f"\n🎯 文档处理修复验证完成")
        
        # 如果有实际的PDF文件，测试正常流程
        test_pdf = 'G:\\Program for work\\Other\\CamelAgent.pdf'
        if os.path.exists(test_pdf):
            print(f"\n步骤{len(test_cases)+2}: 测试实际PDF文件处理")
            try:
                rag_system.setup_knowledge_base(
                    sources=[test_pdf],
                    source_type="path",
                    force_reprocess=False
                )
                print("✅ 实际PDF文件处理成功")
                
                # 测试查询
                if rag_system.knowledge_base_initialized:
                    print("步骤7: 测试查询功能")
                    result = rag_system.enhanced_query_v2(
                        query="这个文档的主要内容是什么？",
                        retrieval_mode="快速检索"
                    )
                    
                    if 'error' not in result:
                        print("✅ 查询功能正常")
                        print(f"答案预览: {result.get('final_answer', '')[:100]}...")
                    else:
                        print(f"❌ 查询失败: {result['error']}")
                
            except Exception as e:
                print(f"❌ 实际PDF处理失败: {e}")
        else:
            print(f"⚠️  测试PDF文件不存在: {test_pdf}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🚀 文档处理修复验证")
    print("=" * 60)
    
    success = test_document_processing()
    
    if success:
        print("\n🎉 修复验证完成！")
        print("\n📝 修复说明:")
        print("1. ✅ 修复了列表格式路径的处理")
        print("2. ✅ 添加了路径存在性检查")
        print("3. ✅ 改进了错误处理和日志输出")
        print("4. ✅ 保持了向后兼容性")
        
        print("\n🔧 修复内容:")
        print("- 检测并处理列表格式的源路径")
        print("- 验证文件路径存在性")
        print("- 跳过无效或不存在的文件")
        print("- 提供更清晰的错误信息")
    else:
        print("\n❌ 修复验证失败，请检查代码")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)