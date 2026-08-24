<!-- 
 4. 气温距平分析图（Anomaly Analysis）
展示内容：计算 20 年的平均值作为基准线，每一年的平均温减去基准线。
图表建议：使用 bar 图，正值向上红色显示，负值向下蓝色显示。
-->
<template>
  <div class="chart-wrapper">
    <div v-if="loading" class="chart-loading">
      <span class="spinner"></span>
    </div>
    <div ref="chartRef" class="chart-container"></div>
    <div class="analysis-panel">
      <div class="analysis-title">数据解读：</div>
      <p class="analysis-text">
        本图通过计算近20年年均温的<strong>偏离值（距平）</strong>，直观展示了气候波动。
        <span style="color: #ff4d4f">红色柱状</span
        >代表该年份气温高于20年平均水平，<span style="color: #1890ff"
          >蓝色柱状</span
        >代表低于平均水平。
        <strong>趋势判断：</strong
        >若近期红柱连续出现且高度增加，预示着该区域气温呈现显著的<strong>暖化趋势</strong>；柱状高度差反映了气候年际波动剧烈程度。
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import * as echarts from "echarts";

const props = defineProps({ trendYear: Object });
const chartRef = ref(null);
const loading = ref(true);
let myChart = null;

const updateChart = (data) => {
  if (!myChart || !data || !data.avgSeries) {
    return;
  }

  const avgArray = data.avgSeries;
  const globalAvg = avgArray.reduce((a, b) => a + b, 0) / avgArray.length;
  const anomalyData = avgArray.map((val) =>
    Number((val - globalAvg).toFixed(2)),
  );

  myChart.setOption({
    title: {
      text: "气温距平分析 (20年变暖趋势)",
      textStyle: { color: "#fff", fontSize: 16 },
      left: "center",
      top: "10px",
    },
    tooltip: {
      trigger: "axis",
      backgroundColor: "rgba(0,0,0,0.8)",
      borderColor: "#1890ff",
      formatter: (params) =>
        `${params[0].name}年: ${params[0].value > 0 ? "+" : ""}${params[0].value}°C`,
    },

    dataZoom: [{ type: "slider", show: false }],
    visualMap: {
      show: false,
      pieces: [
        { gt: 0, color: "#ff4d4f" },
        { lte: 0, color: "#1890ff" },
      ],
    },

    grid: {
      top: "80px",
      left: "5%",
      right: "5%",
      bottom: "100px", 
      containLabel: true,
    },
    xAxis: {
      type: "category",
      data: data.xaxis,
      axisLabel: { color: "#8a99ad" },
      axisLine: { lineStyle: { color: "#1e293b" } },
    },
    yAxis: {
      type: "value",
      name: "距平(℃)",
      splitLine: { lineStyle: { color: "#1e293b" } },
      axisLabel: { color: "#8a99ad" },
    },
    series: [
      {
        type: "bar",
        data: anomalyData,
        barWidth: "50%",
        markLine: {
          symbol: "none",
          lineStyle: { color: "#fff", type: "dashed" },
          data: [{ yAxis: 0 }],
        },
      },
    ],
  });
  loading.value = false;
};

onMounted(() => {
  myChart = echarts.init(chartRef.value);
  if (props.trendYear) updateChart(props.trendYear);
  window.addEventListener("resize", () => myChart?.resize());
});

watch(
  () => props.trendYear,
  (newData) => {
    if (newData) updateChart(newData);
  },
  { deep: true },
);
</script>

<style scoped>
.chart-wrapper {
  position: relative;
}
.chart-loading {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(16, 24, 48, 0.6);
  border-radius: 8px;
  z-index: 10;
}
.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid rgba(59, 130, 246, 0.2);
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
.chart-container {
  width: 100%;
  height: 350px; /* 统一高度 */
  margin-bottom: 20px;
  background: rgba(16, 24, 48, 0.4);
  border: 1px solid #1e293b;
  border-radius: 8px;
  padding: 10px; /* 保持内外边距统一 */
}
.analysis-panel {
  background: rgba(16, 24, 48, 0.6);
  padding: 10px;
  border-radius: 0 0 8px 8px;
  border: 1px solid #1e293b;
  border-top: none;
  color: #8a99ad;
  font-size: 13px;
  line-height: 1.6;
}
.analysis-title {
  color: #fff;
  font-weight: bold;
  margin-bottom: 5px;
}
</style>
