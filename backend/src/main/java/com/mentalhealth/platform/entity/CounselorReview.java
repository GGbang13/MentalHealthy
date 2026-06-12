package com.mentalhealth.platform.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("counselor_review")
public class CounselorReview extends BaseEntity {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long counselorId;
    private Long userId;
    private Integer rating;
    private String content;
}
