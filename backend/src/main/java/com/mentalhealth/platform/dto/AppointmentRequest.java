package com.mentalhealth.platform.dto;

import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.time.LocalDateTime;

@Data
public class AppointmentRequest {
    @NotNull(message = "咨询师不能为空")
    private Long counselorId;
    @NotNull(message = "预约时间不能为空")
    private LocalDateTime appointmentTime;
    private Integer durationMinutes;
    private String type;
    private String issueDescription;
}
