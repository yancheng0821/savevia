package com.savevia.optimizer.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class SaveResultResponse {
    private String shareId;
    private String shareUrl;
}
