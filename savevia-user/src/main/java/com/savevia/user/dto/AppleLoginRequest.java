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
}
