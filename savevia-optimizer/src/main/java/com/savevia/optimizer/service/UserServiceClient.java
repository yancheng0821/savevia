package com.savevia.optimizer.service;

import com.savevia.common.response.Result;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;

@FeignClient(name = "savevia-user", path = "/api/v1/users/ai-usage")
public interface UserServiceClient {

    @GetMapping("/check/{userId}")
    Result<Boolean> checkCanUseAi(@PathVariable("userId") Long userId);

    @PostMapping("/record/{userId}")
    Result<Boolean> recordAiUsage(@PathVariable("userId") Long userId);
}
