# finSight

金融资产管理平台 - 让用户注册、登录并管理自己关注的资产列表

## 技术栈

### 后端
- Node.js + Express + TypeScript
- PostgreSQL 数据库
- Prisma ORM
- JWT 认证
- bcrypt 密码加密

### 前端
- React + TypeScript
- Axios HTTP 客户端
- React Router

## 项目结构

```
finSight/
├── backend/              # 后端服务
│   ├── src/
│   │   ├── config/      # 配置文件
│   │   ├── controllers/ # 控制器
│   │   ├── middleware/  # 中间件
│   │   ├── routes/      # 路由
│   │   ├── utils/       # 工具函数
│   │   └── server.ts    # 入口文件
│   ├── prisma/          # 数据库模型
│   └── package.json
├── frontend/            # 前端应用
│   ├── src/
│   │   ├── components/  # 组件
│   │   ├── pages/       # 页面
│   │   ├── services/    # API 服务
│   │   ├── types/       # 类型定义
│   │   └── App.tsx
│   └── package.json
└── README.md
```

## 快速开始

### 后端启动

```bash
cd backend
npm install
cp .env.example .env
# 配置 .env 文件中的数据库连接
npm run migrate
npm run dev
```

### 前端启动

```bash
cd frontend
npm install
npm start
```

## API 端点

### 认证
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录

### 资产管理
- `GET /api/assets` - 获取用户资产列表
- `POST /api/assets` - 添加资产
- `DELETE /api/assets/:id` - 删除资产
