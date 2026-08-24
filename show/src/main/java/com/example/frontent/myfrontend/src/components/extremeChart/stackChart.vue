<template>
  <div class="chart-wrapper">
    <div v-if="loading" class="chart-loading">
      <span class="spinner"></span>
    </div>
    <div
      class="chart-container"
      ref="chartRef"
      style="width: 100%; height: 400px"
    ></div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from "vue";
import * as echarts from "echarts";

const props = defineProps({ data: Object });
const chartRef = ref(null);
const loading = ref(true);
let chart = null;

const initChart = async (data) => {
  // 等待 DOM 渲染完成
  await nextTick();
  if (!chartRef.value) return;

  loading.value = true;

  // 如果已初始化，先销毁旧实例防止重叠
  if (chart) chart.dispose();

  chart = echarts.init(chartRef.value);
  const option = {
    textStyle: { color: "#ffffff" },
    title: {
      text: "2004-2023 极端天气频次演变",
      textStyle: { color: "#ffffff" },
    },
    tooltip: {
      trigger: "axis",
      formatter: (params) =>
        params
          .map((p) => `${p.seriesName}: ${Math.abs(p.value)} 天`)
          .join("<br/>"),
    },
    grid: {
      top: "80px",
      left: "5%",
      right: "5%",
      bottom: "100px", // 保持与 Anomaly Chart 一致的底部空间
      containLabel: true,
    },
    // 必须加入这个占位，否则底部的刻度对不齐
    dataZoom: [{ type: "slider", show: false }],
    legend: { textStyle: { color: "#ffffff" }, data: ["极端高温", "极端低温"] },
    xAxis: {
      type: "category",
      data: data.xaxis,
      axisLine: { lineStyle: { color: "#ffffff" } },
    },
    yAxis: {
      type: "value",
      axisLabel: { formatter: (v) => Math.abs(v), color: "#ffffff" },
    },
    series: [
      {
        name: "极端高温",
        type: "bar",
        stack: "total",
        data: data.highSeries,
        itemStyle: { color: "#ef5350" },
      },
      {
        name: "极端低温",
        type: "bar",
        stack: "total",
        data: data.lowSeries,
        itemStyle: { color: "#42a5f5" },
      },
    ],
  };
  chart.setOption(option);
  loading.value = false;
};

watch(
  () => props.data,
  (newData) => {
    if (newData?.xaxis) initChart(newData);
  },
  { deep: true, immediate: true },
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
</style>