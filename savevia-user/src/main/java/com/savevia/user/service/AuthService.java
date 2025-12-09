package com.savevia.user.service;

import com.savevia.common.exception.BusinessException;
import com.savevia.common.exception.ErrorCode;
import com.savevia.user.dto.*;
import com.savevia.user.entity.User;
import com.savevia.user.mapper.UserMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class AuthService {

    private static final int PASSWORD_RESET_EXPIRY_HOURS = 1;
    private static final int EMAIL_VERIFICATION_EXPIRY_HOURS = 24;

    private final UserMapper userMapper;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;
    private final GoogleAuthService googleAuthService;
    private final AppleAuthService appleAuthService;
    private final EmailService emailService;

    @Transactional
    public UserDTO register(RegisterRequest request) {
        // Check if email already exists
        if (userMapper.countByEmail(request.getEmail()) > 0) {
            throw new BusinessException(ErrorCode.USER_ALREADY_EXISTS);
        }

        // Create new user
        LocalDateTime now = LocalDateTime.now(ZoneOffset.UTC);
        User user = User.builder()
                .email(request.getEmail().toLowerCase())
                .passwordHash(passwordEncoder.encode(request.getPassword()))
                .name(request.getName())
                .isActive(true)
                .createdAt(now)
                .updatedAt(now)
                .build();

        userMapper.insert(user);
        log.info("User registered: {}", user.getEmail());

        return toDTO(user);
    }

    public LoginResponse login(LoginRequest request) {
        // Find user by email
        User user = userMapper.selectByEmail(request.getEmail().toLowerCase())
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));

        // Verify password
        if (!passwordEncoder.matches(request.getPassword(), user.getPasswordHash())) {
            throw new BusinessException(ErrorCode.INVALID_PASSWORD);
        }

        // Generate JWT token
        String token = jwtService.generateToken(user.getId(), user.getEmail());

        log.info("User logged in: {}", user.getEmail());

        return LoginResponse.of(token, jwtService.getExpiration(), toDTO(user));
    }

    @Transactional
    public LoginResponse loginWithGoogle(String credential) {
        // Verify Google token
        GoogleAuthService.GoogleUserInfo googleUser = googleAuthService.verifyToken(credential);

        // Check if user exists by Google ID
        User user = userMapper.selectByGoogleId(googleUser.googleId())
                .orElseGet(() -> {
                    // Check if email already exists (user registered with email/password)
                    return userMapper.selectByEmail(googleUser.email().toLowerCase())
                            .map(existingUser -> {
                                // Link Google account to existing user
                                existingUser.setGoogleId(googleUser.googleId());
                                existingUser.setAvatarUrl(googleUser.pictureUrl());
                                userMapper.update(existingUser);
                                log.info("Linked Google account to existing user: {}", existingUser.getEmail());
                                return existingUser;
                            })
                            .orElseGet(() -> {
                                // Create new user
                                LocalDateTime now = LocalDateTime.now(ZoneOffset.UTC);
                                User newUser = User.builder()
                                        .email(googleUser.email().toLowerCase())
                                        .name(googleUser.name())
                                        .googleId(googleUser.googleId())
                                        .avatarUrl(googleUser.pictureUrl())
                                        .isActive(true)
                                        .createdAt(now)
                                        .updatedAt(now)
                                        .build();
                                userMapper.insert(newUser);
                                log.info("Created new user via Google: {}", newUser.getEmail());
                                return newUser;
                            });
                });

        // Generate JWT token
        String token = jwtService.generateToken(user.getId(), user.getEmail());
        log.info("User logged in via Google: {}", user.getEmail());

        return LoginResponse.of(token, jwtService.getExpiration(), toDTO(user));
    }

    @Transactional
    public LoginResponse loginWithApple(String identityToken, String fullName) {
        // Verify Apple token
        AppleAuthService.AppleUserInfo appleUser = appleAuthService.verifyToken(identityToken);

        // Check if user exists by Apple ID
        User user = userMapper.selectByAppleId(appleUser.appleId())
                .orElseGet(() -> {
                    // Check if email already exists (user registered with email/password or Google)
                    return userMapper.selectByEmail(appleUser.email().toLowerCase())
                            .map(existingUser -> {
                                // Link Apple account to existing user
                                existingUser.setAppleId(appleUser.appleId());
                                userMapper.update(existingUser);
                                log.info("Linked Apple account to existing user: {}", existingUser.getEmail());
                                return existingUser;
                            })
                            .orElseGet(() -> {
                                // Create new user
                                LocalDateTime now = LocalDateTime.now(ZoneOffset.UTC);
                                // Use full name from Apple or email prefix as fallback
                                String userName = (fullName != null && !fullName.isBlank())
                                        ? fullName
                                        : appleUser.email().split("@")[0];

                                User newUser = User.builder()
                                        .email(appleUser.email().toLowerCase())
                                        .name(userName)
                                        .appleId(appleUser.appleId())
                                        .emailVerified(appleUser.emailVerified())
                                        .isActive(true)
                                        .createdAt(now)
                                        .updatedAt(now)
                                        .build();
                                userMapper.insert(newUser);
                                log.info("Created new user via Apple: {}", newUser.getEmail());
                                return newUser;
                            });
                });

        // Generate JWT token
        String token = jwtService.generateToken(user.getId(), user.getEmail());
        log.info("User logged in via Apple: {}", user.getEmail());

        return LoginResponse.of(token, jwtService.getExpiration(), toDTO(user));
    }

    @Transactional
    public UserDTO updateAvatar(Long userId, String avatarUrl) {
        User user = userMapper.selectById(userId);
        if (user == null) {
            throw new BusinessException(ErrorCode.USER_NOT_FOUND);
        }

        user.setAvatarUrl(avatarUrl);
        user.setUpdatedAt(LocalDateTime.now(ZoneOffset.UTC));
        userMapper.update(user);

        log.info("User avatar updated: {}", user.getEmail());
        return toDTO(user);
    }

    public UserDTO getUserById(Long userId) {
        User user = userMapper.selectById(userId);
        if (user == null) {
            throw new BusinessException(ErrorCode.USER_NOT_FOUND);
        }
        return toDTO(user);
    }

    @Transactional
    public void deleteAccount(Long userId, String password) {
        User user = userMapper.selectById(userId);
        if (user == null) {
            throw new BusinessException(ErrorCode.USER_NOT_FOUND);
        }

        // For users with password (non-OAuth only users), verify password
        if (user.getPasswordHash() != null) {
            if (password == null || password.isEmpty()) {
                throw new BusinessException(ErrorCode.INVALID_PASSWORD, "Password is required");
            }
            if (!passwordEncoder.matches(password, user.getPasswordHash())) {
                throw new BusinessException(ErrorCode.INVALID_PASSWORD);
            }
        }

        userMapper.deleteById(userId);
        log.info("User account deleted: {}", user.getEmail());
    }

    /**
     * Change password for logged-in user
     */
    @Transactional
    public void changePassword(Long userId, String currentPassword, String newPassword) {
        User user = userMapper.selectById(userId);
        if (user == null) {
            throw new BusinessException(ErrorCode.USER_NOT_FOUND);
        }

        // User must have a password set (not OAuth-only user)
        if (user.getPasswordHash() == null) {
            throw new BusinessException(ErrorCode.INVALID_PASSWORD, "No password set for this account. Use 'Set Password' instead.");
        }

        // Verify current password
        if (!passwordEncoder.matches(currentPassword, user.getPasswordHash())) {
            throw new BusinessException(ErrorCode.INVALID_PASSWORD, "Current password is incorrect");
        }

        // Update password
        user.setPasswordHash(passwordEncoder.encode(newPassword));
        user.setUpdatedAt(LocalDateTime.now(ZoneOffset.UTC));
        userMapper.update(user);

        log.info("Password changed for user: {}", user.getEmail());
    }

    /**
     * Set password for OAuth-only user
     */
    @Transactional
    public void setPassword(Long userId, String newPassword) {
        User user = userMapper.selectById(userId);
        if (user == null) {
            throw new BusinessException(ErrorCode.USER_NOT_FOUND);
        }

        // User must NOT have a password set (OAuth-only user)
        if (user.getPasswordHash() != null) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "Password already set. Use 'Change Password' instead.");
        }

        // Set password
        user.setPasswordHash(passwordEncoder.encode(newPassword));
        user.setUpdatedAt(LocalDateTime.now(ZoneOffset.UTC));
        userMapper.update(user);

        log.info("Password set for OAuth user: {}", user.getEmail());
    }

    /**
     * Send password reset email
     */
    @Transactional
    public void forgotPassword(String email) {
        User user = userMapper.selectByEmail(email.toLowerCase()).orElse(null);

        // Always return success to prevent email enumeration attacks
        if (user == null) {
            log.info("Password reset requested for non-existent email: {}", email);
            return;
        }

        // Generate reset token
        String token = UUID.randomUUID().toString().replace("-", "");
        LocalDateTime expiresAt = LocalDateTime.now(ZoneOffset.UTC).plusHours(PASSWORD_RESET_EXPIRY_HOURS);

        user.setPasswordResetToken(token);
        user.setPasswordResetExpiresAt(expiresAt);
        user.setUpdatedAt(LocalDateTime.now(ZoneOffset.UTC));
        userMapper.update(user);

        // Send email asynchronously
        emailService.sendPasswordResetEmail(user.getEmail(), token);
        log.info("Password reset email sent to: {}", user.getEmail());
    }

    /**
     * Reset password using token
     */
    @Transactional
    public void resetPassword(String token, String newPassword) {
        User user = userMapper.selectByPasswordResetToken(token)
                .orElseThrow(() -> new BusinessException(ErrorCode.TOKEN_INVALID, "Invalid or expired reset token"));

        // Check if token is expired
        if (user.getPasswordResetExpiresAt() == null ||
            user.getPasswordResetExpiresAt().isBefore(LocalDateTime.now(ZoneOffset.UTC))) {
            throw new BusinessException(ErrorCode.PASSWORD_RESET_TOKEN_EXPIRED);
        }

        // Update password and clear reset token
        user.setPasswordHash(passwordEncoder.encode(newPassword));
        userMapper.update(user);
        userMapper.clearPasswordResetToken(user.getId());

        log.info("Password reset successful for user: {}", user.getEmail());
    }

    /**
     * Send email verification (for new users or resend)
     */
    @Transactional
    public void sendEmailVerification(Long userId) {
        User user = userMapper.selectById(userId);
        if (user == null) {
            throw new BusinessException(ErrorCode.USER_NOT_FOUND);
        }

        if (Boolean.TRUE.equals(user.getEmailVerified())) {
            throw new BusinessException(ErrorCode.EMAIL_ALREADY_VERIFIED);
        }

        // Generate verification token
        String token = UUID.randomUUID().toString().replace("-", "");
        LocalDateTime expiresAt = LocalDateTime.now(ZoneOffset.UTC).plusHours(EMAIL_VERIFICATION_EXPIRY_HOURS);

        user.setEmailVerificationToken(token);
        user.setEmailVerificationExpiresAt(expiresAt);
        user.setUpdatedAt(LocalDateTime.now(ZoneOffset.UTC));
        userMapper.update(user);

        // Send email asynchronously
        emailService.sendEmailVerificationEmail(user.getEmail(), token);
        log.info("Email verification sent to: {}", user.getEmail());
    }

    /**
     * Verify email using token
     */
    @Transactional
    public void verifyEmail(String token) {
        User user = userMapper.selectByEmailVerificationToken(token)
                .orElseThrow(() -> new BusinessException(ErrorCode.TOKEN_INVALID, "Invalid or expired verification token"));

        // Check if token is expired
        if (user.getEmailVerificationExpiresAt() == null ||
            user.getEmailVerificationExpiresAt().isBefore(LocalDateTime.now(ZoneOffset.UTC))) {
            throw new BusinessException(ErrorCode.EMAIL_VERIFICATION_TOKEN_EXPIRED);
        }

        // Mark email as verified and clear token
        userMapper.clearEmailVerificationToken(user.getId());
        log.info("Email verified for user: {}", user.getEmail());
    }

    private UserDTO toDTO(User user) {
        return UserDTO.builder()
                .id(user.getId())
                .email(user.getEmail())
                .name(user.getName())
                .avatarUrl(user.getAvatarUrl())
                .createdAt(user.getCreatedAt())
                .hasPassword(user.getPasswordHash() != null)
                .emailVerified(Boolean.TRUE.equals(user.getEmailVerified()))
                .build();
    }
}
