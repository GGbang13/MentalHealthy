package com.mentalhealth.platform.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.mentalhealth.platform.common.BusinessException;
import com.mentalhealth.platform.dto.AppointmentRequest;
import com.mentalhealth.platform.entity.Appointment;
import com.mentalhealth.platform.entity.CounselorProfile;
import com.mentalhealth.platform.entity.User;
import com.mentalhealth.platform.mapper.AppointmentMapper;
import com.mentalhealth.platform.mapper.CounselorProfileMapper;
import com.mentalhealth.platform.mapper.UserMapper;
import com.mentalhealth.platform.service.AppointmentService;
import com.mentalhealth.platform.vo.AppointmentVO;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class AppointmentServiceImpl implements AppointmentService {
    private final AppointmentMapper appointmentMapper;
    private final CounselorProfileMapper counselorProfileMapper;
    private final UserMapper userMapper;

    @Override
    public AppointmentVO create(Long userId, AppointmentRequest request) {
        CounselorProfile profile = counselorProfileMapper.selectById(request.getCounselorId());
        if (profile == null) {
            throw new BusinessException("咨询师不存在");
        }
        Appointment appointment = new Appointment();
        BeanUtils.copyProperties(request, appointment);
        appointment.setUserId(userId);
        appointment.setStatus("PENDING");
        appointment.setReminderStatus("WAITING");
        if (appointment.getDurationMinutes() == null || appointment.getDurationMinutes() <= 0) {
            appointment.setDurationMinutes(50);
        }
        appointmentMapper.insert(appointment);
        return toVO(appointment);
    }

    @Override
    public List<AppointmentVO> listByUser(Long userId) {
        return appointmentMapper.selectList(new LambdaQueryWrapper<Appointment>()
            .eq(Appointment::getUserId, userId)
            .orderByDesc(Appointment::getAppointmentTime))
            .stream()
            .map(this::toVO)
            .toList();
    }

    @Override
    public List<AppointmentVO> listByCounselor(Long userId) {
        CounselorProfile profile = getCounselorProfile(userId);
        return appointmentMapper.selectList(new LambdaQueryWrapper<Appointment>()
            .eq(Appointment::getCounselorId, profile.getId())
            .orderByDesc(Appointment::getAppointmentTime))
            .stream()
            .map(this::toVO)
            .toList();
    }

    @Override
    public void cancel(Long userId, Long appointmentId) {
        Appointment appointment = assertOwner(userId, appointmentId);
        appointment.setStatus("CANCELLED");
        appointment.setReminderStatus("CLOSED");
        appointmentMapper.updateById(appointment);
    }

    @Override
    public void reschedule(Long userId, Long appointmentId, AppointmentRequest request) {
        Appointment appointment = assertOwner(userId, appointmentId);
        appointment.setAppointmentTime(request.getAppointmentTime());
        appointment.setDurationMinutes(request.getDurationMinutes());
        appointment.setIssueDescription(request.getIssueDescription());
        appointment.setType(request.getType());
        appointment.setStatus("PENDING");
        appointment.setReminderStatus("WAITING");
        appointmentMapper.updateById(appointment);
    }

    @Override
    public void confirm(Long userId, Long appointmentId) {
        Appointment appointment = assertCounselorOwner(userId, appointmentId);
        if (!"PENDING".equals(appointment.getStatus())) {
            throw new BusinessException("当前预约状态不能执行同意操作");
        }
        appointment.setStatus("CONFIRMED");
        appointment.setReminderStatus("READY");
        appointmentMapper.updateById(appointment);
    }

    @Override
    public void reject(Long userId, Long appointmentId) {
        Appointment appointment = assertCounselorOwner(userId, appointmentId);
        if (!"PENDING".equals(appointment.getStatus())) {
            throw new BusinessException("当前预约状态不能执行拒绝操作");
        }
        appointment.setStatus("REJECTED");
        appointment.setReminderStatus("CLOSED");
        appointmentMapper.updateById(appointment);
    }

    private Appointment assertOwner(Long userId, Long appointmentId) {
        Appointment appointment = appointmentMapper.selectById(appointmentId);
        if (appointment == null || !appointment.getUserId().equals(userId)) {
            throw new BusinessException("预约记录不存在");
        }
        return appointment;
    }

    private Appointment assertCounselorOwner(Long userId, Long appointmentId) {
        CounselorProfile profile = getCounselorProfile(userId);
        Appointment appointment = appointmentMapper.selectById(appointmentId);
        if (appointment == null || !appointment.getCounselorId().equals(profile.getId())) {
            throw new BusinessException("预约记录不存在");
        }
        return appointment;
    }

    private CounselorProfile getCounselorProfile(Long userId) {
        CounselorProfile profile = counselorProfileMapper.selectOne(new LambdaQueryWrapper<CounselorProfile>()
            .eq(CounselorProfile::getUserId, userId)
            .last("limit 1"));
        if (profile == null) {
            throw new BusinessException("当前账号未绑定咨询师资料");
        }
        return profile;
    }

    private AppointmentVO toVO(Appointment appointment) {
        AppointmentVO vo = new AppointmentVO();
        BeanUtils.copyProperties(appointment, vo);

        User user = userMapper.selectById(appointment.getUserId());
        if (user != null) {
            vo.setUserNickname(user.getNickname() != null && !user.getNickname().isBlank() ? user.getNickname() : user.getUsername());
        }

        CounselorProfile profile = counselorProfileMapper.selectById(appointment.getCounselorId());
        if (profile != null) {
            vo.setCounselorUserId(profile.getUserId());
            vo.setCounselorTitle(profile.getTitle());
            vo.setCounselorSpecialties(profile.getSpecialties());

            User counselor = userMapper.selectById(profile.getUserId());
            if (counselor != null) {
                vo.setCounselorName(counselor.getNickname() != null && !counselor.getNickname().isBlank()
                    ? counselor.getNickname()
                    : counselor.getUsername());
            }
        }

        vo.setCanChat("CONFIRMED".equals(appointment.getStatus()) && vo.getCounselorUserId() != null);
        return vo;
    }
}
