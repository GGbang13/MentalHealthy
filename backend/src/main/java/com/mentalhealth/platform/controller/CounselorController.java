package com.mentalhealth.platform.controller;

import com.mentalhealth.platform.common.ApiResponse;
import com.mentalhealth.platform.dto.CounselorProfileRequest;
import com.mentalhealth.platform.entity.CounselorReview;
import com.mentalhealth.platform.service.CounselorService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/counselors")
@RequiredArgsConstructor
public class CounselorController {
    private final CounselorService counselorService;

    @GetMapping
    public ApiResponse<?> page(@RequestParam(required = false) String keyword,
                               @RequestParam(required = false) Integer onlineStatus,
                               @RequestParam(defaultValue = "1") long current,
                               @RequestParam(defaultValue = "10") long size) {
        return ApiResponse.success(counselorService.pageCounselors(keyword, onlineStatus, current, size));
    }

    @GetMapping("/{id}")
    public ApiResponse<?> detail(@PathVariable Long id) {
        return ApiResponse.success(counselorService.getDetail(id));
    }

    @GetMapping("/me")
    public ApiResponse<?> current(Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        return ApiResponse.success(counselorService.getCurrentCounselor(userId));
    }

    @PutMapping("/me")
    public ApiResponse<Void> updateCurrent(Authentication authentication,
                                           @RequestBody CounselorProfileRequest request) {
        Long userId = (Long) authentication.getPrincipal();
        counselorService.updateCurrentCounselor(userId, request);
        return ApiResponse.success("咨询师资料已更新", null);
    }

    @GetMapping("/{id}/reviews")
    public ApiResponse<?> reviews(@PathVariable Long id) {
        return ApiResponse.success(counselorService.listReviews(id));
    }

    @PostMapping("/{id}/reviews")
    public ApiResponse<Void> submitReview(Authentication authentication,
                                          @PathVariable Long id,
                                          @RequestBody CounselorReview review) {
        Long userId = (Long) authentication.getPrincipal();
        review.setCounselorId(id);
        counselorService.submitReview(userId, review);
        return ApiResponse.success("评价成功", null);
    }
}
