package com.mentalhealth.platform.service;

import com.mentalhealth.platform.dto.AppointmentRequest;
import com.mentalhealth.platform.vo.AppointmentVO;

import java.util.List;

public interface AppointmentService {
    AppointmentVO create(Long userId, AppointmentRequest request);
    List<AppointmentVO> listByUser(Long userId);
    List<AppointmentVO> listByCounselor(Long userId);
    void cancel(Long userId, Long appointmentId);
    void reschedule(Long userId, Long appointmentId, AppointmentRequest request);
    void confirm(Long userId, Long appointmentId);
    void reject(Long userId, Long appointmentId);
}
