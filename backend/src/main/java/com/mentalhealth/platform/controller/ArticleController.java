package com.mentalhealth.platform.controller;

import com.mentalhealth.platform.common.ApiResponse;
import com.mentalhealth.platform.dto.ArticleRequest;
import com.mentalhealth.platform.service.ArticleService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/articles")
@RequiredArgsConstructor
public class ArticleController {
    private final ArticleService articleService;

    @GetMapping
    public ApiResponse<?> page(Authentication authentication,
                               @RequestParam(required = false) String keyword,
                               @RequestParam(required = false) String category,
                               @RequestParam(required = false) String status,
                               @RequestParam(required = false) String publishedFrom,
                               @RequestParam(required = false) String publishedTo,
                               @RequestParam(defaultValue = "1") long current,
                               @RequestParam(defaultValue = "12") long size) {
        boolean includeDrafts = authentication != null
            && authentication.getAuthorities().stream().anyMatch(auth -> "ROLE_ADMIN".equals(auth.getAuthority()));
        return ApiResponse.success(articleService.page(keyword, category, status, publishedFrom, publishedTo, current, size, includeDrafts));
    }

    @GetMapping("/{id}")
    public ApiResponse<?> detail(Authentication authentication, @PathVariable Long id) {
        boolean includeDrafts = authentication != null
            && authentication.getAuthorities().stream().anyMatch(auth -> "ROLE_ADMIN".equals(auth.getAuthority()));
        return ApiResponse.success(articleService.detail(id, includeDrafts));
    }

    @PostMapping
    public ApiResponse<?> create(Authentication authentication, @RequestBody @Valid ArticleRequest request) {
        Long userId = (Long) authentication.getPrincipal();
        return ApiResponse.success("文章已创建", articleService.create(userId, request));
    }

    @PutMapping("/{id}")
    public ApiResponse<?> update(Authentication authentication, @PathVariable Long id, @RequestBody @Valid ArticleRequest request) {
        Long userId = (Long) authentication.getPrincipal();
        return ApiResponse.success("文章已更新", articleService.update(userId, id, request));
    }

    @DeleteMapping("/{id}")
    public ApiResponse<Void> delete(Authentication authentication, @PathVariable Long id) {
        Long userId = (Long) authentication.getPrincipal();
        articleService.delete(userId, id);
        return ApiResponse.success("文章已删除", null);
    }
}
