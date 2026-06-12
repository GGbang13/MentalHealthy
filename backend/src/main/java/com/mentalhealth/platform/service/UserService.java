package com.mentalhealth.platform.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.mentalhealth.platform.entity.Notification;
import com.mentalhealth.platform.entity.User;
import com.mentalhealth.platform.vo.UserVO;

import java.util.List;

public interface UserService extends IService<User> {
    UserVO getProfile(Long userId);
    void updateProfile(Long userId, UserVO userVO);
    List<Notification> listNotifications(Long userId);
}
