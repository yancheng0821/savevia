package com.savevia.optimizer;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
import org.springframework.cloud.openfeign.EnableFeignClients;

@SpringBootApplication(scanBasePackages = {"com.savevia.optimizer", "com.savevia.common"})
@EnableDiscoveryClient
@EnableFeignClients
public class SaveviaOptimizerApplication {

    public static void main(String[] args) {
        SpringApplication.run(SaveviaOptimizerApplication.class, args);
    }
}
