package com.mentalhealth.platform.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.mentalhealth.platform.entity.Appointment;
import com.mentalhealth.platform.entity.AssessmentRecord;
import com.mentalhealth.platform.entity.CounselorProfile;
import com.mentalhealth.platform.entity.User;
import com.mentalhealth.platform.mapper.AppointmentMapper;
import com.mentalhealth.platform.mapper.AssessmentRecordMapper;
import com.mentalhealth.platform.mapper.CounselorProfileMapper;
import com.mentalhealth.platform.mapper.UserMapper;
import com.mentalhealth.platform.service.DashboardService;
import com.mentalhealth.platform.vo.DashboardSummaryVO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

@Service
@RequiredArgsConstructor
public class DashboardServiceImpl implements DashboardService {
    private static final DateTimeFormatter FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm");

    private final UserMapper userMapper;
    private final CounselorProfileMapper counselorProfileMapper;
    private final AppointmentMapper appointmentMapper;
    private final AssessmentRecordMapper assessmentRecordMapper;

    @Override
    public DashboardSummaryVO summary() {
        DashboardSummaryVO summary = new DashboardSummaryVO();
        summary.setUserCount(userMapper.selectCount(null));
        summary.setCounselorCount(counselorProfileMapper.selectCount(null));
        summary.setOnlineCounselorCount(counselorProfileMapper.selectCount(new LambdaQueryWrapper<CounselorProfile>()
            .eq(CounselorProfile::getOnlineStatus, 1)));
        summary.setAppointmentCount(appointmentMapper.selectCount(null));
        summary.setPendingAppointmentCount(appointmentMapper.selectCount(new LambdaQueryWrapper<Appointment>()
            .in(Appointment::getStatus, List.of("PENDING", "CONFIRMED"))));
        summary.setAssessmentCount(assessmentRecordMapper.selectCount(null));
        summary.setHighRiskCount(assessmentRecordMapper.selectCount(new LambdaQueryWrapper<AssessmentRecord>()
            .eq(AssessmentRecord::getResultLevel, "HIGH")));
        summary.setRiskDistribution(buildRiskDistribution());
        summary.setRecentActivities(buildRecentActivities());
        return summary;
    }

    private List<DashboardSummaryVO.RiskSliceVO> buildRiskDistribution() {
        List<DashboardSummaryVO.RiskSliceVO> slices = new ArrayList<>();
        slices.add(slice("LOW"));
        slices.add(slice("MEDIUM"));
        slices.add(slice("HIGH"));
        return slices;
    }

    private DashboardSummaryVO.RiskSliceVO slice(String level) {
        DashboardSummaryVO.RiskSliceVO slice = new DashboardSummaryVO.RiskSliceVO();
        slice.setLevel(level);
        slice.setCount(assessmentRecordMapper.selectCount(new LambdaQueryWrapper<AssessmentRecord>()
            .eq(AssessmentRecord::getResultLevel, level)));
        return slice;
    }

    private List<DashboardSummaryVO.ActivityVO> buildRecentActivities() {
        List<DashboardSummaryVO.ActivityVO> activities = new ArrayList<>();

        List<AssessmentRecord> records = assessmentRecordMapper.selectList(new LambdaQueryWrapper<AssessmentRecord>()
            .orderByDesc(AssessmentRecord::getCreatedAt)
            .last("limit 5"));

        for (AssessmentRecord record : records) {
            DashboardSummaryVO.ActivityVO activity = new DashboardSummaryVO.ActivityVO();
            activity.setTitle("心理测评已提交");
            activity.setDescription("风险等级 " + defaultText(record.getResultLevel()) + "，模型 " + defaultText(record.getModelName()));
            activity.setTimestamp(record.getCreatedAt() == null ? "" : record.getCreatedAt().format(FORMATTER));
            activities.add(activity);
        }

        if (!activities.isEmpty()) {
            return activities;
        }

        List<Appointment> appointments = appointmentMapper.selectList(new LambdaQueryWrapper<Appointment>()
            .orderByDesc(Appointment::getCreatedAt)
            .last("limit 5"));

        for (Appointment appointment : appointments) {
            DashboardSummaryVO.ActivityVO activity = new DashboardSummaryVO.ActivityVO();
            activity.setTitle("咨询预约已创建");
            activity.setDescription("状态 " + defaultText(appointment.getStatus()) + "，类型 " + defaultText(appointment.getType()));
            activity.setTimestamp(appointment.getCreatedAt() == null ? "" : appointment.getCreatedAt().format(FORMATTER));
            activities.add(activity);
        }
        return activities;
    }

    private String defaultText(String value) {
        return value == null || value.isBlank() ? "暂无" : value;
    }
}
