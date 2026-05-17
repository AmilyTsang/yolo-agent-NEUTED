# YOLO-Agent 工业缺陷分析助手

基于 YOLO 的工业缺陷检测与分析系统，能够识别图像中的缺陷并提供专业的分析报告。

## 功能特点

- 📷 **图像上传**：支持拖拽和点击上传工业产品图片
- 🔍 **缺陷检测**：使用 YOLO 模型自动识别图像中的缺陷
- 📊 **智能分析**：提供缺陷原因分析、解决方案和预防措施
- 📄 **报告生成**：自动生成包含检测结果的专业分析报告
- 🔗 **知识来源**：所有分析内容均标注来源，确保专业性

## 支持的缺陷类型

| 缺陷类型 | 描述 |
|---------|------|
| 划痕 | 物体表面被尖锐物体划过留下的痕迹 |
| 裂纹 | 材料内部或表面出现的裂缝 |
| 凹陷 | 物体表面向内凹陷的缺陷 |
| 凸起 | 物体表面向外突出的缺陷 |
| 腐蚀 | 材料与周围环境发生化学反应导致的损坏 |
| 磨损 | 物体表面因摩擦导致的材料损失 |
| 变形 | 物体形状发生非预期的改变 |
| 污渍 | 物体表面附着的污染物 |
| 气泡 | 材料内部或表面形成的气体空隙 |
| 断裂 | 材料发生完全分离的严重缺陷 |

## 技术栈

- **前端**: HTML5, CSS3, JavaScript
- **后端**: Python Flask
- **检测模型**: YOLOv8
- **图像处理**: OpenCV

## 项目结构

```
yolo-agent/
├── backend/
│   ├── app.py              # Flask 应用入口
│   ├── yolo_detector.py    # YOLO 检测器模块
│   ├── knowledge_base.py   # 缺陷知识库
│   └── report_generator.py # 报告生成器
├── frontend/
│   └── index.html          # 前端页面
├── models/                 # YOLO 模型文件
├── uploads/                # 上传的图片
├── static/                 # 检测结果图片
├── reports/                # 生成的报告
└── requirements.txt        # 依赖列表
```

## 快速开始

### 1. 安装依赖

```bash
cd yolo-agent
pip install -r requirements.txt
```

### 2. 下载 YOLO 模型（可选）

将 YOLOv8 模型文件（如 yolov8n.pt）放入 `models/` 目录。

如果没有模型文件，系统会使用模拟检测模式。

### 3. 运行应用

```bash
cd backend
python app.py
```

### 4. 访问应用

打开浏览器访问 `http://localhost:5000`

## 使用说明

1. **上传图片**：点击或拖拽图片到上传区域
2. **开始分析**：点击"开始分析"按钮进行缺陷检测
3. **查看结果**：在检测结果区域查看检测到的缺陷
4. **查看分析**：在缺陷详细分析区域查看专业分析内容
5. **生成报告**：点击"生成报告"按钮下载分析报告

## API 接口

### 上传图片并检测

**POST** `/api/upload`

```bash
curl -X POST -F "file=@image.jpg" http://localhost:5000/api/upload
```

响应示例：
```json
{
    "success": true,
    "file_id": "uuid",
    "original_filename": "image.jpg",
    "defects": [...],
    "analysis": [...],
    "result_image": "/static/uuid_result.jpg"
}
```

### 生成报告

**POST** `/api/generate_report`

```bash
curl -X POST -H "Content-Type: application/json" \
    -d '{"file_id": "uuid", "defects": [...], "analysis": [...]}' \
    http://localhost:5000/api/generate_report
```

### 获取缺陷信息

**GET** `/api/defect_info/<defect_type>`

```bash
curl http://localhost:5000/api/defect_info/划痕
```

### 搜索知识库

**POST** `/api/search_knowledge`

```bash
curl -X POST -H "Content-Type: application/json" \
    -d '{"query": "腐蚀"}' \
    http://localhost:5000/api/search_knowledge
```

## 注意事项

- 确保 Python 版本 >= 3.8
- 如果使用真实 YOLO 模型，需要安装 PyTorch
- 首次运行可能需要下载模型权重
- 建议使用 GPU 加速以提高检测速度

## License

MIT License