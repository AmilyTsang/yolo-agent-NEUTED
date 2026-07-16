# 工业缺陷分析助手

基于 **YOLOv8 + Qwen2.5-VL** 的智能工业缺陷检测系统，支持端到端的缺陷检测、多模态验证、智能决策和报告生成。

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-blue.svg)](https://flask.palletsprojects.com)

## ✨ 功能特点

- 📷 **图像上传**：支持拖拽和点击上传工业产品图片（PNG/JPG/JPEG/BMP/GIF）
- 🔍 **图像预处理**：自动进行图像读取、RGB转换和归一化处理
- 🧠 **YOLO缺陷检测**：使用 YOLOv8 模型自动识别图像中的缺陷，输出边界框和置信度
- 🎯 **置信度判断**：根据置信度阈值(0.6)智能决策分析策略
- 📐 **ROI裁剪**：低置信度时对检测框进行20%扩边裁剪，保留更多上下文信息
- 📚 **RAG检索**：检索企业缺陷标准和历史相似案例，增强分析准确性
- 🤖 **多模态验证**：基于 Qwen2.5-VL 大语言模型验证低置信度缺陷，输出结构化分析
- 🔄 **Detection Fusion**：融合YOLO检测结果、Qwen分析和企业规则，生成统一输出
- ⚖️ **Decision Engine**：根据缺陷风险等级自动决策（自动通过/自动判NG/人工审核）
- 📋 **报告生成**：自动生成 JSON + PDF 格式的专业分析报告
- 🔗 **知识来源**：所有分析内容均标注来源，确保专业性和可追溯性
- 🧪 **模型训练**：支持 YOLOv8 训练和 Qwen2-VL LoRA 微调训练
- 📊 **主动学习**：支持主动学习数据收集和标注管理

## 🔄 检测流程

```
工业图片 
                         │ 
                         ▼ 
                   图像预处理 
                         │ 
                         ▼ 
                 YOLO缺陷检测 
                         │ 
             Bounding Box + Score 
                         │ 
         ┌───────────────┴────────────────┐ 
         │                                │ 
      高置信度(>0.6)                  低置信度(≤0.6) 
         │                                │ 
         │                         ROI裁剪(扩边20%) 
         │                                │ 
         │                                ▼ 
         │                       RAG知识检索 
         │                                │ 
         │                                ▼ 
         │                   Prompt Builder 
         │                                │ 
         │                                ▼ 
         │                      Qwen2.5-VL验证 
         │                                │ 
         └───────────────┬────────────────┘ 
                         │ 
                         ▼ 
                  Detection Fusion 
                         │ 
           (YOLO + Qwen + 企业规则) 
                         │ 
                         ▼ 
                  Decision Engine 
                         │ 
          ┌──────────────┴──────────────┐ 
          ▼                             ▼ 
      自动通过/自动判NG              人工审核 
          │                             │ 
          └──────────────┬──────────────┘ 
                         ▼ 
                   Report Generator 
                         │ 
                         ▼ 
                   JSON + PDF报告 
```

## 🛠️ 技术栈

| 层次 | 技术 | 说明 |
|------|------|------|
| 前端 | HTML5, CSS3, JavaScript | 单页应用界面 |
| 后端 | Flask 2.3+ | RESTful API服务 |
| 检测模型 | YOLOv8 (ultralytics) | 目标检测 |
| 视觉语言 | Qwen2.5-VL-2B-Instruct | 多模态分析 |
| LoRA训练 | PEFT, Transformers | 大模型微调 |
| 图像处理 | OpenCV, PIL | 图像预处理 |
| PDF生成 | ReportLab | 报告生成 |
| 向量检索 | sentence-transformers | RAG检索 |
| 数据格式 | YOLO, VOC XML | 标注数据 |

## 📁 项目结构

```
yolo-agent-NEUTED/
│
├── app/                                    # 应用服务层
│   ├── __init__.py
│   │
│   ├── api/                                # Flask API接口
│   │   ├── __init__.py
│   │   ├── app.py                          # Flask应用入口
│   │   ├── routes.py                       # API路由定义
│   │   ├── schemas.py                      # 数据模型定义
│   │   └── dependencies.py                 # 依赖注入
│   │
│   ├── pipeline/                           # 检测流程管道
│   │   ├── __init__.py
│   │   ├── inference_pipeline.py           # 主流程控制器
│   │   ├── context.py                      # 上下文管理
│   │   └── exceptions.py                   # 异常定义
│   │
│   ├── detector/                           # 检测模型层
│   │   ├── __init__.py
│   │   ├── base.py                         # 检测器基类
│   │   ├── yolo_detector.py                # YOLO检测器
│   │   ├── preprocess.py                   # 图像预处理
│   │   └── postprocess.py                  # 检测后处理
│   │
│   ├── verifier/                           # 大模型验证模块
│   │   ├── __init__.py
│   │   ├── base.py                         # 验证器基类
│   │   ├── qwen_verifier.py                # Qwen验证器
│   │   ├── prompt_builder.py               # Prompt构建器
│   │   └── parser.py                       # 输出解析器
│   │
│   ├── rag/                                # RAG知识库
│   │   ├── __init__.py
│   │   ├── retriever.py                    # 检索器
│   │   ├── vector_store.py                 # 向量存储
│   │   ├── embedding.py                    # 嵌入模型
│   │   ├── knowledge_loader.py             # 知识加载器
│   │   └── schemas.py                      # RAG数据模型
│   │
│   ├── fusion/                             # 结果融合
│   │   ├── __init__.py
│   │   ├── fusion_engine.py                # 融合引擎
│   │   └── score_calibrator.py             # 分数校准器
│   │
│   ├── decision/                           # 决策引擎
│   │   ├── __init__.py
│   │   ├── decision_engine.py              # 决策引擎主类
│   │   ├── risk_assessment.py              # 风险评估模块
│   │   ├── rule_engine.py                  # 规则引擎模块
│   │   └── rules.py                        # 决策规则定义
│   │
│   ├── report/                             # 报告生成
│   │   ├── __init__.py
│   │   ├── report_generator.py             # 报告生成器
│   │   ├── report_template.py              # 报告模板
│   │   └── serializers.py                  # 序列化工具
│   │
│   ├── repositories/                       # 数据仓储层
│   │   ├── __init__.py
│   │   ├── detection_repository.py         # 检测结果仓储
│   │   ├── review_repository.py            # 审核记录仓储
│   │   └── case_repository.py              # 案例仓储
│   │
│   ├── services/                           # 业务服务层
│   │   ├── __init__.py
│   │   ├── review_service.py               # 审核服务
│   │   └── active_learning_service.py      # 主动学习服务
│   │
│   ├── core/                               # 核心模块
│   │   ├── __init__.py
│   │   ├── config.py                       # 配置加载器
│   │   ├── constants.py                    # 常量定义
│   │   ├── logging.py                      # 日志配置
│   │   └── lifecycle.py                    # 生命周期管理
│   │
│   └── utils/                              # 工具模块
│       ├── __init__.py
│       ├── image_utils.py                  # 图像处理工具
│       ├── json_utils.py                   # JSON工具
│       ├── file_utils.py                   # 文件工具
│       └── time_utils.py                   # 时间工具
│
├── configs/                                # 配置文件
│   ├── yolo.yaml                           # YOLO模型配置
│   ├── qwen.yaml                           # Qwen模型配置
│   ├── rag.yaml                            # RAG检索配置
│   ├── decision_rules.yaml                 # 决策规则配置
│   └── system.yaml                         # 系统配置
│
├── models/                                 # 模型文件（需自行下载）
│   ├── yolo/                               # YOLO模型
│   │   └── best.pt
│   │
│   └── qwen/                               # Qwen模型
│       ├── base/                           # 基础模型
│       └── adapters/                        # LoRA适配器
│
├── knowledge/                              # 企业知识库
│   ├── raw/                                # 原始知识
│   │   ├── enterprise_standard/            # 企业缺陷标准
│   │   ├── historical_cases/               # 历史案例
│   │   ├── repair_guidelines/              # 修复指南
│   │   └── defect_manual/                  # 缺陷手册
│   ├── processed/                          # 处理后知识
│   └── indexes/                            # 向量索引
│
├── datasets/                               # 数据集
│   ├── raw/                                # 原始数据
│   │   └── neu_det/                        # NEU-DET数据集
│   ├── interim/                            # 中间数据
│   ├── processed/                          # 处理后数据
│   │   ├── yolo/                           # YOLO格式
│   │   └── qwen/                           # Qwen格式
│   └── active_learning/                    # 主动学习数据
│       ├── pending/                         # 待审核
│       ├── reviewed/                        # 已审核
│       └── rejected/                        # 已拒绝
│
├── training/                               # 训练脚本
│   ├── yolo/                               # YOLO训练
│   │   ├── train.py
│   │   ├── evaluate.py
│   │   └── export.py
│   │
│   ├── qwen/                               # Qwen训练
│   │   ├── train_lora.py
│   │   ├── inference.py
│   │   ├── convert_dataset.py
│   │   └── evaluate.py
│   │
│   └── scripts/                            # 工具脚本
│       ├── clean_dataset.py
│       ├── xml2yolo.py
│       └── yolo2qwen.py
│
├── web/                                    # 前端页面
│   ├── static/                             # 静态资源
│   ├── templates/                          # 模板文件
│   └── index.html                          # 主页面
│
├── runtime/                                # 运行时目录（自动创建）
│   ├── uploads/                            # 上传文件
│   ├── reports/                            # 生成的报告
│   ├── cache/                              # 缓存数据
│   └── logs/                               # 日志文件
│
├── scripts/                                # 运维脚本
│   ├── build_knowledge_base.py             # 构建知识库
│   ├── init_project.py                     # 初始化项目
│   ├── run_server.py                       # 启动服务
│   └── evaluate_pipeline.py                # 评估流程
│
├── tests/                                  # 测试目录
│   ├── unit/                               # 单元测试
│   ├── integration/                        # 集成测试
│   ├── fixtures/                           # 测试夹具
│   └── test_data/                          # 测试数据
│
├── docs/                                   # 文档
│   ├── architecture.md                     # 架构文档
│   ├── deployment.md                       # 部署文档
│   ├── api.md                              # API文档
│   ├── experiment.md                       # 实验文档
│   └── decision_rules.md                   # 决策规则文档
│
├── .env.example                            # 环境变量示例
├── .gitignore                              # Git忽略配置
├── Dockerfile                              # Docker配置
├── docker-compose.yml                      # Docker Compose配置
├── pyproject.toml                          # Python项目配置
├── requirements.txt                        # Python依赖
└── README.md                               # 项目说明
```

## 📦 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd yolo-agent-NEUTED
```

### 2. 创建虚拟环境

```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 初始化项目

```bash
python scripts/init_project.py
```

### 5. 下载模型

1. **YOLOv8模型**：下载训练好的权重文件到 `models/yolo/best.pt`
2. **Qwen2-VL模型**：下载基础模型到 `models/qwen/base/`

### 6. 构建知识库（可选）

```bash
python scripts/build_knowledge_base.py
```

## 🚀 使用说明

### 启动服务

```bash
# 方式1：使用脚本
python scripts/run_server.py

# 方式2：直接运行
python -m app.api.app

# 方式3：使用Docker
docker-compose up -d
```

服务将在 `http://localhost:5000` 启动。

### 前端界面操作

1. **上传图片**：点击或拖拽图片到上传区域
2. **开始分析**：点击"开始分析"按钮进行缺陷检测
3. **查看结果**：在检测结果区域查看检测到的缺陷和决策结果
4. **查看分析**：在缺陷详细分析区域查看专业分析内容（含分析依据和处理建议）
5. **确认/决策**：根据风险等级进行人工确认或自动决策
6. **生成报告**：点击"生成报告"按钮下载 JSON + PDF 格式报告

### API调用示例

#### 上传图片

```bash
curl -X POST -F "image=@test.jpg" http://localhost:5000/api/upload
```

#### 缺陷检测

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"file_id": "your-file-id"}' \
  http://localhost:5000/api/detect
