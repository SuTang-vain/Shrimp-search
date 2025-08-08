"""
文档管理功能演示脚本
展示增强的文档预处理缓存、增量更新和多格式支持功能
"""

import os
import sys
from pathlib import Path
from enhanced_document_manager import EnhancedDocumentManager

def demo_document_formats():
    """演示多种文档格式支持"""
    print("🎯 演示1: 多种文档格式支持")
    print("="*60)
    
    manager = EnhancedDocumentManager(cache_dir="demo_cache")
    
    # 显示支持的格式
    print("📋 支持的文档格式:")
    for fmt in manager.supported_formats.keys():
        print(f"  • {fmt}")
    
    print(f"\n✅ 文档管理器支持 {len(manager.supported_formats)} 种格式")

def demo_caching_system():
    """演示缓存系统"""
    print("\n🎯 演示2: 文档预处理缓存系统")
    print("="*60)
    
    manager = EnhancedDocumentManager(
        cache_dir="demo_cache",
        enable_cache=True,
        max_cache_size_mb=100
    )
    
    # 创建测试文档
    test_content = """
# 测试文档

这是一个测试文档，用于演示缓存功能。

## 第一章
这里是第一章的内容。

## 第二章
这里是第二章的内容。

### 2.1 小节
这是一个小节的内容。

## 总结
这是文档的总结部分。
    """
    
    test_file = "test_document.md"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    try:
        print("📄 首次处理文档...")
        chunks1 = manager.process_document(test_file)
        print(f"✅ 处理完成: {len(chunks1)} 个文档块")
        
        print("\n📄 再次处理同一文档 (应使用缓存)...")
        chunks2 = manager.process_document(test_file)
        print(f"✅ 处理完成: {len(chunks2)} 个文档块")
        
        # 显示缓存统计
        cache_stats = manager.get_cache_stats()
        print(f"\n💾 缓存统计:")
        print(f"  • 缓存文档数: {cache_stats['cached_documents']}")
        print(f"  • 缓存大小: {cache_stats['total_size_mb']:.2f}MB")
        print(f"  • 缓存使用率: {cache_stats['cache_usage_percent']:.1f}%")
        
    finally:
        # 清理测试文件
        if os.path.exists(test_file):
            os.unlink(test_file)

def demo_batch_processing():
    """演示批量文档处理"""
    print("\n🎯 演示3: 批量文档处理")
    print("="*60)
    
    manager = EnhancedDocumentManager(cache_dir="demo_cache")
    
    # 创建多个测试文档
    test_files = []
    for i in range(3):
        filename = f"test_doc_{i+1}.txt"
        content = f"""
文档 {i+1}

这是第 {i+1} 个测试文档。

内容包括:
- 项目 1
- 项目 2
- 项目 3

结束。
        """
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        test_files.append(filename)
    
    try:
        print(f"📚 批量处理 {len(test_files)} 个文档...")
        results = manager.batch_process_documents(test_files, max_workers=2)
        
        total_chunks = sum(len(chunks) for chunks in results.values())
        print(f"✅ 批量处理完成: 总共 {total_chunks} 个文档块")
        
        for file_path, chunks in results.items():
            print(f"  • {file_path}: {len(chunks)} 个块")
            
    finally:
        # 清理测试文件
        for file_path in test_files:
            if os.path.exists(file_path):
                os.unlink(file_path)

