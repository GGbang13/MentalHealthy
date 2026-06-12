package com.mentalhealth.platform.vo;

import lombok.Data;

@Data
public class UserVO {
    private Long id;
    private String username;
    private String email;
    private String phone;
    private String role;
    private String nickname;
    private String avatar;
    private String gender;
    private Integer age;
    private String profile;
}
