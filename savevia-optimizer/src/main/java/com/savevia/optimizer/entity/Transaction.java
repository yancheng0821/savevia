package com.savevia.optimizer.entity;

import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
public class Transaction {
    private Long id;
    private Long userId;
    private Long accountId;
    private String flinksTransactionId;
    private BigDecimal amount;
    private String merchant;
    private String description;
    private String mcc;
    private String category;
    private LocalDateTime transactionDate;
    private Long cardUsedId;
    private Long bestCardId;
    private BigDecimal actualCashback;
    private BigDecimal optimalCashback;
    private BigDecimal missedCashback;
    private Boolean isAnalyzed;
    private LocalDateTime createdAt;
}
