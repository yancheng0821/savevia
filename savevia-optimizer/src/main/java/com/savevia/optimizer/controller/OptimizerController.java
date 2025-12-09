package com.savevia.optimizer.controller;

import com.savevia.common.response.Result;
import com.savevia.optimizer.dto.OptimizationRequest;
import com.savevia.optimizer.dto.OptimizationResult;
import com.savevia.optimizer.service.CashbackOptimizerService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/optimize")
@RequiredArgsConstructor
public class OptimizerController {

    private final CashbackOptimizerService optimizerService;

    @PostMapping("/calculate")
    public Result<OptimizationResult> calculate(@Valid @RequestBody OptimizationRequest request) {
        return Result.success(optimizerService.optimize(request));
    }
}
