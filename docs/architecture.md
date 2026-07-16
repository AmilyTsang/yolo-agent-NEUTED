# 架构文档

## 1. 系统概述

本项目是一个基于 **YOLOv8 + Qwen2.5-VL** 的智能工业缺陷检测系统，采用微服务架构设计，支持端到端的缺陷检测、多模态验证、智能决策和报告生成。

## 2. 架构设计

### 2.1 分层架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        展示层 (Presentation)                     │
│                    web/index.html + JavaScript                   │
├─────────────────────────────────────────────────────────────────┤
│                        接口层 (API)                              │
│                    app/api/app.py + routes.py                    │
├─────────────────────────────────────────────────────────────────┤
│                        业务层 (Business)                         │
│                     app/pipeline/pipeline.py                     │
├─────────────────────────────────────────────────────────────────┤
│                        服务层 (Service)                          │
│  detector | verifier | rag | decision | report | utils          │
├─────────────────────────────────────────────────────────────────┤
│                        数据层 (Data)                             │
│              knowledge/ | datasets/ | models/                    │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 模块划分

| 模块 | 职责 | 核心文件 |
|------|------|----------|
| API | 对外RESTful接口 | app/api/app.py, routes.py, schemas.py |
| Pipeline | 检测流程编排 | app/pipeline/pipeline.py |
| Detector | YOLO目标检测 | app/detector/yolo_detector.py |
| Verifier | 多模态验证 | app/verifier/qwen_verifier.py |
| RAG | 知识库检索 | app/rag/retriever.py |
| Decision | 智能决策 | app/decision/decision_engine.py |
| Report | 报告生成 | app/report/report_generator.py |
| Utils | 工具函数 | app/utils/image_utils.py |

## 3. 核心流程

### 3.1 检测流程

```
工业图片 → 图像预处理 → YOLO检测 → 置信度判断
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
              高置信度                          低置信度
                    │                               │
                    │                   ROI裁剪 → RAG检索 → 
                    │                   Prompt构建 → Qwen验证
                    └───────────────┬───────────────┘
                                    │
                            Detection Fusion
                                    │
                            Decision Engine
                                    │
                            Report Generator
```

### 3.2 数据流向

```
┌──────────┐    HTTP    ┌─────────┐    调用    ┌──────────┐
│  前端    │ ─────────→ │  API层  │ ─────────→ │ Pipeline │
└──────────┘            └─────────┘            └────┬─────┘
                                                    │
              ┌───────────────┬───────────────┐      │
              ▼               ▼               ▼      │
        ┌─────────┐    ┌──────────┐    ┌──────────┐ │
        │ Detector│    │ Verifier │    │   RAG    │ │
        └────┬────┘    └────┬─────┘    └────┬─────┘ │
             │              │               │       │
             └──────────────┼───────────────┘       │
                            ▼                       │
                     ┌──────────┐                   │
                     │  Fusion  │ ←─────────────────┘
                     └────┬─────┘
                          │
                          ▼
                   ┌──────────┐
                   │ Decision │
                   └────┬─────┘
                        │
                        ▼
                   ┌──────────┐
                   │  Report  │
                   └──────────┘
```

## 4. 关键技术

### 4.1 YOLOv8 检测

- 使用 ultralytics 库进行目标检测
- 支持多尺度输入和自动设备选择
- 输出检测框、类别和置信度

### 4.2 Qwen2.5-VL 验证

- 使用 Hugging Face Transformers 加载模型
- 支持 LoRA 微调权重加载
- 多模态输入（图像 + 文本）

### 4.3 RAG 知识检索

- 使用 sentence-transformers 进行文本嵌入
- 基于余弦相似度的向量检索
- 支持企业标准和历史案例检索

## 5. 配置管理

配置文件位于 `configs/` 目录：

- **yolo.yaml**: YOLO模型配置
- **qwen.yaml**: Qwen模型配置
- **rag.yaml**: RAG检索配置
- **system.yaml**: 系统全局配置

## 6. 部署建议

### 6.1 开发环境

```bash
python -m app.api.app
```

### 6.2 生产环境

建议使用 Gunicorn + Nginx 部署：

```bash
gunicorn --workers=4 --bind=0.0.0.0:5000 app.api.app:create_app()
```

### 6.3 Docker 部署

```dockerfile
FROM python:3.10
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["gunicorn", "--workers=4", "--bind=0.0.0.0:5000", "app.api.app:create_app()"]
```