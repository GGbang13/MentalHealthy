package com.mentalhealth.platform.service;

public interface OperationLogService {
    void record(Long userId, String module, String action, String detail);
}
