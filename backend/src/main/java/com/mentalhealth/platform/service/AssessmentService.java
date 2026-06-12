package com.mentalhealth.platform.service;

import com.mentalhealth.platform.dto.AssessmentSubmitRequest;
import com.mentalhealth.platform.entity.AssessmentRecord;
import com.mentalhealth.platform.entity.AssessmentScale;
import com.mentalhealth.platform.vo.AssessmentMonitorRecordVO;

import java.util.List;

public interface AssessmentService {
    List<AssessmentScale> listScales();
    AssessmentRecord submit(Long userId, AssessmentSubmitRequest request);
    List<AssessmentRecord> history(Long userId);
    List<AssessmentMonitorRecordVO> adminRecords(Long operatorId);
}
