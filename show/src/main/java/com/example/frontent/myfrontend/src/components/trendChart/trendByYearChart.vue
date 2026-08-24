<template>
  <div class="chart-wrapper">
    <div v-if="loading" class="chart-loading">
      <span class="spinner"></span>
    </div>
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from "vue";
import * as echarts from "echarts";

// 1. 确保这里的 prop 名称与父组件传递的保持一致 (这里使用 trendYear)
const props = defineProps({
  trendYear: {
    type: Object,
    required: true,
  },
});

const chartRef = ref(null);
const loading = ref(true);
let myChart = null;

const initChart = () => {
  if (!chartRef.value) return;
  myChart = echarts.init(chartRef.value);

  const option = {
    title: { text: "温度年度趋势分析", textStyle: { color: "#fff" } },
    tooltip: { trigger: "axis" },
    // 关键点：添加一个空的 dataZoom 占位，保持布局和下方月度图一致
    dataZoom: [{ type: "slider", show: false }],
    legend: {
      data: ["最高温", "平均温", "最低温"],
      textStyle: { color: "#fff" },
    },
    // 关键点：将 bottom 设置为 80px，强制让绘图区和下面的图对齐
    grid: {
      top: "80px",
      left: "5%",
      right: "5%",
      bottom: "80px",
      containLabel: true,
    },
    xAxis: { type: "category", data: [], axisLabel: { color: "#fff" } },
    yAxis: {
      type: "value",
      name: "温度 (°C)",
      nameTextStyle: { color: "#fff" },
      axisLabel: { color: "#fff" },
    },
    series: [
      {
        name: "最高温",
        type: "line",
        itemStyle: { color: "#ff4d4f" },
        data: [],
      },
      {
        name: "平均温",
        type: "line",
        smooth: true,
        areaStyle: { opacity: 0.1 },
        itemStyle: { color: "#1890ff" },
        data: [],
      },
      {
        name: "最低温",
        type: "line",
        itemStyle: { color: "#52c41a" },
        data: [],
      },
    ],
  };
  myChart.setOption(option);
};

const updateChart = (data) => {
  if (!myChart || !data) return;
  myChart.setOption({
    xAxis: { data: data.xaxis },
    series: [
      { data: data.maxSeries },
      { data: data.avgSeries },
      { data: data.minSeries },
    ],
  });
  loading.value = false;
};

// 监听 trendYear 而不是 chartData
watch(
  () => props.trendYear,
  (newData) => {
    if (newData) updateChart(newData);
  },
  { deep: true },
);

const handleResize = () => myChart?.resize();

onMounted(() => {
  initChart();
  // 初始数据渲染也使用 trendYear
  if (props.trendYear) updateChart(props.trendYear);
  window.addEventListener("resize", handleResize);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", handleResize);
  myChart?.dispose();
});
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
  height: 350px; 
  margin-bottom: 20px;
  background: rgba(16, 24, 48, 0.4);
  border: 1px solid #1e293b;
  border-radius: 8px;
  padding: 10px;
}
</style>
