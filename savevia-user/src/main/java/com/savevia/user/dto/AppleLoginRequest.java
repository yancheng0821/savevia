package com.savevia.user.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class AppleLoginRequest {

    @NotBlank(message = "Apple identity token is required")
    private String identityToken;

    // Apple only provides name on first authorization
    // Can be null for subsequent logins
    private String fullName;

    // Apple provides email in the response (not in JWT token)
    // Only available on first authorization when user chooses to share
    private String email;
}
