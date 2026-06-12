package com.mentalhealth.platform.dto;

import lombok.Data;

import java.math.BigDecimal;

@Data
public class CounselorProfileRequest {
    private String title;
    private String specialties;
    private Integer yearsOfExperience;
    private String introduction;
    private BigDecimal pricePerHour;
    private Integer onlineStatus;
    private String scheduleJson;
}
