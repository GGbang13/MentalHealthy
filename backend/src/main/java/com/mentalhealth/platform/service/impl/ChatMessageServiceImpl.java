package com.mentalhealth.platform.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.mentalhealth.platform.common.BusinessException;
import com.mentalhealth.platform.entity.Appointment;
import com.mentalhealth.platform.entity.ChatMessage;
import com.mentalhealth.platform.entity.CounselorProfile;
import com.mentalhealth.platform.entity.User;
import com.mentalhealth.platform.mapper.AppointmentMapper;
import com.mentalhealth.platform.mapper.ChatMessageMapper;
import com.mentalhealth.platform.mapper.CounselorProfileMapper;
import com.mentalhealth.platform.mapper.UserMapper;
import com.mentalhealth.platform.service.ChatMessageService;
import com.mentalhealth.platform.vo.ChatContactVO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

@Service
@RequiredArgsConstructor
public class ChatMessageServiceImpl implements ChatMessageService {
    private static final Set<String> SENSITIVE_WORDS = Set.of(
        "自杀", "暴力", "傻逼", "傻b", "煞笔", "蠢货", "脑残", "废物", "滚", "去死"
    );
    private static final Set<String> CHAT_ENABLED_STATUSES = Set.of("CONFIRMED");
    private final ChatMessageMapper chatMessageMapper;
    private final UserMapper userMapper;
    private final AppointmentMapper appointmentMapper;
    private final CounselorProfileMapper counselorProfileMapper;

    @Override
    public ChatMessage saveMessage(Long senderId, Long receiverId, String content, String fileUrl) {
        assertChatAllowed(senderId, receiverId);
        ChatMessage message = new ChatMessage();
        message.setSenderId(senderId);
        message.setReceiverId(receiverId);
        message.setContent(maskSensitive(content));
        message.setFileUrl(fileUrl);
        message.setSensitiveFlag(containsSensitive(content) ? 1 : 0);
        message.setReviewStatus(containsSensitive(content) ? "PENDING" : "APPROVED");
        chatMessageMapper.insert(message);
        return message;
    }

    @Override
    public List<ChatMessage> history(Long userId, Long peerId) {
        assertChatAllowed(userId, peerId);
        return chatMessageMapper.selectList(new LambdaQueryWrapper<ChatMessage>()
            .and(wrapper -> wrapper
                .eq(ChatMessage::getSenderId, userId).eq(ChatMessage::getReceiverId, peerId)
                .or()
                .eq(ChatMessage::getSenderId, peerId).eq(ChatMessage::getReceiverId, userId))
            .orderByAsc(ChatMessage::getCreatedAt));
    }

    @Override
    public List<ChatContactVO> contacts(Long userId) {
        List<ChatMessage> messages = chatMessageMapper.selectList(new LambdaQueryWrapper<ChatMessage>()
            .and(wrapper -> wrapper.eq(ChatMessage::getSenderId, userId).or().eq(ChatMessage::getReceiverId, userId))
            .orderByDesc(ChatMessage::getCreatedAt));

        Set<Long> peerIds = new LinkedHashSet<>();
        for (ChatMessage message : messages) {
            if (message.getSenderId().equals(userId)) {
                peerIds.add(message.getReceiverId());
            } else {
                peerIds.add(message.getSenderId());
            }
        }

        peerIds.addAll(resolveAppointmentContacts(userId));

        return peerIds.stream().map(this::toContact).toList();
    }

    @Override
    public boolean canChat(Long userId, Long peerId) {
        return hasMessageHistory(userId, peerId) || hasConfirmedAppointmentRelation(userId, peerId);
    }

    private boolean containsSensitive(String content) {
        if (content == null) {
            return false;
        }
        return SENSITIVE_WORDS.stream().anyMatch(content::contains);
    }

    private String maskSensitive(String content) {
        if (content == null) {
            return null;
        }
        String result = content;
        for (String word : SENSITIVE_WORDS) {
            result = result.replace(word, "*".repeat(word.length()));
        }
        return result;
    }

    private void assertChatAllowed(Long userId, Long peerId) {
        if (!canChat(userId, peerId)) {
            throw new BusinessException("该聊天对象尚未建立可沟通的预约关系");
        }
    }

