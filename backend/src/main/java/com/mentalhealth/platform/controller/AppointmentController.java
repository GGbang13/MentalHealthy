package com.mentalhealth.platform.controller;

import com.mentalhealth.platform.common.ApiResponse;
import com.mentalhealth.platform.dto.AppointmentRequest;
import com.mentalhealth.platform.service.AppointmentService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/appointments")
@RequiredArgsConstructor
public class AppointmentController {
    private final AppointmentService appointmentService;

    @PostMapping
    public ApiResponse<?> create(Authentication authentication, @RequestBody @Valid AppointmentRequest request) {
        Long userId = (Long) authentication.getPrincipal();
        return ApiResponse.success("预约成功", appointmentService.create(userId, request));
    }

    @GetMapping
    public ApiResponse<?> list(Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        return ApiResponse.success(appointmentService.listByUser(userId));
    }

    @GetMapping("/counselor")
    public ApiResponse<?> counselorList(Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        return ApiResponse.success(appointmentService.listByCounselor(userId));
    }

    @PostMapping("/{id}/cancel")
    public ApiResponse<Void> cancel(Authentication authentication, @PathVariable Long id) {
        Long userId = (Long) authentication.getPrincipal();
        appointmentService.cancel(userId, id);
        return ApiResponse.success("已取消", null);
    }

    @PostMapping("/{id}/reschedule")
    public ApiResponse<Void> reschedule(Authentication authentication,
                                        @PathVariable Long id,
                                        @RequestBody @Valid AppointmentRequest request) {
        Long userId = (Long) authentication.getPrincipal();
        appointmentService.reschedule(userId, id, request);
        return ApiResponse.success("已改期", null);
    }

    @PostMapping("/{id}/confirm")
    public ApiResponse<Void> confirm(Authentication authentication, @PathVariable Long id) {
        Long userId = (Long) authentication.getPrincipal();
        appointmentService.confirm(userId, id);
        return ApiResponse.success("已同意预约", null);
    }

    @PostMapping("/{id}/reject")
    public ApiResponse<Void> reject(Authentication authentication, @PathVariable Long id) {
        Long userId = (Long) authentication.getPrincipal();
        appointmentService.reject(userId, id);
        return ApiResponse.success("已拒绝预约", null);
    }
}
