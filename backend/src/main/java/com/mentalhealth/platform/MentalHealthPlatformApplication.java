package com.mentalhealth.platform;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@MapperScan("com.mentalhealth.platform.mapper")
@SpringBootApplication
public class MentalHealthPlatformApplication {

    public static void main(String[] args) {
        SpringApplication.run(MentalHealthPlatformApplication.class, args);
    }
}
