package com.mentalhealth.platform.dto;

import lombok.Data;

@Data
public class NotificationRequest {
    private Long targetUserId;
    private String targetRole;
    private String title;
    private String content;
}
