package com.mentalhealth.platform.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("notification")
public class Notification extends BaseEntity {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long targetUserId;
    private String targetRole;
    private String title;
    private String content;
    private Long createdBy;
}
