package com.mentalhealth.platform.controller;

import com.mentalhealth.platform.common.ApiResponse;
import com.mentalhealth.platform.service.DashboardService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/dashboard")
@RequiredArgsConstructor
public class DashboardController {
    private final DashboardService dashboardService;

    @GetMapping("/summary")
    public ApiResponse<?> summary() {
        return ApiResponse.success(dashboardService.summary());
    }
}
