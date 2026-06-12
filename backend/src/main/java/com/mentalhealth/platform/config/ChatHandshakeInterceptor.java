package com.mentalhealth.platform.config;

import com.mentalhealth.platform.util.JwtTokenUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.server.ServerHttpRequest;
import org.springframework.http.server.ServerHttpResponse;
import org.springframework.http.server.ServletServerHttpRequest;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.WebSocketHandler;
import org.springframework.web.socket.server.HandshakeInterceptor;
import org.springframework.web.util.UriComponentsBuilder;

import java.util.Map;

@Component
@RequiredArgsConstructor
public class ChatHandshakeInterceptor implements HandshakeInterceptor {
    private final JwtTokenUtil jwtTokenUtil;

    @Override
    public boolean beforeHandshake(ServerHttpRequest request, ServerHttpResponse response,
                                   WebSocketHandler wsHandler, Map<String, Object> attributes) {
        if (!(request instanceof ServletServerHttpRequest servletRequest)) {
            response.setStatusCode(HttpStatus.UNAUTHORIZED);
            return false;
        }

        String token = UriComponentsBuilder.fromUri(servletRequest.getURI())
            .build()
            .getQueryParams()
            .getFirst("token");

        if (token == null || !jwtTokenUtil.validateToken(token)) {
            response.setStatusCode(HttpStatus.UNAUTHORIZED);
            return false;
        }

        attributes.put("userId", jwtTokenUtil.getUserId(token));
        attributes.put("role", jwtTokenUtil.getRole(token));
        return true;
    }

    @Override
    public void afterHandshake(ServerHttpRequest request, ServerHttpResponse response,
                               WebSocketHandler wsHandler, Exception exception) {
    }
}
