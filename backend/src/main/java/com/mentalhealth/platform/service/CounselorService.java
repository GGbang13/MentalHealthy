package com.mentalhealth.platform.service;

import com.mentalhealth.platform.common.PageResult;
import com.mentalhealth.platform.dto.CounselorProfileRequest;
import com.mentalhealth.platform.entity.CounselorReview;
import com.mentalhealth.platform.vo.CounselorVO;

import java.util.List;

public interface CounselorService {
    PageResult<CounselorVO> pageCounselors(String keyword, Integer onlineStatus, long current, long size);
    CounselorVO getDetail(Long counselorId);
    CounselorVO getCurrentCounselor(Long userId);
    void updateCurrentCounselor(Long userId, CounselorProfileRequest request);
    List<CounselorReview> listReviews(Long counselorId);
    void submitReview(Long userId, CounselorReview review);
}