def demo_incremental_updates():
    """演示增量更新功能"""
    print("\n🎯 演示4: 增量文档更新")
    print("="*60)
    
    from Enhanced_Interactive_Multimodal_RAG import EnhancedRAGSystem, LLMConfig
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv('MODELSCOPE_SDK_TOKEN')
    
    if not api_key:
        print("⚠️ 未找到API密钥，跳过增量更新演示")
        return
    
    try:
        # 初始化RAG系统
        config = LLMConfig(
            model_name="Qwen/Qwen2.5-72B-Instruct",
            max_tokens=500,
            temperature=0.7
        )
        
        rag_system = EnhancedRAGSystem(
            api_key=api_key,
            config=config,
            enable_performance_monitoring=False
        )
        
        # 创建初始文档
        doc1_content = """
# 初始文档

这是知识库中的第一个文档。

## 主要内容
- 概念A
- 概念B
- 概念C
        """
        
        doc1_file = "initial_doc.md"
        with open(doc1_file, 'w', encoding='utf-8') as f:
            f.write(doc1_content)
        
        print("📚 设置初始知识库...")
        rag_system.setup_knowledge_base([doc1_file], "path")
        print(f"✅ 初始知识库包含 {len(rag_system.current_sources)} 个文档")
        
        # 创建新文档
        doc2_content = """
# 新增文档

这是后来添加的文档。

## 新内容
- 概念D
- 概念E
- 概念F
        """
        
        doc2_file = "new_doc.md"
        with open(doc2_file, 'w', encoding='utf-8') as f:
            f.write(doc2_content)
        
        print("\n📄 增量添加新文档...")
        success = rag_system.add_documents_to_knowledge_base([doc2_file], "path")
        
        if success:
            print(f"✅ 增量更新成功! 知识库现包含 {len(rag_system.current_sources)} 个文档")
            
            # 测试查询
            print("\n🔍 测试查询...")
            results = rag_system.enhanced_query("概念D是什么？", "快速检索")
            
            if 'error' not in results:
                print("✅ 查询成功，新文档内容已可检索")
            else:
                print(f"❌ 查询失败: {results['error']}")
        
        # 清理文件
        for file_path in [doc1_file, doc2_file]:
            if os.path.exists(file_path):
                os.unlink(file_path)
                
    except Exception as e:
        print(f"❌ 增量更新演示失败: {e}")

def demo_cache_management():
    """演示缓存管理功能"""
    print("\n🎯 演示5: 缓存管理功能")
    print("="*60)
    
    manager = EnhancedDocumentManager(
        cache_dir="demo_cache",
        max_cache_size_mb=1  # 设置很小的缓存限制用于演示
    )
    
    # 创建多个文档来填满缓存
    test_files = []
    for i in range(5):
        filename = f"cache_test_{i+1}.txt"
        # 创建较大的内容
        content = f"文档 {i+1}\n" + "这是测试内容。\n" * 100
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        test_files.append(filename)
    
    try:
        print("📚 处理多个文档以测试缓存管理...")
        
        for i, file_path in enumerate(test_files):
            print(f"\n📄 处理文档 {i+1}: {file_path}")
            chunks = manager.process_document(file_path)
            
            cache_stats = manager.get_cache_stats()
            print(f"  缓存使用: {cache_stats['cache_usage_percent']:.1f}%")
            
            if cache_stats['cache_usage_percent'] > 80:
                print("  🗑️ 缓存使用率过高，自动清理中...")
        
        print("\n💾 最终缓存统计:")
        final_stats = manager.get_cache_stats()
        for key, value in final_stats.items():
            print(f"  • {key}: {value}")
        
        # 演示手动清理缓存
        print("\n🗑️ 手动清理所有缓存...")
        manager.clear_cache()
        
        after_clear_stats = manager.get_cache_stats()
        print(f"✅ 清理后缓存文档数: {after_clear_stats['cached_documents']}")
        
    finally:
        # 清理测试文件
        for file_path in test_files:
            if os.path.exists(file_path):
                os.unlink(file_path)

def main():
    """主演示函数"""
    print("🚀 文档管理功能演示")
    print("="*80)
    
    try:
        # 演示1: 多种文档格式支持
        demo_document_formats()
        
        # 演示2: 缓存系统
        demo_caching_system()
        
        # 演示3: 批量处理
        demo_batch_processing()
        
        # 演示4: 增量更新 (需要API密钥)
        demo_incremental_updates()
        
        # 演示5: 缓存管理
        demo_cache_management()
        
        print("\n🎉 所有演示完成!")
        
    except KeyboardInterrupt:
        print("\n⚠️ 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
    finally:
        # 清理演示缓存目录
        import shutil
        cache_dir = Path("demo_cache")
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
            print("🗑️ 演示缓存已清理")

if __name__ == "__main__":
    main()