package com.mentalhealth.platform.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.socket.config.annotation.EnableWebSocket;
import org.springframework.web.socket.config.annotation.WebSocketConfigurer;
import org.springframework.web.socket.config.annotation.WebSocketHandlerRegistry;

import java.util.Arrays;
import java.util.List;

@Configuration
@EnableWebSocket
public class WebSocketConfig implements WebSocketConfigurer {

    private final ChatWebSocketHandler chatWebSocketHandler;
    private final ChatHandshakeInterceptor chatHandshakeInterceptor;
    private final List<String> allowedOrigins;

    public WebSocketConfig(ChatWebSocketHandler chatWebSocketHandler,
                           ChatHandshakeInterceptor chatHandshakeInterceptor,
                           @Value("${app.security.allowed-origins:http://localhost:5173,http://127.0.0.1:5173}") String allowedOrigins) {
        this.chatWebSocketHandler = chatWebSocketHandler;
        this.chatHandshakeInterceptor = chatHandshakeInterceptor;
        this.allowedOrigins = Arrays.stream(allowedOrigins.split(","))
            .map(String::trim)
            .filter(origin -> !origin.isEmpty())
            .toList();
    }

    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        registry.addHandler(chatWebSocketHandler, "/ws/chat")
            .addInterceptors(chatHandshakeInterceptor)
            .setAllowedOrigins(allowedOrigins.toArray(String[]::new));
    }
}