    private boolean hasMessageHistory(Long userId, Long peerId) {
        return chatMessageMapper.selectCount(new LambdaQueryWrapper<ChatMessage>()
            .and(wrapper -> wrapper
                .eq(ChatMessage::getSenderId, userId).eq(ChatMessage::getReceiverId, peerId)
                .or()
                .eq(ChatMessage::getSenderId, peerId).eq(ChatMessage::getReceiverId, userId))) > 0;
    }

    private boolean hasConfirmedAppointmentRelation(Long userId, Long peerId) {
        User currentUser = userMapper.selectById(userId);
        User peerUser = userMapper.selectById(peerId);
        if (currentUser == null || peerUser == null) {
            return false;
        }
        if ("ADMIN".equals(currentUser.getRole()) || "ADMIN".equals(peerUser.getRole())) {
            return true;
        }

        if ("COUNSELOR".equals(currentUser.getRole())) {
            CounselorProfile currentProfile = getCounselorProfileByUserId(userId);
            if (currentProfile == null) {
                return false;
            }
            return appointmentMapper.selectCount(new LambdaQueryWrapper<Appointment>()
                .eq(Appointment::getCounselorId, currentProfile.getId())
                .eq(Appointment::getUserId, peerId)
                .in(Appointment::getStatus, CHAT_ENABLED_STATUSES)) > 0;
        }

        if ("COUNSELOR".equals(peerUser.getRole())) {
            CounselorProfile peerProfile = getCounselorProfileByUserId(peerId);
            if (peerProfile == null) {
                return false;
            }
            return appointmentMapper.selectCount(new LambdaQueryWrapper<Appointment>()
                .eq(Appointment::getUserId, userId)
                .eq(Appointment::getCounselorId, peerProfile.getId())
                .in(Appointment::getStatus, CHAT_ENABLED_STATUSES)) > 0;
        }

        return false;
    }

    private Set<Long> resolveAppointmentContacts(Long userId) {
        LinkedHashSet<Long> peerIds = new LinkedHashSet<>();
        User currentUser = userMapper.selectById(userId);
        if (currentUser == null) {
            return peerIds;
        }

        if ("COUNSELOR".equals(currentUser.getRole())) {
            CounselorProfile profile = getCounselorProfileByUserId(userId);
            if (profile == null) {
                return peerIds;
            }
            appointmentMapper.selectList(new LambdaQueryWrapper<Appointment>()
                    .eq(Appointment::getCounselorId, profile.getId())
                    .in(Appointment::getStatus, CHAT_ENABLED_STATUSES)
                    .orderByDesc(Appointment::getAppointmentTime))
                .forEach(appointment -> peerIds.add(appointment.getUserId()));
            return peerIds;
        }

        appointmentMapper.selectList(new LambdaQueryWrapper<Appointment>()
                .eq(Appointment::getUserId, userId)
                .in(Appointment::getStatus, CHAT_ENABLED_STATUSES)
                .orderByDesc(Appointment::getAppointmentTime))
            .forEach(appointment -> {
                CounselorProfile profile = counselorProfileMapper.selectById(appointment.getCounselorId());
                if (profile != null) {
                    peerIds.add(profile.getUserId());
                }
            });
        return peerIds;
    }

    private ChatContactVO toContact(Long peerId) {
        User user = userMapper.selectById(peerId);
        ChatContactVO contact = new ChatContactVO();
        contact.setUserId(peerId);
        if (user != null) {
            contact.setUsername(user.getUsername());
            contact.setNickname(user.getNickname());
            contact.setRole(user.getRole());
            contact.setAvatar(user.getAvatar());
            if ("COUNSELOR".equals(user.getRole())) {
                CounselorProfile profile = getCounselorProfileByUserId(peerId);
                if (profile != null) {
                    contact.setTitle(profile.getTitle());
                    contact.setSpecialties(profile.getSpecialties());
                }
            }
        }
        return contact;
    }

    private CounselorProfile getCounselorProfileByUserId(Long userId) {
        return counselorProfileMapper.selectOne(new LambdaQueryWrapper<CounselorProfile>()
            .eq(CounselorProfile::getUserId, userId)
            .last("limit 1"));
    }
}
