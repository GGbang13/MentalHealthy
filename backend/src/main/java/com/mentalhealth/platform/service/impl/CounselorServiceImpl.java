package com.mentalhealth.platform.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mentalhealth.platform.common.BusinessException;
import com.mentalhealth.platform.common.PageResult;
import com.mentalhealth.platform.dto.CounselorProfileRequest;
import com.mentalhealth.platform.entity.CounselorProfile;
import com.mentalhealth.platform.entity.CounselorReview;
import com.mentalhealth.platform.entity.User;
import com.mentalhealth.platform.mapper.CounselorProfileMapper;
import com.mentalhealth.platform.mapper.CounselorReviewMapper;
import com.mentalhealth.platform.mapper.UserMapper;
import com.mentalhealth.platform.service.CounselorService;
import com.mentalhealth.platform.vo.CounselorVO;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

@Service
@RequiredArgsConstructor
public class CounselorServiceImpl implements CounselorService {
    private final CounselorProfileMapper counselorProfileMapper;
    private final UserMapper userMapper;
    private final CounselorReviewMapper counselorReviewMapper;

    @Override
    public PageResult<CounselorVO> pageCounselors(String keyword, Integer onlineStatus, long current, long size) {
        syncMissingCounselorProfiles();
        LambdaQueryWrapper<CounselorProfile> wrapper = new LambdaQueryWrapper<>();
        wrapper.like(keyword != null && !keyword.isBlank(), CounselorProfile::getSpecialties, keyword)
            .eq(onlineStatus != null, CounselorProfile::getOnlineStatus, onlineStatus)
            .orderByDesc(CounselorProfile::getRating);
        Page<CounselorProfile> page = counselorProfileMapper.selectPage(new Page<>(current, size), wrapper);
        List<CounselorVO> list = page.getRecords().stream().map(this::toVO).toList();
        return new PageResult<>(page.getTotal(), list);
    }

    @Override
    public CounselorVO getDetail(Long counselorId) {
        CounselorProfile profile = counselorProfileMapper.selectById(counselorId);
        if (profile == null) {
            throw new BusinessException("咨询师不存在");
        }
        return toVO(profile);
    }

    @Override
    public CounselorVO getCurrentCounselor(Long userId) {
        CounselorProfile profile = getOrCreateByUserId(userId);
        return toVO(profile);
    }

    @Override
    public void updateCurrentCounselor(Long userId, CounselorProfileRequest request) {
        CounselorProfile profile = getOrCreateByUserId(userId);
        profile.setTitle(normalizeBlank(request.getTitle()));
        profile.setSpecialties(normalizeBlank(request.getSpecialties()));
        profile.setYearsOfExperience(request.getYearsOfExperience());
        profile.setIntroduction(normalizeBlank(request.getIntroduction()));
        profile.setPricePerHour(request.getPricePerHour());
        if (request.getOnlineStatus() != null) {
            profile.setOnlineStatus(request.getOnlineStatus());
        }
        profile.setScheduleJson(normalizeJsonText(request.getScheduleJson()));
        counselorProfileMapper.updateById(profile);
    }

    @Override
    public List<CounselorReview> listReviews(Long counselorId) {
        return counselorReviewMapper.selectList(new LambdaQueryWrapper<CounselorReview>()
            .eq(CounselorReview::getCounselorId, counselorId)
            .orderByDesc(CounselorReview::getCreatedAt));
    }

    @Override
    public void submitReview(Long userId, CounselorReview review) {
        review.setUserId(userId);
        counselorReviewMapper.insert(review);
        updateRating(review.getCounselorId());
    }

    private CounselorVO toVO(CounselorProfile profile) {
        CounselorVO vo = new CounselorVO();
        BeanUtils.copyProperties(profile, vo);
        User user = userMapper.selectById(profile.getUserId());
        if (user != null) {
            vo.setNickname(user.getNickname() != null && !user.getNickname().isBlank() ? user.getNickname() : user.getUsername());
            vo.setAvatar(user.getAvatar());
        }
        return vo;
    }

    private CounselorProfile getByUserId(Long userId) {
        return getOrCreateByUserId(userId);
    }

    private CounselorProfile getOrCreateByUserId(Long userId) {
        CounselorProfile profile = counselorProfileMapper.selectOne(new LambdaQueryWrapper<CounselorProfile>()
            .eq(CounselorProfile::getUserId, userId)
            .last("limit 1"));
        if (profile != null) {
            return profile;
        }
        User user = userMapper.selectById(userId);
        if (user == null || !"COUNSELOR".equals(user.getRole())) {
            throw new BusinessException("当前账号不是咨询师");
        }
        CounselorProfile created = new CounselorProfile();
        created.setUserId(userId);
        created.setTitle("待完善");
        created.setSpecialties("");
        created.setYearsOfExperience(0);
        created.setIntroduction(user.getProfile());
        created.setPricePerHour(BigDecimal.ZERO);
        created.setOnlineStatus(0);
        created.setRating(BigDecimal.valueOf(5));
        created.setReviewCount(0);
        counselorProfileMapper.insert(created);
        return created;
    }

    private void syncMissingCounselorProfiles() {
        List<User> counselorUsers = userMapper.selectList(new LambdaQueryWrapper<User>()
            .eq(User::getRole, "COUNSELOR"));
        Set<Long> existingUserIds = new HashSet<>(counselorProfileMapper.selectList(new LambdaQueryWrapper<CounselorProfile>())
            .stream()
            .map(CounselorProfile::getUserId)
            .toList());

        for (User user : counselorUsers) {
            if (!existingUserIds.contains(user.getId())) {
                CounselorProfile profile = new CounselorProfile();
                profile.setUserId(user.getId());
                profile.setTitle("待完善");
                profile.setSpecialties("");
                profile.setYearsOfExperience(0);
                profile.setIntroduction(user.getProfile());
                profile.setPricePerHour(BigDecimal.ZERO);
                profile.setOnlineStatus(0);
                profile.setRating(BigDecimal.valueOf(5));
                profile.setReviewCount(0);
                counselorProfileMapper.insert(profile);
            }
        }
    }

    private String normalizeBlank(String value) {
        return value == null ? null : value.trim();
    }

    private String normalizeJsonText(String value) {
        if (value == null) {
            return null;
        }
        String trimmed = value.trim();
        return trimmed.isEmpty() ? null : trimmed;
    }

    private void updateRating(Long counselorId) {
        List<CounselorReview> reviews = counselorReviewMapper.selectList(new LambdaQueryWrapper<CounselorReview>()
            .eq(CounselorReview::getCounselorId, counselorId));
        BigDecimal average = reviews.stream()
            .map(r -> BigDecimal.valueOf(r.getRating()))
            .reduce(BigDecimal.ZERO, BigDecimal::add)
            .divide(BigDecimal.valueOf(Math.max(reviews.size(), 1)), 2, RoundingMode.HALF_UP);
        CounselorProfile profile = counselorProfileMapper.selectById(counselorId);
        profile.setRating(average);
        profile.setReviewCount(reviews.size());
        counselorProfileMapper.updateById(profile);
    }
}
