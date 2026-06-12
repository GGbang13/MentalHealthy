package com.mentalhealth.platform.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.mentalhealth.platform.common.BusinessException;
import com.mentalhealth.platform.service.ChatMessageService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.CloseStatus;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;

import java.util.Map;

@Component
@RequiredArgsConstructor
public class ChatWebSocketHandler extends TextWebSocketHandler {
    private final ObjectMapper objectMapper;
    private final ChatMessageService chatMessageService;
    private final ChatSessionRegistry chatSessionRegistry;

    @Override
    public void afterConnectionEstablished(WebSocketSession session) {
        chatSessionRegistry.register(getAuthenticatedUserId(session), session);
    }

    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
        Map<?, ?> payload = objectMapper.readValue(message.getPayload(), Map.class);
        Long senderId = getAuthenticatedUserId(session);
        Long receiverId = Long.valueOf(String.valueOf(payload.get("receiverId")));
        String content = String.valueOf(payload.get("content"));
        String fileUrl = payload.get("fileUrl") == null ? null : String.valueOf(payload.get("fileUrl"));

        var saved = chatMessageService.saveMessage(senderId, receiverId, content, fileUrl);
        chatSessionRegistry.push(receiverId, saved);
        chatSessionRegistry.push(senderId, saved);
    }

    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) {
        chatSessionRegistry.unregister(session);
    }

    private Long getAuthenticatedUserId(WebSocketSession session) {
        Object userId = session.getAttributes().get("userId");
        if (userId == null) {
            throw new BusinessException("未授权的聊天连接");
        }
        return Long.parseLong(String.valueOf(userId));
    }
}
