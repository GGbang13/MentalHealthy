package com.mentalhealth.platform.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.math.BigDecimal;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("counselor_profile")
public class CounselorProfile extends BaseEntity {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long userId;
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
