package com.savevia.optimizer.controller;

import com.savevia.common.response.Result;
import com.savevia.optimizer.dto.OptimizationResult;
import com.savevia.optimizer.dto.SaveResultRequest;
import com.savevia.optimizer.dto.SaveResultResponse;
import com.savevia.optimizer.service.SavedResultService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/optimize")
@RequiredArgsConstructor
public class SavedResultController {

    @Value("${app.frontend-url:https://savevia.app}")
    private String frontendUrl;

    private final SavedResultService savedResultService;

    /**
     * Save/share optimization result
     */
    @PostMapping("/share")
    public Result<SaveResultResponse> shareResult(
            @RequestHeader(value = "X-User-Id", required = false) Long userId,
            @Valid @RequestBody SaveResultRequest request) {
        SaveResultResponse response = savedResultService.saveResult(request.getResult(), userId);
        return Result.success(response);
    }

    /**
     * Get shared result by shareId
     */
    @GetMapping("/share/{shareId}")
    public Result<OptimizationResult> getSharedResult(@PathVariable String shareId) {
        OptimizationResult result = savedResultService.getByShareId(shareId);
        if (result == null) {
            return Result.error(404, "Shared result not found or expired");
        }
        return Result.success(result);
    }

    /**
     * OG meta tags page for social media crawlers
     * This returns an HTML page with proper Open Graph tags that redirects to the SPA
     */
    @GetMapping(value = "/share/{shareId}/og", produces = MediaType.TEXT_HTML_VALUE)
    @ResponseBody
    public String getShareOgPage(@PathVariable String shareId, HttpServletRequest request) {
        OptimizationResult result = savedResultService.getByShareId(shareId);

        String title = "SaveVia - Credit Card Cashback Optimizer";
        String description = "Optimize your credit card rewards with SaveVia";
        String savings = "0";

        if (result != null && result.getNetAnnualSavings() != null) {
            savings = result.getNetAnnualSavings().setScale(0, java.math.RoundingMode.HALF_UP).toString();
            title = "I'm saving $" + savings + "/year with SaveVia!";
            description = "I optimized my credit card rewards and I'm saving $" + savings + " per year. Try SaveVia for free!";
        }

        String shareUrl = frontendUrl + "/share/" + shareId;
        String logoUrl = frontendUrl + "/logo-og.png";

        return """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>%s</title>

                <!-- Open Graph / Facebook -->
                <meta property="og:type" content="website">
                <meta property="og:url" content="%s">
                <meta property="og:title" content="%s">
                <meta property="og:description" content="%s">
                <meta property="og:image" content="%s">
                <meta property="og:site_name" content="SaveVia">

                <!-- Twitter -->
                <meta name="twitter:card" content="summary_large_image">
                <meta name="twitter:url" content="%s">
                <meta name="twitter:title" content="%s">
                <meta name="twitter:description" content="%s">
                <meta name="twitter:image" content="%s">

                <!-- Redirect to SPA -->
                <meta http-equiv="refresh" content="0;url=%s">
                <link rel="canonical" href="%s">
            </head>
            <body>
                <p>Redirecting to <a href="%s">SaveVia</a>...</p>
                <script>window.location.href = "%s";</script>
            </body>
            </html>
            """.formatted(
                title,
                shareUrl, title, description, logoUrl,
                shareUrl, title, description, logoUrl,
                shareUrl, shareUrl,
                shareUrl, shareUrl
            );
    }

    /**
     * Save user's current optimization result
     */
    @PostMapping("/user-result")
    public Result<Void> saveUserResult(
            @RequestHeader(value = "X-User-Id", required = false) Long userId,
            @Valid @RequestBody SaveResultRequest request) {
        if (userId == null) {
            return Result.error(401, "User not authenticated");
        }
        savedResultService.saveUserResult(request.getResult(), userId);
        return Result.success(null);
    }

    /**
     * Get user's latest optimization result
     */
    @GetMapping("/user-result")
    public Result<OptimizationResult> getUserResult(
            @RequestHeader(value = "X-User-Id", required = false) Long userId) {
        if (userId == null) {
            return Result.error(401, "User not authenticated");
        }
        OptimizationResult result = savedResultService.getUserResult(userId);
        return Result.success(result);
    }
}
