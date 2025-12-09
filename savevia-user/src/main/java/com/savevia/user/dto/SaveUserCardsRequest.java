package com.savevia.user.dto;

import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.util.List;

@Data
public class SaveUserCardsRequest {

    @NotNull(message = "Card IDs are required")
    private List<Long> cardIds;
}
