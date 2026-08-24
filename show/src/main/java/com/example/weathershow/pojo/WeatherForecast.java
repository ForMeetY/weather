package com.example.weathershow.pojo;

import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;

/**
 * @author X
 * @date 2026/6/14 14:48
 */

@Data
@AllArgsConstructor
@NoArgsConstructor
public class WeatherForecast {
    @JsonFormat(pattern = "yyyy-MM-dd")
    private LocalDate ds;

    private Double yhat;

    private Double yhatLower;

    private Double yhatUpper;
}