```

#### 人工确认

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"file_id": "your-file-id", "user_id": "admin", "confirm_decision": "pass"}' \
  http://localhost:5000/api/confirm
```

#### 自动决策

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"file_id": "your-file-id"}' \
  http://localhost:5000/api/auto_decision
```

#### 生成报告

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"file_id": "your-file-id"}' \
  http://localhost:5000/api/generate_report
```

#### 获取知识

```bash
curl "http://localhost:5000/api/get_knowledge?defect_type=crazing"
```

## 📡 API接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/upload` | POST | 上传图片 |
| `/api/detect` | POST | 缺陷检测 |
| `/api/confirm` | POST | 人工确认 |
| `/api/auto_decision` | POST | 自动决策 |
| `/api/generate_report` | POST | 生成报告（JSON + PDF） |
| `/api/get_knowledge` | GET | 获取知识库 |
| `/api/reports/<filename>` | GET | 下载报告 |

### 响应示例

```json
{
    "success": true,
    "defects": [
        {
            "defect_type": "crazing",
            "confidence": 0.95,
            "bbox": [100, 50, 200, 150]
        }
    ],
    "fused_results": [
        {
            "defect_type": "crazing",
            "confidence_level": 0.95,
            "bbox": [100, 50, 200, 150],
            "evidence": ["YOLO检测: crazing, 置信度: 0.9500"],
            "severity": "medium",
            "recommendation": "检测到中等风险缺陷(crazing)，建议优化相关工艺参数",
            "causes": "",
            "measures": "",
            "suggestions": "",
            "confidence_judgment": "high"
        }
    ],
    "decision": "auto_pass",
    "decision_reason": "仅检测到低风险缺陷或无缺陷，自动通过",
    "needs_review": false
}
```

