package com.savevia.optimizer.entity;

import java.time.LocalDateTime;

public class ConnectionHistory {
    private Long id;
    private Long userId;
    private String institutionName;
    private String action;  // CONNECT, DISCONNECT, REFRESH
    private String flinksLoginId;
    private LocalDateTime createdAt;

    // Getters and Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getUserId() {
        return userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }

    public String getInstitutionName() {
        return institutionName;
    }

    public void setInstitutionName(String institutionName) {
        this.institutionName = institutionName;
    }

    public String getAction() {
        return action;
    }

    public void setAction(String action) {
        this.action = action;
    }

    public String getFlinksLoginId() {
        return flinksLoginId;
    }

    public void setFlinksLoginId(String flinksLoginId) {
        this.flinksLoginId = flinksLoginId;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
}
