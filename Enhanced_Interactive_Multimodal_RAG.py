"""
增强的交互式多模态RAG系统 v2.0
解决了CAMEL稳定性、多模态支持、网页研究、性能监控和界面体验等问题
"""

import os
import sys
import json
import time
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# 导入增强模块
from enhanced_llm_interface import EnhancedLLMInterface, LLMConfig
from enhanced_multimodal_processor import EnhancedMultimodalProcessor
from enhanced_web_research import EnhancedWebResearchSystem
from performance_monitor import PerformanceMonitor, PerformanceContext
from enhanced_user_interface import EnhancedUserInterface
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

class EnhancedVectorRetriever:
    """增强的向量检索器"""
    
    def __init__(self, embedding_model, performance_monitor: Optional[PerformanceMonitor] = None):
        self.embedding_model = embedding_model
        self.performance_monitor = performance_monitor
        self.documents = []
        self.doc_metadata = []
        self.document_ids = []
        self.doc_embeddings = None
        print("✅ 增强向量检索器初始化完成")
    
    def add_documents(self, texts: List[str], metadata: List[Dict[str, Any]]):
        """添加文档到检索器"""
        if not texts:
            return
        
        operation_name = "add_documents"
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
            print(f"⏳ 正在计算 {len(texts)} 个文档的嵌入向量...")
            new_embeddings = self.embedding_model.encode(texts)
            
            if self.doc_embeddings is None:
                self.doc_embeddings = new_embeddings
            else:
                self.doc_embeddings = np.vstack([self.doc_embeddings, new_embeddings])
            
            print(f"✅ 成功添加 {len(texts)} 个文档到检索器")
            
        except Exception as e:
            print(f"❌ 添加文档失败: {e}")
            raise
    
    def query(self, query_text: str, top_k: int = 5, filter_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """查询相关文档"""
        if not self.documents or self.doc_embeddings is None:
            print("⚠ 检索器中没有文档")
            return []
        
        operation_name = "vector_query"
        additional_data = {"query_length": len(query_text), "top_k": top_k, "filter_type": filter_type}
        
        if self.performance_monitor:
            with PerformanceContext(self.performance_monitor, operation_name, additional_data) as ctx:
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
            
            print(f"✅ 检索到 {len(results)} 个相关文档")
            return results
            
        except Exception as e:
            print(f"❌ 查询失败: {e}")
            return []

class EnhancedRAGSystem:
    """增强的RAG系统 - 集成所有改进功能"""
    
    def __init__(self, api_key: str, config: Optional[LLMConfig] = None, 
                 enable_performance_monitoring: bool = True,
                 cache_dir: str = "document_cache"):
        if not api_key:
            raise ValueError("API密钥不能为空")
        
        # 初始化性能监控
        self.performance_monitor = PerformanceMonitor(enable_performance_monitoring) if enable_performance_monitoring else None
        
        try:
            print("🚀 初始化增强RAG系统...")
            
            # 初始化LLM接口
            self.llm = EnhancedLLMInterface(api_key=api_key, config=config)
            
            # 初始化嵌入模型
            if not EMBEDDING_AVAILABLE:
                raise ImportError("sentence-transformers不可用")
            
            self.embedding_model = SentenceTransformer('intfloat/e5-large-v2')
            print("✅ 嵌入模型加载成功")
            
            # 初始化检索器
            self.vector_retriever = EnhancedVectorRetriever(
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
            self.current_sources = []  # 支持多个文档源
            self.document_chunks_store = {}  # 存储文档块
            
            print("✅ 增强RAG系统初始化完成!")
            
        except Exception as e:
            print(f"❌ 系统初始化失败: {e}")
            raise
    
    def setup_knowledge_base(self, sources: List[str] = None, source_type: str = "path", 
                           force_reprocess: bool = False):
        """设置知识库 - 支持多文档和增量更新"""
        if sources is None:
            sources = []
        
        operation_name = "setup_knowledge_base"
        additional_data = {"source_type": source_type, "source_count": len(sources)}
        
        if self.performance_monitor:
            with PerformanceContext(self.performance_monitor, operation_name, additional_data):
                self._setup_knowledge_base_impl(sources, source_type, force_reprocess)
        else:
            self._setup_knowledge_base_impl(sources, source_type, force_reprocess)
    
    def setup_single_document(self, source: str, source_type: str = "path", 
                            force_reprocess: bool = False):
        """设置单个文档 - 兼容原有接口"""
        self.setup_knowledge_base([source], source_type, force_reprocess)
    
    def _setup_knowledge_base_impl(self, sources: List[str], source_type: str, 
                                 force_reprocess: bool):
        """知识库设置实现 - 支持多文档处理"""
        try:
            print(f"📚 正在设置知识库...")
            print(f"文档数量: {len(sources)}")
            print(f"来源类型: {source_type}")
            
            all_texts_to_embed = []
            all_metadata_to_embed = []
            total_chunks = 0
            processing_stats = {"text": 0, "image": 0, "table": 0, "other": 0}
            
            for source in sources:
                print(f"\n📄 处理文档: {source}")
                
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
                    print(f"✅ 文档处理完成: {len(document_chunks)} 个块")
                    
                except Exception as e:
                    print(f"❌ 文档处理失败: {source} - {e}")
                    continue
            
            if not all_texts_to_embed:
                raise ValueError("未能从任何文档中提取到内容")
            
            # 添加文档到检索器
            print(f"\n⏳ 正在构建向量索引...")
            self.vector_retriever.add_documents(all_texts_to_embed, all_metadata_to_embed)
            
            # 更新系统状态
            self.knowledge_base_initialized = True
            self.current_sources = sources
            
            print(f"\n✅ 知识库设置完成!")
            print(f"处理文档数: {len(sources)}")
            print(f"总文档块数: {total_chunks}")
            print(f"内容统计: 文本({processing_stats['text']}) 图像({processing_stats['image']}) 表格({processing_stats['table']}) 其他({processing_stats['other']})")
            
            # 显示缓存统计
            cache_stats = self.document_manager.get_cache_stats()
            print(f"缓存统计: {cache_stats['cached_documents']} 个文档, {cache_stats['total_size_mb']:.1f}MB")
            
        except Exception as e:
            print(f"❌ 知识库设置失败: {e}")
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
            print(f"❌ URL文档处理失败: {e}")
            return []
    
    def enhanced_query(self, query: str, retrieval_mode: str = "快速检索") -> Dict[str, Any]:
        """执行增强查询"""
        if not self.knowledge_base_initialized:
            raise RuntimeError("知识库未初始化")
        
        operation_name = f"enhanced_query_{retrieval_mode}"
        additional_data = {"query_length": len(query), "mode": retrieval_mode}
        
        if self.performance_monitor:
            with PerformanceContext(self.performance_monitor, operation_name, additional_data):
                return self._enhanced_query_impl(query, retrieval_mode)
        else:
            return self._enhanced_query_impl(query, retrieval_mode)
    
    def _enhanced_query_impl(self, query: str, retrieval_mode: str) -> Dict[str, Any]:
        """增强查询实现"""
        try:
            print(f"\n🔍 执行{retrieval_mode}: {query}")
            print("="*60)
            
            if retrieval_mode == "快速检索":
                return self._quick_retrieval(query)
            elif retrieval_mode == "深度检索":
                return self._deep_retrieval(query)
            elif retrieval_mode == "主题检索":
                return self._topic_retrieval(query)
            else:
                raise ValueError(f"未知的检索模式: {retrieval_mode}")
                
        except Exception as e:
            print(f"❌ 查询执行失败: {e}")
            return {"error": f"查询执行失败: {e}"}
    
    def _quick_retrieval(self, query: str) -> Dict[str, Any]:
        """快速检索 - 基础向量检索"""
        print("⚡ 执行快速检索...")
        
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
        
        final_answer = self.llm.generate(prompt, max_tokens=400)
        
        return {
            'original_query': query,
            'retrieved_docs': retrieved_docs,
            'final_answer': final_answer,
            'retrieval_method': '快速检索'
        }
    
    def _deep_retrieval(self, query: str) -> Dict[str, Any]:
        """深度检索 - 查询重写+HyDE+RRF"""
        print("🔬 执行深度检索...")
        
        # 步骤1: 查询重写
        print("📝 步骤1: 查询重写")
        rewritten_query = self._query_rewriting(query)
        
        # 步骤2: HyDE生成
        print("🧠 步骤2: HyDE假设文档生成")
        hyde_doc = self._hyde_generation(rewritten_query)
        
        # 步骤3: 多路检索
        print("🔍 步骤3: 多路检索")
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
        print("🔀 步骤4: RRF结果融合")
        final_docs = self._rrf_fusion(all_results)
        
        # 步骤5: 生成最终答案
        print("💡 步骤5: 生成最终答案")
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
        
        final_answer = self.llm.generate(prompt, max_tokens=800)
        
        return {
            'original_query': query,
            'rewritten_query': rewritten_query,
            'hyde_doc': hyde_doc,
            'retrieved_docs': final_docs,
            'final_answer': final_answer,
            'retrieval_method': '深度检索(重写+HyDE+RRF)'
        }
    
    def _topic_retrieval(self, query: str) -> Dict[str, Any]:
        """主题检索 - PDF+网页综合分析"""
        print("🌐 执行主题检索...")
        
        # 步骤1: PDF检索
        print("📄 步骤1: PDF文档检索")
        pdf_docs = self.vector_retriever.query(query, top_k=5)
        
        # 步骤2: 网页研究
        print("🔍 步骤2: 网页研究")
        web_research_result = self.web_research_system.research_topic(query, max_pages=3)
        
        # 步骤3: 综合分析
        print("🧩 步骤3: 综合分析")
        
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
        
        final_answer = self.llm.generate(prompt, max_tokens=800)
        
        return {
            'original_query': query,
            'pdf_docs': pdf_docs,
            'web_research': web_research_result,
            'final_answer': final_answer,
            'retrieval_method': '主题检索(PDF+网页)'
        }
    
    def _query_rewriting(self, query: str) -> str:
        """查询重写"""
        try:
            prompt = f"""请重写以下查询，使其更适合文档检索：

原始查询：{query}

重写要求：
1. 保持核心意图
2. 使用更具体的词汇
3. 适合向量检索
4. 只返回重写后的查询

重写查询："""
            
            rewritten = self.llm.generate(prompt, max_tokens=100)
            
            # 清理结果
            if rewritten and not rewritten.startswith("抱歉"):
                lines = rewritten.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('重写') and not line.startswith('原始'):
                        return line
            
            return query
            
        except Exception as e:
            print(f"⚠ 查询重写失败: {e}")
            return query
    
    def _hyde_generation(self, query: str) -> str:
        """HyDE假设文档生成"""
        try:
            prompt = f"""基于查询生成一个假设性文档片段：

查询：{query}

要求：
1. 生成200-300字的文档片段
2. 直接回答查询问题
3. 使用专业准确的语言
4. 包含相关技术细节

假设文档："""
            
            hyde_doc = self.llm.generate(prompt, max_tokens=300)
            
            if hyde_doc and not hyde_doc.startswith("抱歉"):
                return hyde_doc.strip()
            else:
                return query
                
        except Exception as e:
            print(f"⚠ HyDE生成失败: {e}")
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
            print(f"⚠ RRF融合失败: {e}")
            return all_results[0] if all_results else []
    
    def add_documents_to_knowledge_base(self, new_sources: List[str], 
                                      source_type: str = "path") -> bool:
        """增量添加文档到知识库"""
        try:
            print(f"📚 增量添加文档到知识库...")
            print(f"新文档数量: {len(new_sources)}")
            
            if not self.knowledge_base_initialized:
                print("⚠️ 知识库未初始化，将进行完整初始化")
                self.setup_knowledge_base(new_sources, source_type)
                return True
            
            # 过滤已存在的文档
            existing_sources = set(self.current_sources)
            truly_new_sources = [s for s in new_sources if s not in existing_sources]
            
            if not truly_new_sources:
                print("ℹ️ 所有文档都已存在于知识库中")
                return True
            
            print(f"📄 实际新增文档: {len(truly_new_sources)}")
            
            # 处理新文档
            new_texts_to_embed = []
            new_metadata_to_embed = []
            
            for source in truly_new_sources:
                try:
                    if source_type == "path":
                        document_chunks = self.document_manager.process_document(source)
                    else:
                        document_chunks = self._process_url_document(source, False)
                    
                    self.document_chunks_store[source] = document_chunks
                    
                    for chunk in document_chunks:
                        new_texts_to_embed.append(chunk.content)
                        enhanced_metadata = chunk.metadata.copy()
                        enhanced_metadata.update({
                            'chunk_id': chunk.chunk_id,
                            'chunk_type': chunk.chunk_type,
                            'source_file': source
                        })
                        new_metadata_to_embed.append(enhanced_metadata)
                    
                    print(f"✅ 新增文档处理完成: {source} ({len(document_chunks)} 个块)")
                    
                except Exception as e:
                    print(f"❌ 新增文档处理失败: {source} - {e}")
                    continue
            
            if new_texts_to_embed:
                # 添加到向量检索器
                self.vector_retriever.add_documents(new_texts_to_embed, new_metadata_to_embed)
                
                # 更新源列表
                self.current_sources.extend(truly_new_sources)
                
                print(f"✅ 增量更新完成! 新增 {len(new_texts_to_embed)} 个文档块")
                return True
            else:
                print("⚠️ 没有成功处理任何新文档")
                return False
                
        except Exception as e:
            print(f"❌ 增量更新失败: {e}")
            return False
    
    def remove_documents_from_knowledge_base(self, sources_to_remove: List[str]) -> bool:
        """从知识库中移除文档"""
        try:
            print(f"🗑️ 从知识库中移除文档...")
            print(f"待移除文档: {len(sources_to_remove)}")
            
            removed_count = 0
            for source in sources_to_remove:
                if source in self.current_sources:
                    # 从存储中移除
                    if source in self.document_chunks_store:
                        del self.document_chunks_store[source]
                    
                    # 从源列表中移除
                    self.current_sources.remove(source)
                    
                    # 清理缓存
                    self.document_manager.clear_cache(source)
                    
                    removed_count += 1
                    print(f"✅ 已移除: {source}")
                else:
                    print(f"⚠️ 文档不存在: {source}")
            
            if removed_count > 0:
                print(f"✅ 成功移除 {removed_count} 个文档")
                
                # 如果移除了文档，需要重建向量索引
                if self.current_sources:
                    print("🔄 重建向量索引...")
                    self._rebuild_vector_index()
                else:
                    print("ℹ️ 知识库已清空")
                    self.knowledge_base_initialized = False
                
                return True
            else:
                print("ℹ️ 没有移除任何文档")
                return False
                
        except Exception as e:
            print(f"❌ 移除文档失败: {e}")
            return False
    
    def _rebuild_vector_index(self):
        """重建向量索引"""
        try:
            # 重新初始化检索器
            self.vector_retriever = EnhancedVectorRetriever(
                self.embedding_model, 
                self.performance_monitor
            )
            
            # 重新添加所有文档
            all_texts = []
            all_metadata = []
            
            for source in self.current_sources:
                if source in self.document_chunks_store:
                    chunks = self.document_chunks_store[source]
                    for chunk in chunks:
                        all_texts.append(chunk.content)
                        enhanced_metadata = chunk.metadata.copy()
                        enhanced_metadata.update({
                            'chunk_id': chunk.chunk_id,
                            'chunk_type': chunk.chunk_type,
                            'source_file': source
                        })
                        all_metadata.append(enhanced_metadata)
            
            if all_texts:
                self.vector_retriever.add_documents(all_texts, all_metadata)
                print(f"✅ 向量索引重建完成: {len(all_texts)} 个文档块")
            
        except Exception as e:
            print(f"❌ 重建向量索引失败: {e}")
            raise
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        cache_stats = self.document_manager.get_cache_stats()
        
        return {
            "LLM接口": self.llm.get_status(),
            "嵌入模型": {"available": EMBEDDING_AVAILABLE, "details": "intfloat/e5-large-v2"},
            "文档管理": {
                "支持格式": list(self.document_manager.supported_formats.keys()),
                "缓存文档数": cache_stats['cached_documents'],
                "缓存大小": f"{cache_stats['total_size_mb']:.1f}MB",
                "缓存使用率": f"{cache_stats['cache_usage_percent']:.1f}%"
            },
            "多模态处理": {
                "available": True,
                "details": f"OCR: {self.multimodal_processor.image_ocr_available}, 表格: {self.multimodal_processor.table_processing_available}"
            },
            "网页研究": self.web_research_system.get_research_statistics(),
            "知识库": {
                "initialized": self.knowledge_base_initialized, 
                "文档数量": len(self.current_sources),
                "文档列表": self.current_sources[:5] + ["..."] if len(self.current_sources) > 5 else self.current_sources
            },
            "性能监控": {"enabled": self.performance_monitor is not None}
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        if self.performance_monitor:
            return self.performance_monitor.get_system_performance_summary()
        else:
            return {"message": "性能监控未启用"}

class EnhancedInteractiveMultimodalRAG:
    """增强的交互式多模态RAG系统主类"""
    
    def __init__(self):
        self.api_key = None
        self.rag_system = None
        self.ui = EnhancedUserInterface()
        self.system_initialized = False
    
    def initialize_system(self) -> bool:
        """初始化系统"""
        try:
            print("🚀 正在初始化增强RAG系统...")
            
            # 加载环境变量
            load_dotenv()
            
            # 获取API密钥
            self.api_key = os.getenv('MODELSCOPE_SDK_TOKEN')
            if not self.api_key:
                self.ui.display_error("请设置MODELSCOPE_SDK_TOKEN环境变量")
                return False
            
            # 创建LLM配置
            config = LLMConfig(
                model_name="Qwen/Qwen2.5-72B-Instruct",
                max_tokens=1000,
                temperature=0.7,
                timeout=60,
                max_retries=3
            )
            
            # 初始化RAG系统
            self.rag_system = EnhancedRAGSystem(
                api_key=self.api_key,
                config=config,
                enable_performance_monitoring=True
            )
            
            self.system_initialized = True
            self.ui.display_success("增强RAG系统初始化成功!")
            
            # 显示系统状态
            status = self.rag_system.get_system_status()
            self.ui.display_system_status(status)
            
            return True
            
        except Exception as e:
            self.ui.display_error(f"系统初始化失败: {e}")
            return False
    
    def setup_knowledge_base(self) -> bool:
        """设置知识库 - 支持多文档"""
        try:
            # 获取文档来源
            sources, source_type = self.ui.get_document_sources()
            
            if not sources:
                self.ui.display_error("文档来源不能为空")
                return False
            
            # 验证输入
            if source_type == "path":
                for source in sources:
                    if not os.path.exists(source):
                        self.ui.display_error(f"文件不存在: {source}")
                        return False
            
            # 设置知识库
            self.ui.display_loading(f"正在加载 {len(sources)} 个文档...")
            self.rag_system.setup_knowledge_base(sources, source_type)
            
            self.ui.display_success("知识库设置完成!")
            return True
            
        except Exception as e:
            self.ui.display_error(f"知识库设置失败: {e}")
            return False
    
    def manage_documents(self):
        """文档管理功能"""
        while True:
            try:
                action = self.ui.get_document_management_action()
                
                if action == "add":
                    # 添加文档
                    sources, source_type = self.ui.get_document_sources()
                    if sources:
                        self.ui.display_loading(f"正在添加 {len(sources)} 个文档...")
                        success = self.rag_system.add_documents_to_knowledge_base(sources, source_type)
                        if success:
                            self.ui.display_success("文档添加成功!")
                        else:
                            self.ui.display_error("文档添加失败!")
                
                elif action == "remove":
                    # 移除文档
                    current_sources = self.rag_system.current_sources
                    if not current_sources:
                        self.ui.display_warning("知识库中没有文档")
                        continue
                    
                    sources_to_remove = self.ui.select_documents_to_remove(current_sources)
                    if sources_to_remove:
                        self.ui.display_loading(f"正在移除 {len(sources_to_remove)} 个文档...")
                        success = self.rag_system.remove_documents_from_knowledge_base(sources_to_remove)
                        if success:
                            self.ui.display_success("文档移除成功!")
                        else:
                            self.ui.display_error("文档移除失败!")
                
                elif action == "list":
                    # 列出文档
                    current_sources = self.rag_system.current_sources
                    if current_sources:
                        self.ui.display_document_list(current_sources)
                    else:
                        self.ui.display_warning("知识库中没有文档")
                
                elif action == "cache":
                    # 缓存管理
                    cache_stats = self.rag_system.document_manager.get_cache_stats()
                    self.ui.display_cache_stats(cache_stats)
                    
                    if self.ui.ask_clear_cache():
                        self.rag_system.document_manager.clear_cache()
                        self.ui.display_success("缓存已清理!")
                
                elif action == "back":
                    break
                    
            except Exception as e:
                self.ui.display_error(f"文档管理操作失败: {e}")
    
    def run_interactive_session(self):
        """运行交互式会话"""
        # 显示欢迎信息
        self.ui.print_welcome()
        
        # 初始化系统
        if not self.initialize_system():
            return
        
        # 设置知识库
        if not self.setup_knowledge_base():
            return
        
        # 主查询循环
        while True:
            try:
                # 获取用户查询
                query = self.ui.get_user_query()
                
                if not query:
                    continue
                elif query.lower() in ['quit', 'exit', '退出']:
                    break
                elif query.lower() in ['status', '状态']:
                    status = self.rag_system.get_system_status()
                    self.ui.display_system_status(status)
                    continue
                elif query.lower() in ['performance', '性能']:
                    perf_data = self.rag_system.get_performance_summary()
                    self.ui.display_performance_summary(perf_data)
                    continue
                elif query.lower() in ['reload', '重新加载']:
                    if self.setup_knowledge_base():
                        self.ui.display_success("知识库已重新加载")
                    continue
                elif query.lower() in ['manage', 'docs', '文档管理']:
                    self.manage_documents()
                    continue
                
                # 获取检索模式
                retrieval_mode = self.ui.get_retrieval_mode()
                
                # 执行查询
                self.ui.display_loading(f"正在执行{retrieval_mode}...")
                results = self.rag_system.enhanced_query(query, retrieval_mode)
                
                # 显示结果
                self.ui.display_results(results)
                
                # 询问是否保存结果
                if 'error' not in results and self.ui.ask_save_results():
                    self.ui.save_results_to_file(results)
                
                # 询问是否继续
                if not self.ui.ask_continue():
                    break
                    
            except KeyboardInterrupt:
                self.ui.display_warning("用户中断操作")
                if not self.ui.ask_continue():
                    break
            except Exception as e:
                self.ui.display_error(f"系统错误: {e}")
                continue
        
        # 显示最终性能报告
        if self.rag_system and self.rag_system.performance_monitor:
            print("\n" + "="*60)
            print("📊 最终性能报告")
            print("="*60)
            self.rag_system.performance_monitor.print_performance_report()
            
            # 询问是否保存性能数据
            if self.ui.ask_save_results():
                self.rag_system.performance_monitor.save_metrics_to_file()
        
        self.ui.display_success("感谢使用增强的交互式多模态RAG系统!")

def main():
    """主函数"""
    try:
        enhanced_rag = EnhancedInteractiveMultimodalRAG()
        enhanced_rag.run_interactive_session()
    except Exception as e:
        print(f"❌ 系统启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
