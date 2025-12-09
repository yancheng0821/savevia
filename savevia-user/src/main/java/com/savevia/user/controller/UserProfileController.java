package com.savevia.user.controller;

import com.savevia.common.response.Result;
import com.savevia.user.dto.UserDTO;
import com.savevia.user.service.AuthService;
import com.savevia.user.service.FileStorageService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/v1/users/me")
@RequiredArgsConstructor
public class UserProfileController {

    private final AuthService authService;
    private final FileStorageService fileStorageService;

    /**
     * Get current user profile
     */
    @GetMapping
    public Result<UserDTO> getCurrentUser(@RequestHeader("X-User-Id") Long userId) {
        return Result.success(authService.getUserById(userId));
    }

    /**
     * Upload and update user avatar
     */
    @PostMapping("/avatar")
    public Result<UserDTO> uploadAvatar(
            @RequestHeader("X-User-Id") Long userId,
            @RequestParam("file") MultipartFile file) {
        // Store file and get URL
        String avatarUrl = fileStorageService.storeAvatar(userId, file);
        // Update user's avatar URL in database
        return Result.success("Avatar updated", authService.updateAvatar(userId, avatarUrl));
    }

    /**
     * Delete user account (soft delete) - requires password verification
     */
    @DeleteMapping
    public Result<String> deleteAccount(
            @RequestHeader("X-User-Id") Long userId,
            @RequestBody java.util.Map<String, String> request) {
        String password = request.get("password");
        authService.deleteAccount(userId, password);
        return Result.success("Account deleted", null);
    }
}
