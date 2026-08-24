package com.example.weathershow.pojo;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * @author X
 * @date 2026/6/11 16:18
 */

@Data
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class DistributionRangeVo {
    private Integer year;
    private Long range0to5;   // 0-5℃
    private Long range5to10;  // 5-10℃
    private Long range10to15; // 10-15℃
    private Long rangeOver15; // >15℃
}
