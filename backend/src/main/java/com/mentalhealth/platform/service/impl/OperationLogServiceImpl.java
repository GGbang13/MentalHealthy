package com.mentalhealth.platform.service.impl;

import com.mentalhealth.platform.entity.OperationLog;
import com.mentalhealth.platform.mapper.OperationLogMapper;
import com.mentalhealth.platform.service.OperationLogService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class OperationLogServiceImpl implements OperationLogService {
    private final OperationLogMapper operationLogMapper;

    @Override
    public void record(Long userId, String module, String action, String detail) {
        OperationLog log = new OperationLog();
        log.setUserId(userId);
        log.setModule(module);
        log.setAction(action);
        log.setDetail(detail);
        log.setIp("127.0.0.1");
        operationLogMapper.insert(log);
    }
}
