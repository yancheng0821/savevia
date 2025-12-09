# 🚀《加拿大信用卡返现优化助手》完整技术实现方案（可直接落地）

------

# 1. 产品定位（核心一句话）

> **SmartCard AI —— 加拿大首个自动计算消费记录、分析信用卡最优返现策略、帮用户每年省下 $300–$1000 的金融助手。**

------

# 2. 产品功能（MVP → V1 → V2 发展路线）

## **MVP（不接银行）｜约 2 周**

- 用户选择自己的信用卡
- 输入消费类别（外食、超市等占比）
- 系统输出最优卡组合
- 展示可节省返现估算
- 信用卡知识库（年费、返现结构）

**主要目标：让用户快速意识到“我真的可以省钱”。**

------

## **V1（接银行，自动化分析）｜约 6–8 周**

集成 Flinks（只读，不触钱）实现：

- 自动获取用户 90 天交易数据
- 解析商户、MCC、消费类别
- 计算历史 90 天实际返现 vs 最优返现
- 输出“你错失了 X 元返现”报告
- 自动推荐用户应该刷哪张卡
- 月度返现优化报告（PDF 或页面显示）

------

## **V2（AI 驱动）｜3–6 个月**

- AI 解读每笔消费为什么推荐那张卡
- 消费趋势预测（未来 30 天）
- 最优卡申请推荐（signup bonus 优化）
- 税务优化建议
- 订阅识别（自动找出 recurring payments）

------

## **V3（成为加拿大财务助手）**

- Phone/Internet/Hydro 账单比价
- 保险比价
- 房贷续约分析
- 手机 App（实时提醒，GPS 触发提示）

------

# 3. 技术架构（最佳实践）

```
 ┌─────────────────────────────────┐
 │             Web 前端 (React)    │
 │  - 用户操作界面                  │
 │  - Flinks Connect Widget         │
 │  - Dashboard + 报告展示          │
 └─────────────────────────────────┘
                 ↓ REST API
 ┌─────────────────────────────────┐
 │    Spring Boot 主后端服务        │
 │  Modules:                       │
 │   - User Service                │
 │   - Card Rule Engine            │
 │   - Cashback Optimizer          │
 │   - Transaction Parser          │
 │   - Flinks Integration          │
 │   - Report Generator            │
 │   - Security & Token            │
 └─────────────────────────────────┘
                ↓ 
 ┌───────────────┬────────────────┬──────────────┐
 │ MySQL 8       │ Redis 7        │ Python AI     │
 │ 用户/交易表   │ 规则缓存/MCC   │ Claude/ML模型 │
 │ 卡片规则      │ 会话缓存       │ 分类/解释文本 │
 └───────────────┴────────────────┴──────────────┘
```

------

# 4. 模块设计（后端 Java）

## **4.1 User Module**

- 用户注册 / 登录
- OAuth Token
- Bank Connection 状态

## **4.2 Flinks Integration Module**

- 触发获取银行账户列表
- 拉取 90 天交易明细
- 标准化转换为内部 Transaction DTO

## **4.3 Transaction Parser**

- 去重
- 格式化金额
- 识别商户、类别、MCC
- 存入数据库

## **4.4 Card Rule Engine（核心）**

实现业务逻辑：

```
double calculateReward(Card card, Transaction tx) {
    double percent = ruleRepository.getRate(card.id, tx.mcc);
    return tx.amount * percent;
}
```

支持：

- MCC → 类别转换
- 年费折算
- 分段奖励类别（如 Amex Cobalt：餐饮 5%，外卖 5%）
- 每月上限（如 gas 每月 $500 封顶）
- 限时奖励（季度 category）

## **4.5 Cashback Optimizer**

- 基于交易记录计算实际返现
- 再计算用户应该刷的最优方案
- 产生“错失返现报告”

## **4.6 AI Explanation Service（Python）**

使用 Claude：

输入：

- 交易信息
- 最优卡规则
   输出：
- 文本解释（用户为什么应该用这张卡）

------

# 5. 数据库设计（MySQL）

