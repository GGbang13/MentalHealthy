package com.mentalhealth.platform.controller;

import com.mentalhealth.platform.common.ApiResponse;
import com.mentalhealth.platform.config.ChatSessionRegistry;
import com.mentalhealth.platform.dto.ChatMessageRequest;
import com.mentalhealth.platform.service.ChatMessageService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/chat")
@RequiredArgsConstructor
public class ChatController {
    private final ChatMessageService chatMessageService;
    private final ChatSessionRegistry chatSessionRegistry;

    @GetMapping("/history/{peerId}")
    public ApiResponse<?> history(Authentication authentication, @PathVariable Long peerId) {
        Long userId = (Long) authentication.getPrincipal();
        return ApiResponse.success(chatMessageService.history(userId, peerId));
    }

    @GetMapping("/contacts")
    public ApiResponse<?> contacts(Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        return ApiResponse.success(chatMessageService.contacts(userId));
    }

    @PostMapping("/send")
    public ApiResponse<?> send(Authentication authentication, @RequestBody @Valid ChatMessageRequest request) {
        Long userId = (Long) authentication.getPrincipal();
        var saved = chatMessageService.saveMessage(userId, request.getReceiverId(), request.getContent(), request.getFileUrl());
        chatSessionRegistry.push(request.getReceiverId(), saved);
        chatSessionRegistry.push(userId, saved);
        return ApiResponse.success(saved);
    }
}
