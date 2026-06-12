package com.mentalhealth.platform.config;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;

import java.io.IOException;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Slf4j
@Component
@RequiredArgsConstructor
public class ChatSessionRegistry {
    private final ObjectMapper objectMapper;
    private final Map<Long, WebSocketSession> sessions = new ConcurrentHashMap<>();

    public void register(Long userId, WebSocketSession session) {
        sessions.put(userId, session);
    }

    public void unregister(WebSocketSession session) {
        sessions.entrySet().removeIf(entry -> entry.getValue().getId().equals(session.getId()));
    }

    public void push(Long userId, Object payload) {
        WebSocketSession session = sessions.get(userId);
        if (session == null || !session.isOpen()) {
            return;
        }
        try {
            session.sendMessage(new TextMessage(objectMapper.writeValueAsString(payload)));
        } catch (JsonProcessingException e) {
            log.warn("Serialize websocket payload failed", e);
        } catch (IOException e) {
            log.warn("Push websocket message failed", e);
        }
    }
}