## **cards（信用卡定义表）**

| 字段              | 类型    | 说明                  |
| ----------------- | ------- | --------------------- |
| id                | bigint  | PK                    |
| bank              | varchar | RBC / TD / BMO / Amex |
| name              | varchar | 卡名                  |
| annual_fee        | int     | 年费                  |
| reward_rules_json | json    | 返现规则              |
| promo_json        | json    | 开卡奖励              |

------

## **transactions（用户交易数据）**

| 字段     | 类型          |
| -------- | ------------- |
| id       | bigint        |
| user_id  | bigint        |
| amount   | decimal(10,2) |
| merchant | varchar       |
| mcc      | varchar       |
| category | varchar       |
| date     | datetime      |

------

## **user_cards（用户持有卡）**

| 字段    | 类型   |
| ------- | ------ |
| id      | bigint |
| user_id | bigint |
| card_id | bigint |

------

## **reward_rule（规则缓存表）**

| 字段    | 类型    |
| ------- | ------- |
| card_id | bigint  |
| mcc     | varchar |
| reward  | double  |

------

# 6. 关键算法（返现优化引擎）

## **算法 1：给每笔消费选最优卡**

```
Card bestCard = null;
double bestReward = 0;

for (Card card : userCards) {
    double reward = calculateReward(card, tx);
    if (reward > bestReward) {
        bestReward = reward;
        bestCard = card;
    }
}
return bestCard;
```

------

## **算法 2：计算用户错失返现**

```
double lost = optimalReward - actualReward;
```

------

## **算法 3：未来30天消费预测（简单版）**

使用 Python:

```
import pandas as pd

prediction = df['amount'].rolling(30).mean()
```

------

# 7. API 设计（REST）

## **POST /auth/register**

## **POST /auth/login**

## **POST /bank/connect**

启动 Flinks 连接流程。

## **GET /bank/transactions**

获取用户交易。

## **GET /cards/recommend**

根据交易 + 卡片给出最优推荐。

## **GET /cashback/report**

返回：

- 实际返现
- 最优返现
- 错失金额
- 每笔消费该用哪张卡

## **POST /ai/explain**

调用 Claude 分析。

------

# 8. 前端（React）结构

```
/src
 ├── pages
 │    ├── LandingPage.jsx
 │    ├── Dashboard.jsx
 │    ├── ConnectBank.jsx
 │    ├── CashbackReport.jsx
 │    ├── CardCompare.jsx
 ├── components
 │    ├── CardSelector.jsx
 │    ├── TransactionTable.jsx
 │    ├── SavingsChart.jsx
 │    ├── BankConnectWidget.jsx
 ├── services
 │    ├── api.js
 ├── utils
 └── styles
```

------

# 9. 部署方案

## **后端**

- AWS ECS or EC2 + Docker
- NGINX 反向代理
- RDS MySQL
- Elasticache Redis

## **前端**

- S3 + CloudFront CDN
- HTTPS 强制

## **AI 服务（Python）**

- AWS Lambda + API Gateway 或 EC2 容器

------

# 10. 安全与合规（关键）

### ✔ 不保存银行密码

### ✔ 使用 Flinks（只读 access）

### ✔ 数据加密（AES-256）

### ✔ 存储在加拿大机房（AWS ca-central-1）

### ✔ 用户可随时 revoke 权限

### ✔ 完整 Privacy Policy + Terms

------

# 11. 货币化模式

## **1. 订阅（最核心）**

$4.99–$9.99 / 月

## **2. 信用卡申请佣金（最高利润）**

每申请一张卡：$50–$200 奖励。

## **3. Premium AI 版**

- 税务优化
- 订阅检测
- 房贷建议

------

# 12. 项目时间线（现实估计）

| 阶段 | 功能              | 时间   |
| ---- | ----------------- | ------ |
| MVP  | 静态推荐          | 2 周   |
| V1   | Flinks + 自动分析 | 6–8 周 |
| V2   | AI + 强化优化     | 3–6 月 |
| V3   | 扩展财务助手      | 1 年   |