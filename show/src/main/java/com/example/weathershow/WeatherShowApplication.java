package com.example.weathershow;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.example.weathershow.mapper")
public class WeatherShowApplication {

    public static void main(String[] args) {
        SpringApplication.run(WeatherShowApplication.class, args);
    }

}
