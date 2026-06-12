package com.mentalhealth.platform.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("assessment_scale")
public class AssessmentScale extends BaseEntity {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String name;
    private String code;
    private String description;
    private String questionJson;
    private String ruleJson;
    private Integer enabled;
}
