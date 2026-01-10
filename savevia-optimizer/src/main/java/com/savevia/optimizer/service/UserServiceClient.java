package com.savevia.optimizer.service;

import com.savevia.common.response.Result;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@FeignClient(name = "savevia-user", path = "/api/v1/users", contextId = "userServiceClient")
public interface UserServiceClient {

    @GetMapping("/ai-usage/check/{userId}")
    Result<Boolean> checkCanUseAi(@PathVariable("userId") Long userId);

    @PostMapping("/ai-usage/record/{userId}")
    Result<Boolean> recordAiUsage(@PathVariable("userId") Long userId);

    @GetMapping("/ai-usage/chat/check/{userId}")
    Result<Boolean> checkCanUseChat(@PathVariable("userId") Long userId);

    @PostMapping("/ai-usage/chat/record/{userId}")
    Result<Boolean> recordChatUsage(@PathVariable("userId") Long userId);

    @GetMapping("/me/cards")
    Result<List<Long>> getUserCardIds(@RequestHeader("X-User-Id") Long userId);
}
