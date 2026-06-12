package com.mentalhealth.platform.controller;

import com.mentalhealth.platform.common.ApiResponse;
import com.mentalhealth.platform.dto.ForgotPasswordRequest;
import com.mentalhealth.platform.dto.LoginRequest;
import com.mentalhealth.platform.dto.RegisterRequest;
import com.mentalhealth.platform.service.AuthService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {
    private final AuthService authService;

    @PostMapping("/register")
    public ApiResponse<Void> register(@RequestBody @Valid RegisterRequest request) {
        authService.register(request);
        return ApiResponse.success("注册成功", null);
    }

    @PostMapping("/login")
    public ApiResponse<?> login(@RequestBody @Valid LoginRequest request) {
        return ApiResponse.success(authService.login(request));
    }

    @PostMapping("/forgot-password")
    public ApiResponse<Void> forgotPassword(@RequestBody @Valid ForgotPasswordRequest request) {
        authService.resetPassword(request);
        return ApiResponse.success("密码重置成功", null);
    }
}
