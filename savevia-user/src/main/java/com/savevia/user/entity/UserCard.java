package com.savevia.user.entity;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserCard {

    private Long id;

    private Long userId;

    private Long cardId;

    private LocalDate acquiredDate;

    private LocalDateTime createdAt;
}
