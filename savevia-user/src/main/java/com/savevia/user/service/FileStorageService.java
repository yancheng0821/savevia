package com.savevia.user.service;

import com.savevia.common.exception.BusinessException;
import com.savevia.common.exception.ErrorCode;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import jakarta.annotation.PostConstruct;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.Set;
import java.util.UUID;

@Slf4j
@Service
public class FileStorageService {

    @Value("${file.upload-dir:./uploads}")
    private String uploadDir;

    @Value("${file.base-url:}")
    private String baseUrl;

    private static final Set<String> ALLOWED_CONTENT_TYPES = Set.of(
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/webp"
    );

    private static final long MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB

    @PostConstruct
    public void init() {
        try {
            Path uploadPath = Paths.get(uploadDir, "avatars");
            Files.createDirectories(uploadPath);
            log.info("Upload directory initialized: {}", uploadPath.toAbsolutePath());
        } catch (IOException e) {
            throw new RuntimeException("Could not create upload directory", e);
        }
    }

    public String storeAvatar(Long userId, MultipartFile file) {
        // Validate file
        if (file.isEmpty()) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "File is empty");
        }

        if (file.getSize() > MAX_FILE_SIZE) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "File size exceeds 5MB limit");
        }

        String contentType = file.getContentType();
        if (contentType == null || !ALLOWED_CONTENT_TYPES.contains(contentType)) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "Invalid file type. Allowed: JPEG, PNG, GIF, WebP");
        }

        // Generate unique filename
        String extension = getExtension(contentType);
        String filename = String.format("avatar_%d_%s%s", userId, UUID.randomUUID().toString().substring(0, 8), extension);

        try {
            Path avatarsDir = Paths.get(uploadDir, "avatars");
            Path targetPath = avatarsDir.resolve(filename);

            // Delete old avatar files for this user
            deleteOldAvatars(avatarsDir, userId);

            // Save new file
            Files.copy(file.getInputStream(), targetPath, StandardCopyOption.REPLACE_EXISTING);
            log.info("Avatar saved: {} for user {}", filename, userId);

            // Return URL
            if (baseUrl != null && !baseUrl.isEmpty()) {
                return baseUrl + "/uploads/avatars/" + filename;
            }
            return "/uploads/avatars/" + filename;

        } catch (IOException e) {
            log.error("Failed to store avatar for user {}", userId, e);
            throw new BusinessException(ErrorCode.INTERNAL_ERROR, "Failed to store avatar");
        }
    }

    private void deleteOldAvatars(Path avatarsDir, Long userId) {
        try {
            String prefix = "avatar_" + userId + "_";
            Files.list(avatarsDir)
                    .filter(path -> path.getFileName().toString().startsWith(prefix))
                    .forEach(path -> {
                        try {
                            Files.delete(path);
                            log.info("Deleted old avatar: {}", path.getFileName());
                        } catch (IOException e) {
                            log.warn("Failed to delete old avatar: {}", path.getFileName());
                        }
                    });
        } catch (IOException e) {
            log.warn("Failed to list avatars directory", e);
        }
    }

    private String getExtension(String contentType) {
        return switch (contentType) {
            case "image/jpeg" -> ".jpg";
            case "image/png" -> ".png";
            case "image/gif" -> ".gif";
            case "image/webp" -> ".webp";
            default -> ".jpg";
        };
    }
}
