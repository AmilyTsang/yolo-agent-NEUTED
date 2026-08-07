

# Industrial Defect Analysis Assistant

An intelligent industrial defect detection system based on **YOLOv8 + Qwen2.5-VL**, supporting end-to-end defect detection, multimodal verification, intelligent decision-making, and report generation.

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-blue.svg)](https://flask.palletsprojects.com)

## ✨ Features

- 📷 **Image Upload**: Supports drag-and-drop and click-to-upload for industrial product images (PNG/JPG/JPEG/BMP/GIF)
- 🔍 **Image Preprocessing**: Automatically performs image reading, RGB conversion, and normalization
- 🧠 **YOLO Defect Detection**: Uses the YOLOv8 model to automatically identify defects in images, outputting bounding boxes and confidence scores
- 🎯 **Confidence Judgment**: Intelligently decides analysis strategies based on a confidence threshold (0.6)
- 📐 **ROI Cropping**: Expands bounding boxes by 20% for low-confidence detections to retain more contextual information
- 📚 **RAG Retrieval**: Retrieves enterprise defect standards and historical similar cases to enhance analysis accuracy
- 🤖 **Multimodal Verification**: Verifies low-confidence defects using the Qwen2.5-VL large language model, outputting structured analysis
- 🔄 **Detection Fusion**: Integrates YOLO detection results, Qwen analysis, and enterprise rules to generate a unified output
- ⚖️ **Decision Engine**: Automatically makes decisions based on defect risk levels (Auto Pass / Auto Reject (NG) / Manual Review)
- 📋 **Report Generation**: Automatically generates professional analysis reports in JSON and PDF formats
- 🔗 **Knowledge Sourcing**: All analysis content cites its sources, ensuring professionalism and traceability
- 🧪 **Model Training**: Supports YOLOv8 training and Qwen2-VL LoRA fine-tuning
- 📊 **Active Learning**: Supports active learning data collection and annotation management

## 🔄 Detection Workflow

```
Industrial Image 
                         │ 
                         ▼ 
                   Image Preprocessing 
                         │ 
                         ▼ 
                 YOLO Defect Detection 
                         │ 
             Bounding Box + Score 
                         │ 
         ┌───────────────┴────────────────┐ 
         │                                │ 
      High Confidence (>0.6)          Low Confidence (≤0.6) 
         │                                │ 
         │                         ROI Cropping (20% Padding) 
         │                                │ 
         │                                ▼ 
         │                       RAG Knowledge Retrieval 
         │                                │ 
         │                                ▼ 
         │                   Prompt Builder 
         │                                │ 
         │                                ▼ 
         │                      Qwen2.5-VL Verification 
         │                                │ 
         └───────────────┬────────────────┘ 
                         │ 
                         ▼ 
                  Detection Fusion 
                         │ 
           (YOLO + Qwen + Enterprise Rules) 
                         │ 
                         ▼ 
                  Decision Engine 
                         │ 
          ┌──────────────┴──────────────┐ 
          ▼                             ▼ 
      Auto Pass / Auto Reject          Manual Review 
          │                             │ 
          └──────────────┬──────────────┘ 
                         ▼ 
                   Report Generator 
                         │ 
                         ▼ 
                   JSON + PDF Report 
```

## 🛠️ Tech Stack

| Layer | Technology | Description |
|------|------|------|
| Frontend | HTML5, CSS3, JavaScript | Single-page application interface |
| Backend | Flask 2.3+ | RESTful API service |
| Detection Model | YOLOv8 (ultralytics) | Object detection |
| Vision-Language | Qwen2.5-VL-2B-Instruct | Multimodal analysis |
| LoRA Training | PEFT, Transformers | Large model fine-tuning |
| Image Processing | OpenCV, PIL | Image preprocessing |
| PDF Generation | ReportLab | Report generation |
| Vector Retrieval | sentence-transformers | RAG retrieval |
| Data Format | YOLO, VOC XML | Annotation data |

## 📁 Project Structure

```
yolo-agent-NEUTED/
│
├── app/                                    # Application Service Layer
│   ├── __init__.py
│   │
│   ├── api/                                # Flask API Interfaces
│   │   ├── __init__.py
│   │   ├── app.py                          # Flask application entry point
│   │   ├── routes.py                       # API route definitions
│   │   ├── schemas.py                      # Data model definitions
│   │   └── dependencies.py                 # Dependency injection
│   │
│   ├── pipeline/                           # Detection Pipeline
│   │   ├── __init__.py
│   │   ├── inference_pipeline.py           # Main pipeline controller
│   │   ├── context.py                      # Context management
│   │   └── exceptions.py                   # Exception definitions
│   │
│   ├── detector/                           # Detection Model Layer
│   │   ├── __init__.py
│   │   ├── base.py                         # Detector base class
│   │   ├── yolo_detector.py                # YOLO detector
│   │   ├── preprocess.py                   # Image preprocessing
│   │   └── postprocess.py                  # Detection post-processing
│   │
│   ├── verifier/                           # LLM Verification Module
│   │   ├── __init__.py
│   │   ├── base.py                         # Verifier base class
│   │   ├── qwen_verifier.py                # Qwen verifier
│   │   ├── prompt_builder.py               # Prompt builder
│   │   └── parser.py                       # Output parser
│   │
│   ├── rag/                                # RAG Knowledge Base
│   │   ├── __init__.py
│   │   ├── retriever.py                    # Retriever
│   │   ├── vector_store.py                 # Vector store
│   │   ├── embedding.py                    # Embedding model
│   │   ├── knowledge_loader.py             # Knowledge loader
│   │   └── schemas.py                      # RAG data model
│   │
│   ├── fusion/                             # Result Fusion
│   │   ├── __init__.py
│   │   ├── fusion_engine.py                # Fusion engine
│   │   └── score_calibrator.py             # Score calibrator
│   │
│   ├── decision/                           # Decision Engine
│   │   ├── __init__.py
│   │   ├── decision_engine.py              # Decision engine main class
│   │   ├── risk_assessment.py              # Risk assessment module
│   │   ├── rule_engine.py                  # Rule engine module
│   │   └── rules.py                        # Decision rule definitions
│   │
│   ├── report/                             # Report Generation
│   │   ├── __init__.py
│   │   ├── report_generator.py             # Report generator
│   │   ├── report_template.py              # Report template
│   │   └── serializers.py                  # Serialization utilities
│   │
│   ├── repositories/                       # Data Repository Layer
│   │   ├── __init__.py
│   │   ├── detection_repository.py         # Detection result repository
│   │   ├── review_repository.py            # Review record repository
│   │   └── case_repository.py              # Case repository
│   │
│   ├── services/                           # Business Service Layer
│   │   ├── __init__.py
│   │   ├── review_service.py               # Review service
│   │   └── active_learning_service.py      # Active learning service
│   │
│   ├── core/                               # Core Modules
│   │   ├── __init__.py
│   │   ├── config.py                       # Configuration loader
│   │   ├── constants.py                    # Constant definitions
│   │   ├── logging.py                      # Logging configuration
│   │   └── lifecycle.py                    # Lifecycle management
│   │
│   └── utils/                              # Utility Modules
│       ├── __init__.py
│       ├── image_utils.py                  # Image processing utilities
│       ├── json_utils.py                   # JSON utilities
│       ├── file_utils.py                   # File utilities
│       └── time_utils.py                   # Time utilities
│
├── configs/                                # Configuration Files
│   ├── yolo.yaml                           # YOLO model configuration
│   ├── qwen.yaml                           # Qwen model configuration
│   ├── rag.yaml                            # RAG retrieval configuration
│   ├── decision_rules.yaml                 # Decision rule configuration
│   └── system.yaml                         # System configuration
│
├── models/                                 # Model Files (Download separately)
│   ├── yolo/                               # YOLO Models
│   │   └── best.pt
│   │
│   └── qwen/                               # Qwen Models
│       ├── base/                           # Base model
│       └── adapters/                        # LoRA adapters
│
├── knowledge/                              # Enterprise Knowledge Base
│   ├── raw/                                # Raw knowledge
│   │   ├── enterprise_standard/            # Enterprise defect standards
│   │   ├── historical_cases/               # Historical cases
│   │   ├── repair_guidelines/              # Repair guidelines
│   │   └── defect_manual/                  # Defect manual
│   ├── processed/                          # Processed knowledge
│   └── indexes/                            # Vector indexes
│
├── datasets/                               # Datasets
│   ├── raw/                                # Raw data
│   │   └── neu_det/                        # NEU-DET dataset
│   ├── interim/                            # Interim data
│   ├── processed/                          # Processed data
│   │   ├── yolo/                           # YOLO format
│   │   └── qwen/                           # Qwen format
│   └── active_learning/                    # Active learning data
│       ├── pending/                         # Pending
│       ├── reviewed/                        # Reviewed
│       └── rejected/                        # Rejected
│
├── training/                               # Training Scripts
│   ├── yolo/                               # YOLO Training
│   │   ├── train.py
│   │   ├── evaluate.py
│   │   └── export.py
│   │
│   ├── qwen/                               # Qwen Training
│   │   ├── train_lora.py
│   │   ├── inference.py
│   │   ├── convert_dataset.py
│   │   └── evaluate.py
│   │
│   └── scripts/                            # Utility Scripts
│       ├── clean_dataset.py
│       ├── xml2yolo.py
│       └── yolo2qwen.py
│
├── web/                                    # Frontend Pages
│   ├── static/                             # Static assets
│   ├── templates/                          # Template files
│   └── index.html                          # Main page
│
├── runtime/                                # Runtime Directory (Auto-created)
│   ├── uploads/                            # Uploaded files
│   ├── reports/                            # Generated reports
│   ├── cache/                              # Cache data
│   └── logs/                               # Log files
│
├── scripts/                                # DevOps Scripts
│   ├── build_knowledge_base.py             # Build knowledge base
│   ├── init_project.py                     # Initialize project
│   ├── run_server.py                       # Start server
│   └── evaluate_pipeline.py                # Evaluate pipeline
│
├── tests/                                  # Test Directory
│   ├── unit/                               # Unit tests
│   ├── integration/                        # Integration tests
│   ├── fixtures/                           # Test fixtures
│   └── test_data/                          # Test data
│
├── docs/                                   # Documentation
│   ├── architecture.md                     # Architecture documentation
│   ├── deployment.md                       # Deployment documentation
│   ├── api.md                              # API documentation
│   ├── experiment.md                       # Experiment documentation
│   └── decision_rules.md                   # Decision rules documentation
│
├── .env.example                            # Environment variables example
├── .gitignore                              # Git ignore configuration
├── Dockerfile                              # Docker configuration
├── docker-compose.yml                      # Docker Compose configuration
├── pyproject.toml                          # Python project configuration
├── requirements.txt                        # Python dependencies
└── README.md                               # Project README
```

## 📦 Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd yolo-agent-NEUTED
```

### 2. Create a Virtual Environment

```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize the Project

```bash
python scripts/init_project.py
```

### 5. Download Models

1. **YOLOv8 Model**: Download the trained weights to `models/yolo/best.pt`
2. **Qwen2-VL Model**: Download the base model to `models/qwen/base/`

### 6. Build Knowledge Base (Optional)

```bash
python scripts/build_knowledge_base.py
```

## 🚀 Usage Instructions

### Start the Service

```bash
# Method 1: Using script
python scripts/run_server.py

# Method 2: Direct execution
python -m app.api.app

# Method 3: Using Docker
docker-compose up -d
```

The service will start at `http://localhost:5000`.

### Frontend Interface Operations

1. **Upload Image**: Click or drag and drop an image into the upload area
2. **Start Analysis**: Click the "Start Analysis" button to perform defect detection
3. **View Results**: Check the detected defects and decision results in the results area
4. **View Analysis**: Review professional analysis content (including evidence and handling recommendations) in the detailed analysis area
5. **Confirm/Decide**: Manually confirm or let the system auto-decide based on the risk level
6. **Generate Report**: Click the "Generate Report" button to download reports in JSON and PDF formats

### API Call Examples

#### Upload Image

```bash
curl -X POST -F "image=@test.jpg" http://localhost:5000/api/upload
```

#### Defect Detection

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"file_id": "your-file-id"}' \
  http://localhost:5000/api/detect
