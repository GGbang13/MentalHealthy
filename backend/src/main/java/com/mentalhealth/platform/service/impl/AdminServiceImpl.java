package com.mentalhealth.platform.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mentalhealth.platform.common.BusinessException;
import com.mentalhealth.platform.common.PageResult;
import com.mentalhealth.platform.dto.AdminUserRequest;
import com.mentalhealth.platform.dto.DeleteUserRequest;
import com.mentalhealth.platform.dto.NotificationRequest;
import com.mentalhealth.platform.entity.CounselorProfile;
import com.mentalhealth.platform.entity.Notification;
import com.mentalhealth.platform.entity.User;
import com.mentalhealth.platform.mapper.CounselorProfileMapper;
import com.mentalhealth.platform.mapper.NotificationMapper;
import com.mentalhealth.platform.mapper.UserMapper;
import com.mentalhealth.platform.service.AdminService;
import com.mentalhealth.platform.vo.AdminUserVO;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.List;

@Service
@RequiredArgsConstructor
public class AdminServiceImpl implements AdminService {
    private final UserMapper userMapper;
    private final CounselorProfileMapper counselorProfileMapper;
    private final NotificationMapper notificationMapper;
    private final PasswordEncoder passwordEncoder;

    @Override
    public PageResult<AdminUserVO> pageUsers(Long operatorId, String role, String keyword, long current, long size) {
        assertAdmin(operatorId);
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(role != null && !role.isBlank(), User::getRole, role)
            .and(keyword != null && !keyword.isBlank(), q -> q
                .like(User::getUsername, keyword)
                .or()
                .like(User::getNickname, keyword)
                .or()
                .like(User::getEmail, keyword))
            .orderByDesc(User::getCreatedAt);
        Page<User> page = userMapper.selectPage(new Page<>(current, size), wrapper);
        return new PageResult<>(page.getTotal(), page.getRecords().stream().map(this::toVO).toList());
    }

    @Override
    public AdminUserVO createUser(Long operatorId, AdminUserRequest request) {
        assertAdmin(operatorId);
        User existing = userMapper.selectOne(new LambdaQueryWrapper<User>().eq(User::getUsername, request.getUsername()));
        if (existing != null) {
            throw new BusinessException("用户名已存在");
        }
        User user = new User();
        applyUserRequest(user, request, true);
        userMapper.insert(user);
        syncCounselorProfile(user, request);
        return toVO(user);
    }

    @Override
    public AdminUserVO updateUser(Long operatorId, Long id, AdminUserRequest request) {
        assertAdmin(operatorId);
        User user = userMapper.selectById(id);
        if (user == null) {
            throw new BusinessException("用户不存在");
        }
        applyUserRequest(user, request, false);
        userMapper.updateById(user);
        syncCounselorProfile(user, request);
        return toVO(user);
    }

    @Override
    public void deleteUser(Long operatorId, Long id, DeleteUserRequest request) {
        User operator = assertAdmin(operatorId);
        User user = userMapper.selectById(id);
        if (user == null) {
            throw new BusinessException("用户不存在");
        }
        if (operator.getId().equals(id)) {
            throw new BusinessException("不能删除当前登录管理员");
        }
        Notification notification = new Notification();
        notification.setTargetUserId(id);
        notification.setTargetRole(user.getRole());
        notification.setTitle("账号已被管理员删除");
        notification.setContent(request.getReason());
        notification.setCreatedBy(operatorId);
        notificationMapper.insert(notification);
        userMapper.deleteById(id);
    }

    @Override
    public List<Notification> listNotifications(Long operatorId, String targetRole) {
        assertAdmin(operatorId);
        return notificationMapper.selectList(new LambdaQueryWrapper<Notification>()
            .eq(targetRole != null && !targetRole.isBlank(), Notification::getTargetRole, targetRole)
            .orderByDesc(Notification::getCreatedAt));
    }

