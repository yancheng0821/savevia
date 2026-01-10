# 智能推送提醒系统方案

> 创建时间: 2025-01-08

## 概述

学习用户消费习惯和时间规律，从对话内容中提取关键信息，主动做 app 推送，提供有价值的卡片使用建议。

---

## 1. 数据收集层

### 需要收集的数据

**1.1 用户行为数据**
- 使用 app 的时间规律
- 查看的卡片和分类
- 优化结果的消费场景

**1.2 对话数据**
- 提取关键实体：日期、地点、消费场景、金额
- 例如："下个月去欧洲" → 提取: `{event: "travel", destination: "europe", time: "next_month"}`

**1.3 交易数据（如有 Plaid 连接）**
- 消费时间规律
- 消费地点/商户
- 消费金额模式

---

## 2. 数据库设计

```sql
-- 用户洞察表
CREATE TABLE user_insights (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    insight_type VARCHAR(50) NOT NULL,  -- 'spending_pattern', 'upcoming_event', 'preference'
    insight_key VARCHAR(100),            -- 'grocery_day', 'travel_plan', 'favorite_category'
    insight_value JSON,                  -- {"day": "saturday", "time": "10:00-12:00"}
    confidence DECIMAL(3,2),             -- 0.00-1.00
    source VARCHAR(50),                  -- 'chat', 'transaction', 'behavior'
    expires_at DATETIME,                 -- 对于临时事件
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_type (user_id, insight_type),
    INDEX idx_expires (expires_at)
);

-- 推送记录表
CREATE TABLE push_notifications (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    title VARCHAR(200),
    body TEXT,
    data JSON,
    scheduled_at DATETIME,
    sent_at DATETIME,
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'sent', 'failed', 'cancelled'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_status (user_id, status),
    INDEX idx_scheduled (scheduled_at, status)
);

-- 用户推送设置
CREATE TABLE user_push_settings (
    user_id BIGINT PRIMARY KEY,
    enabled BOOLEAN DEFAULT TRUE,
    quiet_hours_start TIME,              -- 免打扰开始时间
    quiet_hours_end TIME,
    max_daily_pushes INT DEFAULT 3,
    preferred_time TIME,                 -- 首选推送时间
    categories JSON,                     -- {"spending_reminder": true, "travel_alert": true}
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

---

## 3. 对话内容分析服务

```java
@Service
public class ChatInsightExtractor {

    // 从对话中提取洞察
    public List<UserInsight> extractInsights(Long userId, String message, String response) {
        List<UserInsight> insights = new ArrayList<>();

        // 1. 提取旅行计划
        extractTravelPlan(message, insights);

        // 2. 提取大额消费计划
        extractSpendingPlan(message, insights);

        // 3. 提取时间相关信息
        extractTimeBasedEvents(message, insights);

        return insights;
    }

    // 使用 AI 提取结构化信息
    public InsightExtractionResult extractWithAI(String conversationContext) {
        // 调用 OpenAI 提取关键信息
        String prompt = """
            从以下对话中提取用户的计划和偏好，返回JSON格式：
            {
                "travel_plans": [{"destination": "", "date": "", "duration": ""}],
                "spending_plans": [{"category": "", "amount": "", "date": ""}],
                "preferences": [{"category": "", "preference": ""}]
            }
            对话内容: %s
            """;
        // ...
    }
}
```

---

## 4. 推送类型设计

| 类型 | 触发条件 | 示例 |
|------|---------|------|
| **消费提醒** | 用户规律性消费时间前 | "周六买菜记得用 Tangerine World，超市返现 2%！" |
| **旅行提醒** | 对话中提到旅行日期临近 | "下周去欧洲？记得带 Scotiabank Passport，无外汇手续费" |
| **优惠到期** | 卡片优惠即将到期 | "您的 Amex 餐饮 5x 积分优惠本月底到期" |
| **最佳时机** | 特定节日/购物季 | "黑五购物用 CIBC Dividend 网购返现 4%" |
| **错过提醒** | 分析到更好的选择 | "上周超市消费 $200，用 X 卡可多省 $6" |

---

## 5. 推送调度服务

```java
@Service
public class PushNotificationScheduler {

    // 每天运行一次，生成当天的推送计划
    @Scheduled(cron = "0 0 6 * * *")  // 每天早上6点
    public void generateDailyPushPlan() {
        List<User> users = userService.getActiveUsers();

        for (User user : users) {
            // 1. 检查用户洞察
            List<UserInsight> insights = insightService.getActiveInsights(user.getId());

            // 2. 生成推送内容
            List<PushNotification> notifications = generateNotifications(user, insights);

            // 3. 调度推送（考虑用户偏好时间）
            scheduleNotifications(user, notifications);
        }
    }

    // 发送推送
    @Scheduled(fixedRate = 60000)  // 每分钟检查
    public void sendScheduledPushes() {
        List<PushNotification> pending = pushRepo.findReadyToSend();
        for (PushNotification push : pending) {
            sendPush(push);
        }
    }
}
```

---

## 6. 实现步骤

### Phase 1 - 基础设施 (1-2周)
- [ ] 创建数据库表
- [ ] 集成 APNs (iOS) 推送服务
- [ ] 集成 FCM (Android) 推送服务
- [ ] 实现基础推送发送功能
- [ ] 前端集成推送 SDK，获取 device token

### Phase 2 - 数据收集 (1周)
- [ ] 在对话完成后调用 AI 提取洞察
- [ ] 记录用户行为数据
- [ ] 存储用户偏好到 user_insights 表

### Phase 3 - 智能推送 (2周)
- [ ] 实现各类推送规则引擎
- [ ] 推送调度器 (Spring Scheduler)
- [ ] 用户推送设置页面
- [ ] 推送内容多语言支持

### Phase 4 - 优化 (持续)
- [ ] 推送效果追踪（打开率、转化）
- [ ] 调整推送策略
- [ ] A/B 测试不同推送内容
- [ ] 防疲劳机制优化

---

## 7. 技术选型

| 组件 | 技术 | 说明 |
|------|------|------|
| iOS 推送 | APNs | Apple Push Notification service |
| Android 推送 | FCM | Firebase Cloud Messaging |
| 调度 | Spring Scheduler | 定时任务 |
| AI 分析 | OpenAI API | 从对话提取结构化信息 |
| 消息队列 | (可选) Redis/RabbitMQ | 高并发时使用 |

---

## 8. 注意事项

1. **用户隐私**: 明确告知用户数据收集用途，提供关闭选项
2. **推送频率**: 控制每日推送数量，避免骚扰用户
3. **时区处理**: 根据用户所在时区发送推送
4. **免打扰时段**: 尊重用户设置的免打扰时间
5. **推送权限**: 优雅处理用户拒绝推送权限的情况
