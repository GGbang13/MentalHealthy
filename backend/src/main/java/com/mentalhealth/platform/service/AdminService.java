package com.mentalhealth.platform.service;

import com.mentalhealth.platform.common.PageResult;
import com.mentalhealth.platform.dto.AdminUserRequest;
import com.mentalhealth.platform.dto.DeleteUserRequest;
import com.mentalhealth.platform.dto.NotificationRequest;
import com.mentalhealth.platform.entity.Notification;
import com.mentalhealth.platform.vo.AdminUserVO;

import java.util.List;

public interface AdminService {
    PageResult<AdminUserVO> pageUsers(Long operatorId, String role, String keyword, long current, long size);
    AdminUserVO createUser(Long operatorId, AdminUserRequest request);
    AdminUserVO updateUser(Long operatorId, Long id, AdminUserRequest request);
    void deleteUser(Long operatorId, Long id, DeleteUserRequest request);
    List<Notification> listNotifications(Long operatorId, String targetRole);
    Notification createNotification(Long operatorId, NotificationRequest request);
}
