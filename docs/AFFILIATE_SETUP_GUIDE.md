# SaveVia 银行申卡联盟链接配置指南

## 概述
本文档说明如何配置加拿大各大银行的申卡联盟链接，以实现通过推荐用户申卡获得佣金。

## ✅ 已实现的系统架构

### 后端服务
- **AffiliateService**: 管理联盟链接配置和点击追踪
- **AffiliateController**: REST API 端点
- **AffiliateClickTracking**: 点击统计表

### 前端集成
- **CardDetailPage**: 添加"申请"按钮，点击时追踪行为
- **affiliateApi**: 前端 API 调用

### 数据库
- **affiliate_click_tracking**: 记录所有申卡链接点击

---

## 🔗 加拿大银行联盟计划

### 1. American Express (AMEX) ⭐
**佣金**: $25-50 CAD/申卡

**如何注册**:
1. 访问: https://www.americanexpress.com/ca/en/partners/
2. 点击 "Affiliate Program" 或 "Partnerships"
3. 申请个人推荐者账户（无需企业账户）
4. 获批后，进入 Dashboard 生成你的专属链接

**获取链接**:
- Dashboard → Referral Links
- 选择 "AMEX Cobalt Card" 或其他卡片
- 复制你的个人推荐链接 (通常格式: `https://www.americanexpress.com/ca/en/credit-cards/...?ref=YOUR_ID`)

**配置方式**:
```java
// 在 AffiliateService.initializeAffiliateLinks() 中添加:
affiliateLinksMap.put(1L, new AffiliateLinkDTO(
    1L,
    "American Express",
    "AMEX_AFFILIATE",
    "https://www.americanexpress.com/ca/en/credit-cards/cobalt-credit-card/?ref=YOUR_AMEX_ID",
    50.0  // 预估佣金
));
```

---

### 2. RBC (Royal Bank of Canada)
**佣金**: $20-40 CAD/申卡

**如何注册**:
1. 访问: https://www.rbcroyalbank.com/affiliate/
2. 点击 "Join Our Affiliate Program"
3. 填写个人信息（无需企业账户）
4. RBC 会在 2-3 天内审批

**获取链接**:
- RBC Affiliate Portal → Referral Links
- 选择卡片 (如 "RBC Avion Card")
- 复制你的推荐链接

**配置方式**:
```java
affiliateLinksMap.put(2L, new AffiliateLinkDTO(
    2L,
    "RBC",
    "RBC_AFFILIATE",
    "https://www.rbcroyalbank.com/credit-cards/rbc-avion-infinite/?ref=YOUR_RBC_ID",
    30.0
));
```

---

### 3. TD Bank (Toronto-Dominion)
**佣金**: $20-35 CAD/申卡

**如何注册**:
1. 访问: https://www.td.com/affiliates/
2. 点击 "Become an Affiliate"
3. 注册个人账户
4. 邮件确认

**获取链接**:
- TD Affiliate Dashboard → Referral Program
- 选择信用卡产品
- 生成专属链接

**配置方式**:
```java
affiliateLinksMap.put(3L, new AffiliateLinkDTO(
    3L,
    "TD",
    "TD_AFFILIATE",
    "https://www.td.com/ca/en/credit-cards/td-infinite-credit-card/?ref=YOUR_TD_ID",
    25.0
));
```

---

### 4. BMO (Bank of Montreal)
**佣金**: $20-30 CAD/申卡

**如何注册**:
1. 访问: https://www.bmo.com/affiliate/
2. 点击 "Affiliate Program"
3. 个人推荐者申请
4. 2-3 天审批

**配置方式**:
```java
affiliateLinksMap.put(4L, new AffiliateLinkDTO(
    4L,
    "BMO",
    "BMO_AFFILIATE",
    "https://www.bmo.com/ca/credit-cards/bmo-premium-cash-back/?ref=YOUR_BMO_ID",
    25.0
));
```

---

### 5. Scotiabank
**佣金**: $15-30 CAD/申卡

**如何注册**:
1. 访问: https://www.scotiabank.com/ca/en/partners/
2. 搜索 Affiliate Program
3. 个人推荐者注册
4. 获批并获得链接

**配置方式**:
```java
affiliateLinksMap.put(5L, new AffiliateLinkDTO(
    5L,
    "Scotiabank",
    "SCOTIAB_AFFILIATE",
    "https://www.scotiabank.com/ca/en/credit-cards/.../?ref=YOUR_SCOTIAB_ID",
    25.0
));
```

---

### 6. CIBC
**佣金**: $15-30 CAD/申卡

**配置方式**:
```java
affiliateLinksMap.put(6L, new AffiliateLinkDTO(
    6L,
    "CIBC",
    "CIBC_AFFILIATE",
    "https://www.cibc.com/ca/credit-cards/.../?ref=YOUR_CIBC_ID",
    25.0
));
```

