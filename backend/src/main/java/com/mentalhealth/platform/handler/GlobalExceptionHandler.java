package com.mentalhealth.platform.handler;

import com.mentalhealth.platform.common.ApiResponse;
import com.mentalhealth.platform.common.BusinessException;
import jakarta.validation.ConstraintViolationException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.dao.DataAccessException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BusinessException.class)
    public ApiResponse<Void> handleBusinessException(BusinessException e) {
        return ApiResponse.fail(400, e.getMessage());
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ApiResponse<Void> handleMethodArgumentNotValidException(MethodArgumentNotValidException e) {
        String message = e.getBindingResult().getFieldError() != null
            ? e.getBindingResult().getFieldError().getDefaultMessage() : "Validation failed";
        return ApiResponse.fail(400, message);
    }

    @ExceptionHandler(ConstraintViolationException.class)
    public ApiResponse<Void> handleConstraintViolationException(ConstraintViolationException e) {
        return ApiResponse.fail(400, e.getMessage());
    }

    @ExceptionHandler(DataAccessException.class)
    public ApiResponse<Void> handleDataAccessException(DataAccessException e) {
        log.error("Database access exception", e);
        return ApiResponse.fail(500, "数据库结构或数据访问异常，请重启后端后重试");
    }

    @ExceptionHandler(Exception.class)
    public ApiResponse<Void> handleException(Exception e) {
        log.error("Unhandled server exception", e);
        return ApiResponse.fail(500, "服务器内部错误，请稍后重试");
    }
}
