package com.mentalhealth.platform.vo;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class AppointmentVO {
    private Long id;
    private Long userId;
    private String userNickname;
    private Long counselorId;
    private Long counselorUserId;
    private String counselorName;
    private String counselorTitle;
    private String counselorSpecialties;
    private LocalDateTime appointmentTime;
    private Integer durationMinutes;
    private String type;
    private String issueDescription;
    private String status;
    private String reminderStatus;
    private Boolean canChat;
}
