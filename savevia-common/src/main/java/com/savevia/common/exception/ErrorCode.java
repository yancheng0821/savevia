package com.savevia.common.exception;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public enum ErrorCode {

    // Common errors
    SUCCESS(200, "Success"),
    BAD_REQUEST(400, "Bad request"),
    UNAUTHORIZED(401, "Unauthorized"),
    FORBIDDEN(403, "Forbidden"),
    NOT_FOUND(404, "Resource not found"),
    INTERNAL_ERROR(500, "Internal server error"),

    // User errors (1xxx)
    USER_NOT_FOUND(1001, "User not found"),
    USER_ALREADY_EXISTS(1002, "User already exists"),
    INVALID_PASSWORD(1003, "Invalid password"),
    TOKEN_EXPIRED(1004, "Token expired"),
    TOKEN_INVALID(1005, "Invalid token"),
    GOOGLE_AUTH_FAILED(1006, "Google authentication failed"),
    APPLE_AUTH_FAILED(1007, "Apple authentication failed"),
    PASSWORD_RESET_TOKEN_EXPIRED(1008, "Password reset token has expired"),
    EMAIL_VERIFICATION_TOKEN_EXPIRED(1009, "Email verification token has expired"),
    EMAIL_NOT_VERIFIED(1010, "Email not verified"),
    EMAIL_ALREADY_VERIFIED(1011, "Email already verified"),

    // Card errors (2xxx)
    CARD_NOT_FOUND(2001, "Credit card not found"),
    INVALID_CARD_RULE(2002, "Invalid card rule"),

    // Optimizer errors (3xxx)
    NO_CARDS_SELECTED(3001, "No cards selected for optimization"),
    INVALID_SPENDING_DATA(3002, "Invalid spending data"),

    // Bank errors (4xxx)
    BANK_CONNECTION_FAILED(4001, "Failed to connect to bank"),
    TRANSACTION_FETCH_FAILED(4002, "Failed to fetch transactions");

    private final int code;
    private final String message;
}
