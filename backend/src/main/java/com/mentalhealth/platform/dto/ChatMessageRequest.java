package com.mentalhealth.platform.dto;

import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
public class ChatMessageRequest {
    @NotNull(message = "接收方不能为空")
    private Long receiverId;
    private String content;
    private String fileUrl;
}
