package com.mentalhealth.platform.vo;

import lombok.Data;

@Data
public class RiskFactorVO {
    private String key;
    private String name;
    private Double value;
    private Double contributionScore;
    private String direction;
    private String description;
}
