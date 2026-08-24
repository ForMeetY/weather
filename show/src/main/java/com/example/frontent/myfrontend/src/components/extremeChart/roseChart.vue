<!-- 玫瑰图 -->
<template>
  <div class="chart-wrapper">
    <div v-if="loading" class="chart-loading">
      <span class="spinner"></span>
    </div>
    <div class="chart-container" ref="chartRef"></div>
    <div class="chart-desc">
      <p>
        展示20年间极端高温与低温事件在四个季节的<b>发生天数分布</b>。柱体越长说明该季节极端天气越频繁；橙色为高温，蓝色为低温。可点击图例单独查看某类型。
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount, nextTick } from "vue";
import * as echarts from "echarts";

const props = defineProps({ data: Array });
const chartRef = ref(null);
const loading = ref(true);
let chart = null;

const initChart = async (dataList) => {
  await nextTick();
  if (!chartRef.value || !dataList || dataList.length === 0) return;

  loading.value = true;
  if (chart) chart.dispose();
  chart = echarts.init(chartRef.value);

  const seasons = dataList.map((item) => item.season);
  const highSeries = dataList.map((item) => item.highCount);
  const lowSeries = dataList.map((item) => item.lowCount);

  const option = {
    title: {
      text: "极端天气季节分布",
      left: "center",
      top: "3%",
      textStyle: { color: "#e2e8f0", fontSize: 18, fontWeight: "bold" },
    },

    tooltip: {
      trigger: "axis",
      axisPointer: { type: "cross", lineStyle: { color: "#ffffff44" } },
      backgroundColor: "rgba(16,24,48,0.92)",
      borderColor: "#334155",
      borderWidth: 1,
      textStyle: { color: "#e2e8f0", fontSize: 13 },
      formatter: (params) => {
        const season = params[0]?.axisValueLabel ?? "";
        const lines = params
          .map(
            (p) =>
              `<span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${p.color};margin-right:6px;"></span>${p.seriesName}：<b>${p.value}</b> 天`,
          )
          .join("<br/>");
        return `<div style="padding:4px 8px"><div style="margin-bottom:6px;font-weight:bold">${season}</div>${lines}</div>`;
      },
    },

    legend: {
      bottom: "3%",
      left: "center",
      itemWidth: 14,
      itemHeight: 14,
      itemGap: 24,
      icon: "roundRect",
      textStyle: { color: "#cbd5e1", fontSize: 13 },
      data: ["极端高温", "极端低温"],
      selectedMode: true, // 点击图例可单独显示/隐藏
    },

    polar: {
      center: ["50%", "50%"],
      radius: ["15%", "75%"],
    },

    angleAxis: {
      type: "category",
      data: seasons,
      startAngle: 90,
      clockwise: false,
      axisLine: { lineStyle: { color: "#ffffff33" } },
      axisTick: { lineStyle: { color: "#ffffff33" } },
      axisLabel: {
        color: "#94a3b8",
        fontSize: 14,
        fontWeight: "bold",
        margin: 12,
      },
      splitLine: { lineStyle: { color: "#ffffff14", type: "dashed" } },
    },

    radiusAxis: {
      min: 0,
      axisLabel: { color: "#64748b", fontSize: 11 },
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: "#ffffff18", type: "dashed" } },
    },

    series: [
      {
        type: "bar",
        name: "极端高温",
        data: highSeries,
        coordinateSystem: "polar",
        // 不堆叠：高温/低温各自独立，避免视觉遮挡
        barGap: "-30%", // 两组柱子适当重叠，视觉更紧凑
        barMaxWidth: 18,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "#ff7043" },
            { offset: 1, color: "#ef5350" },
          ]),
          borderRadius: [4, 4, 0, 0],
        },
        emphasis: {
          itemStyle: { color: "#ff8a65" },
        },
        label: {
          show: true,
          position: "outside", // 标签移到柱外，不遮挡柱体
          color: "#ffa07a",
          fontSize: 11,
          formatter: (p) => (p.value > 0 ? p.value : ""),
        },
      },
      {
        type: "bar",
        name: "极端低温",
        data: lowSeries,
        coordinateSystem: "polar",
        barGap: "-30%",
        barMaxWidth: 18,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "#64b5f6" },
            { offset: 1, color: "#1565c0" },
          ]),
          borderRadius: [4, 4, 0, 0],
        },
        emphasis: {
          itemStyle: { color: "#90caf9" },
        },
        label: {
          show: true,
          position: "outside",
          color: "#90caf9",
          fontSize: 11,
          formatter: (p) => (p.value > 0 ? p.value : ""),
        },
      },
    ],
  };

  chart.setOption(option);
  loading.value = false;
};

watch(
  () => props.data,
  (newData) => {
    if (newData) initChart(newData);
  },
  { deep: true, immediate: true },
);

const onResize = () => chart?.resize();

onMounted(() => {
  window.addEventListener("resize", onResize);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", onResize);
  chart?.dispose();
  chart = null;
});
</script>

<style scoped>
.chart-wrapper {
  position: relative;
  display: flex;
  flex-direction: column;
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
.chart-container {
  width: 100%;
  height: 420px;
  background: rgba(16, 24, 48, 0.4);
  border: 1px solid #1e293b;
  border-radius: 8px 8px 0 0;
  padding: 10px;
  box-sizing: border-box;
}

.chart-desc {
  padding: 10px 14px 12px;
  background: rgba(16, 24, 48, 0.4);
  border: 1px solid #1e293b;
  border-top: none; /* 和图表容器连在一起 */
  border-radius: 0 0 8px 8px;
  color: #64748b;
  font-size: 12px;
  line-height: 1.7;
}

.chart-desc b {
  color: #94a3b8;
}

/* 原来的 chart-container 圆角只保留上方 */
.chart-container {
  border-radius: 8px 8px 0 0;
}
</style>
