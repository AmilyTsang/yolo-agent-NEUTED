# API文档

## 1. 接口总览

| 接口 | 方法 | 路径 | 描述 |
|------|------|------|------|
| 图片上传 | POST | /api/upload | 上传待检测图片 |
| 缺陷检测 | POST | /api/detect | 执行缺陷检测流程 |
| 人工确认 | POST | /api/confirm | 人工确认检测结果 |
| 自动决策 | POST | /api/auto_decision | 自动决策检测结果 |
| 生成报告 | POST | /api/generate_report | 生成检测报告 |
| 获取知识 | GET | /api/get_knowledge | 获取缺陷知识 |
| 下载报告 | GET | /api/reports/{filename} | 下载报告文件 |

## 2. 接口详情

### 2.1 图片上传

**请求**

```
POST /api/upload
Content-Type: multipart/form-data
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| image | File | 是 | 待检测图片 |

**响应**

```json
{
    "success": true,
    "file_id": "uuid-string",
    "image_path": "uploads/uuid_filename.jpg",
    "message": "图片上传成功"
}
```

### 2.2 缺陷检测

**请求**

```
POST /api/detect
Content-Type: application/json
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file_id | String | 是 | 上传时返回的文件ID |

**响应**

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

### 2.3 人工确认

**请求**

```
POST /api/confirm
Content-Type: application/json
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file_id | String | 是 | 文件ID |
| user_id | String | 是 | 用户ID |
| confirm_decision | String | 是 | 通过: pass, 不通过: reject |

**响应**

```json
{
    "success": true,
    "message": "人工确认成功，判定结果：通过",
    "decision": "auto_pass"
}
```

### 2.4 自动决策

**请求**

```
POST /api/auto_decision
Content-Type: application/json
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file_id | String | 是 | 文件ID |

**响应**

```json
{
    "success": true,
    "decision": "auto_pass",
    "reason": "未检测到缺陷，自动通过"
}
```

### 2.5 生成报告

**请求**

```
POST /api/generate_report
Content-Type: application/json
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file_id | String | 是 | 文件ID |

**响应**

```json
{
    "success": true,
    "json_report": "report_uuid_20240101_120000.json",
    "pdf_report": "report_uuid_20240101_120000.pdf",
    "message": "报告生成成功"
}
```

### 2.6 获取知识

**请求**

```
GET /api/get_knowledge?defect_type=crazing
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| defect_type | String | 是 | 缺陷类型 |

**响应**

```json
{
    "success": true,
    "defect_type": "crazing",
    "enterprise_standard": {
        "name": "crazing (发丝纹)",
        "description": "钢板表面呈现细小、密集的发丝状裂纹",
        "standard": "发丝纹缺陷长度超过50mm判定为不合格",
        "severity": "medium"
    },
    "historical_cases": [
        {
            "case_id": "CASE-2024-03-A01",
            "title": "产线A发丝纹缺陷分析",
            "description": "...",
            "solution": "..."
        }
    ]
}
```

### 2.7 下载报告

**请求**

```
GET /api/reports/report_uuid_20240101_120000.pdf
```

**响应**

返回文件流

## 3. 错误码

| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 404 | 资源未找到 |
| 500 | 服务器内部错误 |

## 4. 响应格式

### 4.1 成功响应

```json
{
    "success": true,
    "data": { ... }
}
```

### 4.2 失败响应

```json
{
    "success": false,
    "error": "错误描述"
}
```

## 5. 示例代码

### 5.1 Python

```python
import requests

# 上传图片
with open('test.jpg', 'rb') as f:
    upload_response = requests.post('http://localhost:5000/api/upload', files={'image': f})
    file_id = upload_response.json()['file_id']

# 检测缺陷
detect_response = requests.post(
    'http://localhost:5000/api/detect',
    json={'file_id': file_id}
)
print(detect_response.json())
```

### 5.2 cURL

```bash
# 上传图片
curl -X POST -F "image=@test.jpg" http://localhost:5000/api/upload

# 检测缺陷
curl -X POST -H "Content-Type: application/json" \
  -d '{"file_id": "your-file-id"}' \
  http://localhost:5000/api/detect
```