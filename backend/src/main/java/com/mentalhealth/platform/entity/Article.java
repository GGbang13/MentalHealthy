package com.mentalhealth.platform.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("article")
public class Article extends BaseEntity {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String title;
    private String category;
    private String summary;
    private String content;
    private String authorName;
    private String status;
}
