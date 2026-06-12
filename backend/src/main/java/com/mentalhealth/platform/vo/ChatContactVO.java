package com.mentalhealth.platform.vo;

import lombok.Data;

@Data
public class ChatContactVO {
    private Long userId;
    private String username;
    private String nickname;
    private String role;
    private String avatar;
    private String title;
    private String specialties;
}
