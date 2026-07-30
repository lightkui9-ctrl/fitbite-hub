package com.fitbite;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.fitbite.mapper")
public class FitBiteApplication {
    public static void main(String[] args) {
        SpringApplication.run(FitBiteApplication.class, args);
    }
}