    @Override
    public Notification createNotification(Long operatorId, NotificationRequest request) {
        assertAdmin(operatorId);
        if ((request.getTargetUserId() == null) == (request.getTargetRole() == null || request.getTargetRole().isBlank())) {
            throw new BusinessException("通知必须指定目标用户或目标角色");
        }
        if (request.getTargetRole() != null
            && !"USER".equals(request.getTargetRole())
            && !"COUNSELOR".equals(request.getTargetRole())) {
            throw new BusinessException("通知对象仅支持普通用户或咨询师");
        }
        Notification notification = new Notification();
        notification.setTargetUserId(request.getTargetUserId());
        notification.setTargetRole(request.getTargetRole());
        notification.setTitle(request.getTitle());
        notification.setContent(request.getContent());
        notification.setCreatedBy(operatorId);
        notificationMapper.insert(notification);
        return notification;
    }

    private void applyUserRequest(User user, AdminUserRequest request, boolean createMode) {
        user.setUsername(request.getUsername().trim());
        user.setNickname(request.getNickname());
        user.setEmail(request.getEmail());
        user.setPhone(request.getPhone());
        user.setRole(request.getRole().trim());
        user.setStatus(request.getStatus() == null ? 1 : request.getStatus());
        user.setGender(request.getGender());
        user.setAge(request.getAge());
        user.setProfile(request.getProfile());
        if (createMode) {
            if (request.getPassword() == null || request.getPassword().isBlank()) {
                throw new BusinessException("新增用户时密码不能为空");
            }
            user.setPassword(passwordEncoder.encode(request.getPassword()));
        } else if (request.getPassword() != null && !request.getPassword().isBlank()) {
            user.setPassword(passwordEncoder.encode(request.getPassword()));
        }
    }

    private void syncCounselorProfile(User user, AdminUserRequest request) {
        CounselorProfile profile = counselorProfileMapper.selectOne(new LambdaQueryWrapper<CounselorProfile>()
            .eq(CounselorProfile::getUserId, user.getId())
            .last("limit 1"));
        if ("COUNSELOR".equals(user.getRole())) {
            if (profile == null) {
                profile = new CounselorProfile();
                profile.setUserId(user.getId());
                profile.setTitle(request.getTitle() == null || request.getTitle().isBlank() ? "待完善" : request.getTitle().trim());
                profile.setSpecialties(request.getSpecialties() == null ? "" : request.getSpecialties().trim());
                profile.setYearsOfExperience(0);
                profile.setIntroduction(user.getProfile());
                profile.setPricePerHour(BigDecimal.ZERO);
                profile.setOnlineStatus(0);
                profile.setRating(BigDecimal.valueOf(5));
                profile.setReviewCount(0);
                counselorProfileMapper.insert(profile);
            } else {
                profile.setTitle(request.getTitle() == null || request.getTitle().isBlank() ? profile.getTitle() : request.getTitle().trim());
                profile.setSpecialties(request.getSpecialties() == null ? profile.getSpecialties() : request.getSpecialties().trim());
                profile.setIntroduction(user.getProfile());
                counselorProfileMapper.updateById(profile);
            }
        } else if (profile != null) {
            counselorProfileMapper.deleteById(profile.getId());
        }
    }

    private AdminUserVO toVO(User user) {
        AdminUserVO vo = new AdminUserVO();
        vo.setId(user.getId());
        vo.setUsername(user.getUsername());
        vo.setNickname(user.getNickname());
        vo.setEmail(user.getEmail());
        vo.setPhone(user.getPhone());
        vo.setRole(user.getRole());
        vo.setStatus(user.getStatus());
        vo.setGender(user.getGender());
        vo.setAge(user.getAge());
        vo.setProfile(user.getProfile());
        CounselorProfile profile = counselorProfileMapper.selectOne(new LambdaQueryWrapper<CounselorProfile>()
            .eq(CounselorProfile::getUserId, user.getId())
            .last("limit 1"));
        if (profile != null) {
            vo.setTitle(profile.getTitle());
            vo.setSpecialties(profile.getSpecialties());
        }
        return vo;
    }

    private User assertAdmin(Long operatorId) {
        User operator = userMapper.selectById(operatorId);
        if (operator == null || !"ADMIN".equals(operator.getRole())) {
            throw new BusinessException("当前账号没有管理权限");
        }
        return operator;
    }
}