## ⚖️ 决策规则

| 条件 | 决策结果 |
|------|----------|
| 高风险缺陷 | 人工审核 |
| 3个及以上中等风险缺陷 | 人工审核 |
| 1-2个中等风险缺陷 | 自动判NG |
| 仅低风险缺陷或无缺陷 | 自动通过 |

## 📊 缺陷类型

| 类型 | 名称 | 严重程度 |
|------|------|----------|
| crazing | 发丝纹 | 中 |
| inclusion | 夹杂 | 高 |
| patches | 斑块 | 中 |
| pitted_surface | 麻点 | 低 |
| rolled-in_scale | 氧化铁皮压入 | 中 |
| scratches | 划痕 | 低 |

## ⚙️ 配置说明

配置文件位于 `configs/` 目录：

- **yolo.yaml**: YOLO模型路径、置信度阈值、类别列表
- **qwen.yaml**: Qwen模型路径、推理参数、Prompt配置
- **rag.yaml**: 知识库路径、向量存储配置、嵌入模型
- **decision_rules.yaml**: 决策规则配置
- **system.yaml**: 服务端口、目录配置、报告格式

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| APP_HOST | 服务地址 | 0.0.0.0 |
| APP_PORT | 服务端口 | 5000 |
| APP_DEBUG | 调试模式 | false |

