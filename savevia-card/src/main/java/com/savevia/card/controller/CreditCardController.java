package com.savevia.card.controller;

import com.savevia.card.dto.CreditCardDTO;
import com.savevia.card.service.CreditCardService;
import com.savevia.common.response.Result;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/cards")
@RequiredArgsConstructor
public class CreditCardController {

    private final CreditCardService creditCardService;

    @GetMapping
    public Result<List<CreditCardDTO>> getAllCards() {
        return Result.success(creditCardService.getAllCards());
    }

    @GetMapping("/{id}")
    public Result<CreditCardDTO> getCardById(@PathVariable Long id) {
        return Result.success(creditCardService.getCardById(id));
    }

    @GetMapping("/bank/{bank}")
    public Result<List<CreditCardDTO>> getCardsByBank(@PathVariable String bank) {
        return Result.success(creditCardService.getCardsByBank(bank));
    }

    @PostMapping("/batch")
    public Result<List<CreditCardDTO>> getCardsByIds(@RequestBody List<Long> ids) {
        return Result.success(creditCardService.getCardsByIds(ids));
    }
}
