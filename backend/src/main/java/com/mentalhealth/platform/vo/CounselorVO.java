package com.mentalhealth.platform.vo;

import lombok.Data;

import java.math.BigDecimal;

@Data
public class CounselorVO {
    private Long id;
    private Long userId;
    private String nickname;
    private String avatar;
    private String title;
    private String specialties;
    private Integer yearsOfExperience;
    private String introduction;
    private BigDecimal pricePerHour;
    private Integer onlineStatus;
    private String scheduleJson;
    private BigDecimal rating;
    private Integer reviewCount;
}
