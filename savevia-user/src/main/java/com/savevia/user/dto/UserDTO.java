package com.savevia.user.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserDTO {

    private Long id;
    private String email;
    private String name;
    private String avatarUrl;
    private LocalDateTime createdAt;
    private Boolean hasPassword;
    private Boolean emailVerified;
}
