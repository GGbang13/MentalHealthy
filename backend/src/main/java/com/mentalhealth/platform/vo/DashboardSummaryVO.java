package com.mentalhealth.platform.vo;

import lombok.Data;

import java.util.List;

@Data
public class DashboardSummaryVO {
    private Long userCount;
    private Long counselorCount;
    private Long onlineCounselorCount;
    private Long appointmentCount;
    private Long pendingAppointmentCount;
    private Long assessmentCount;
    private Long highRiskCount;
    private List<RiskSliceVO> riskDistribution;
    private List<ActivityVO> recentActivities;

    @Data
    public static class RiskSliceVO {
        private String level;
        private Long count;
    }

    @Data
    public static class ActivityVO {
        private String title;
        private String description;
        private String timestamp;
    }
}
