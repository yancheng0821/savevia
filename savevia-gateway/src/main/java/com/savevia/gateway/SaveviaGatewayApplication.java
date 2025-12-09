package com.savevia.gateway;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;

@SpringBootApplication
@EnableDiscoveryClient
public class SaveviaGatewayApplication {

    public static void main(String[] args) {
        SpringApplication.run(SaveviaGatewayApplication.class, args);
    }
}
