package com.savevia.optimizer.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

@Data
public class BankConnectionDTO {
    private Long id;
    private String institutionName;
    private String status;

    @JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ss")
    private LocalDateTime lastSyncAt;

    private String errorMessage;
    private List<BankAccountDTO> accounts;

    @JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ss")
    private LocalDateTime createdAt;

    @Data
    public static class BankAccountDTO {
        private Long id;
        private String accountType;
        private String accountName;
        private String accountNumberMasked;
        private BigDecimal balance;
        private Boolean isActive;
    }
}
