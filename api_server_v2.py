#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shrimp Search API服务器 V2
基于Enhanced_Interactive_Multimodal_RAG_v2.py的增强RAG系统
为前端提供完整的多模态RAG搜索功能
"""

import os
import sys
import json
import time
import uuid
import traceback
import threading
from typing import Dict, Any, Optional, List
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# 导入V2增强RAG系统
from Enhanced_Interactive_Multimodal_RAG_v2 import EnhancedRAGSystemV2
from enhanced_llm_interface_v2 import EnhancedLLMInterfaceV2, GenerationResult
from model_manager import ModelManager
from ollama_interface import OllamaInterface

# 加载环境变量
load_dotenv()

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 全局变量
rag_system = None
search_tasks = {}  # 存储搜索任务
search_results = {}  # 存储搜索结果

class SearchTask:
    """搜索任务类"""
    
    def __init__(self, search_id: str, query: str, model: str, mode: str, max_results: int = 5):
        self.search_id = search_id
        self.query = query
        self.model = model
        self.mode = mode
        self.max_results = max_results
        self.status = "pending"  # pending, running, completed, failed
        self.progress = 0
        self.current_step = ""
        self.message = ""
        self.result = None
        self.error = None
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        
    def to_dict(self):
        """转换为字典格式"""
        return {
            "search_id": self.search_id,
            "query": self.query,
            "model": self.model,
            "mode": self.mode,
            "max_results": self.max_results,
            "status": self.status,
            "progress": self.progress,
            "current_step": self.current_step,
            "message": self.message,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

def initialize_rag_system():
    """初始化RAG系统V2"""
    global rag_system
    
    try:
        print("🚀 初始化增强RAG系统V2...")
        
        # 获取API密钥
        api_key = os.getenv('MODELSCOPE_SDK_TOKEN')
        
        # 初始化RAG系统V2
        rag_system = EnhancedRAGSystemV2(
            api_key=api_key,
            enable_performance_monitoring=True,
            cache_dir="document_cache"
        )
        
        print("🔧 设置默认模型...")
        
        # 尝试设置默认模型
        model_priority = ['qwen2.5-7b', 'qwen2.5-14b', 'glm4.5', 'qwen2.5-7b-local']
        
        model_set = False
        for model_key in model_priority:
            try:
                if rag_system.llm.set_model(model_key):
                    print(f"✅ 成功设置默认模型: {model_key}")
                    model_set = True
                    break
            except Exception as e:
                print(f"⚠️ 设置模型 {model_key} 失败: {e}")
                continue
        
        if not model_set:
            print("⚠️ 未能设置任何默认模型，将在搜索时尝试")
        
        # 设置默认知识库
        print("📚 检查知识库...")
        document_dirs = ["documents", "uploaded_documents", "document_cache"]
        documents = []
        
        for doc_dir in document_dirs:
            if os.path.exists(doc_dir):
                for root, dirs, files in os.walk(doc_dir):
                    for file in files:
                        if file.endswith(('.pdf', '.txt', '.md', '.docx', '.doc')):
                            documents.append(os.path.join(root, file))
        
        if documents:
            print(f"📄 找到 {len(documents)} 个文档，正在建立知识库...")
            try:
                rag_system.setup_knowledge_base(
                    sources=documents,
                    source_type="path",
                    force_reprocess=False
                )
                print("✅ 知识库初始化完成")
            except Exception as e:
                print(f"⚠️ 知识库初始化失败: {e}")
        else:
            print("📝 未找到文档，将使用在线模式")
        
        print("🎉 RAG系统V2初始化完成!")
        return True
        
    except Exception as e:
        print(f"❌ RAG系统初始化失败: {e}")
        traceback.print_exc()
        return False

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    global rag_system
    
    try:
        status = {
            "status": "healthy" if rag_system else "initializing",
            "rag_system_ready": rag_system is not None,
            "timestamp": time.time(),
            "version": "2.0",
            "features": [
                "multimodal_processing",
                "web_research",
                "performance_monitoring",
                "multi_model_support",
                "async_search"
            ]
        }
        
        if rag_system:
            try:
                # 获取当前模型信息
                current_model = rag_system.llm.get_current_model()
                if current_model:
                    status["current_model"] = current_model
                
                # 获取知识库状态
                status["knowledge_base_ready"] = rag_system.knowledge_base_initialized
                
                # 获取系统统计
                if hasattr(rag_system, 'current_sources'):
                    status["knowledge_base_sources"] = len(rag_system.current_sources)
                
                # 获取性能统计
                if rag_system.performance_monitor:
                    perf_stats = rag_system.performance_monitor.get_summary()
                    status["performance_stats"] = perf_stats
                    
            except Exception as e:
                status["warning"] = f"获取系统状态时出错: {str(e)}"
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }), 500

@app.route('/api/models', methods=['GET'])
def get_available_models():
    """获取可用模型列表"""
    global rag_system
    
    if not rag_system:
        return jsonify({
            "success": False,
            "error": "RAG系统未初始化"
        }), 500
    
    try:
        # 获取可用模型
        available_models = rag_system.llm.list_available_models()
        
        # 转换为前端友好的格式
        models_list = []
        
        # 远程模型
        for key, config in available_models.get('remote', {}).items():
            models_list.append({
                "id": key,
                "name": f"{config['name']} ({config['provider']})",
                "type": "remote",
                "provider": config['provider'],
                "description": config.get('description', ''),
                "available": config.get('available', True),
                "default": key == 'qwen2.5-7b'
            })
        
        # 本地模型
        for key, config in available_models.get('local', {}).items():
            models_list.append({
                "id": key,
                "name": f"{config['name']} (本地)",
                "type": "local",
                "provider": config['provider'],
                "description": config.get('description', ''),
                "available": config.get('available', False),
                "installed": config.get('installed', False),
                "default": False
            })
        
        # 获取当前模型
        current_model = rag_system.llm.get_current_model()
        
        return jsonify({
            "success": True,
            "data": models_list,
            "current_model": current_model
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"获取模型列表失败: {str(e)}"
        }), 500

@app.route('/api/search', methods=['POST'])
def start_search():
    """开始搜索"""
    global rag_system, search_tasks
    
    if not rag_system:
        return jsonify({
            "success": False,
            "error": "RAG系统未初始化"
        }), 500
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "请求数据为空"
            }), 400
        
        # 提取搜索参数
        query = data.get('query', '').strip()
        model = data.get('model', '')
        mode = data.get('mode', '快速检索')
        max_results = data.get('max_results', 5)
        
        if not query:
            return jsonify({
                "success": False,
                "error": "查询内容不能为空"
            }), 400
        
        # 生成搜索ID
        search_id = str(uuid.uuid4())
        
        # 创建搜索任务
        search_task = SearchTask(
            search_id=search_id,
            query=query,
            model=model,
            mode=mode,
            max_results=max_results
        )
        
        search_tasks[search_id] = search_task
        
        # 在后台线程中执行搜索
        search_thread = threading.Thread(
            target=execute_search_task,
            args=(search_task,),
            daemon=True
        )
        search_thread.start()
        
        return jsonify({
            "success": True,
            "search_id": search_id,
            "message": "搜索已开始"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"搜索启动失败: {str(e)}"
        }), 500

def execute_search_task(search_task: SearchTask):
    """执行搜索任务"""
    global rag_system, search_results
    
    try:
        search_task.status = "running"
        search_task.started_at = datetime.now()
        
        # 步骤1: 解析意图
        search_task.current_step = "parsing"
        search_task.message = "正在解析用户意图..."
        search_task.progress = 10
        time.sleep(0.5)  # 模拟处理时间
        
        # 切换模型（如果指定）
        if search_task.model:
            try:
                current_model = rag_system.llm.get_current_model()
                if not current_model or current_model.get('key') != search_task.model:
                    if not rag_system.llm.set_model(search_task.model):
                        raise Exception(f"切换到模型 {search_task.model} 失败")
            except Exception as e:
                search_task.status = "failed"
                search_task.error = f"模型切换失败: {str(e)}"
                search_task.completed_at = datetime.now()
                return
        
        # 步骤2: 搜索知识库
        search_task.current_step = "searching"
        search_task.message = "正在搜索知识库..."
        search_task.progress = 30
        time.sleep(0.8)
        
        # 步骤3: 获取信息
        search_task.current_step = "retrieving"
        search_task.message = "正在获取相关信息..."
        search_task.progress = 60
        time.sleep(1.0)
        
        # 步骤4: 生成回答
        search_task.current_step = "generating"
        search_task.message = "正在生成回答..."
        search_task.progress = 80
        
        # 执行实际搜索
        try:
            if rag_system.knowledge_base_initialized:
                # 使用RAG搜索
                result = rag_system.enhanced_query_v2(
                    query=search_task.query,
                    retrieval_mode=search_task.mode,
                    generation_settings={
                        'max_tokens': 800,
                        'temperature': 0.7
                    }
                )
            else:
                # 直接使用LLM
                result = direct_llm_query(search_task.query)
        except RuntimeError as e:
            # 如果enhanced_query_v2抛出RuntimeError（如知识库未初始化），回退到直接LLM查询
            print(f"RAG查询失败，回退到直接LLM查询: {e}")
            result = direct_llm_query(search_task.query)
        except Exception as e:
            # 处理其他异常
            print(f"搜索过程中发生异常: {e}")
            result = {'error': f"搜索过程中发生异常: {str(e)}"}
        
        # 处理结果
        if 'error' in result:
            search_task.status = "failed"
            search_task.error = result['error']
        else:
            search_task.status = "completed"
            search_task.progress = 100
            search_task.message = "搜索完成"
            
            # 格式化结果
            formatted_result = format_search_result(result, search_task)
            search_results[search_task.search_id] = formatted_result
        
        search_task.completed_at = datetime.now()
        
    except Exception as e:
        search_task.status = "failed"
        search_task.error = f"搜索执行失败: {str(e)}"
        search_task.completed_at = datetime.now()
        print(f"搜索任务失败: {e}")
        traceback.print_exc()

def direct_llm_query(query: str) -> Dict[str, Any]:
    """直接使用LLM查询（无知识库模式）"""
    global rag_system
    
    try:
        prompt = f"""请回答以下问题：

