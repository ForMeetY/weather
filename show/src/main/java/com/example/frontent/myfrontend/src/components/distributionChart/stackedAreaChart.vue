<script setup>
import { ref, onMounted, watch,nextTick } from "vue";
import * as echarts from "echarts";

const props = defineProps({
  data: { type: Array, default: () => [] }
});

const chartRef = ref(null);
let myChart = null;

const initChart = () => {
  if (!chartRef.value) {
    console.warn("DOM 尚未挂载，跳过初始化");
    return;
  }
  
  // 销毁旧实例
  if (myChart) {
    myChart.dispose();
    myChart = null;
  }

  myChart = echarts.init(chartRef.value);
  const years = props.data.map(item => item.year);

  const option = {
    backgroundColor: "transparent",

    title: {
      text: "日较差分布趋势",
      subtext: "各年度日温差区间占比分析",
      left: "24px",
      top: "20px",
      textStyle: { color: "#e2eaf6", fontSize: 16, fontWeight: "bold" },
      subtextStyle: { color: "#4a7abf", fontSize: 12 },
    },

    tooltip: {
      trigger: "axis",
      axisPointer: { type: "cross", label: { backgroundColor: "#1e3a5f" } },
      backgroundColor: "rgba(8, 15, 40, 0.92)",
      borderColor: "#1e3a6a",
      borderWidth: 1,
      textStyle: { color: "#e2eaf6", fontSize: 13 },
      formatter(params) {
        const total = params.reduce((s, p) => s + p.value, 0);
        let html = `<div style="margin-bottom:6px;font-weight:bold;color:#7eb8ff">${params[0].axisValue} 年</div>`;
        params.forEach(p => {
          const pct = total ? ((p.value / total) * 100).toFixed(1) : 0;
          html += `<div style="display:flex;justify-content:space-between;gap:24px;margin:3px 0">
            <span>${p.marker}${p.seriesName}</span>
            <span style="color:#fff;font-weight:bold">${p.value} 天 <span style="color:#64748b">(${pct}%)</span></span>
          </div>`;
        });
        return html;
      },
    },

    legend: {
      data: ["0–5℃", "5–10℃", "10–15℃", ">15℃"],
      right: "24px",
      top: "24px",
      textStyle: { color: "#94a3b8", fontSize: 13 },
      itemWidth: 12,
      itemHeight: 12,
      borderRadius: 2,
    },

    grid: { left: "24px", right: "24px", bottom: "60px", top: "100px", containLabel: true },

    xAxis: {
      type: "category",
      boundaryGap: false,
      data: years,
      axisLine: { lineStyle: { color: "#1e3a6a" } },
      axisTick: { show: false },
      axisLabel: { color: "#4a7abf", fontSize: 12 },
    },

    yAxis: {
      type: "value",
      name: "天数",
      nameTextStyle: { color: "#4a7abf", fontSize: 12 },
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: "#4a7abf", fontSize: 12 },
      splitLine: { lineStyle: { color: "#0f2040", type: "dashed" } },
    },

    dataZoom: [
      { type: "slider", bottom: 10, height: 20, borderColor: "#1e3a6a", fillerColor: "rgba(58,143,255,0.15)", textStyle: { color: "#4a7abf" } },
      { type: "inside" },
    ],

    color: ["#3b82f6", "#06b6d4", "#f59e0b", "#f43f5e"],

    series: [
      {
        name: "0–5℃",
        type: "line", stack: "Total",
        smooth: true, lineStyle: { width: 0 }, showSymbol: false,
        areaStyle: { opacity: 0.85, color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: "rgba(59,130,246,0.9)" }, { offset: 1, color: "rgba(59,130,246,0.3)" }]) },
        emphasis: { focus: "series" },
        data: props.data.map(i => i.range0to5),
      },
      {
        name: "5–10℃",
        type: "line", stack: "Total",
        smooth: true, lineStyle: { width: 0 }, showSymbol: false,
        areaStyle: { opacity: 0.85, color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: "rgba(6,182,212,0.9)" }, { offset: 1, color: "rgba(6,182,212,0.3)" }]) },
        emphasis: { focus: "series" },
        data: props.data.map(i => i.range5to10),
      },
      {
        name: "10–15℃",
        type: "line", stack: "Total",
        smooth: true, lineStyle: { width: 0 }, showSymbol: false,
        areaStyle: { opacity: 0.85, color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: "rgba(245,158,11,0.9)" }, { offset: 1, color: "rgba(245,158,11,0.3)" }]) },
        emphasis: { focus: "series" },
        data: props.data.map(i => i.range10to15),
      },
      {
        name: ">15℃",
        type: "line", stack: "Total",
        smooth: true, lineStyle: { width: 0 }, showSymbol: false,
        areaStyle: { opacity: 0.85, color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: "rgba(244,63,94,0.9)" }, { offset: 1, color: "rgba(244,63,94,0.3)" }]) },
        emphasis: { focus: "series" },
        data: props.data.map(i => i.rangeOver15),
      },
    ],
  };

  myChart.setOption(option);
};

// 删掉 onMounted 里的 initChart()，改成：
// 使用 watch 监听，但移除 immediate: true，改用手动调用
watch(() => props.data, async (newData) => {
  if (newData && newData.length > 0) {
    await nextTick(); // 确保 DOM 更新完毕
    initChart();
  }
}, { deep: true });

onMounted(() => {
  // 组件挂载后，检查是否有数据，有则初始化
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