package com.savevia.card;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;

@SpringBootApplication(scanBasePackages = {"com.savevia.card", "com.savevia.common"})
@EnableDiscoveryClient
@MapperScan("com.savevia.card.mapper")
public class SaveviaCardApplication {

    public static void main(String[] args) {
        SpringApplication.run(SaveviaCardApplication.class, args);
    }
}
