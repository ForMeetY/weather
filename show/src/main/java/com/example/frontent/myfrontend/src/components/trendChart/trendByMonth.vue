<!-- 气温月度趋势图 -->
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

const props = defineProps({
  trendMonth: {
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
    title: { text: "月度气温趋势 (20年回顾)", textStyle: { color: "#fff" } },
    tooltip: { trigger: "axis" },
    // 关键配置：添加数据缩放区域
    dataZoom: [
      { type: "slider", show: true, start: 80, end: 100 }, // 默认显示最后20%数据
      { type: "inside" }, // 支持鼠标滚轮缩放
    ],
    legend: {
      data: ["最高温", "平均温", "最低温"],
      bottom: "5%", // 靠底部
      left: "center", // 水平居中
      textStyle: { color: "#fff" },
    },
    // 同时需要增大 grid 的 bottom，防止图例遮挡底部数据
    legend: {
      data: ["最高温", "平均温", "最低温"],
      bottom: "15%", // 靠底部
      left: "center", // 水平居中
      textStyle: { color: "#fff" },
    },
    // 同时需要增大 grid 的 bottom，防止图例遮挡底部数据
    grid: {
      top: "80px",
      left: "5%",
      right: "5%",
      bottom: "100px",
      containLabel: true,
    },
    // 修改 initChart 中的 xAxis 部分
xAxis: {
  type: "category",
  data: [],
  axisLabel: { color: "#fff" },
  // 添加以下 splitLine 配置
  splitLine: {
    show: true,
    interval: (index, value) => {
      // 假设数据格式是 'yyyy-MM'，当月份为 '01' 时显示竖线
      return value.endsWith("-01");
    },
    lineStyle: {
      type: "dashed", // 虚线
      color: "pink", 
    },
  },
},
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
        data: [],
        itemStyle: { color: "#ff4d4f" },
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
        data: [],
        itemStyle: { color: "#52c41a" },
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

watch(
  () => props.trendMonth,
  (newData) => {
    if (newData) updateChart(newData);
  },
  { deep: true },
);

const handleResize = () => myChart?.resize();

onMounted(() => {
  initChart();
  if (props.trendMonth) updateChart(props.trendMonth);
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
  width: 100%; /* 充满父容器 */
  height: 350px; /* 统一设定高度，避免上下图高度不一致 */
  margin-bottom: 20px;
  background: rgba(16, 24, 48, 0.4);
  border: 1px solid #1e293b;
  border-radius: 8px;
  padding: 10px;
}
</style>
