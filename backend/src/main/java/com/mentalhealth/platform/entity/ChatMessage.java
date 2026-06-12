package com.mentalhealth.platform.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("chat_message")
public class ChatMessage extends BaseEntity {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long senderId;
    private Long receiverId;
    private String content;
    private String fileUrl;
    private Integer sensitiveFlag;
    private String reviewStatus;
}
