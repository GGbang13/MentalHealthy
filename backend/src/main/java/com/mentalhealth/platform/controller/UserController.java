package com.mentalhealth.platform.controller;

import com.mentalhealth.platform.common.ApiResponse;
import com.mentalhealth.platform.service.UserService;
import com.mentalhealth.platform.vo.UserVO;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {
    private final UserService userService;

    @GetMapping("/me")
    public ApiResponse<UserVO> profile(Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        return ApiResponse.success(userService.getProfile(userId));
    }

    @PutMapping("/me")
    public ApiResponse<Void> updateProfile(Authentication authentication, @RequestBody UserVO request) {
        Long userId = (Long) authentication.getPrincipal();
        userService.updateProfile(userId, request);
        return ApiResponse.success("更新成功", null);
    }

    @GetMapping("/notifications")
    public ApiResponse<?> notifications(Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        return ApiResponse.success(userService.listNotifications(userId));
    }
}
