package com.mentalhealth.platform.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class AdminUserRequest {
    @NotBlank(message = "用户名不能为空")
    private String username;
    private String password;
    private String nickname;
    private String email;
    private String phone;
    @NotBlank(message = "角色不能为空")
    private String role;
    private Integer status;
    private String gender;
    private Integer age;
    private String profile;
    private String title;
    private String specialties;
}
