package com.mentalhealth.platform.service;

import com.mentalhealth.platform.dto.ForgotPasswordRequest;
import com.mentalhealth.platform.dto.LoginRequest;
import com.mentalhealth.platform.dto.RegisterRequest;
import com.mentalhealth.platform.vo.LoginResponse;

public interface AuthService {
    LoginResponse login(LoginRequest request);
    void register(RegisterRequest request);
    void resetPassword(ForgotPasswordRequest request);
}
