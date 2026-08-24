<script setup>
import { ref, onMounted, watch, nextTick } from "vue";
import * as echarts from "echarts";

const props = defineProps({
  data: { type: Array, default: () => [] },
});

const chartRef = ref(null);
let myChart = null;

const seasonColorMap = {
  春: "#22c55e",
  夏: "#f43f5e",
  秋: "#f59e0b",
  冬: "#3b82f6",
};

const initChart = () => {
  if (!chartRef.value) return;

  if (myChart) {
    myChart.dispose();
    myChart = null;
  }

  myChart = echarts.init(chartRef.value);

  const seasons = ["春", "夏", "秋", "冬"];
  const seriesData = seasons.map((season) => ({
    name: season,
    type: "scatter",
    symbolSize: 10,
    itemStyle: {
      color: seasonColorMap[season],
      opacity: 0.75,
    },
    emphasis: {
      itemStyle: {
        borderColor: "#fff",
        borderWidth: 1.5,
        opacity: 1,
      },
    },
    data: props.data
      .filter((item) => item.season === season)
      .map((item) => [item.avgTemp, item.avgDailyRange, item.monthDimension]),
  }));

  // 简单线性回归，计算趋势线
  const allPoints = props.data.map((item) => [
    item.avgTemp,
    item.avgDailyRange,
  ]);
  let trendLineData = [];
  if (allPoints.length >= 2) {
    const n = allPoints.length;
    const sumX = allPoints.reduce((s, p) => s + p[0], 0);
    const sumY = allPoints.reduce((s, p) => s + p[1], 0);
    const sumXY = allPoints.reduce((s, p) => s + p[0] * p[1], 0);
    const sumXX = allPoints.reduce((s, p) => s + p[0] * p[0], 0);
    const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
    const intercept = (sumY - slope * sumX) / n;

    const xs = allPoints.map((p) => p[0]);
    const minX = Math.min(...xs);
    const maxX = Math.max(...xs);
    trendLineData = [
      [minX, slope * minX + intercept],
      [maxX, slope * maxX + intercept],
    ];
  }

  const option = {
    backgroundColor: "transparent",
    title: {
      text: "日较差与平均气温散点分析",
      subtext: "按季节着色，观察日较差与气温的分布关系",
      left: "24px",
      top: "20px",
      textStyle: { color: "#e2eaf6", fontSize: 16, fontWeight: "bold" },
      subtextStyle: { color: "#4a7abf", fontSize: 12 },
    },
    tooltip: {
      trigger: "item",
      backgroundColor: "rgba(8, 15, 40, 0.92)",
      borderColor: "#1e3a6a",
      borderWidth: 1,
      textStyle: { color: "#e2eaf6", fontSize: 13 },
      formatter(param) {
        if (param.seriesType !== "scatter" || !param.data[2]) return "";
        const [temp, range, month] = param.data;
        return `<div style="margin-bottom:6px;font-weight:bold;color:#7eb8ff">${month}</div>
          <div style="display:flex;justify-content:space-between;gap:24px;margin:3px 0"><span>平均气温</span><span style="color:#fff;font-weight:bold">${temp.toFixed(2)}℃</span></div>
          <div style="display:flex;justify-content:space-between;gap:24px;margin:3px 0"><span>日较差</span><span style="color:#fff;font-weight:bold">${range.toFixed(2)}℃</span></div>`;
      },
    },
    legend: {
      data: [...seasons, "趋势线"],
      title: "线性拟合",
      right: "24px",
      top: "24px",
      textStyle: { color: "#94a3b8", fontSize: 13 },
      itemWidth: 12,
      itemHeight: 12,
    },
    grid: {
      left: "12px",
      right: "120px",
      bottom: "40px",
      top: "140px",
      containLabel: true,
    },
    xAxis: {
      type: "value",
      name: "平均气温 (℃)",
      nameTextStyle: { color: "#4a7abf", fontSize: 12 },
      axisLine: { lineStyle: { color: "#1e3a6a" } },
      axisTick: { show: false },
      axisLabel: { color: "#4a7abf", fontSize: 12 },
      splitLine: { lineStyle: { color: "#0f2040", type: "dashed" } },
    },
    yAxis: {
      type: "value",
      name: "日较差 (℃)",
      nameLocation: "end",
      nameGap: 15,
      nameTextStyle: {
        color: "#4a7abf",
        fontSize: 12,
        align: "left",
      },
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: "#4a7abf", fontSize: 12 },
      splitLine: { lineStyle: { color: "#0f2040", type: "dashed" } },
    },
    series: [
      ...seriesData,
      {
        name: "趋势线",
        type: "line",
        data: trendLineData,
        symbol: "none",
        lineStyle: { color: "#94a3b8", type: "dashed", width: 1.5 },
        tooltip: { show: false },
        z: 0,
      },
    ],
  };

  myChart.setOption(option);
};

watch(
  () => props.data,
  async (newData) => {
    if (newData && newData.length > 0) {
      await nextTick();
      initChart();
    }
  },
  { deep: true },
);

onMounted(() => {
  if (props.data && props.data.length > 0) {
    nextTick(initChart);
  }
  window.addEventListener("resize", () => myChart?.resize());
});
</script>

<template>
  <div class="chart-wrapper">
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<style scoped>
.chart-wrapper {
  background: rgba(8, 15, 40, 0.5);
  border: 1px solid #1e3a6a;
  border-radius: 12px;
  padding: 4px;
  box-shadow: 0 0 40px rgba(58, 143, 255, 0.06);
}

.chart-container {
  width: 100%;
  height: 480px;
}
</style>
