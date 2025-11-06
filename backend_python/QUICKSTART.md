# finSight 快速启动指南

## ✅ 问题已修复

已修复的问题：
1. ✅ 数据库session问题
2. ✅ 密码加密兼容性问题
3. ✅ 用户注册和登录功能正常

## 🚀 快速启动

### 1. 安装依赖（如果还没安装）

```bash
cd backend_python
pip install fastapi uvicorn sqlalchemy bcrypt python-jose[cryptography] python-dotenv loguru pandas numpy
```

### 2. 初始化数据库（如果还没初始化）

```bash
python init_db.py
```

输出应该显示：
```
正在初始化数据库...
✅ 数据库初始化成功！
```

### 3. 启动服务器

```bash
python main.py
```

服务器将在 `http://localhost:8000` 启动

### 4. 测试API

访问自动生成的API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 5. 测试认证功能

#### 测试注册：
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "myuser",
    "password": "password123"
  }'
```

#### 测试登录：
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "myuser",
    "password": "password123"
  }'
```

## 📝 已创建的测试账号

测试账号已存在，可以直接使用：
- **用户名**: testuser
- **邮箱**: test@example.com
- **密码**: password123

## 🧪 运行测试脚本

```bash
# 测试登录功能
python test_login.py

# 测试注册功能（会创建新用户）
python test_auth.py
```

## ⚠️ 常见问题

### 问题：ModuleNotFoundError

**解决方案**：安装缺失的包
```bash
pip install <缺失的包名>
```

### 问题：端口被占用

**解决方案**：修改 .env 文件中的 PORT 值
```bash
PORT=8001
```

### 问题：数据库文件不存在

**解决方案**：运行初始化脚本
```bash
python init_db.py
```

## 📊 API端点列表

### 认证
- POST `/api/auth/register` - 注册
- POST `/api/auth/login` - 登录
- GET `/api/auth/me` - 获取当前用户

### 资产
- GET `/api/assets/search?q=AAPL` - 搜索资产
- GET `/api/assets/{symbol}/info` - 资产信息
- GET `/api/assets/{symbol}/history` - 历史数据
- GET `/api/assets/{symbol}/realtime` - 实时价格
- GET `/api/assets/{symbol}/analysis` - 综合分析（含AI）

### 投资组合
- GET `/api/portfolio` - 获取组合
- POST `/api/portfolio` - 添加资产
- DELETE `/api/portfolio/{id}` - 删除资产

### 宏观经济
- GET `/api/macro/{country}` - 宏观指标
- GET `/api/macro/{country}/analysis` - AI分析

### 新闻
- GET `/api/news/market/{market}` - 市场新闻
- GET `/api/news/asset/{symbol}` - 资产新闻

### 笔记本
- GET `/api/notebook` - 获取笔记
- POST `/api/notebook` - 创建笔记
- PUT `/api/notebook/{id}` - 更新笔记
- DELETE `/api/notebook/{id}` - 删除笔记

### 每日总结
- GET `/api/daily-summary` - AI生成每日市场总结

## 🔗 下一步

1. **配置前端**：更新前端API地址为 `http://localhost:8000`
2. **安装完整依赖**：`pip install -r requirements.txt`（获取所有功能）
3. **配置API Keys**：在 `.env` 文件中配置Gemini API key
4. **测试完整功能**：访问 http://localhost:8000/docs 测试所有端点

## ✨ 成功！

你的finSight后端已经成功运行！🎉
