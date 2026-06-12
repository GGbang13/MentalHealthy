package com.mentalhealth.platform.controller;

import com.mentalhealth.platform.common.ApiResponse;
import com.mentalhealth.platform.dto.AdminUserRequest;
import com.mentalhealth.platform.dto.DeleteUserRequest;
import com.mentalhealth.platform.dto.NotificationRequest;
import com.mentalhealth.platform.service.AdminService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/admin")
@RequiredArgsConstructor
public class AdminController {
    private final AdminService adminService;

    @GetMapping("/users")
    public ApiResponse<?> pageUsers(Authentication authentication,
                                    @RequestParam(required = false) String role,
                                    @RequestParam(required = false) String keyword,
                                    @RequestParam(defaultValue = "1") long current,
                                    @RequestParam(defaultValue = "10") long size) {
        Long userId = (Long) authentication.getPrincipal();
        return ApiResponse.success(adminService.pageUsers(userId, role, keyword, current, size));
    }

    @PostMapping("/users")
    public ApiResponse<?> createUser(Authentication authentication, @RequestBody @Valid AdminUserRequest request) {
        Long userId = (Long) authentication.getPrincipal();
        return ApiResponse.success("账号已创建", adminService.createUser(userId, request));
    }

    @PutMapping("/users/{id}")
    public ApiResponse<?> updateUser(Authentication authentication,
                                     @PathVariable Long id,
                                     @RequestBody @Valid AdminUserRequest request) {
        Long userId = (Long) authentication.getPrincipal();
        return ApiResponse.success("账号已更新", adminService.updateUser(userId, id, request));
    }

    @DeleteMapping("/users/{id}")
    public ApiResponse<Void> deleteUser(Authentication authentication,
                                        @PathVariable Long id,
                                        @RequestBody @Valid DeleteUserRequest request) {
        Long userId = (Long) authentication.getPrincipal();
        adminService.deleteUser(userId, id, request);
        return ApiResponse.success("账号已删除", null);
    }

    @GetMapping("/notifications")
    public ApiResponse<?> listNotifications(Authentication authentication,
                                            @RequestParam(required = false) String targetRole) {
        Long userId = (Long) authentication.getPrincipal();
        return ApiResponse.success(adminService.listNotifications(userId, targetRole));
    }

    @PostMapping("/notifications")
    public ApiResponse<?> createNotification(Authentication authentication,
                                             @RequestBody NotificationRequest request) {
        Long userId = (Long) authentication.getPrincipal();
        return ApiResponse.success("通知已发布", adminService.createNotification(userId, request));
    }
}
