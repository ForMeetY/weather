package com.example.weathershow.pojo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * @author X
 * @date 2026/6/11 17:15
 */

//按月聚合

    @Data
    @AllArgsConstructor
    @NoArgsConstructor
public class DistributionCorrelationVo {
    private String monthDimension;
    private Double avgTemp;
    private Double avgDailyRange;
    private String season;
}
