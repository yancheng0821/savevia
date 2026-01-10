package com.savevia.optimizer.service;

import com.savevia.common.response.Result;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;

import java.util.Map;

@FeignClient(name = "savevia-user", path = "/api/v1/admin", contextId = "adminServiceClient")
public interface AdminServiceClient {

    @PostMapping("/track")
    Result<Void> trackEvent(
            @RequestBody Map<String, String> request,
            @RequestHeader(value = "X-User-Id", required = false) Long userId
    );
}
