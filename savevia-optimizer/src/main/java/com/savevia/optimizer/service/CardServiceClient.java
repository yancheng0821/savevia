package com.savevia.optimizer.service;

import com.savevia.common.response.Result;
import com.savevia.optimizer.dto.CreditCardDTO;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;

import java.util.List;

@FeignClient(name = "savevia-card", path = "/api/v1/cards")
public interface CardServiceClient {

    @PostMapping("/batch")
    Result<List<CreditCardDTO>> getCardsByIds(@RequestBody List<Long> ids);
}
