package com.mentalhealth.platform.controller;

import com.mentalhealth.platform.common.ApiResponse;
import com.mentalhealth.platform.dto.AssessmentSubmitRequest;
import com.mentalhealth.platform.service.AssessmentService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/assessments")
@RequiredArgsConstructor
public class AssessmentController {
    private final AssessmentService assessmentService;

    @GetMapping("/scales")
    public ApiResponse<?> scales() {
        return ApiResponse.success(assessmentService.listScales());
    }

    @PostMapping("/submit")
    public ApiResponse<?> submit(Authentication authentication, @RequestBody @Valid AssessmentSubmitRequest request) {
        Long userId = (Long) authentication.getPrincipal();
        return ApiResponse.success("提交成功", assessmentService.submit(userId, request));
    }

    @GetMapping("/history")
    public ApiResponse<?> history(Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        return ApiResponse.success(assessmentService.history(userId));
    }

    @GetMapping("/admin/records")
    public ApiResponse<?> adminRecords(Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        return ApiResponse.success(assessmentService.adminRecords(userId));
    }
}
