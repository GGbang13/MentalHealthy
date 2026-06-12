package com.mentalhealth.platform.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mentalhealth.platform.common.BusinessException;
import com.mentalhealth.platform.common.PageResult;
import com.mentalhealth.platform.dto.ArticleRequest;
import com.mentalhealth.platform.entity.Article;
import com.mentalhealth.platform.entity.User;
import com.mentalhealth.platform.mapper.ArticleMapper;
import com.mentalhealth.platform.mapper.UserMapper;
import com.mentalhealth.platform.service.ArticleService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Service
@Slf4j
@RequiredArgsConstructor
public class ArticleServiceImpl implements ArticleService {
    private final ArticleMapper articleMapper;
    private final UserMapper userMapper;

    @Override
    public PageResult<Article> page(String keyword, String category, String status, String publishedFrom, String publishedTo, long current, long size, boolean includeDrafts) {
        String normalizedPublishedFrom = normalizeDateFilter(publishedFrom);
        String normalizedPublishedTo = normalizeDateFilter(publishedTo);
        LocalDateTime publishedFromStart = normalizedPublishedFrom == null ? null : parseDateStart(normalizedPublishedFrom);
        LocalDateTime publishedToEndExclusive = normalizedPublishedTo == null ? null : parseDateEndExclusive(normalizedPublishedTo);

        LambdaQueryWrapper<Article> wrapper = new LambdaQueryWrapper<>();
        wrapper.like(keyword != null && !keyword.isBlank(), Article::getTitle, keyword)
            .like(category != null && !category.isBlank(), Article::getCategory, category)
            .eq(status != null && !status.isBlank(), Article::getStatus, status)
            .ge(publishedFromStart != null, Article::getCreatedAt, publishedFromStart)
            .lt(publishedToEndExclusive != null, Article::getCreatedAt, publishedToEndExclusive)
            .eq(!includeDrafts, Article::getStatus, "PUBLISHED")
            .orderByDesc(Article::getUpdatedAt);
        Page<Article> page = articleMapper.selectPage(new Page<>(current, size), wrapper);
        return new PageResult<>(page.getTotal(), page.getRecords());
    }

    @Override
    public Article detail(Long id, boolean includeDrafts) {
        Article article = articleMapper.selectById(id);
        if (article == null || (!includeDrafts && !"PUBLISHED".equals(article.getStatus()))) {
            throw new BusinessException("文章不存在");
        }
        return article;
    }

    @Override
    public Article create(Long operatorId, ArticleRequest request) {
        Article article = new Article();
        fillArticle(article, operatorId, request);
        articleMapper.insert(article);
        return article;
    }

    @Override
    public Article update(Long operatorId, Long id, ArticleRequest request) {
        Article article = articleMapper.selectById(id);
        if (article == null) {
            throw new BusinessException("文章不存在");
        }
        fillArticle(article, operatorId, request);
        articleMapper.updateById(article);
        return article;
    }

    @Override
    public void delete(Long operatorId, Long id) {
        assertAdmin(operatorId);
        articleMapper.deleteById(id);
    }

    private void fillArticle(Article article, Long operatorId, ArticleRequest request) {
        User operator = assertAdmin(operatorId);
        article.setTitle(request.getTitle().trim());
        article.setCategory(request.getCategory() == null || request.getCategory().isBlank() ? "心理科普" : request.getCategory().trim());
        article.setSummary(request.getSummary());
        article.setContent(request.getContent().trim());
        article.setStatus(request.getStatus() == null || request.getStatus().isBlank() ? "PUBLISHED" : request.getStatus().trim());
        article.setAuthorName(operator.getNickname() != null && !operator.getNickname().isBlank() ? operator.getNickname() : operator.getUsername());
    }

    private User assertAdmin(Long operatorId) {
        User operator = userMapper.selectById(operatorId);
        if (operator == null || !"ADMIN".equals(operator.getRole())) {
            throw new BusinessException("当前账号没有管理权限");
        }
        return operator;
    }

    private LocalDateTime parseDateStart(String value) {
        try {
            return LocalDate.parse(value).atStartOfDay();
        } catch (Exception exception) {
            log.warn("Invalid article publishedFrom filter: {}", value);
            throw new BusinessException("发布时间筛选格式错误");
        }
    }

    private LocalDateTime parseDateEndExclusive(String value) {
        try {
            return LocalDate.parse(value).plusDays(1).atStartOfDay();
        } catch (Exception exception) {
            log.warn("Invalid article publishedTo filter: {}", value);
            throw new BusinessException("发布时间筛选格式错误");
        }
    }

    private String normalizeDateFilter(String value) {
        if (value == null) {
            return null;
        }
        String trimmed = value.trim();
        if (trimmed.isEmpty() || "undefined".equalsIgnoreCase(trimmed) || "null".equalsIgnoreCase(trimmed)) {
            return null;
        }
        return trimmed;
    }
}
