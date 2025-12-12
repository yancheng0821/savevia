package com.savevia.user.service;

import com.savevia.common.exception.BusinessException;
import com.savevia.common.exception.ErrorCode;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider;
import software.amazon.awssdk.core.sync.RequestBody;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.*;

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

    @Value("${file.storage-type:local}")
    private String storageType;

    @Value("${aws.s3.bucket:}")
    private String s3Bucket;

    @Value("${aws.s3.region:ca-central-1}")
    private String s3Region;

    @Value("${aws.s3.base-url:}")
    private String s3BaseUrl;

    private S3Client s3Client;

    private static final Set<String> ALLOWED_CONTENT_TYPES = Set.of(
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/webp"
    );

    private static final long MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB

    @PostConstruct
    public void init() {
        if ("s3".equalsIgnoreCase(storageType)) {
            initS3Client();
        } else {
            initLocalStorage();
        }
    }

    private void initS3Client() {
        try {
            s3Client = S3Client.builder()
                    .region(Region.of(s3Region))
                    .credentialsProvider(DefaultCredentialsProvider.create())
                    .build();
            log.info("S3 storage initialized: bucket={}, region={}", s3Bucket, s3Region);
        } catch (Exception e) {
            log.error("Failed to initialize S3 client, falling back to local storage", e);
            storageType = "local";
            initLocalStorage();
        }
    }

    private void initLocalStorage() {
        try {
            Path uploadPath = Paths.get(uploadDir, "avatars");
            Files.createDirectories(uploadPath);
            log.info("Local upload directory initialized: {}", uploadPath.toAbsolutePath());
        } catch (IOException e) {
            throw new RuntimeException("Could not create upload directory", e);
        }
    }

    public String storeAvatar(Long userId, MultipartFile file) {
        // Validate file
        validateFile(file);

        // Generate unique filename
        String contentType = file.getContentType();
        String extension = getExtension(contentType);
        String filename = String.format("avatar_%d_%s%s", userId, UUID.randomUUID().toString().substring(0, 8), extension);

        if ("s3".equalsIgnoreCase(storageType)) {
            return storeToS3(userId, file, filename, contentType);
        } else {
            return storeToLocal(userId, file, filename);
        }
    }

    private void validateFile(MultipartFile file) {
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
    }

    private String storeToS3(Long userId, MultipartFile file, String filename, String contentType) {
        try {
            String key = "avatars/" + filename;

            // Delete old avatars for this user
            deleteOldAvatarsFromS3(userId);

            // Upload to S3
            PutObjectRequest putRequest = PutObjectRequest.builder()
                    .bucket(s3Bucket)
                    .key(key)
                    .contentType(contentType)
                    .cacheControl("public, max-age=31536000")
                    .build();

            s3Client.putObject(putRequest, RequestBody.fromInputStream(file.getInputStream(), file.getSize()));
            log.info("Avatar uploaded to S3: {} for user {}", key, userId);

            // Return CloudFront URL or S3 URL
            if (s3BaseUrl != null && !s3BaseUrl.isEmpty()) {
                return s3BaseUrl + "/" + key;
            }
            return String.format("https://%s.s3.%s.amazonaws.com/%s", s3Bucket, s3Region, key);

        } catch (Exception e) {
            log.error("Failed to upload avatar to S3 for user {}", userId, e);
            throw new BusinessException(ErrorCode.INTERNAL_ERROR, "Failed to store avatar");
        }
    }

    private void deleteOldAvatarsFromS3(Long userId) {
        try {
            String prefix = "avatars/avatar_" + userId + "_";

            ListObjectsV2Request listRequest = ListObjectsV2Request.builder()
                    .bucket(s3Bucket)
                    .prefix(prefix)
                    .build();

            ListObjectsV2Response listResponse = s3Client.listObjectsV2(listRequest);

            for (S3Object object : listResponse.contents()) {
                DeleteObjectRequest deleteRequest = DeleteObjectRequest.builder()
                        .bucket(s3Bucket)
                        .key(object.key())
                        .build();
                s3Client.deleteObject(deleteRequest);
                log.info("Deleted old avatar from S3: {}", object.key());
            }
        } catch (Exception e) {
            log.warn("Failed to delete old avatars from S3 for user {}", userId, e);
        }
    }

    private String storeToLocal(Long userId, MultipartFile file, String filename) {
        try {
            Path avatarsDir = Paths.get(uploadDir, "avatars");
            Path targetPath = avatarsDir.resolve(filename);

            // Delete old avatar files for this user
            deleteOldAvatarsFromLocal(avatarsDir, userId);

            // Save new file
            Files.copy(file.getInputStream(), targetPath, StandardCopyOption.REPLACE_EXISTING);
            log.info("Avatar saved locally: {} for user {}", filename, userId);

            return "/uploads/avatars/" + filename;

        } catch (IOException e) {
            log.error("Failed to store avatar locally for user {}", userId, e);
            throw new BusinessException(ErrorCode.INTERNAL_ERROR, "Failed to store avatar");
        }
    }

    private void deleteOldAvatarsFromLocal(Path avatarsDir, Long userId) {
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
