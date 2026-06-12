package com.mentalhealth.platform.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.mentalhealth.platform.common.BusinessException;
import com.mentalhealth.platform.dto.ForgotPasswordRequest;
import com.mentalhealth.platform.dto.LoginRequest;
import com.mentalhealth.platform.dto.RegisterRequest;
import com.mentalhealth.platform.entity.CounselorProfile;
import com.mentalhealth.platform.entity.User;
import com.mentalhealth.platform.mapper.CounselorProfileMapper;
import com.mentalhealth.platform.mapper.UserMapper;
import com.mentalhealth.platform.service.AuthService;
import com.mentalhealth.platform.util.JwtTokenUtil;
import com.mentalhealth.platform.vo.LoginResponse;
import com.mentalhealth.platform.vo.UserVO;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.BeanUtils;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class AuthServiceImpl implements AuthService {
    private final UserMapper userMapper;
    private final CounselorProfileMapper counselorProfileMapper;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenUtil jwtTokenUtil;

    @Override
    public LoginResponse login(LoginRequest request) {
        User user = userMapper.selectOne(new LambdaQueryWrapper<User>().eq(User::getUsername, request.getUsername()));
        if (user == null || !passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new BusinessException("用户名或密码错误");
        }
        UserVO userVO = new UserVO();
        BeanUtils.copyProperties(user, userVO);
        return new LoginResponse(jwtTokenUtil.generateToken(user.getId(), user.getRole()), userVO);
    }

    @Override
    public void register(RegisterRequest request) {
        User exist = userMapper.selectOne(new LambdaQueryWrapper<User>().eq(User::getUsername, request.getUsername()));
        if (exist != null) {
            throw new BusinessException("用户名已存在");
        }
        String role = normalizeRole(request.getRole());
        User user = new User();
        BeanUtils.copyProperties(request, user);
        user.setPassword(passwordEncoder.encode(request.getPassword()));
        user.setRole(role);
        user.setStatus(1);
        userMapper.insert(user);
        if ("COUNSELOR".equals(role)) {
            validateCounselorRegistration(request);
            CounselorProfile profile = new CounselorProfile();
            profile.setUserId(user.getId());
            profile.setTitle(request.getTitle());
            profile.setSpecialties(request.getSpecialties());
            profile.setYearsOfExperience(request.getYearsOfExperience());
            profile.setIntroduction(request.getIntroduction());
            profile.setPricePerHour(request.getPricePerHour());
            profile.setOnlineStatus(0);
            counselorProfileMapper.insert(profile);
        }
    }

    @Override
    public void resetPassword(ForgotPasswordRequest request) {
        User user = userMapper.selectOne(new LambdaQueryWrapper<User>().eq(User::getUsername, request.getUsername()));
        if (user == null) {
            throw new BusinessException("用户不存在");
        }
        user.setPassword(passwordEncoder.encode(request.getNewPassword()));
        userMapper.updateById(user);
    }

    private String normalizeRole(String role) {
        if (role == null || role.isBlank()) {
            return "USER";
        }
        if (!"USER".equals(role) && !"COUNSELOR".equals(role)) {
            throw new BusinessException("仅支持注册普通用户或咨询师账号");
        }
        return role;
    }

    private void validateCounselorRegistration(RegisterRequest request) {
        if (isBlank(request.getTitle()) || isBlank(request.getSpecialties()) || isBlank(request.getIntroduction())
            || request.getYearsOfExperience() == null || request.getPricePerHour() == null) {
            throw new BusinessException("咨询师登记请填写职称、擅长方向、从业年限、简介和咨询价格");
        }
    }

    private boolean isBlank(String value) {
        return value == null || value.isBlank();
    }
}
