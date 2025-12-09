package com.savevia.user;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;

@SpringBootApplication(scanBasePackages = {"com.savevia.user", "com.savevia.common"})
@EnableDiscoveryClient
@MapperScan("com.savevia.user.mapper")
public class SaveviaUserApplication {

    public static void main(String[] args) {
        SpringApplication.run(SaveviaUserApplication.class, args);
    }
}
