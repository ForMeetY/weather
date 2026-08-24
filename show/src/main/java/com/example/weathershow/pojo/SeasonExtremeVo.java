package com.example.weathershow.pojo;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;
/**
 * @author X
 * @date 2026/6/10 16:59
 */

@Data
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class SeasonExtremeVo {
    // 四个季节的名称，如 ["春", "夏", "秋", "冬"]
    private String season;      // 对应 SQL 的 season
    private Integer highCount;  // 对应 SQL 的 highCount
    private Integer lowCount;   // 对应 SQL 的 lowCount

    private Double highAvgIntensity;  // 高温平均偏差强度
    private Double lowAvgIntensity;   // 低温平均偏差强度
}
