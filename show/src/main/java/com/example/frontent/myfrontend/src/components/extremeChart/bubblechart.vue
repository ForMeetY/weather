<!--
  季节极端天气四象限气泡图
  Props:
    data: Array<SeasonExtremeVo>
      { season, highCount, lowCount, highAvgIntensity, lowAvgIntensity }
-->
<template>
  <div class="chart-wrapper">
    <div v-if="loading" class="chart-loading">
      <span class="spinner"></span>
    </div>
    <div class="chart-container" ref="chartRef"></div>
    <div class="chart-desc">
      <p>
        横轴为各季节<b>极端高温天数</b>，纵轴为<b>极端低温天数</b>，气泡大小反映<b>高温偏差强度</b>。
        右下角季节高温频繁但低温少，左上角则相反；气泡越大说明高温时偏离正常值越剧烈。
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

const SEASON_COLOR = {
  春: "#66bb6a",
  夏: "#ff7043",
  秋: "#ffa726",
  冬: "#42a5f5",
};

const initChart = async (dataList) => {
  await nextTick();
  if (!chartRef.value || !dataList || dataList.length === 0) return;

  loading.value = true;
  if (chart) chart.dispose();
  chart = echarts.init(chartRef.value);

  const maxIntensity = Math.max(
    ...dataList.map((d) => d.highAvgIntensity ?? 0),
    0.01,
  );

  const scatterData = dataList.map((d) => ({
    name: d.season,
    value: [d.highCount ?? 0, d.lowCount ?? 0, d.highAvgIntensity ?? 0],
    symbolSize: Math.max(((d.highAvgIntensity ?? 0) / maxIntensity) * 64, 18),
    itemStyle: {
      color: SEASON_COLOR[d.season] ?? "#90a4ae",
      opacity: 0.92,
      borderColor: "rgba(255,255,255,0.5)",
      borderWidth: 2,
    },
    emphasis: {
      itemStyle: {
        opacity: 1,
        borderColor: "#fff",
        borderWidth: 2.5,
        shadowBlur: 16,
        shadowColor: SEASON_COLOR[d.season] ?? "#90a4ae",
      },
    },
  }));

  const allHigh = dataList.map((d) => d.highCount ?? 0);
  const allLow = dataList.map((d) => d.lowCount ?? 0);
  const xMax = Math.ceil(Math.max(...allHigh) * 1.35);
  const yMax = Math.ceil(Math.max(...allLow) * 1.35);
  const xMid = Math.round(allHigh.reduce((a, b) => a + b, 0) / allHigh.length);
  const yMid = Math.round(allLow.reduce((a, b) => a + b, 0) / allLow.length);

  const option = {
    title: {
      text: "季节极端天气分布",
      left: "center",
      top: "3%",
      textStyle: { color: "#e2e8f0", fontSize: 18, fontWeight: "bold" },
    },

    tooltip: {
      trigger: "item",
      backgroundColor: "rgba(16,24,48,0.92)",
      borderColor: "#475569",
      borderWidth: 1,
      textStyle: { color: "#e2e8f0", fontSize: 12 },
      formatter: (p) => {
        const [hc, lc, intensity] = p.value;
        return `
          <div style="padding:4px 10px;line-height:2">
            <div style="margin-bottom:4px">
              <span style="display:inline-block;width:10px;height:10px;border-radius:50%;
                background:${p.color};margin-right:6px"></span>
              <b>${p.name}</b>
            </div>
            极端高温天数：<b>${hc}</b> 天<br/>
            极端低温天数：<b>${lc}</b> 天<br/>
            高温偏差强度：<b>${intensity.toFixed(3)}</b> ℃
          </div>`;
      },
    },

    graphic: [],

    grid: { top: "15%", bottom: "18%", left: "13%", right: "6%" },

    xAxis: {
      name: "极端高温天数（天）",
      nameLocation: "middle",
      nameGap: 30,
      nameTextStyle: { color: "#94a3b8", fontSize: 12 },
      min: 0,
      max: xMax,
      axisLine: { lineStyle: { color: "#475569" } },
      axisTick: { lineStyle: { color: "#475569" } },
      axisLabel: { color: "#94a3b8", fontSize: 12 },
      splitLine: { lineStyle: { color: "#1e293b", type: "dashed" } },
    },

    yAxis: {
      name: "极端低温天数（天）",
      nameLocation: "middle",
      nameGap: 44,
      nameTextStyle: { color: "#94a3b8", fontSize: 12 },
      min: 0,
      max: yMax,
      axisLine: { lineStyle: { color: "#475569" } },
      axisTick: { lineStyle: { color: "#475569" } },
      axisLabel: { color: "#94a3b8", fontSize: 12 },
      splitLine: { lineStyle: { color: "#1e293b", type: "dashed" } },
    },

    series: [
      {
        type: "scatter",
        data: scatterData,
        label: {
          show: true,
          formatter: (p) => p.name,
          position: "top",
          color: "#e2e8f0",
          fontSize: 13,
          fontWeight: "bold",
          distance: 8,
        },
        markLine: {
          silent: true,
          symbol: "none",
          lineStyle: { color: "#475569", type: "dashed", width: 1 },
          label: { show: false },
          data: [{ xAxis: xMid }, { yAxis: yMid }],
        },
        markPoint: {
          silent: true,
          symbol: "rect",
          symbolSize: 0,
          label: { show: true, fontSize: 10 },
          data: [
            {
              coord: [xMax * 0.75, yMax * 0.93],
            },
            {
              coord: [xMax * 0.25, yMax * 0.93],
            },
            {
              coord: [xMax * 0.75, yMax * 0.55],
            },
            {
              coord: [xMax * 0.25, yMax * 0.55],
            },
          ],
        },
      },
    ],
  };

  chart.setOption(option);
  loading.value = false;
};

watch(
  () => props.data,
  (val) => {
    if (val) initChart(val);
  },
  { deep: true, immediate: true },
);

const onResize = () => chart?.resize();
onMounted(() => window.addEventListener("resize", onResize));
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
  border-top: none;
  border-radius: 0 0 8px 8px;
  color: #94a3b8;
  font-size: 12px;
  line-height: 1.7;
}

.chart-desc b {
  color: #cbd5e1;
}
</style>
