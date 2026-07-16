# 部署文档

## 1. 环境要求

### 1.1 硬件要求

| 配置 | 最低要求 | 推荐配置 |
|------|----------|----------|
| CPU | 4核8线程 | 8核16线程 |
| 内存 | 16GB | 32GB |
| GPU | 无 | NVIDIA RTX 3090+ |
| 显存 | 无 | 24GB+ |

### 1.2 软件要求

- Python 3.10+
- CUDA 11.8+（GPU加速）
- Git

## 2. 安装步骤

### 2.1 克隆项目

```bash
git clone <repository-url>
cd industrial-defect-agent
```

### 2.2 创建虚拟环境

```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 2.3 安装依赖

```bash
pip install -r requirements.txt
```

### 2.4 下载模型

1. YOLOv8模型：下载权重文件到 `models/yolo/best.pt`
2. Qwen2-VL模型：下载基础模型到 `models/qwen/base/`

## 3. 配置说明

### 3.1 修改配置文件

编辑 `configs/system.yaml`：

```yaml
app:
  host: "0.0.0.0"
  port: 5000
  debug: false
```

### 3.2 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| APP_HOST | 服务地址 | 0.0.0.0 |
| APP_PORT | 服务端口 | 5000 |
| APP_DEBUG | 调试模式 | false |
| UPLOADS_DIR | 上传目录 | uploads |
| REPORTS_DIR | 报告目录 | reports |

## 4. 启动服务

### 4.1 开发模式

```bash
python -m app.api.app
```

### 4.2 生产模式

```bash
gunicorn --workers=4 --bind=0.0.0.0:5000 app.api.app:create_app()
```

### 4.3 后台运行

```bash
nohup python -m app.api.app > app.log 2>&1 &
```

## 5. 验证服务

```bash
curl http://localhost:5000/api/upload
```

预期响应：

```json
{"success": false, "error": "未上传图片"}
```

## 6. 监控日志

日志文件位于 `logs/` 目录：

```bash
tail -f logs/defect_agent_*.log
```

## 7. 常见问题

### 7.1 模型加载失败

确保模型文件路径正确：

```bash
ls models/yolo/best.pt
ls models/qwen/base/pytorch_model.bin
```

### 7.2 CUDA 错误

检查 CUDA 是否正确安装：

```bash
nvidia-smi
python -c "import torch; print(torch.cuda.is_available())"
```

### 7.3 端口占用

修改端口号：

```bash
export APP_PORT=5001
python -m app.api.app
```