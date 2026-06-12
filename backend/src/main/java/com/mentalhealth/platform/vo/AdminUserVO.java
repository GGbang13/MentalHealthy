package com.mentalhealth.platform.vo;

import lombok.Data;

@Data
public class AdminUserVO {
    private Long id;
    private String username;
    private String nickname;
    private String email;
    private String phone;
    private String role;
    private Integer status;
    private String gender;
    private Integer age;
    private String profile;
    private String title;
    private String specialties;
}