问题：{query}

请提供详细、准确的回答："""
        
        result = rag_system.llm.generate(
            prompt=prompt,
            max_tokens=800,
            temperature=0.7
        )
        
        if result.error:
            return {'error': result.error}
        
        return {
            'original_query': query,
            'final_answer': result.content,
            'retrieval_method': '直接LLM查询',
            'model_info': {
                'key': result.model_key,
                'type': result.model_type,
                'generation_time': result.generation_time
            },
            'retrieved_docs': []
        }
        
    except Exception as e:
        return {'error': f"LLM查询失败: {str(e)}"}

def format_file_size(size_bytes):
    """格式化文件大小"""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f}{size_names[i]}"

def format_search_result(result: Dict[str, Any], search_task: SearchTask) -> Dict[str, Any]:
    """格式化搜索结果"""
    try:
        formatted = {
            'answer': result.get('final_answer', ''),
            'model': search_task.model,
            'mode': search_task.mode,
            'processing_time': 0,
            'sources': [],
            'web_results': []
        }
        
        # 处理模型信息
        model_info = result.get('model_info', {})
        if model_info:
            formatted['processing_time'] = model_info.get('generation_time', 0)
        
        # 处理检索到的文档
        retrieved_docs = result.get('retrieved_docs', [])
        for doc in retrieved_docs:
            source = {
                'title': doc.get('metadata', {}).get('title', '相关文档'),
                'content': doc.get('text', ''),
                'similarity': doc.get('similarity', 0),
                'source': doc.get('metadata', {}).get('source_file', '知识库')
            }
            formatted['sources'].append(source)
        
        # 处理网页研究结果
        web_research = result.get('web_research', {})
        if web_research and 'search_results' in web_research:
            for web_result in web_research['search_results']:
                formatted['web_results'].append({
                    'title': web_result.get('title', ''),
                    'url': web_result.get('url', ''),
                    'snippet': web_result.get('snippet', '')
                })
        
        return formatted
        
    except Exception as e:
        print(f"格式化结果失败: {e}")
        return {
            'answer': result.get('final_answer', '处理结果时出错'),
            'model': search_task.model,
            'mode': search_task.mode,
            'processing_time': 0,
            'sources': [],
            'web_results': []
        }

@app.route('/api/search/<search_id>/progress', methods=['GET'])
def get_search_progress(search_id: str):
    """获取搜索进度"""
    global search_tasks
    
    if search_id not in search_tasks:
        return jsonify({
            "success": False,
            "error": "搜索ID不存在"
        }), 404
    
    try:
        search_task = search_tasks[search_id]
        
        return jsonify({
            "success": True,
            "status": search_task.status,
            "progress": search_task.progress,
            "current_step": search_task.current_step,
            "message": search_task.message,
            "error": search_task.error
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"获取进度失败: {str(e)}"
        }), 500

@app.route('/api/search/<search_id>/results', methods=['GET'])
def get_search_results(search_id: str):
    """获取搜索结果"""
    global search_tasks, search_results
    
    if search_id not in search_tasks:
        return jsonify({
            "success": False,
            "error": "搜索ID不存在"
        }), 404
    
    try:
        search_task = search_tasks[search_id]
        
        if search_task.status == "failed":
            return jsonify({
                "success": False,
                "error": search_task.error or "搜索失败"
            }), 500
        
        if search_task.status != "completed":
            return jsonify({
                "success": False,
                "error": "搜索尚未完成",
                "status": search_task.status
            }), 202
        
        if search_id not in search_results:
            return jsonify({
                "success": False,
                "error": "搜索结果不可用"
            }), 500
        
        return jsonify({
            "success": True,
            "data": search_results[search_id]
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"获取结果失败: {str(e)}"
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload_documents():
    """上传文档"""
    global rag_system
    
    if not rag_system:
        return jsonify({
            "success": False,
            "error": "RAG系统未初始化"
        }), 500
    
    try:
        if 'files' not in request.files:
            return jsonify({
                "success": False,
                "error": "没有文件"
            }), 400
        
        files = request.files.getlist('files')
        if not files or all(f.filename == '' for f in files):
            return jsonify({
                "success": False,
                "error": "没有选择文件"
            }), 400
        
        # 创建上传目录
        upload_dir = "uploaded_documents"
        os.makedirs(upload_dir, exist_ok=True)
        
        uploaded_files = []
        for file in files:
            if file.filename and file.filename.strip():
                # 生成安全的文件名
                filename = file.filename
                file_path = os.path.join(upload_dir, filename)
                
                # 如果文件已存在，添加时间戳
                if os.path.exists(file_path):
                    name, ext = os.path.splitext(filename)
                    timestamp = int(time.time())
                    filename = f"{name}_{timestamp}{ext}"
                    file_path = os.path.join(upload_dir, filename)
                
                # 保存文件
                file.save(file_path)
                uploaded_files.append(file_path)
        
        if not uploaded_files:
            return jsonify({
                "success": False,
                "error": "没有有效文件"
            }), 400
        
        # 更新知识库
        try:
            # 获取现有文档
            existing_sources = getattr(rag_system, 'current_sources', [])
            all_sources = existing_sources + uploaded_files
            
            rag_system.setup_knowledge_base(
                sources=all_sources,
                source_type="path",
                force_reprocess=True
            )
            
            # 准备详细的文件信息
            uploaded_files_info = []
            for file_path in uploaded_files:
                stat = os.stat(file_path)
                uploaded_files_info.append({
                    "filename": os.path.basename(file_path),
                    "size": stat.st_size,
                    "formatted_size": format_file_size(stat.st_size),
                    "upload_time": stat.st_mtime,
                    "formatted_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime))
                })
            
            return jsonify({
                "success": True,
                "message": f"成功上传 {len(uploaded_files)} 个文件",
                "uploaded_files": uploaded_files_info,
                "knowledge_base_updated": True
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"文件上传成功但知识库更新失败: {str(e)}",
                "uploaded_files": [os.path.basename(f) for f in uploaded_files]
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"文件上传失败: {str(e)}"
        }), 500

@app.route('/api/documents', methods=['GET'])
def get_documents():
    """获取已上传的文档列表"""
    try:
        upload_dir = "uploaded_documents"
        if not os.path.exists(upload_dir):
            return jsonify({
                "success": True,
                "documents": []
            })
        
        documents = []
        for filename in os.listdir(upload_dir):
            file_path = os.path.join(upload_dir, filename)
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                documents.append({
                    "filename": filename,
                    "size": stat.st_size,
                    "upload_time": stat.st_mtime,
                    "formatted_size": format_file_size(stat.st_size),
                    "formatted_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime))
                })
        
        # 按上传时间倒序排列
        documents.sort(key=lambda x: x['upload_time'], reverse=True)
        
        return jsonify({
            "success": True,
            "documents": documents
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"获取文档列表失败: {str(e)}"
        }), 500

@app.route('/api/documents/delete', methods=['POST'])
def delete_document():
    """删除指定文档"""
    global rag_system
    
    try:
        data = request.get_json()
        if not data or 'filename' not in data:
            return jsonify({
                "success": False,
                "error": "缺少文件名参数"
            }), 400
        
        filename = data['filename']
        upload_dir = "uploaded_documents"
        file_path = os.path.join(upload_dir, filename)
        
        if not os.path.exists(file_path):
            return jsonify({
                "success": False,
                "error": "文件不存在"
            }), 404
        
        # 删除文件
        os.remove(file_path)
        
        # 更新知识库
        if rag_system:
            try:
                # 获取剩余文档
                remaining_files = []
                if os.path.exists(upload_dir):
                    for f in os.listdir(upload_dir):
                        remaining_files.append(os.path.join(upload_dir, f))
                
                # 重新构建知识库
                if remaining_files:
                    rag_system.setup_knowledge_base(
                        sources=remaining_files,
                        source_type="path",
                        force_reprocess=True
                    )
                else:
                    # 如果没有文件了，清空知识库
                    rag_system.current_sources = []
                    rag_system.knowledge_base_initialized = False
                    
            except Exception as e:
                print(f"更新知识库时出错: {e}")
        
        return jsonify({
            "success": True,
            "message": f"文件 {filename} 删除成功"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"删除文件失败: {str(e)}"
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_system_stats():
    """获取系统统计信息"""
    global rag_system, search_tasks
    
    if not rag_system:
        return jsonify({
            "success": False,
            "error": "RAG系统未初始化"
        }), 500
    
    try:
        # 搜索统计
        search_stats = {
            "total_searches": len(search_tasks),
            "completed_searches": len([t for t in search_tasks.values() if t.status == "completed"]),
            "failed_searches": len([t for t in search_tasks.values() if t.status == "failed"]),
            "running_searches": len([t for t in search_tasks.values() if t.status == "running"])
        }
        
        # 系统统计
        system_stats = {
            "knowledge_base_initialized": rag_system.knowledge_base_initialized,
            "current_sources_count": len(getattr(rag_system, 'current_sources', [])),
            "current_model": rag_system.llm.get_current_model()
        }
        
        # 性能统计
        performance_stats = {}
        if rag_system.performance_monitor:
            performance_stats = rag_system.performance_monitor.get_summary()
        
        # LLM统计
        llm_stats = getattr(rag_system.llm, 'generation_stats', {})
        
        return jsonify({
            "success": True,
            "data": {
                "search_stats": search_stats,
                "system_stats": system_stats,
                "performance_stats": performance_stats,
                "llm_stats": llm_stats
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"获取统计信息失败: {str(e)}"
        }), 500

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "API端点不存在"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "服务器内部错误"
    }), 500

@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({
        "success": False,
        "error": f"未处理的异常: {str(e)}"
    }), 500

if __name__ == '__main__':
    print("🦐 Shrimp Search API服务器 V2 启动中...")
    print("📋 基于Enhanced_Interactive_Multimodal_RAG_v2.py")
    
    # 初始化RAG系统
    if initialize_rag_system():
        print("✅ RAG系统V2初始化成功")
    else:
        print("⚠️ RAG系统V2初始化失败，某些功能可能不可用")
    
    print("\n🌐 API服务器启动在 http://localhost:5000")
    print("📚 API接口文档:")
    print("  GET  /api/health - 健康检查")
    print("  GET  /api/models - 获取可用模型列表")
    print("  POST /api/search - 开始搜索")
    print("  GET  /api/search/<id>/progress - 获取搜索进度")
    print("  GET  /api/search/<id>/results - 获取搜索结果")
    print("  POST /api/upload - 上传文档")
    print("  GET  /api/stats - 获取系统统计信息")
    print("\n🔧 支持的功能:")
    print("  ✅ 多模态文档处理")
    print("  ✅ 网页研究集成")
    print("  ✅ 性能监控")
    print("  ✅ 多模型支持 (ModelScope + Ollama)")
    print("  ✅ 异步搜索处理")
    print("  ✅ 实时进度跟踪")
    print("  ✅ 文件上传和知识库管理")
    print("-" * 60)
    
    # 启动Flask应用
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )