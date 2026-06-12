package com.mentalhealth.platform.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.time.LocalDateTime;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("appointment")
public class Appointment extends BaseEntity {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long userId;
    private Long counselorId;
    private LocalDateTime appointmentTime;
    private Integer durationMinutes;
    private String type;
    private String issueDescription;
    private String status;
    private String reminderStatus;
}
