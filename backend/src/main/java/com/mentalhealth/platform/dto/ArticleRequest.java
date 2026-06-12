package com.mentalhealth.platform.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class ArticleRequest {
    @NotBlank(message = "文章标题不能为空")
    private String title;
    private String category;
    private String summary;
    @NotBlank(message = "文章内容不能为空")
    private String content;
    private String status;
}