## 🧪 训练说明

### YOLOv8训练

```bash
python training/yolo/train.py --config configs/yolo.yaml
```

### Qwen2-VL LoRA微调

```bash
python training/qwen/train_lora.py --config configs/qwen.yaml
```

## 📝 注意事项

1. **模型文件**：需要下载YOLO和Qwen模型权重文件并放置在 `models/` 目录
2. **GPU环境**：推荐使用GPU加速推理，需要安装CUDA
3. **知识更新**：企业标准和历史案例可在 `knowledge/raw/` 目录更新
4. **置信度阈值**：可在 `configs/yolo.yaml` 中调整，默认值为0.6
5. **PDF生成**：需要安装 reportlab 库（已包含在 requirements.txt 中）
6. **中文显示**：PDF报告使用SimHei字体，需确保系统中存在该字体
7. **Docker部署**：使用 `docker-compose up -d` 启动容器化服务

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发流程

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

### 代码规范

- 遵循 PEP 8 代码风格
- 使用类型提示
- 添加适当的注释
- 编写测试用例

## 📄 License

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

如有问题或建议，请提交Issue或联系开发团队。

## 📚 文档

- [架构文档](docs/architecture.md)
- [部署文档](docs/deployment.md)
- [API文档](docs/api.md)
- [实验文档](docs/experiment.md)
- [决策规则文档](docs/decision_rules.md)