---

## 🔧 实现步骤

### Step 1: 注册银行联盟账户
对于上面列出的每家银行：
1. 点击对应的官网链接
2. 选择"个人推荐者"或"Affiliate"选项
3. 使用个人信息注册（**无需企业账户**）
4. 等待审批（通常 1-5 天）

### Step 2: 获取申卡链接
审批通过后：
1. 登陆银行的 Affiliate Dashboard
2. 找到"Referral Links"或"Share Links"部分
3. 为每张卡生成你的专属链接
4. 复制链接

### Step 3: 更新 AffiliateService
编辑文件:
```
/savevia-card/src/main/java/com/savevia/card/service/AffiliateService.java
```

在 `initializeAffiliateLinks()` 方法中添加:
```java
affiliateLinksMap.put(CARD_ID_HERE, new AffiliateLinkDTO(
    CARD_ID_HERE,
    "BankName",
    "BANK_AFFILIATE",
    "YOUR_AFFILIATE_LINK_HERE",
    COMMISSION_AMOUNT  // 预估佣金
));
```

### Step 4: 重启后端服务
```bash
./restart-backend.sh
```

### Step 5: 测试
1. 打开应用，进入卡片详情页
2. 点击"申请"按钮
3. 确保跳转到正确的联盟链接
4. 检查后端日志:
   ```
   [INFO] Tracked affiliate click - userId: 123, cardId: 1, bank: American Express
   ```

---

## 📊 追踪点击数据

### 查看点击统计
```bash
# 查询今日点击数
curl http://localhost:8080/api/v1/affiliate/stats/1/today \
  -H "Authorization: Bearer YOUR_TOKEN"

# 查询数据库
mysql> SELECT DATE(clicked_at), COUNT(*) as clicks
       FROM affiliate_click_tracking
       WHERE card_id = 1
       GROUP BY DATE(clicked_at);
```

### 数据库查询
```sql
-- 查看所有点击
SELECT * FROM affiliate_click_tracking
ORDER BY clicked_at DESC
LIMIT 100;

-- 按银行统计
SELECT bank_name, COUNT(*) as total_clicks, DATE(clicked_at) as date
FROM affiliate_click_tracking
GROUP BY bank_name, DATE(clicked_at)
ORDER BY date DESC;

-- 按用户统计
SELECT user_id, COUNT(*) as total_clicks
FROM affiliate_click_tracking
WHERE user_id IS NOT NULL
GROUP BY user_id
ORDER BY total_clicks DESC;
```

---

## 💰 预估收益计算

假设有 1000 个月活跃用户:

| 银行 | 申卡转化率 | 用户数 | 佣金/次 | 月收入 |
|------|----------|--------|---------|---------|
| AMEX | 5% | 50 | $40 | $2,000 |
| RBC | 4% | 40 | $30 | $1,200 |
| TD | 3% | 30 | $25 | $750 |
| BMO | 3% | 30 | $25 | $750 |
| Scotiabank | 2% | 20 | $20 | $400 |
| **Total** | **17%** | **170** | - | **$5,100/月** |

---

## ⚠️ 注意事项

### ✅ 允许的做法
- ✅ 在你的应用中展示联盟链接
- ✅ 用户点击自愿申卡
- ✅ 透明地告诉用户这是联盟链接
- ✅ 追踪点击和转化

### ❌ 禁止的做法
- ❌ 未经同意自动点击链接
- ❌ 虚假流量或机器人点击
- ❌ 误导用户点击
- ❌ 在隐私政策中隐瞒联盟关系

### 建议
1. **透明度**: 在应用中声明"通过链接申卡，我们可能获得返利"
2. **隐私政策**: 更新政策说明联盟关系
3. **用户体验**: 不要强迫点击，让用户自愿选择

---

## 🔄 更新流程（未来改进）

当你获得企业账户或 DUNS 号后：

1. **升级到官方合作伙伴**
   - 联系每家银行的商务部门
   - 申请正式的商业合作关系
   - 获得更高佣金（$50-100+/申卡）

2. **API 集成**
   - 使用银行的 API 直接验证申卡成功
   - 自动化佣金结算

3. **高级功能**
   - Revenue Share 模式（按申卡后消费额分成）
   - Co-branded 产品

---

## 📞 支持

如有问题：
- 银行联盟问题: 联系对应银行的 Affiliate Team
- 系统集成问题: 检查后端日志 `/logs/savevia-card.log`
- 数据追踪问题: 查询 `affiliate_click_tracking` 表

---

**最后更新**: 2025-12-19
**作者**: SaveVia Team
