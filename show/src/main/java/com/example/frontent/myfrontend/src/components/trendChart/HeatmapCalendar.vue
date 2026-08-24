<template>
  <div class="chart-wrapper">
    <div v-if="loading" class="chart-loading">
      <span class="spinner"></span>
    </div>
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from "vue";
import * as echarts from "echarts";

const props = defineProps({ heatmapData: Object });
const chartRef = ref(null);
const loading = ref(true);
let myChart = null;

const initChart = () => {
  nextTick(() => {
    if (!chartRef.value) return;
    myChart = echarts.init(chartRef.value);

    const option = {
      title: {
        text: "20年气温演变热力矩阵",
        subtext:
          "解读：颜色越红气温越高 | 红色块垂直扩展说明夏季变长 | 整体右移说明长期变暖",
        left: "center",
        textStyle: { color: "#fff", fontSize: 16 },
        subtextStyle: { color: "#8a99ad", fontSize: 12 },
      },
      tooltip: {
        position: "top",
        formatter: (p) =>
          `${p.data[0] + 2004}年 ${p.data[1] + 1}月: ${p.data[2]}°C`,
      },
      grid: {
        top: "100px",
        left: "5%",
        right: "5%",
        bottom: "100px",
        containLabel: true,
      },
      xAxis: { type: "category", axisLabel: { color: "#8a99ad", rotate: 45 } },
      yAxis: {
        type: "category",
        data: [
          "1月",
          "2月",
          "3月",
          "4月",
          "5月",
          "6月",
          "7月",
          "8月",
          "9月",
          "10月",
          "11月",
          "12月",
        ],
        axisLabel: { color: "#8a99ad" },
      },
      visualMap: {
        min: -15,
        max: 35,
        calculable: true,
        orient: "horizontal",
        left: "center",
        bottom: "10px",
        inRange: {
          color: [
            "#313695", // 极寒 深蓝
            "#4575b4",
            "#74add1", // 偏冷 浅蓝
            "#e0f3f8", // 凉爽 极浅蓝
            "#ffffbf", // 适宜 淡黄 (作为中间过渡色，取代纯白)
            "#fee090",
            "#fdae61", // 温暖 橙色
            "#f46d43",
            "#d73027", // 炎热 红色
            "#a50026", // 酷热 暗红
          ],
        },
      },
      series: [
        {
          type: "heatmap",
          label: { show: false },
          emphasis: { itemStyle: { borderColor: "#fff", borderWidth: 1 } },
        },
      ],
    };
    myChart.setOption(option);
    if (props.heatmapData) updateChart(props.heatmapData);
    else loading.value = false;
  });
};

const updateChart = (data) => {
  if (!myChart || !data) return;
  myChart.setOption({
    xAxis: { data: data.years },
    series: [{ data: data.matrixData }],
  });
  loading.value = false;
};

onMounted(() => {
  initChart();
  window.addEventListener("resize", () => myChart?.resize());
});

watch(
  () => props.heatmapData,
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
  height: 550px;
  background: rgba(16, 24, 48, 0.4);
  border: 1px solid #1e293b;
  border-radius: 8px;
  padding: 10px;
  margin-bottom: 20px;
}
</style>
