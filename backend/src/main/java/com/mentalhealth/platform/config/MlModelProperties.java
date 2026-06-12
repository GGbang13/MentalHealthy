package com.mentalhealth.platform.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Data
@Component
@ConfigurationProperties(prefix = "app.ml")
public class MlModelProperties {
    private boolean enabled = true;
    private String pythonCommand = "python";
    private String scriptPath = "../ml/predict_catboost.py";
    private String artifactsDir = "../ml/artifacts";
    private long timeoutSeconds = 15L;
}
