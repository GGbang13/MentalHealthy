package com.mentalhealth.platform.service;

import com.mentalhealth.platform.entity.ChatMessage;
import com.mentalhealth.platform.vo.ChatContactVO;

import java.util.List;

public interface ChatMessageService {
    ChatMessage saveMessage(Long senderId, Long receiverId, String content, String fileUrl);
    List<ChatMessage> history(Long userId, Long peerId);
    List<ChatContactVO> contacts(Long userId);
    boolean canChat(Long userId, Long peerId);
}
