<script setup>
import { ref, onMounted, watch, nextTick } from "vue";
import * as echarts from "echarts";

const props = defineProps({
  data: { type: Array, default: () => [] },
});

const chartRef = ref(null);
let myChart = null;

const initChart = () => {
  if (!chartRef.value) return;
  if (myChart) {
    myChart.dispose();
    myChart = null;
  }

  myChart = echarts.init(chartRef.value);

  const months = props.data.map((item) => item.monthDimension);
  const avgData = props.data.map((item) => item.avgDailyRange);
  const maxData = props.data.map((item) => item.maxDailyRange);
  const minData = props.data.map((item) => item.minDailyRange);

  const overallAvg = avgData.length
    ? avgData.reduce((a, b) => a + b, 0) / avgData.length
    : null;

  const option = {
    backgroundColor: "transparent",
    title: {
      text: "月度平均日较差趋势",
      subtext: "阴影区域为该月日较差波动范围（最小值~最大值）",
      left: "24px",
      top: "20px",
      textStyle: { color: "#e2eaf6", fontSize: 16, fontWeight: "bold" },
      subtextStyle: { color: "#4a7abf", fontSize: 12 },
    },
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "cross", crossStyle: { color: "#3b82f6" } },
      backgroundColor: "rgba(8, 15, 40, 0.92)",
      borderColor: "#1e3a6a",
      borderWidth: 1,
      textStyle: { color: "#e2eaf6", fontSize: 13 },
      formatter(params) {
        const idx = params[0].dataIndex;
        const item = props.data[idx];
        return `<div style="margin-bottom:6px;font-weight:bold;color:#7eb8ff">${item.monthDimension}</div>
          <div style="display:flex;justify-content:space-between;gap:24px;margin:3px 0"><span>平均值</span><span style="color:#fff;font-weight:bold">${item.avgDailyRange.toFixed(2)}℃</span></div>
          <div style="display:flex;justify-content:space-between;gap:24px;margin:3px 0"><span>最大值</span><span style="color:#fff;font-weight:bold">${item.maxDailyRange.toFixed(2)}℃</span></div>
          <div style="display:flex;justify-content:space-between;gap:24px;margin:3px 0"><span>最小值</span><span style="color:#fff;font-weight:bold">${item.minDailyRange.toFixed(2)}℃</span></div>`;
      },
    },
    legend: {
      data: ["平均日较差", "波动范围(最小~最大)"],
      right: "104px",
      top: "24px",
      textStyle: { color: "#94a3b8", fontSize: 13 },
      selectedMode: false,
    },
    grid: {
      left: "40px",
      right: "100px",
      bottom: "60px",
      top: "120px",
      containLabel: true,
    },
    xAxis: {
      type: "category",
      boundaryGap: false,
      data: months,
      axisLine: { lineStyle: { color: "#1e3a6a" } },
      axisLabel: { color: "#4a7abf", fontSize: 11, rotate: 45 },
    },
    yAxis: {
      type: "value",
      name: "日较差 (℃)",
      nameLocation: "end",
      nameTextStyle: {
        color: "#94a3b8",
        fontSize: 12,
        padding: [0, 0, 0, -30],
      },
      axisLine: { show: false },
      axisLabel: { color: "#4a7abf", fontSize: 12 },
      splitLine: { lineStyle: { color: "#0f2040", type: "dashed" } },
    },
    dataZoom: [
      {
        type: "slider",
        bottom: 10,
        height: 20,
        borderColor: "#1e3a6a",
        fillerColor: "rgba(58,143,255,0.15)",
      },
      { type: "inside" },
    ],
    series: [
      {
        name: "max-helper",
        type: "line",
        data: minData,
        lineStyle: { opacity: 0 },
        showSymbol: false,
        stack: "range-band",
        tooltip: { show: false },
        z: 1,
      },
      {
        name: "波动范围(最小~最大)",
        type: "line",
        data: maxData.map((max, i) => max - minData[i]),
        lineStyle: { opacity: 0 },
        showSymbol: false,
        stack: "range-band",
        smooth: true,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "rgba(96, 165, 250, 0.4)" },
            { offset: 1, color: "rgba(96, 165, 250, 0.15)" },
          ]),
        },
        z: 1,
      },
      {
        name: "平均日较差",
        type: "line",
        data: avgData,
        smooth: true,
        symbol: "circle",
        symbolSize: 8,
        lineStyle: {
          width: 3,
          color: "#60a5fa",
          shadowBlur: 8,
          shadowColor: "rgba(96, 165, 250, 0.6)",
        },
        itemStyle: { color: "#3b82f6", borderWidth: 2, borderColor: "#fff" },
        emphasis: { scale: 1.5 },
        z: 3,
        markLine:
          overallAvg !== null
            ? {
                silent: true,
                symbol: "none",
                lineStyle: { color: "#94a3b8", type: "dashed", width: 1.5 },
                label: {
                  formatter: () => `均值 ${overallAvg.toFixed(2)}℃`,
                  position: "end",
                },
                data: [{ yAxis: overallAvg }],
              }
            : undefined,
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
