# 智谱AI Vision MCP Server

这是一个遵循 Model Context Protocol (MCP) 规范的视觉模型服务器，用于处理图像分析请求。

## 功能特性

- 符合 MCP 规范的视觉模型接口
- 支持智谱AI的GLM-Vision模型
- 图像分析、物体检测、场景理解
- 支持多种图像格式 (JPEG, PNG, WEBP)
- RESTful API 接口

## 安装依赖

```bash
pip install zhipuai aiohttp
```

## 配置

1. 获取智谱AI API密钥：访问 [https://bigmodel.cn](https://bigmodel.cn) 注册并获取API密钥
2. 编辑 `zhipu_vision_config.json` 文件，替换 `YOUR_ZHIPU_API_KEY_HERE` 为实际的API密钥

## 启动服务器

```bash
./start_zhipu_vision.sh
```

服务器将在 `http://localhost:8000` 上运行。

## API接口

### 获取服务器能力
```
GET http://localhost:8000/capabilities
```

返回服务器支持的模型和功能。

### 执行视觉分析
```
POST http://localhost:8000/execute
Content-Type: application/json

{
  "model": "glm-vision",
  "image": "base64_encoded_image_data",
  "prompt": "请详细描述这张图片的内容"
}
```

## 请求参数

- `model`: 使用的模型ID (默认: glm-vision)
- `image`: Base64编码的图像数据，支持data URL格式
- `prompt`: 分析提示词 (可选，默认为描述图片内容)

## 响应格式

```json
{
  "success": true,
  "result": {
    "text": "模型生成的文本描述",
    "usage": {...},
    "finish_reason": "stop"
  },
  "model_used": "glm-vision"
}
```

## 使用示例

```javascript
// JavaScript示例
const imageFile = document.getElementById('imageInput').files[0];
const reader = new FileReader();

reader.onload = function(event) {
  const base64Image = event.target.result;
  
  fetch('http://localhost:8000/execute', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: 'glm-vision',
      image: base64Image,
      prompt: '请描述这张图片的内容'
    })
  })
  .then(response => response.json())
  .then(data => console.log(data.result.text));
};

reader.readAsDataURL(imageFile);
```

## 错误处理

- `400`: 请求参数错误
- `500`: 服务器内部错误或API调用失败

## 安全注意事项

- 请妥善保管API密钥
- 限制服务器访问权限
- 考虑添加认证机制

## 故障排除

1. 如果出现API密钥错误，请检查配置文件中的密钥是否正确
2. 如果服务器无法启动，请检查端口是否被占用
3. 如果API调用失败，请检查网络连接和API配额