package com.savevia.user.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class LoginResponse {

    private String token;
    private String tokenType;
    private Long expiresIn;
    private UserDTO user;

    public static LoginResponse of(String token, Long expiresIn, UserDTO user) {
        return LoginResponse.builder()
            .token(token)
            .tokenType("Bearer")
            .expiresIn(expiresIn)
            .user(user)
            .build();
    }
}
