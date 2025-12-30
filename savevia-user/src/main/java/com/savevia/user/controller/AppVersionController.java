package com.savevia.user.controller;

import com.savevia.common.response.Result;
import lombok.Data;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/app")
public class AppVersionController {

    @Value("${app.version.latest:1.0.2}")
    private String latestVersion;

    @Value("${app.version.min:1.0.0}")
    private String minVersion;

    @Value("${app.version.ios-store-url:https://apps.apple.com/app/id6756332569}")
    private String iosStoreUrl;

    @Value("${app.version.android-store-url:https://play.google.com/store/apps/details?id=app.savevia}")
    private String androidStoreUrl;

    @GetMapping("/version")
    public Result<AppVersionResponse> getVersion() {
        AppVersionResponse response = new AppVersionResponse();
        response.setLatestVersion(latestVersion);
        response.setMinVersion(minVersion);
        response.setIosStoreUrl(iosStoreUrl);
        response.setAndroidStoreUrl(androidStoreUrl);
        return Result.success(response);
    }

    @Data
    public static class AppVersionResponse {
        private String latestVersion;
        private String minVersion;
        private String iosStoreUrl;
        private String androidStoreUrl;
    }
}
