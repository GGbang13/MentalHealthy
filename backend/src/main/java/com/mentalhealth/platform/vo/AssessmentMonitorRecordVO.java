package com.mentalhealth.platform.vo;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class AssessmentMonitorRecordVO {
    private Long id;
    private Long userId;
    private String username;
    private String nickname;
    private Long scaleId;
    private String scaleName;
    private Integer score;
    private Double riskProbability;
    private String resultLevel;
    private String analysis;
    private String modelName;
    private String status;
    private LocalDateTime createdAt;
}
