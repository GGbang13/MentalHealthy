package com.mentalhealth.platform.config;

import com.baomidou.mybatisplus.core.handlers.MetaObjectHandler;
import org.apache.ibatis.reflection.MetaObject;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;

@Component
public class MetaObjectHandlerConfig implements MetaObjectHandler {

    @Override
    public void insertFill(MetaObject metaObject) {
        strictInsertFill(metaObject, "createdAt", LocalDateTime.class, LocalDateTime.now());
        strictInsertFill(metaObject, "updatedAt", LocalDateTime.class, LocalDateTime.now());
        strictInsertFill(metaObject, "deleted", Integer.class, 0);
    }

    @Override
    public void updateFill(MetaObject metaObject) {
        strictUpdateFill(metaObject, "updatedAt", LocalDateTime.class, LocalDateTime.now());
    }
}
