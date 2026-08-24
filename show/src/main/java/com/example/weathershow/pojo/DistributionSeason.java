package com.example.weathershow.pojo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * @author X
 * @date 2026/6/11 17:29
 */
/*
* 日较季节
* */


    @Data
    @AllArgsConstructor
    @NoArgsConstructor
public class DistributionSeason {
    private String season;
    private Double avgDailyRange;
    private Double maxDailyRange;
    private Double minDailyRange;
    private Double q1;
    private Double median;
    private Double q3;
}
