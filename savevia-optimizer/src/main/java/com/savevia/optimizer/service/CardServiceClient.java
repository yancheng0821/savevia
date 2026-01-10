package com.savevia.optimizer.service;

import com.savevia.common.response.Result;
import com.savevia.optimizer.dto.CardUsageGuideDTO;
import com.savevia.optimizer.dto.CreditCardDTO;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;

import java.util.List;

@FeignClient(name = "savevia-card", path = "/api/v1/cards")
public interface CardServiceClient {

    @PostMapping("/batch")
    Result<List<CreditCardDTO>> getCardsByIds(@RequestBody List<Long> ids);

    @GetMapping
    Result<List<CreditCardDTO>> getAllCards();

    @GetMapping("/{id}/usage-guide")
    Result<CardUsageGuideDTO> getCardUsageGuide(
            @PathVariable("id") Long id,
            @RequestParam(value = "lang", defaultValue = "en") String lang);
}
