package com.savevia.user.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class EmailService {

    private final JavaMailSender mailSender;

    @Value("${spring.mail.username:noreply@savevia.com}")
    private String fromEmail;

    @Value("${app.frontend-url:http://localhost:5173}")
    private String frontendUrl;

    @Async
    public void sendPasswordResetEmail(String toEmail, String token) {
        try {
            String resetUrl = frontendUrl + "/reset-password?token=" + token;

            SimpleMailMessage message = new SimpleMailMessage();
            message.setFrom(fromEmail);
            message.setTo(toEmail);
            message.setSubject("Reset Your SaveVia Password");
            message.setText(buildPasswordResetEmailBody(resetUrl));

            mailSender.send(message);
            log.info("Password reset email sent to: {}", toEmail);
        } catch (Exception e) {
            log.error("Failed to send password reset email to: {}", toEmail, e);
        }
    }

    @Async
    public void sendEmailVerificationEmail(String toEmail, String token) {
        try {
            String verifyUrl = frontendUrl + "/verify-email?token=" + token;

            SimpleMailMessage message = new SimpleMailMessage();
            message.setFrom(fromEmail);
            message.setTo(toEmail);
            message.setSubject("Verify Your SaveVia Email");
            message.setText(buildEmailVerificationBody(verifyUrl));

            mailSender.send(message);
            log.info("Email verification sent to: {}", toEmail);
        } catch (Exception e) {
            log.error("Failed to send verification email to: {}", toEmail, e);
        }
    }

    private String buildPasswordResetEmailBody(String resetUrl) {
        return """
            Hi,

            You requested to reset your password for SaveVia.

            Click the link below to reset your password:
            %s

            This link will expire in 1 hour.

            If you didn't request this, please ignore this email.

            Best regards,
            The SaveVia Team
            """.formatted(resetUrl);
    }

    private String buildEmailVerificationBody(String verifyUrl) {
        return """
            Welcome to SaveVia!

            Please verify your email address by clicking the link below:
            %s

            This link will expire in 24 hours.

            If you didn't create an account, please ignore this email.

            Best regards,
            The SaveVia Team
            """.formatted(verifyUrl);
    }
}
