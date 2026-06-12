package com.mentalhealth.platform.service;

import com.mentalhealth.platform.common.PageResult;
import com.mentalhealth.platform.dto.ArticleRequest;
import com.mentalhealth.platform.entity.Article;

public interface ArticleService {
    PageResult<Article> page(String keyword, String category, String status, String publishedFrom, String publishedTo, long current, long size, boolean includeDrafts);
    Article detail(Long id, boolean includeDrafts);
    Article create(Long operatorId, ArticleRequest request);
    Article update(Long operatorId, Long id, ArticleRequest request);
    void delete(Long operatorId, Long id);
}
