<!-- 
面积组合图
展示每年的平均偏差，它能展示天气极端到什么程度 
-->
<script setup>
import { ref, onMounted, watch } from "vue";
import * as echarts from "echarts";

/* 图表数据格式：{ highSeries, lowSeries, xaxis } */
const props = defineProps({ currentIntensity: Object });
console.log("areaChart data:", props.currentIntensity);
const chartRef = ref(null);
const loading = ref(true);

const initChart = () => {
  if (
    !props.currentIntensity ||
    !props.currentIntensity.lowSeries ||
    !props.currentIntensity.highSeries
  ) {
    console.warn("数据尚未准备好，跳过图表渲染");
    return;
  }

  loading.value = true;
  const chart = echarts.init(chartRef.value);

  // 处理低温数据为负值，实现双向展示
  const lowSeriesNeg = props.currentIntensity.lowSeries.map((val) => -val);

  const option = {
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    legend: {
      top: 20,
      data: ["高温偏差", "低温偏差"],
      textStyle: { color: "#fff" },
    },
    xAxis: {
      type: "category",
      data: props.currentIntensity.xaxis,
      axisLine: { lineStyle: { color: "#ccc" } },
    },
    yAxis: { type: "value", splitLine: { lineStyle: { color: "#334155" } } },
    dataZoom: [
      {
        type: "slider", // 底部滑动条
        show: true,
        xAxisIndex: [0],
        start: 0,
        end: 100, // 初始显示比例
        bottom: 10,
        borderColor: "#334155",
        fillerColor: "rgba(59, 130, 246, 0.2)",
      },
      {
        type: "inside", // 支持鼠标滚轮缩放
        xAxisIndex: [0],
        start: 0,
        end: 100,
      },
    ],
    grid: {
      top: "60px",
      bottom: "80px", // 增加底部距离
      left: "60px",
      right: "40px",
      containLabel: true,
    },
    series: [
      {
        name: "高温偏差",
        type: "line",
        areaStyle: { color: "rgba(239, 68, 68, 0.3)" }, // 红色区域
        lineStyle: { color: "#ef4444" },
        data: props.currentIntensity.highSeries,
      },
      {
        name: "低温偏差",
        type: "line",
        areaStyle: { color: "rgba(59, 130, 246, 0.3)" }, // 蓝色区域
        lineStyle: { color: "#3b82f6" },
        data: lowSeriesNeg, // 使用负值
      },
    ],
  };
  chart.setOption(option);
  loading.value = false;
};

onMounted(initChart);
watch(() => props.currentIntensity, initChart, { deep: true });
</script>

<template>
  <div class="chart-wrapper">
    <div v-if="loading" class="chart-loading">
      <span class="spinner"></span>
    </div>
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<style scoped>
.chart-wrapper {
  position: relative;
  width: 100%;
  height: 420px;
}
.chart-container {
  width: 100%;
  height: 100%;
  background: rgba(16, 24, 48, 0.4);
  border: 1px solid #1e293b;
  border-radius: 8px 8px 0 0;
}
.chart-loading {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(16, 24, 48, 0.6);
  border-radius: 8px 8px 0 0;
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
</style>
