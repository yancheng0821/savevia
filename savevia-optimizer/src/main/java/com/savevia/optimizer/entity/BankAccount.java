package com.savevia.optimizer.entity;

import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
public class BankAccount {
    private Long id;
    private Long connectionId;
    private Long userId;
    private String flinksAccountId;
    private String accountType; // CHECKING, SAVINGS, CREDIT_CARD, LINE_OF_CREDIT, OTHER
    private String accountName;
    private String accountNumberMasked;
    private String institutionName;
    private BigDecimal balance;
    private Boolean isActive;
    private Long linkedCardId;  // Linked credit card ID from cards table
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
