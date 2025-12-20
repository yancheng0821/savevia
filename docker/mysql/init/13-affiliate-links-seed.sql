-- Affiliate Links Configuration Examples
-- 这是示例配置文件，根据你注册的实际联盟账户修改

-- 注意：在添加前，请确保 card_id 对应的信用卡已经存在！

-- 示例数据（替换为你的实际链接）
INSERT INTO affiliate_links (card_id, bank_name, affiliate_type, affiliate_url, commission_amount, is_active)
VALUES
-- AMEX Cobalt (假设 card_id = 1)
-- (1, 'American Express', 'AMEX_AFFILIATE', 'https://www.americanexpress.com/ca/en/credit-cards/cobalt-card/?ref=YOUR_AMEX_ID', 50.00, TRUE),

-- RBC Avion (假设 card_id = 2)
-- (2, 'RBC', 'RBC_AFFILIATE', 'https://www.rbcroyalbank.com/credit-cards/rbc-avion/?ref=YOUR_RBC_ID', 30.00, TRUE),

-- TD Infinite (假设 card_id = 3)
-- (3, 'TD', 'TD_AFFILIATE', 'https://www.td.com/ca/en/credit-cards/td-infinite/?ref=YOUR_TD_ID', 25.00, TRUE),

-- BMO Premium (假设 card_id = 4)
-- (4, 'BMO', 'BMO_AFFILIATE', 'https://www.bmo.com/ca/credit-cards/bmo-premium/?ref=YOUR_BMO_ID', 25.00, TRUE)

-- 说明：
-- 1. 取消注释(删除开头的--)实际需要的行
-- 2. 修改 card_id 为你实际的卡片ID
-- 3. 修改 affiliate_url 为你的实际联盟链接
-- 4. 修改 commission_amount 为实际的预估佣金
-- 5. 运行此 SQL 添加配置

-- 快速添加模板：
-- INSERT INTO affiliate_links (card_id, bank_name, affiliate_type, affiliate_url, commission_amount, is_active)
-- VALUES (?, '银行名称', '联盟类型', 'https://你的联盟申卡链接', 佣金金额, TRUE);
