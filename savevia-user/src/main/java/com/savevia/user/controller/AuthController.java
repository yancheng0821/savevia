package com.savevia.user.controller;

import com.savevia.common.response.Result;
import com.savevia.user.dto.*;
import com.savevia.user.service.AuthService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    @PostMapping("/register")
    public Result<UserDTO> register(@Valid @RequestBody RegisterRequest request) {
        return Result.success("Registration successful", authService.register(request));
    }

    @PostMapping("/login")
    public Result<LoginResponse> login(@Valid @RequestBody LoginRequest request) {
        return Result.success(authService.login(request));
    }

    @PostMapping("/google")
    public Result<LoginResponse> googleLogin(@Valid @RequestBody GoogleLoginRequest request) {
        return Result.success(authService.loginWithGoogle(request.getCredential()));
    }

    @PostMapping("/apple")
    public Result<LoginResponse> appleLogin(@Valid @RequestBody AppleLoginRequest request) {
        return Result.success(authService.loginWithApple(request.getIdentityToken(), request.getFullName(), request.getEmail()));
    }

    @PutMapping("/avatar")
    public Result<UserDTO> updateAvatar(
            @RequestHeader("X-User-Id") Long userId,
            @Valid @RequestBody UpdateAvatarRequest request) {
        return Result.success("Avatar updated", authService.updateAvatar(userId, request.getAvatarUrl()));
    }

    @GetMapping("/me")
    public Result<UserDTO> getCurrentUser(@RequestHeader("X-User-Id") Long userId) {
        return Result.success(authService.getUserById(userId));
    }

    @PutMapping("/change-password")
    public Result<Void> changePassword(
            @RequestHeader("X-User-Id") Long userId,
            @Valid @RequestBody ChangePasswordRequest request) {
        authService.changePassword(userId, request.getCurrentPassword(), request.getNewPassword());
        return Result.success("Password changed successfully", null);
    }

    @PutMapping("/set-password")
    public Result<Void> setPassword(
            @RequestHeader("X-User-Id") Long userId,
            @Valid @RequestBody SetPasswordRequest request) {
        authService.setPassword(userId, request.getNewPassword());
        return Result.success("Password set successfully", null);
    }

    @PostMapping("/forgot-password")
    public Result<Void> forgotPassword(@Valid @RequestBody ForgotPasswordRequest request) {
        authService.forgotPassword(request.getEmail());
        return Result.success("If the email exists, a password reset link will be sent", null);
    }

    @PostMapping("/reset-password")
    public Result<Void> resetPassword(@Valid @RequestBody ResetPasswordRequest request) {
        authService.resetPassword(request.getToken(), request.getNewPassword());
        return Result.success("Password reset successfully", null);
    }

    @PostMapping("/send-verification")
    public Result<Void> sendVerification(@RequestHeader("X-User-Id") Long userId) {
        authService.sendEmailVerification(userId);
        return Result.success("Verification email sent", null);
    }

    @PostMapping("/verify-email")
    public Result<Void> verifyEmail(@RequestParam String token) {
        authService.verifyEmail(token);
        return Result.success("Email verified successfully", null);
    }

    @PutMapping("/subscription")
    public Result<UserDTO> updateSubscription(
            @RequestHeader("X-User-Id") Long userId,
            @Valid @RequestBody UpdateSubscriptionRequest request) {
        return Result.success("Subscription updated",
                authService.updateSubscription(userId, request.getSubscriptionType(),
                        request.getExpiresAt(), request.getPlatform(), request.getProductId()));
    }

    @GetMapping("/subscription")
    public Result<UserDTO> getSubscription(@RequestHeader("X-User-Id") Long userId) {
        return Result.success(authService.getSubscriptionStatus(userId));
    }
}