```

#### Manual Confirmation

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"file_id": "your-file-id", "user_id": "admin", "confirm_decision": "pass"}' \
  http://localhost:5000/api/confirm
```

#### Auto Decision

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"file_id": "your-file-id"}' \
  http://localhost:5000/api/auto_decision
```

#### Generate Report

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"file_id": "your-file-id"}' \
  http://localhost:5000/api/generate_report
```

#### Get Knowledge

```bash
curl "http://localhost:5000/api/get_knowledge?defect_type=crazing"
```

## 📡 API Reference

| Endpoint | Method | Description |
|------|------|------|
| `/api/upload` | POST | Upload image |
| `/api/detect` | POST | Defect detection |
| `/api/confirm` | POST | Manual confirmation |
| `/api/auto_decision` | POST | Auto decision |
| `/api/generate_report` | POST | Generate report (JSON + PDF) |
| `/api/get_knowledge` | GET | Get knowledge base |
| `/api/reports/<filename>` | GET | Download report |

### Response Example

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
            "evidence": ["YOLO Detection: crazing, Confidence: 0.9500"],
            "severity": "medium",
            "recommendation": "Medium-risk defect (crazing) detected, recommend optimizing relevant process parameters",
            "causes": "",
            "measures": "",
            "suggestions": "",
            "confidence_judgment": "high"
        }
    ],
    "decision": "auto_pass",
    "decision_reason": "Only low-risk defects or no defects detected, auto-passed",
    "needs_review": false
}
```

## ⚖️ Decision Rules

| Condition | Decision Result |
|------|----------|
| High-risk defect | Manual Review |
| 3 or more medium-risk defects | Manual Review |
| 1-2 medium-risk defects | Auto Reject (NG) |
| Only low-risk defects or no defects | Auto Pass |

## 📊 Defect Types

| Type | Name | Severity |
|------|------|----------|
| crazing | Hairline Crack | Medium |
| inclusion | Inclusion | High |
| patches | Patches | Medium |
| pitted_surface | Pitted Surface | Low |
| rolled-in_scale | Rolled-in Scale | Medium |
| scratches | Scratches | Low |

## ⚙️ Configuration Notes

Configuration files are located in the `configs/` directory:

- **yolo.yaml**: YOLO model path, confidence threshold, class list
- **qwen.yaml**: Qwen model path, inference parameters, Prompt configuration
- **rag.yaml**: Knowledge base path, vector store configuration, embedding model
- **decision_rules.yaml**: Decision rule configuration
- **system.yaml**: Service port, directory configuration, report format

### Environment Variables

| Variable | Description | Default Value |
|------|------|--------|
| APP_HOST | Service Address | 0.0.0.0 |
| APP_PORT | Service Port | 5000 |
| APP_DEBUG | Debug Mode | false |

## 🧪 Training Instructions

### YOLOv8 Training

```bash
python training/yolo/train.py --config configs/yolo.yaml
```

### Qwen2-VL LoRA Fine-tuning

```bash
python training/qwen/train_lora.py --config configs/qwen.yaml
```

## 📝 Notes

1. **Model Files**: Download YOLO and Qwen model weights and place them in the `models/` directory
2. **GPU Environment**: GPU-accelerated inference is recommended; CUDA installation is required
3. **Knowledge Updates**: Enterprise standards and historical cases can be updated in the `knowledge/raw/` directory
4. **Confidence Threshold**: Can be adjusted in `configs/yolo.yaml`, default is 0.6
5. **PDF Generation**: Requires the `reportlab` library (already included in `requirements.txt`)
6. **Chinese Display**: PDF reports use the SimHei font; ensure this font is available in your system
7. **Docker Deployment**: Use `docker-compose up -d` to start the containerized service

## 🤝 Contribution Guidelines

Welcome to submit Issues and Pull Requests!

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Coding Standards

- Follow PEP 8 coding style
- Use type hints
- Add appropriate comments
- Write test cases

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## 📞 Contact

For questions or suggestions, please submit an Issue or contact the development team.

## 📚 Documentation

- [Architecture Documentation](docs/architecture.md)
- [Deployment Documentation](docs/deployment.md)
- [API Documentation](docs/api.md)
- [Experiment Documentation](docs/experiment.md)
- [Decision Rules Documentation](docs/decision_rules.md)
