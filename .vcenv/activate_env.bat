@echo off
echo 🚀 激活增强RAG系统环境...
call conda activate enhanced_rag_system
if %errorlevel% neq 0 (
    echo ❌ 环境激活失败
    echo 请先运行: python create_conda_environment.py
    pause
    exit /b 1
)

echo ✅ 环境已激活: enhanced_rag_system
echo 📋 可用命令:
echo   python Enhanced_Interactive_Multimodal_RAG.py  - 启动主程序
echo   python demo_enhanced_features.py              - 运行演示
echo   python quick_test_enhanced_features.py        - 快速测试
echo   python demo_document_management.py            - 文档管理演示
echo.
echo 💡 提示: 首次运行可能需要下载模型文件
echo 🔑 确保.env文件中配置了正确的API密钥
echo.
cmd /k