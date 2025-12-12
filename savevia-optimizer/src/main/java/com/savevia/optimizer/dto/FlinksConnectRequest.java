package com.savevia.optimizer.dto;

import lombok.Data;
import java.util.List;

@Data
public class FlinksConnectRequest {
    private String loginId;          // From Flinks Connect redirect
    private String institutionName;  // Bank name
    private String accountId;        // Optional: specific account filter
    private List<Long> userCardIds;  // User's card IDs for demo mode transaction assignment
}
