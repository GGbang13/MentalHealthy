package com.mentalhealth.platform.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

import java.math.BigDecimal;

@Data
public class RegisterRequest {
    @NotBlank(message = "用户名不能为空")
    private String username;
    @NotBlank(message = "密码不能为空")
    private String password;
    @Email(message = "邮箱格式不正确")
    private String email;
    private String phone;
    private String nickname;
    private String role;
    private String title;
    private String specialties;
    private Integer yearsOfExperience;
    private String introduction;
    private BigDecimal pricePerHour;
}
