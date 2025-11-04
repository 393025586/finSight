# finSight 安装和使用指南

## 项目介绍

finSight 是一个金融资产管理平台，支持用户注册、登录并管理自己关注的资产列表。

## 技术架构

**后端：**
- Node.js + Express + TypeScript
- Prisma ORM (SQLite 开发环境，可切换到 PostgreSQL)
- JWT 用户认证
- bcrypt 密码加密

**前端：**
- React 18 + TypeScript
- Vite 构建工具
- React Router v6
- Axios HTTP 客户端

## 快速开始

### 1. 安装后端依赖

```bash
cd backend
npm install
```

### 2. 初始化数据库

```bash
cd backend
npx prisma generate
npx prisma migrate dev --name init
```

这会创建 SQLite 数据库文件 `backend/dev.db` 并应用数据库迁移。

### 3. 启动后端服务

```bash
cd backend
npm run dev
```

后端服务将运行在 http://localhost:3001

### 4. 安装前端依赖

打开新的终端窗口：

```bash
cd frontend
npm install
```

### 5. 启动前端服务

```bash
cd frontend
npm run dev
```

前端应用将运行在 http://localhost:3000

## 功能说明

### 用户认证

1. **注册新账号**
   - 访问 http://localhost:3000/register
   - 填写邮箱、用户名和密码
   - 密码至少 6 位

2. **登录**
   - 访问 http://localhost:3000/login
   - 使用邮箱或用户名登录
   - 登录成功后会跳转到资产管理页面

### 资产管理

1. **查看资产列表**
   - 登录后自动显示您的资产列表
   - 支持多种资产类型：股票、加密货币、商品、外汇等

2. **添加资产**
   - 点击"添加资产"按钮
   - 填写资产代码（如 AAPL、BTC）
   - 填写资产名称和类型
   - 可选择添加备注

3. **删除资产**
   - 每个资产卡片右下角有"删除"按钮
   - 点击后需要确认

## API 端点

### 认证相关

- `POST /api/auth/register` - 用户注册
  ```json
  {
    "email": "user@example.com",
    "username": "username",
    "password": "password123"
  }
  ```

- `POST /api/auth/login` - 用户登录
  ```json
  {
    "emailOrUsername": "user@example.com",
    "password": "password123"
  }
  ```

### 资产管理（需要认证）

所有资产相关的请求需要在 Header 中添加：
```
Authorization: Bearer <your-jwt-token>
```

- `GET /api/assets` - 获取当前用户的资产列表

- `POST /api/assets` - 添加新资产
  ```json
  {
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "type": "stock",
    "notes": "Optional notes"
  }
  ```

- `PUT /api/assets/:id` - 更新资产信息
  ```json
  {
    "name": "Updated Name",
    "type": "crypto",
    "notes": "Updated notes"
  }
  ```

- `DELETE /api/assets/:id` - 删除资产

## 数据库结构

### User 表
- id (主键)
- email (唯一)
- username (唯一)
- password (bcrypt 加密)
- createdAt
- updatedAt

### Asset 表
- id (主键)
- userId (外键)
- symbol (资产代码)
- name (资产名称)
- type (资产类型)
- notes (备注，可选)
- createdAt
- updatedAt

## 环境配置

### 后端环境变量 (.env)

```env
DATABASE_URL="file:./dev.db"
JWT_SECRET="your-secret-key"
PORT=3001
NODE_ENV=development
FRONTEND_URL=http://localhost:3000
```

### 切换到 PostgreSQL

如需使用 PostgreSQL，修改以下配置：

1. 修改 `backend/prisma/schema.prisma`:
```prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}
```

2. 修改 `backend/.env`:
```env
DATABASE_URL="postgresql://username:password@localhost:5432/finsight"
```

3. 重新运行迁移:
```bash
npx prisma migrate dev --name init
```

## 生产部署建议

1. **安全性**
   - 修改 JWT_SECRET 为强随机字符串
   - 使用 HTTPS
   - 配置 CORS 仅允许特定域名
   - 使用 PostgreSQL 而非 SQLite

2. **性能优化**
   - 启用生产构建: `npm run build`
   - 使用 PM2 或其他进程管理器
   - 配置反向代理（Nginx）
   - 启用缓存和压缩

3. **数据库**
   - 定期备份数据库
   - 配置数据库连接池
   - 监控数据库性能

## 故障排查

### 后端启动失败
- 检查 Node.js 版本（需要 v18+）
- 确保已运行 `npm install`
- 检查数据库配置是否正确

### 前端启动失败
- 检查端口 3000 是否被占用
- 确保后端服务正在运行
- 清除 node_modules 重新安装

### 登录/注册失败
- 检查后端服务是否运行
- 查看浏览器开发者工具的 Network 标签
- 检查后端日志输出

## 开发建议

- 后端代码修改会自动重启（使用 ts-node-dev）
- 前端代码修改会自动热重载（使用 Vite HMR）
- 使用 TypeScript 可获得更好的类型检查
- Prisma Studio 可视化管理数据库: `npx prisma studio`

## 许可证

MIT
