"""
增强的多模态处理器 - 改进图像和表格提取能力
"""

import os
import io
import base64
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

# 图像处理
try:
    from PIL import Image
    import pytesseract
    IMAGE_OCR_AVAILABLE = True
except ImportError:
    print("⚠ PIL或pytesseract未安装，图像OCR功能不可用")
    IMAGE_OCR_AVAILABLE = False

# 表格处理
try:
    import pandas as pd
    import tabula
    TABLE_PROCESSING_AVAILABLE = True
except ImportError:
    print("⚠ pandas或tabula未安装，表格处理功能受限")
    TABLE_PROCESSING_AVAILABLE = False

# PDF处理
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    print("⚠ PyMuPDF未安装，使用基础PDF处理")
    PYMUPDF_AVAILABLE = False

from unstructured.partition.auto import partition
from unstructured.documents.elements import Text, Image as UnstructuredImage, Table

class EnhancedMultimodalProcessor:
    """增强的多模态处理器"""
    
    def __init__(self):
        self.image_ocr_available = IMAGE_OCR_AVAILABLE
        self.table_processing_available = TABLE_PROCESSING_AVAILABLE
        self.pymupdf_available = PYMUPDF_AVAILABLE
        
        print("多模态处理器初始化:")
        print(f"  图像OCR: {'✓' if self.image_ocr_available else '✗'}")
        print(f"  表格处理: {'✓' if self.table_processing_available else '✗'}")
        print(f"  PyMuPDF: {'✓' if self.pymupdf_available else '✗'}")
    
    def process_pdf_with_multimodal(self, pdf_source: str, is_url: bool = False) -> Dict[str, Any]:
        """处理PDF并提取多模态内容"""
        
        # 首先尝试使用PyMuPDF进行更好的多模态提取
        if self.pymupdf_available:
            try:
                return self._process_with_pymupdf(pdf_source, is_url)
            except Exception as e:
                print(f"⚠ PyMuPDF处理失败，使用unstructured: {e}")
        
        # 降级到unstructured
        return self._process_with_unstructured(pdf_source, is_url)
    
    def _process_with_pymupdf(self, pdf_source: str, is_url: bool = False) -> Dict[str, Any]:
        """使用PyMuPDF处理PDF - 更好的多模态支持"""
        import requests
        
        # 获取PDF文档
        if is_url:
            response = requests.get(pdf_source, timeout=30)
            response.raise_for_status()
            pdf_data = response.content
            doc = fitz.open(stream=pdf_data, filetype="pdf")
        else:
            doc = fitz.open(pdf_source)
        
        texts_to_embed = []
        metadata_to_embed = []
        multimodal_content_store = {}
        multimodal_id_counter = 0
        
        print(f"使用PyMuPDF处理PDF，共{len(doc)}页")
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # 提取文本
            text = page.get_text()
            if text.strip():
                multimodal_id = f"multimodal_{multimodal_id_counter}"
                multimodal_id_counter += 1
                
                texts_to_embed.append(text.strip())
                metadata_to_embed.append({
                    'type': 'text',
                    'source': 'pdf',
                    'page': page_num + 1,
                    'multimodal_id': multimodal_id
                })
            
            # 提取图像
            image_list = page.get_images()
            for img_index, img in enumerate(image_list):
                try:
                    # 获取图像数据
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    
                    if pix.n - pix.alpha < 4:  # 确保是RGB或灰度图像
                        img_data = pix.tobytes("png")
                        
                        # 进行OCR提取文本
                        ocr_text = self._extract_text_from_image(img_data)
                        
                        if ocr_text.strip():
                            multimodal_id = f"multimodal_{multimodal_id_counter}"
                            multimodal_id_counter += 1
                            
                            image_description = f"图像内容 (第{page_num + 1}页): {ocr_text}"
                            texts_to_embed.append(image_description)
                            metadata_to_embed.append({
                                'type': 'image',
                                'source': 'pdf',
                                'page': page_num + 1,
                                'multimodal_id': multimodal_id
                            })
                            
                            multimodal_content_store[multimodal_id] = {
                                'type': 'image',
                                'data': ocr_text,
                                'page': page_num + 1,
                                'image_index': img_index
                            }
                            
                            print(f"✓ 提取图像文本 (第{page_num + 1}页): {len(ocr_text)}字符")
                    
                    pix = None  # 释放内存
                    
                except Exception as e:
                    print(f"⚠ 图像提取失败 (第{page_num + 1}页): {e}")
                    continue
            
            # 提取表格
            tables = self._extract_tables_from_page(page, page_num + 1)
            for table_data in tables:
                multimodal_id = f"multimodal_{multimodal_id_counter}"
                multimodal_id_counter += 1
                
                table_description = f"表格内容 (第{page_num + 1}页): {table_data}"
                texts_to_embed.append(table_description)
                metadata_to_embed.append({
                    'type': 'table',
                    'source': 'pdf',
                    'page': page_num + 1,
                    'multimodal_id': multimodal_id
                })
                
                multimodal_content_store[multimodal_id] = {
                    'type': 'table',
                    'data': table_data,
                    'page': page_num + 1
                }
                
                print(f"✓ 提取表格 (第{page_num + 1}页): {len(table_data)}字符")
        
        doc.close()
        
        return {
            'texts_to_embed': texts_to_embed,
            'metadata_to_embed': metadata_to_embed,
            'multimodal_content_store': multimodal_content_store,
            'processing_method': 'PyMuPDF'
        }
    
    def _process_with_unstructured(self, pdf_source: str, is_url: bool = False) -> Dict[str, Any]:
        """使用unstructured处理PDF"""
        import requests
        
        if is_url:
            response = requests.get(pdf_source, timeout=30)
            response.raise_for_status()
            pdf_bytes = response.content
            pdf_file = io.BytesIO(pdf_bytes)
            elements = partition(file=pdf_file)
        else:
            elements = partition(filename=pdf_source)
        
        texts_to_embed = []
        metadata_to_embed = []
        multimodal_content_store = {}
        multimodal_id_counter = 0
        
        print(f"使用unstructured处理PDF，共{len(elements)}个元素")
        
        for element in elements:
            element_text = str(element).strip()
            if not element_text or len(element_text) < 10:
                continue
            
            multimodal_id = f"multimodal_{multimodal_id_counter}"
            multimodal_id_counter += 1
            
            if isinstance(element, Text):
                texts_to_embed.append(element_text)
                metadata_to_embed.append({
                    'type': 'text',
                    'source': 'pdf',
                    'multimodal_id': multimodal_id
                })
            elif isinstance(element, UnstructuredImage):
                # 增强图像处理
                enhanced_image_text = self._enhance_image_description(element_text)
                texts_to_embed.append(enhanced_image_text)
                metadata_to_embed.append({
                    'type': 'image',
                    'source': 'pdf',
                    'multimodal_id': multimodal_id
                })
                multimodal_content_store[multimodal_id] = {
                    'type': 'image',
                    'data': enhanced_image_text
                }
            elif isinstance(element, Table):
                # 增强表格处理
                enhanced_table_text = self._enhance_table_description(element_text)
                texts_to_embed.append(enhanced_table_text)
                metadata_to_embed.append({
                    'type': 'table',
                    'source': 'pdf',
                    'multimodal_id': multimodal_id
                })
                multimodal_content_store[multimodal_id] = {
                    'type': 'table',
                    'data': enhanced_table_text
                }
            else:
                texts_to_embed.append(element_text)
                metadata_to_embed.append({
                    'type': 'text',
                    'source': 'pdf',
                    'multimodal_id': multimodal_id
                })
        
        return {
            'texts_to_embed': texts_to_embed,
            'metadata_to_embed': metadata_to_embed,
            'multimodal_content_store': multimodal_content_store,
            'processing_method': 'unstructured'
        }
    
    def _extract_text_from_image(self, img_data: bytes) -> str:
        """从图像中提取文本"""
        if not self.image_ocr_available:
            return "图像内容 (OCR不可用)"
        
        try:
            # 将字节数据转换为PIL图像
            image = Image.open(io.BytesIO(img_data))
            
            # 使用OCR提取文本
            ocr_text = pytesseract.image_to_string(image, lang='chi_sim+eng')
            
            if ocr_text.strip():
                return ocr_text.strip()
            else:
                return "图像内容 (未检测到文本)"
                
        except Exception as e:
            print(f"⚠ OCR处理失败: {e}")
            return "图像内容 (OCR处理失败)"
    
    def _extract_tables_from_page(self, page, page_num: int) -> List[str]:
        """从页面提取表格"""
        tables = []
        
        try:
            # 获取页面中的表格
            page_tables = page.find_tables()
            
            for table in page_tables:
                try:
                    # 提取表格数据
                    table_data = table.extract()
                    
                    # 转换为可读格式
                    table_text = self._format_table_data(table_data)
                    if table_text:
                        tables.append(table_text)
                        
                except Exception as e:
                    print(f"⚠ 表格提取失败 (第{page_num}页): {e}")
                    continue
                    
        except Exception as e:
            print(f"⚠ 页面表格查找失败 (第{page_num}页): {e}")
        
        return tables
    
    def _format_table_data(self, table_data: List[List]) -> str:
        """格式化表格数据"""
        if not table_data:
            return ""
        
        try:
            # 过滤空行和空列
            filtered_data = []
            for row in table_data:
                if row and any(cell and str(cell).strip() for cell in row):
                    filtered_row = [str(cell).strip() if cell else "" for cell in row]
                    filtered_data.append(filtered_row)
            
            if not filtered_data:
                return ""
            
            # 转换为文本格式
            table_text = "表格数据:\n"
            for i, row in enumerate(filtered_data):
                if i == 0:  # 表头
                    table_text += "| " + " | ".join(row) + " |\n"
                    table_text += "|" + "|".join(["-" * (len(cell) + 2) for cell in row]) + "|\n"
                else:
                    table_text += "| " + " | ".join(row) + " |\n"
            
            return table_text
            
        except Exception as e:
            print(f"⚠ 表格格式化失败: {e}")
            return "表格内容 (格式化失败)"
    
    def _enhance_image_description(self, original_text: str) -> str:
        """增强图像描述"""
        if not original_text or len(original_text) < 20:
            return "图像内容: 包含图形或图表信息"
        
        # 添加更多上下文信息
        enhanced = f"图像内容: {original_text}"
        
        # 检测可能的图像类型
        text_lower = original_text.lower()
        if any(word in text_lower for word in ['chart', 'graph', '图表', '图形']):
            enhanced += " [类型: 图表/图形]"
        elif any(word in text_lower for word in ['diagram', 'flow', '流程', '示意']):
            enhanced += " [类型: 流程图/示意图]"
        elif any(word in text_lower for word in ['photo', 'picture', '照片', '图片']):
            enhanced += " [类型: 照片/图片]"
        
        return enhanced
    
    def _enhance_table_description(self, original_text: str) -> str:
        """增强表格描述"""
        if not original_text:
            return "表格内容: 数据表格"
        
        enhanced = f"表格内容: {original_text}"
        
        # 分析表格特征
        lines = original_text.split('\n')
        row_count = len([line for line in lines if line.strip()])
        
        if row_count > 0:
            enhanced += f" [行数: {row_count}]"
        
        # 检测数据类型
        text_lower = original_text.lower()
        if any(word in text_lower for word in ['数据', 'data', '统计', 'statistics']):
            enhanced += " [类型: 数据统计表]"
        elif any(word in text_lower for word in ['比较', 'comparison', '对比']):
            enhanced += " [类型: 比较表]"
        
        return enhanced
    
    def get_multimodal_statistics(self, metadata_list: List[Dict]) -> Dict[str, int]:
        """获取多模态内容统计"""
        stats = {'text': 0, 'image': 0, 'table': 0, 'other': 0}
        
        for meta in metadata_list:
            content_type = meta.get('type', 'other')
            if content_type in stats:
                stats[content_type] += 1
            else:
                stats['other'] += 1
        
        return stats