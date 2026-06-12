package com.mentalhealth.platform.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.mentalhealth.platform.common.BusinessException;
import com.mentalhealth.platform.entity.Notification;
import com.mentalhealth.platform.entity.User;
import com.mentalhealth.platform.mapper.NotificationMapper;
import com.mentalhealth.platform.mapper.UserMapper;
import com.mentalhealth.platform.service.UserService;
import com.mentalhealth.platform.vo.UserVO;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class UserServiceImpl extends ServiceImpl<UserMapper, User> implements UserService {
    private final NotificationMapper notificationMapper;

    public UserServiceImpl(NotificationMapper notificationMapper) {
        this.notificationMapper = notificationMapper;
    }

    @Override
    public UserVO getProfile(Long userId) {
        User user = getById(userId);
        if (user == null) {
            throw new BusinessException("用户不存在");
        }
        UserVO userVO = new UserVO();
        BeanUtils.copyProperties(user, userVO);
        userVO.setPhone(maskPhone(user.getPhone()));
        return userVO;
    }

    @Override
    public void updateProfile(Long userId, UserVO userVO) {
        User user = getById(userId);
        if (user == null) {
            throw new BusinessException("用户不存在");
        }
        user.setNickname(userVO.getNickname());
        user.setAvatar(userVO.getAvatar());
        user.setGender(userVO.getGender());
        user.setAge(userVO.getAge());
        user.setProfile(userVO.getProfile());
        updateById(user);
    }

    @Override
    public List<Notification> listNotifications(Long userId) {
        User user = getById(userId);
        if (user == null) {
            throw new BusinessException("用户不存在");
        }
        return notificationMapper.selectList(new LambdaQueryWrapper<Notification>()
            .and(wrapper -> wrapper
                .eq(Notification::getTargetUserId, userId)
                .or()
                .eq(Notification::getTargetRole, user.getRole()))
            .orderByDesc(Notification::getCreatedAt));
    }

    private String maskPhone(String phone) {
        if (phone == null || phone.length() < 7) {
            return phone;
        }
        return phone.substring(0, 3) + "****" + phone.substring(phone.length() - 4);
    }
}
