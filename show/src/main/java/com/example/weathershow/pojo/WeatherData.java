package com.example.weathershow.pojo;

import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;

/**
 * @author X
 * @date 2026/6/14 16:52
 */

@Data
@AllArgsConstructor
@NoArgsConstructor
public class WeatherData {
    private String cityName;
    @JsonFormat(pattern = "yyyy-MM-dd")
    private LocalDate date;
    private Double avgTemp;
    private Double minTemp;
    private Double maxTemp;
    private String season;
}
