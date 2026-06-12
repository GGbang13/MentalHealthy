package com.mentalhealth.platform.dto;

import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
public class AssessmentSubmitRequest {
    @NotNull(message = "量表不能为空")
    private Long scaleId;
    private String answerJson;
    private String status;
}
