# SaveVia - 加拿大信用卡返现优化助手

> 帮助加拿大用户选择最优信用卡，最大化每笔消费的返现/积分收益

## 产品概述

SaveVia 是一款智能信用卡优化工具，支持 iOS、Android 和 Web 平台。用户可以：

- **快速选卡**: 根据消费类别（餐饮、超市、加油等）推荐最佳信用卡
- **卡片管理**: 管理个人卡片组合，查看详细返现规则
- **AI 优化**: 基于消费习惯，AI 分析最优卡片组合
- **银行连接**: 通过 Flinks 连接银行账户，自动分析交易记录

## 技术栈

### 前端
- **React 18** + TypeScript + Vite
- **Capacitor 7** (iOS/Android 原生应用)
- **Ant Design 5** + TailwindCSS
- **React Query** + Zustand (状态管理)
- **i18next** (多语言: EN, FR, ZH, JA, KO, ES)

### 后端 (Spring Boot 微服务)
- **savevia-gateway** - API 网关 (端口 8080)
- **savevia-user** - 用户服务 (端口 8081)
- **savevia-optimizer** - 优化算法服务 (端口 8082)
- **savevia-card** - 卡片数据服务 (端口 8083)
- **savevia-eureka** - 服务发现 (端口 8761)

### 基础设施
- **MySQL 8** - 主数据库
- **Redis 7** - 缓存
- **AWS**: EC2, RDS, ElastiCache, S3, CloudFront

## 项目结构

```
savevia/
├── savevia-web/          # React 前端 + Capacitor
│   ├── src/
│   │   ├── pages/        # 页面组件
│   │   ├── components/   # 公共组件
│   │   ├── services/     # API 服务
│   │   ├── i18n/         # 多语言
│   │   └── stores/       # Zustand 状态
│   ├── ios/              # iOS 原生项目
│   └── android/          # Android 原生项目
│
├── savevia-gateway/      # API 网关
├── savevia-user/         # 用户服务 (认证, 订阅, 管理后台)
├── savevia-optimizer/    # 优化算法服务
├── savevia-card/         # 卡片数据服务
├── savevia-eureka/       # 服务发现
├── savevia-common/       # 公共模块
│
├── deployment/           # 生产部署配置
├── docker/               # Docker & MySQL 初始化脚本
└── scripts/              # 工具脚本
```

## 本地开发

### 环境要求
- Node.js 18+
- Java 17+
- MySQL 8
- Redis 7

### 启动后端

```bash
# 1. 启动 MySQL 和 Redis (Docker)
docker-compose up -d

# 2. 启动所有后端服务
./restart-backend.sh
```

### 启动前端

```bash
cd savevia-web

# 安装依赖
npm install

# 开发模式
npm run dev

# 构建 iOS
npm run cap:ios:prod

# 构建 Android
npm run cap:android
```

## 生产部署

### AWS 架构
```
CloudFront (CDN)
    ↓
S3 (前端静态资源)

EC2 (后端服务)
    ├── savevia-gateway:8080
    ├── savevia-user:8081
    ├── savevia-optimizer:8082
    ├── savevia-card:8083
    └── savevia-eureka:8761

RDS MySQL (savevia-prod-db)
ElastiCache Redis (savevia-prod-redis)
```

### 部署命令
```bash
cd deployment

# 部署后端
./deploy.sh

# 部署前端
./deploy-frontend.sh
```

## API 概览

### 认证
- `POST /api/v1/auth/google` - Google 登录
- `POST /api/v1/auth/apple` - Apple 登录
- `GET /api/v1/auth/check` - 验证 Token

### 卡片
- `GET /api/v1/cards` - 获取卡片列表
- `GET /api/v1/cards/{id}` - 卡片详情
- `GET /api/v1/cards/my` - 用户卡片

### 优化
- `POST /api/v1/optimizer/optimize` - AI 优化分析
- `GET /api/v1/optimizer/quick-pick` - 快速选卡

### 用户
- `GET /api/v1/user/profile` - 用户信息
- `PUT /api/v1/user/profile` - 更新信息
- `POST /api/v1/user/cards` - 添加卡片

### 管理后台
- `POST /api/v1/admin/login` - 管理员登录
- `GET /api/v1/admin/stats` - 统计数据
- `GET /api/v1/admin/users` - 用户列表

## 环境变量

主要环境变量 (见 `.env.example`):

```bash
# MySQL
MYSQL_HOST=localhost
MYSQL_DATABASE=savevia
MYSQL_USER=savevia
MYSQL_PASSWORD=savevia123

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT
JWT_SECRET=your-secret-key

# OAuth
GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx
APPLE_CLIENT_ID=com.savevia.app

# OpenAI
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=gpt-4o-mini

# Flinks
FLINKS_API_URL=https://toolbox-api.private.fin.ag/v3
FLINKS_CUSTOMER_ID=xxx
```

## 版本历史

- **v1.0.4** (2024-12) - 积分卡价值优化, 强制更新机制
- **v1.0.3** (2024-12) - Admin Dashboard, 多语言支持
- **v1.0.2** (2024-11) - iOS/Android 应用发布
- **v1.0.0** (2024-10) - 首次发布

## 许可证

Private - All Rights Reserved
