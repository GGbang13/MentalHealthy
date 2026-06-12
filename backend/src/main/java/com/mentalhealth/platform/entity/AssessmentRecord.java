package com.mentalhealth.platform.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.mentalhealth.platform.vo.RiskFactorVO;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.util.List;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("assessment_record")
public class AssessmentRecord extends BaseEntity {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long userId;
    private Long scaleId;
    private String answerJson;
    private Integer score;
    private Double riskProbability;
    private String resultLevel;
    private String analysis;
    private String modelName;
    private String leadingFactorsJson;
    private String status;

    @TableField(exist = false)
    private List<RiskFactorVO> leadingFactors;
}
