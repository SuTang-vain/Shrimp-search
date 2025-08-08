"""
增强的交互式多模态RAG系统 v2.0
集成多端模型选择功能，支持ModelScope远程API和Ollama本地部署
"""

import os
import sys
import json
import time
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# 导入V2增强模块
from enhanced_llm_interface_v2 import EnhancedLLMInterfaceV2, GenerationResult
from enhanced_user_interface_v2 import EnhancedUserInterfaceV2
from model_manager import ModelManager
from ollama_interface import OllamaInterface

# 导入原有增强模块
from enhanced_multimodal_processor import EnhancedMultimodalProcessor
from enhanced_web_research import EnhancedWebResearchSystem
from performance_monitor import PerformanceMonitor, PerformanceContext
from enhanced_document_manager import EnhancedDocumentManager, DocumentChunk

# 基础依赖
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# 嵌入模型
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDING_AVAILABLE = True
except ImportError:
    print("⚠ sentence-transformers库未安装")
    EMBEDDING_AVAILABLE = False

class EnhancedVectorRetrieverV2:
    """增强的向量检索器V2 - 支持多模型嵌入"""
    
    def __init__(self, embedding_model, performance_monitor: Optional[PerformanceMonitor] = None):
        self.embedding_model = embedding_model
        self.performance_monitor = performance_monitor
        self.documents = []
        self.doc_metadata = []
        self.document_ids = []
        self.doc_embeddings = None
        print("增强向量检索器V2初始化完成")
    
    def add_documents(self, texts: List[str], metadata: List[Dict[str, Any]]):
        """添加文档到检索器"""
        if not texts:
            return
        
        operation_name = "add_documents_v2"
        additional_data = {"document_count": len(texts)}
        
        if self.performance_monitor:
            with PerformanceContext(self.performance_monitor, operation_name, additional_data):
                self._add_documents_impl(texts, metadata)
        else:
            self._add_documents_impl(texts, metadata)
    
    def _add_documents_impl(self, texts: List[str], metadata: List[Dict[str, Any]]):
        """添加文档的实现"""
        try:
            # 生成文档ID
            new_ids = [f"doc_{len(self.documents) + i}" for i in range(len(texts))]
            
            # 存储文档
            self.documents.extend(texts)
            self.doc_metadata.extend(metadata)
            self.document_ids.extend(new_ids)
            
            # 计算嵌入
            print(f"正在计算 {len(texts)} 个文档的嵌入向量...")
            new_embeddings = self.embedding_model.encode(texts)
            
            if self.doc_embeddings is None:
                self.doc_embeddings = new_embeddings
            else:
                self.doc_embeddings = np.vstack([self.doc_embeddings, new_embeddings])
            
            print(f"成功添加 {len(texts)} 个文档到检索器")
            
        except Exception as e:
            print(f"添加文档失败: {e}")
            raise
    
    def query(self, query_text: str, top_k: int = 5, filter_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """查询相关文档"""
        if not self.documents or self.doc_embeddings is None:
            print("检索器中没有文档")
            return []
        
        operation_name = "vector_query_v2"
        additional_data = {"query_length": len(query_text), "top_k": top_k, "filter_type": filter_type}
        
        if self.performance_monitor:
            with PerformanceContext(self.performance_monitor, operation_name, additional_data):
                return self._query_impl(query_text, top_k, filter_type)
        else:
            return self._query_impl(query_text, top_k, filter_type)
    
    def _query_impl(self, query_text: str, top_k: int, filter_type: Optional[str]) -> List[Dict[str, Any]]:
        """查询实现"""
        try:
            # 计算查询嵌入
            query_embedding = self.embedding_model.encode([query_text])
            
            # 计算相似度
            similarities = cosine_similarity(query_embedding, self.doc_embeddings)[0]
            
            # 获取top_k结果
            top_indices = np.argsort(similarities)[::-1][:top_k * 2]
            
            results = []
            for idx in top_indices:
                if idx >= len(self.documents):
                    continue
                    
                doc_type = self.doc_metadata[idx].get('type', 'unknown')
                if filter_type and doc_type != filter_type:
                    continue
                
                results.append({
                    'text': self.documents[idx],
                    'similarity': float(similarities[idx]),
                    'metadata': self.doc_metadata[idx],
                    'id': self.document_ids[idx]
                })
                
                if len(results) >= top_k:
                    break
            
            print(f"检索到 {len(results)} 个相关文档")
            return results
            
        except Exception as e:
            print(f"查询失败: {e}")
            return []

class EnhancedRAGSystemV2:
    """增强的RAG系统V2 - 集成多端模型选择"""
    
    def __init__(self, api_key: Optional[str] = None, 
                 enable_performance_monitoring: bool = True,
                 cache_dir: str = "document_cache"):
        
        # 初始化性能监控
        self.performance_monitor = PerformanceMonitor(enable_performance_monitoring) if enable_performance_monitoring else None
        
        try:
            print("🚀 初始化增强RAG系统V2...")
            
            # 初始化V2 LLM接口
            self.llm = EnhancedLLMInterfaceV2(api_key=api_key)
            
            # 初始化嵌入模型
            if not EMBEDDING_AVAILABLE:
                raise ImportError("sentence-transformers不可用")
            
            self.embedding_model = SentenceTransformer('intfloat/e5-large-v2')
            print("嵌入模型加载成功")
            
            # 初始化检索器
            self.vector_retriever = EnhancedVectorRetrieverV2(
                self.embedding_model, 
                self.performance_monitor
            )
            
            # 初始化文档管理器
            self.document_manager = EnhancedDocumentManager(
                cache_dir=cache_dir,
                enable_cache=True,
                max_cache_size_mb=1000
            )
            
            # 初始化多模态处理器
            self.multimodal_processor = EnhancedMultimodalProcessor()
            
            # 初始化网页研究系统
            self.web_research_system = EnhancedWebResearchSystem()
            
            # 系统状态
            self.knowledge_base_initialized = False
            self.multimodal_content_store = {}
            self.current_sources = []
            self.document_chunks_store = {}
            
            print("增强RAG系统V2初始化完成!")
            
        except Exception as e:
            print(f"系统初始化失败: {e}")
            raise
    
    def setup_model(self) -> bool:
        """设置模型"""
        try:
            available_models = self.llm.list_available_models()
            
            # 如果没有可用模型，尝试自动选择
            if not any(models for models in available_models.values()):
                print("没有可用模型")
                return False
            
            # 显示模型选择界面
            ui = EnhancedUserInterfaceV2()
            selected_model = ui.get_model_selection(available_models)
            
            if not selected_model:
                print("未选择模型")
                return False
            
            if selected_model == 'auto':
                # 自动选择最佳模型
                selected_model = self.llm.auto_select_best_model()
                if not selected_model:
                    print("自动选择模型失败")
                    return False
            else:
                # 手动选择模型
                if not self.llm.set_model(selected_model):
                    print(f"设置模型失败: {selected_model}")
                    return False
            
            # 测试模型
            print("正在测试模型...")
            test_result = self.llm.test_model()
            ui.display_test_result(test_result)
            
            return test_result['success']
            
        except Exception as e:
            print(f"模型设置失败: {e}")
            return False
    
    def setup_knowledge_base(self, sources: List[str] = None, source_type: str = "path", 
                           force_reprocess: bool = False):
        """设置知识库 - 支持多文档和增量更新"""
        if sources is None:
            sources = []
        
        operation_name = "setup_knowledge_base_v2"
        additional_data = {"source_type": source_type, "source_count": len(sources)}
        
        if self.performance_monitor:
            with PerformanceContext(self.performance_monitor, operation_name, additional_data):
                self._setup_knowledge_base_impl(sources, source_type, force_reprocess)
        else:
            self._setup_knowledge_base_impl(sources, source_type, force_reprocess)
    
    def _setup_knowledge_base_impl(self, sources: List[str], source_type: str, 
                                 force_reprocess: bool):
        """知识库设置实现"""
        try:
            print(f"正在设置知识库...")
            print(f"文档数量: {len(sources)}")
            print(f"来源类型: {source_type}")
            
            all_texts_to_embed = []
            all_metadata_to_embed = []
            total_chunks = 0
            processing_stats = {"text": 0, "image": 0, "table": 0, "other": 0}
            
            for source in sources:
                print(f"📄 处理文档: {source}")
                
                # 确保source是字符串路径，不是列表
                if isinstance(source, list):
                    print(f"警告: 源是列表格式，取第一个元素: {source}")
                    if source:
                        source = source[0]
                    else:
                        print("跳过空列表源")
                        continue
                
                # 验证路径存在
                if source_type == "path" and not os.path.exists(source):
                    print(f"文件不存在，跳过: {source}")
                    continue
                
                try:
                    # 使用文档管理器处理文档
                    if source_type == "path":
                        document_chunks = self.document_manager.process_document(
                            source, force_reprocess=force_reprocess
                        )
                    else:
                        # 对于URL，先下载再处理
                        document_chunks = self._process_url_document(source, force_reprocess)
                    
                    # 存储文档块
                    self.document_chunks_store[source] = document_chunks
                    
                    # 转换为向量检索格式
                    for chunk in document_chunks:
                        all_texts_to_embed.append(chunk.content)
                        
                        # 增强元数据
                        enhanced_metadata = chunk.metadata.copy()
                        enhanced_metadata.update({
                            'chunk_id': chunk.chunk_id,
                            'chunk_type': chunk.chunk_type,
                            'source_file': source
                        })
                        all_metadata_to_embed.append(enhanced_metadata)
                        
                        # 统计
                        chunk_type = chunk.chunk_type
                        if chunk_type in processing_stats:
                            processing_stats[chunk_type] += 1
                        else:
                            processing_stats["other"] += 1
                    
                    total_chunks += len(document_chunks)
                    print(f"文档处理完成: {len(document_chunks)} 个块")
                    
                except Exception as e:
                    print(f"文档处理失败: {source} - {e}")
                    continue
            
            if not all_texts_to_embed:
                raise ValueError("未能从任何文档中提取到内容")
            
            # 添加文档到检索器
            print(f"\n正在构建向量索引...")
            self.vector_retriever.add_documents(all_texts_to_embed, all_metadata_to_embed)
            
            # 更新系统状态
            self.knowledge_base_initialized = True
            self.current_sources = sources
            
            print(f"\n知识库设置完成!")
            print(f"处理文档数: {len(sources)}")
            print(f"总文档块数: {total_chunks}")
            print(f"内容统计: 文本({processing_stats['text']}) 图像({processing_stats['image']}) 表格({processing_stats['table']}) 其他({processing_stats['other']})")
            
            # 显示缓存统计
            cache_stats = self.document_manager.get_cache_stats()
            print(f"缓存统计: {cache_stats['cached_documents']} 个文档, {cache_stats['total_size_mb']:.1f}MB")
            
        except Exception as e:
            print(f"知识库设置失败: {e}")
            raise
    
    def _process_url_document(self, url: str, force_reprocess: bool) -> List[DocumentChunk]:
        """处理URL文档"""
        import requests
        import tempfile
        from urllib.parse import urlparse
        
        try:
            # 下载文件
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # 获取文件扩展名
            parsed_url = urlparse(url)
            file_ext = os.path.splitext(parsed_url.path)[1]
            if not file_ext:
                file_ext = '.pdf'  # 默认为PDF
            
            # 保存到临时文件
            with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as temp_file:
                temp_file.write(response.content)
                temp_path = temp_file.name
            
            try:
                # 处理文档
                chunks = self.document_manager.process_document(temp_path, force_reprocess)
                
                # 更新元数据中的源信息
                for chunk in chunks:
                    chunk.metadata['original_url'] = url
                    chunk.metadata['source'] = url
                
                return chunks
                
            finally:
                # 清理临时文件
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            print(f"URL文档处理失败: {e}")
            return []
    
    def enhanced_query_v2(self, query: str, retrieval_mode: str = "快速检索", 
                         generation_settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """执行增强查询V2 - 支持自定义生成设置"""
        if not self.knowledge_base_initialized:
            raise RuntimeError("知识库未初始化")
        
        if not self.llm.current_backend:
            raise RuntimeError("未设置模型")
        
        operation_name = f"enhanced_query_v2_{retrieval_mode}"
        additional_data = {"query_length": len(query), "mode": retrieval_mode}
        
        if self.performance_monitor:
            with PerformanceContext(self.performance_monitor, operation_name, additional_data):
                return self._enhanced_query_v2_impl(query, retrieval_mode, generation_settings)
        else:
            return self._enhanced_query_v2_impl(query, retrieval_mode, generation_settings)
    
    def _enhanced_query_v2_impl(self, query: str, retrieval_mode: str, 
                               generation_settings: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """增强查询V2实现"""
        try:
            print(f"\n执行{retrieval_mode}: {query}")
            print("="*60)
            
            # 设置默认生成参数
            gen_settings = generation_settings or {}
            max_tokens = gen_settings.get('max_tokens', 800)
            temperature = gen_settings.get('temperature', 0.7)
            
            if retrieval_mode == "快速检索":
                return self._quick_retrieval_v2(query, max_tokens, temperature)
            elif retrieval_mode == "深度检索":
                return self._deep_retrieval_v2(query, max_tokens, temperature)
            elif retrieval_mode == "主题检索":
                return self._topic_retrieval_v2(query, max_tokens, temperature)
            elif retrieval_mode == "智能检索":
                return self._smart_retrieval_v2(query, max_tokens, temperature)
            else:
                raise ValueError(f"未知的检索模式: {retrieval_mode}")
                
        except Exception as e:
            print(f"查询执行失败: {e}")
            return {"error": f"查询执行失败: {e}"}
    
    def _quick_retrieval_v2(self, query: str, max_tokens: int, temperature: float) -> Dict[str, Any]:
        """快速检索V2"""
        print("执行快速检索...")
        
        # 直接向量检索
        retrieved_docs = self.vector_retriever.query(query, top_k=3, filter_type='text')
        
        if not retrieved_docs:
            return {"error": "未找到相关文档"}
        
        # 生成答案
        context_texts = [doc['text'] for doc in retrieved_docs]
        context_str = '\n---\n'.join(context_texts)
        
        prompt = f"""基于以下文档内容回答问题：

文档内容：
{context_str}

问题：{query}

请提供简洁明确的答案："""
        
        # 使用V2接口生成
        result = self.llm.generate(prompt, max_tokens=max_tokens, temperature=temperature)
        
        return {
            'original_query': query,
            'retrieved_docs': retrieved_docs,
            'final_answer': result.content if not result.error else f"生成失败: {result.error}",
            'retrieval_method': '快速检索V2',
            'model_info': {
                'key': result.model_key,
                'type': result.model_type,
                'generation_time': result.generation_time
            }
        }
    
    def _deep_retrieval_v2(self, query: str, max_tokens: int, temperature: float) -> Dict[str, Any]:
        """深度检索V2"""
        print("执行深度检索...")
        
        # 步骤1: 查询重写
        print("步骤1: 查询重写")
        rewritten_query = self._query_rewriting_v2(query)
        
        # 步骤2: HyDE生成
        print("步骤2: HyDE假设文档生成")
        hyde_doc = self._hyde_generation_v2(rewritten_query)
        
        # 步骤3: 多路检索
        print("步骤3: 多路检索")
        all_results = []
        
        # 原始查询检索
        original_results = self.vector_retriever.query(query, top_k=5)
        all_results.append(original_results)
        
        # 重写查询检索
        rewritten_results = self.vector_retriever.query(rewritten_query, top_k=5)
        all_results.append(rewritten_results)
        
        # HyDE文档检索
        hyde_results = self.vector_retriever.query(hyde_doc, top_k=5)
        all_results.append(hyde_results)
        
        # 多模态检索
        image_results = self.vector_retriever.query(query, top_k=3, filter_type='image')
        if image_results:
            all_results.append(image_results)
        
        table_results = self.vector_retriever.query(query, top_k=3, filter_type='table')
        if table_results:
            all_results.append(table_results)
        
        # 步骤4: RRF融合
        print("步骤4: RRF结果融合")
        final_docs = self._rrf_fusion(all_results)
        
        # 步骤5: 生成最终答案
        print("步骤5: 生成最终答案")
        context_texts = [doc['text'] for doc in final_docs[:5]]
        context_str = '\n---\n'.join(context_texts)
        
        prompt = f"""你是一个专业的文档分析助手。请基于以下文档内容回答用户问题。

文档内容：
{context_str}

用户问题：{query}

回答要求：
1. 仔细分析文档内容
2. 提供准确详细的答案
3. 引用具体文档内容
4. 使用清晰的结构

请提供详细答案："""
        
        result = self.llm.generate(prompt, max_tokens=max_tokens, temperature=temperature)
        
        return {
            'original_query': query,
            'rewritten_query': rewritten_query,
            'hyde_doc': hyde_doc,
            'retrieved_docs': final_docs,
            'final_answer': result.content if not result.error else f"生成失败: {result.error}",
            'retrieval_method': '深度检索V2(重写+HyDE+RRF)',
            'model_info': {
                'key': result.model_key,
                'type': result.model_type,
                'generation_time': result.generation_time
            }
        }
    
    def _topic_retrieval_v2(self, query: str, max_tokens: int, temperature: float) -> Dict[str, Any]:
        """主题检索V2"""
        print("执行主题检索...")
        
        # 步骤1: PDF检索
        print("步骤1: PDF文档检索")
        pdf_docs = self.vector_retriever.query(query, top_k=5)
        
        # 步骤2: 网页研究
        print("步骤2: 网页研究")
        web_research_result = self.web_research_system.research_topic(query, max_pages=3)
        
        # 步骤3: 综合分析
        print("步骤3: 综合分析")
        
        # 合并内容
        combined_context = ""
        
        # 添加PDF内容
        if pdf_docs:
            pdf_context = "\n".join([doc['text'] for doc in pdf_docs])
            combined_context += f"PDF文档内容：\n{pdf_context}\n\n"
        
        # 添加网页内容
        web_analysis = web_research_result.get('analysis', '')
        if web_analysis and not web_analysis.startswith("未能获取"):
            combined_context += f"网页研究内容：\n{web_analysis}\n\n"
        
        if not combined_context.strip():
            combined_context = f"关于'{query}'的信息主要来自PDF文档，网页研究功能当前受限。"
        
        # 生成综合答案
        prompt = f"""基于以下PDF文档和网页研究信息，回答问题：

{combined_context}

问题：{query}

请提供综合性的详细答案，整合PDF和网页信息："""
        
        result = self.llm.generate(prompt, max_tokens=max_tokens, temperature=temperature)
        
        return {
            'original_query': query,
            'pdf_docs': pdf_docs,
            'web_research': web_research_result,
            'final_answer': result.content if not result.error else f"生成失败: {result.error}",
            'retrieval_method': '主题检索V2(PDF+网页)',
            'model_info': {
                'key': result.model_key,
                'type': result.model_type,
                'generation_time': result.generation_time
            }
        }
    
    def _smart_retrieval_v2(self, query: str, max_tokens: int, temperature: float) -> Dict[str, Any]:
        """智能检索V2 - 自适应选择最佳策略"""
        print("执行智能检索...")
        
        # 分析查询复杂度
        query_complexity = self._analyze_query_complexity(query)
        
        print(f"查询复杂度分析: {query_complexity}")
        
        # 根据复杂度选择策略
        if query_complexity['complexity_score'] < 0.3:
            print("选择快速检索策略")
            return self._quick_retrieval_v2(query, max_tokens, temperature)
        elif query_complexity['complexity_score'] < 0.7:
            print("选择深度检索策略")
            return self._deep_retrieval_v2(query, max_tokens, temperature)
        else:
            print("选择主题检索策略")
            return self._topic_retrieval_v2(query, max_tokens, temperature)
    
    def _analyze_query_complexity(self, query: str) -> Dict[str, Any]:
        """分析查询复杂度"""
        complexity_indicators = {
            'length': len(query.split()),
            'has_multiple_questions': '?' in query and query.count('?') > 1,
            'has_comparison': any(word in query.lower() for word in ['比较', '对比', 'vs', '区别', '不同']),
            'has_analysis': any(word in query.lower() for word in ['分析', '解释', '原因', '为什么', '如何']),
            'has_synthesis': any(word in query.lower() for word in ['综合', '总结', '概括', '整体'])
        }
        
        # 计算复杂度分数
        score = 0.0
        if complexity_indicators['length'] > 10:
            score += 0.2
        if complexity_indicators['has_multiple_questions']:
            score += 0.3
        if complexity_indicators['has_comparison']:
            score += 0.2
        if complexity_indicators['has_analysis']:
            score += 0.2
        if complexity_indicators['has_synthesis']:
            score += 0.3
        
        return {
            'complexity_score': min(score, 1.0),
            'indicators': complexity_indicators
        }
    
    def _query_rewriting_v2(self, query: str) -> str:
        """查询重写V2"""
        try:
            prompt = f"""请重写以下查询，使其更适合文档检索：

原始查询：{query}

重写要求：
1. 保持核心意图
2. 使用更具体的词汇
3. 适合向量检索
4. 只返回重写后的查询

重写查询："""
            
            result = self.llm.generate(prompt, max_tokens=100, temperature=0.1)
            
            if result.error:
                print(f"查询重写失败: {result.error}")
                return query
            
            rewritten = result.content.strip()
            
            # 清理结果
            if rewritten and not rewritten.startswith("抱歉"):
                lines = rewritten.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('重写') and not line.startswith('原始'):
                        return line
            
            return query
            
        except Exception as e:
            print(f"查询重写失败: {e}")
            return query
    
    def _hyde_generation_v2(self, query: str) -> str:
        """HyDE假设文档生成V2"""
        try:
            prompt = f"""基于查询生成一个假设性文档片段：

查询：{query}

要求：
1. 生成200-300字的文档片段
2. 直接回答查询问题
3. 使用专业准确的语言
4. 包含相关技术细节

假设文档："""
            
            result = self.llm.generate(prompt, max_tokens=300, temperature=0.3)
            
            if result.error:
                print(f"HyDE生成失败: {result.error}")
                return query
            
            hyde_doc = result.content.strip()
            
            if hyde_doc and not hyde_doc.startswith("抱歉"):
                return hyde_doc
            else:
                return query
                
        except Exception as e:
            print(f"HyDE生成失败: {e}")
            return query
    
    def _rrf_fusion(self, all_results: List[List[Dict]], k: int = 60) -> List[Dict[str, Any]]:
        """RRF融合多个检索结果"""
        try:
            doc_scores = {}
            
            for results in all_results:
                for rank, doc in enumerate(results):
                    doc_id = doc.get('id', '')
                    if doc_id:
                        rrf_score = 1.0 / (k + rank + 1)
                        if doc_id in doc_scores:
                            doc_scores[doc_id]['score'] += rrf_score
                        else:
                            doc_scores[doc_id] = {
                                'doc': doc,
                                'score': rrf_score
                            }
            
            # 按分数排序
            sorted_docs = sorted(doc_scores.values(), key=lambda x: x['score'], reverse=True)
            
            # 添加RRF分数
            final_docs = []
            for item in sorted_docs:
                doc = item['doc'].copy()
                doc['rrf_score'] = item['score']
                final_docs.append(doc)
            
            return final_docs
            
        except Exception as e:
            print(f"RRF融合失败: {e}")
            return all_results[0] if all_results else []
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计信息"""
        if self.performance_monitor:
            return self.performance_monitor.get_stats()
        return {}
    
    def get_model_stats(self) -> Dict[str, Any]:
        """获取模型使用统计"""
        return self.llm.generation_stats
    
    def switch_model(self, model_key: str) -> bool:
        """切换模型"""
        return self.llm.set_model(model_key)
    
    def list_available_models(self) -> Dict[str, Dict[str, Any]]:
        """列出可用模型"""
        return self.llm.list_available_models()
    
    def get_current_model_info(self) -> Optional[Dict[str, Any]]:
        """获取当前模型信息"""
        return self.llm.get_current_model()

def main():
    """主函数 - 演示系统功能"""
    try:
        # 加载环境变量
        load_dotenv()
        api_key = os.getenv('MODELSCOPE_API_KEY')
        
        print("="*60)
        print("增强交互式多模态RAG系统 V2.0")
        print("支持多端模型选择 (ModelScope + Ollama)")
        print("="*60)
        
        # 初始化系统
        rag_system = EnhancedRAGSystemV2(
            api_key=api_key,
            enable_performance_monitoring=True
        )
        
        # 设置模型
        print("\n步骤1: 模型设置")
        if not rag_system.setup_model():
            print("模型设置失败，退出程序")
            return
        
        # 显示当前模型信息
        current_model = rag_system.get_current_model_info()
        if current_model:
            print(f"当前使用模型: {current_model['key']} ({current_model['provider']})")
        
        # 设置知识库
        print("\n步骤2: 知识库设置")
        ui = EnhancedUserInterfaceV2()
        
        # 获取文档路径
        document_sources = ui.get_document_sources()
        if not document_sources:
            print("未提供文档，使用演示模式")
            # 可以在这里添加演示文档
            document_sources = []
        
        if document_sources:
            rag_system.setup_knowledge_base(
                sources=document_sources,
                source_type="path",
                force_reprocess=False
            )
        
        # 交互式查询循环
        print("\n步骤3: 开始交互式查询")
        print("输入 'quit' 退出，'stats' 查看统计，'switch' 切换模型")
        print("-" * 60)
        
        while True:
            try:
                query = input("\n请输入您的问题: ").strip()
                
                if not query:
                    continue
                
                if query.lower() == 'quit':
                    break
                
                if query.lower() == 'stats':
                    # 显示统计信息
                    perf_stats = rag_system.get_performance_stats()
                    model_stats = rag_system.get_model_stats()
                    
                    print("\n性能统计:")
                    if perf_stats:
                        for operation, stats in perf_stats.items():
                            print(f"  {operation}: {stats.get('count', 0)} 次, 平均耗时: {stats.get('avg_time', 0):.2f}s")
                    
                    print("\n模型统计:")
                    print(f"  总请求数: {model_stats.get('total_requests', 0)}")
                    print(f"  成功请求: {model_stats.get('successful_requests', 0)}")
                    print(f"  失败请求: {model_stats.get('failed_requests', 0)}")
                    print(f"  总耗时: {model_stats.get('total_time', 0):.2f}s")
                    
                    model_usage = model_stats.get('model_usage', {})
                    if model_usage:
                        print("  模型使用:")
                        for model, count in model_usage.items():
                            print(f"    {model}: {count} 次")
                    
                    continue
                
                if query.lower() == 'switch':
                    # 切换模型
                    available_models = rag_system.list_available_models()
                    selected_model = ui.get_model_selection(available_models)
                    
                    if selected_model and selected_model != 'auto':
                        if rag_system.switch_model(selected_model):
                            print(f"已切换到模型: {selected_model}")
                        else:
                            print("模型切换失败")
                    continue
                
                if not rag_system.knowledge_base_initialized:
                    print("知识库未初始化，请先设置文档")
                    continue
                
                # 获取检索模式
                retrieval_mode = ui.get_retrieval_mode()
                
                # 获取生成设置
                generation_settings = ui.get_generation_settings()
                
                # 执行查询
                result = rag_system.enhanced_query_v2(
                    query=query,
                    retrieval_mode=retrieval_mode,
                    generation_settings=generation_settings
                )
                
                # 显示结果
                ui.display_query_result_v2(result)
                
            except KeyboardInterrupt:
                print("\n\n程序被用户中断")
                break
            except Exception as e:
                print(f"查询处理错误: {e}")
                continue
        
        print("\n感谢使用增强RAG系统V2!")
        
        # 显示最终统计
        print("\n最终统计:")
        perf_stats = rag_system.get_performance_stats()
        model_stats = rag_system.get_model_stats()
        
        if model_stats.get('total_requests', 0) > 0:
            success_rate = model_stats.get('successful_requests', 0) / model_stats.get('total_requests', 1) * 100
            avg_time = model_stats.get('total_time', 0) / model_stats.get('total_requests', 1)
            print(f"成功率: {success_rate:.1f}%")
            print(f"平均响应时间: {avg_time:.2f}s")
        
    except Exception as e:
        print(f"系统运行错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
