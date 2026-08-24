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

  const seasons = props.data.map((item) => item.season);
  const boxData = props.data.map((item) => [
    item.minDailyRange,
    item.q1,
    item.median,
    item.q3,
    item.maxDailyRange,
  ]);

  // 春季用醒目的暖色突出显示，其他季节用统一灰蓝色弱化
  const seasonColors = props.data.map(
    (item) =>
      item.season === "春"
        ? { fill: "rgba(245,158,11,0.3)", border: "#f59e0b" } // 春-橙色高亮
        : { fill: "rgba(74,122,191,0.18)", border: "#4a7abf" }, // 其他-灰蓝弱化
  );

  // 异常点: 若后端在 item.outliers 中提供离散点数组则绘制
  const outlierData = [];
  props.data.forEach((item, index) => {
    if (Array.isArray(item.outliers)) {
      item.outliers.forEach((val) => outlierData.push([index, val]));
    }
  });

  // 计算夏秋冬三季中位数的平均值，作为参考线
  const otherSeasonsMedian = props.data
    .filter((item) => item.season !== "春")
    .map((item) => item.median);
  const refLineValue = otherSeasonsMedian.length
    ? otherSeasonsMedian.reduce((a, b) => a + b, 0) / otherSeasonsMedian.length
    : null;

  const option = {
    backgroundColor: "transparent",
    title: {
      text: "季节日较差分布",
      subtext: "春季昼夜温差显著高于其他季节",
      left: "24px",
      top: "20px",
      textStyle: { color: "#e2eaf6", fontSize: 16, fontWeight: "bold" },
      subtextStyle: { color: "#4a7abf", fontSize: 12 },
    },
    tooltip: {
      trigger: "item",
      axisPointer: { type: "shadow" },
      backgroundColor: "rgba(8, 15, 40, 0.92)",
      borderColor: "#1e3a6a",
      borderWidth: 1,
      textStyle: { color: "#e2eaf6", fontSize: 13 },
      formatter(param) {
        const v = param.data && (param.data.value || param.data);
        if (!Array.isArray(v) || v.length < 6) return "";
        return `<div style="margin-bottom:6px;font-weight:bold;color:#7eb8ff">${param.name}</div>
    <div style="display:flex;justify-content:space-between;gap:24px;margin:3px 0"><span>最大值</span><span style="color:#fff;font-weight:bold">${v[5].toFixed(2)}℃</span></div>
    <div style="display:flex;justify-content:space-between;gap:24px;margin:3px 0"><span>Q3</span><span style="color:#fff;font-weight:bold">${v[4].toFixed(2)}℃</span></div>
    <div style="display:flex;justify-content:space-between;gap:24px;margin:3px 0"><span>中位数</span><span style="color:#fff;font-weight:bold">${v[3].toFixed(2)}℃</span></div>
    <div style="display:flex;justify-content:space-between;gap:24px;margin:3px 0"><span>Q1</span><span style="color:#fff;font-weight:bold">${v[2].toFixed(2)}℃</span></div>
    <div style="display:flex;justify-content:space-between;gap:24px;margin:3px 0"><span>最小值</span><span style="color:#fff;font-weight:bold">${v[1].toFixed(2)}℃</span></div>`;
      },
    },
    grid: {
      left: "24px",
      right: "24px",
      bottom: "40px",
      top: "100px",
      containLabel: true,
    },
    xAxis: {
      type: "category",
      data: seasons,
      boundaryGap: true,
      axisLine: { lineStyle: { color: "#1e3a6a" } },
      axisTick: { show: false },
      axisLabel: { color: "#4a7abf", fontSize: 13 },
    },
    yAxis: {
      type: "value",
      name: "日温差 (℃)",
      nameTextStyle: { color: "#4a7abf", fontSize: 12 },
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: "#4a7abf", fontSize: 12 },
      splitLine: { lineStyle: { color: "#0f2040", type: "dashed" } },
    },
    series: [
      {
        name: "日温差",
        type: "boxplot",
        data: boxData.map((item, index) => ({
          value: item,
          itemStyle: {
            color: seasonColors[index].fill,
            borderColor: seasonColors[index].border,
            borderWidth: 2,
          },
        })),
        emphasis: {
          itemStyle: {
            borderWidth: 2.5,
            shadowBlur: 10,
            shadowColor: "rgba(126,184,255,0.6)",
          },
        },
        markLine:
          refLineValue !== null
            ? {
                silent: false,
                symbol: "none",
                lineStyle: { color: "#94a3b8", type: "dashed", width: 1.5 },
                label: {
                  color: "#94a3b8",
                  fontSize: 12,
                  formatter: () => `夏秋冬均值 ${refLineValue.toFixed(2)}℃`,
                  position: "end",
                },
                data: [{ yAxis: refLineValue }],
              }
            : undefined,
      },
      ...(outlierData.length
        ? [
            {
              name: "异常值",
              type: "scatter",
              data: outlierData,
              symbolSize: 8,
              itemStyle: {
                color: "#f43f5e",
                borderColor: "#fff",
                borderWidth: 1,
              },
              tooltip: {
                formatter: (p) =>
                  `<div style="color:#7eb8ff;font-weight:bold;margin-bottom:4px">${seasons[p.value[0]]}</div>
                 <div>异常值: <span style="color:#fff;font-weight:bold">${p.value[1].toFixed(2)}℃</span></div>`,
              },
            },
          ]
        : []),
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
