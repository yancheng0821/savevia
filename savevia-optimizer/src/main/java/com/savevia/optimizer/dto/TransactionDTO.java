package com.savevia.optimizer.dto;

import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
public class TransactionDTO {
    private Long id;
    private Long userId;
    private BigDecimal amount;
    private String merchant;
    private String description;
    private String category;
    private LocalDateTime transactionDate;

    // Card info
    private Long cardUsedId;
    private String cardUsedName;
    private Long bestCardId;
    private String bestCardName;
    private String bestCardBank;
    private Boolean isDebitTransaction; // true if paid with debit card/bank account (no cashback)

    // Cashback analysis
    private BigDecimal actualCashback;
    private BigDecimal optimalCashback;
    private BigDecimal missedCashback;
    private BigDecimal bestCardRate;

    private Boolean isAnalyzed;
}
