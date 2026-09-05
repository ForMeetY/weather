<script setup>
import { onBeforeUnmount, onMounted, ref, computed } from "vue";
import * as echarts from "echarts";

/**
 * shortChart.vue —— 短期预测回测（气候态+异常AR(1) vs GBDT 机器学习基线）
 * 图1: MAE vs 预测天数(lead) —— AR(1) 与 GBDT 双线对比
 * 图2: 多窗口 真实 vs AR(1) vs GBDT 温度曲线（可切换窗口/预测天数）
 * 数据源: /short_forecast.json（AR1）, /gbdt_backtest.json（GBDT）
 */
const maeChartRef = ref(null);
const winChartRef = ref(null);
let maeChart = null;
let winChart = null;
const ar1 = ref(null);
const gbdt = ref(null);
const winIdx = ref(0);
const days = ref(7);
const DAY_OPTIONS = [3, 7, 14, 30];

const winLabels = computed(() => (ar1.value?.windows || []).map((w) => w.label));
const curAR1 = computed(() => ar1.value?.windows?.[winIdx.value]?.window || []);
const curGBDT = computed(() => gbdt.value?.windows?.[winIdx.value]?.window || []);

const renderMaeChart = () => {
  if (!maeChart || !ar1.value || !gbdt.value) return;
  const L = 30;
  maeChart.setOption({
    tooltip: { trigger: "axis" },
    legend: { top: 5 },
    grid: { left: "7%", right: "4%", bottom: "10%", containLabel: true },
    xAxis: {
      type: "category",
      name: "预测天数 lead（天）",
      data: Array.from({ length: L }, (_, i) => i + 1),
      nameLocation: "middle",
      nameGap: 32,
    },
    yAxis: { type: "value", name: "MAE（℃）", splitLine: { lineStyle: { type: "dashed" } } },
    series: [
      {
        name: "气候态+异常AR(1)",
        type: "line",
        data: ar1.value.mae.slice(0, L),
        smooth: true,
        symbol: "circle",
        symbolSize: 5,
        lineStyle: { width: 2.2, color: "#2563eb" },
        itemStyle: { color: "#2563eb" },
        markLine: {
          symbol: "none",
          data: [
            {
              yAxis: ar1.value.long_mae_harmonic,
              lineStyle: { color: "#64748b", type: "dotted" },
              label: { formatter: "长期谐波 MAE " + ar1.value.long_mae_harmonic, color: "#64748b" },
            },
          ],
        },
      },
      {
        name: "GBDT(机器学习基线)",
        type: "line",
        data: gbdt.value.mae.slice(0, L),
        smooth: true,
        symbol: "square",
        symbolSize: 5,
        lineStyle: { width: 2.2, color: "#d85a30" },
        itemStyle: { color: "#d85a30" },
      },
    ],
  });
};

const renderWindowChart = () => {
  if (!winChart || !ar1.value || !gbdt.value) return;
  const n = Math.min(days.value, curAR1.value.length, curGBDT.value.length);
  const a = curAR1.value.slice(0, n);
  const g = curGBDT.value.slice(0, n);
  const dates = a.map((w) => w.date);
  winChart.setOption({
    tooltip: { trigger: "axis" },
    legend: { top: 5 },
    grid: { left: "7%", right: "4%", bottom: "14%", containLabel: true },
    xAxis: {
      type: "category",
      data: dates,
      axisLabel: {
        interval: Math.max(0, Math.floor(dates.length / 8) - 1),
        formatter(value) {
          const arr = value.split("-");
          return arr[1] + "/" + arr[2];
        },
      },
    },
    yAxis: { type: "value", name: "气温（℃）", splitLine: { lineStyle: { type: "dashed" } } },
    series: [
      {
        name: "真实值",
        type: "line",
        data: a.map((w) => w.y),
        smooth: true,
        symbol: "circle",
        symbolSize: 6,
        lineStyle: { width: 3, color: "#f8fafc" },
        itemStyle: { color: "#f8fafc", borderColor: "#94a3b8", borderWidth: 1 },
      },
      {
        name: "AR(1) 预测",
        type: "line",
        data: a.map((w) => w.yhat),
        smooth: true,
        symbol: "none",
        lineStyle: { width: 2.2, color: "#2563eb", type: "solid" },
      },
      {
        name: "GBDT 预测",
        type: "line",
        data: g.map((w) => w.yhat),
        smooth: true,
        symbol: "none",
        lineStyle: { width: 2.2, color: "#d85a30", type: "dashed" },
      },
    ],
  });
};

const onSwitch = () => renderWindowChart();
const resize = () => {
  maeChart?.resize();
  winChart?.resize();
};

onMounted(async () => {
  maeChart = echarts.init(maeChartRef.value);
  winChart = echarts.init(winChartRef.value);
  window.addEventListener("resize", resize);
  try {
    const [r1, rg] = await Promise.all([
      fetch("/short_forecast.json").then((r) => r.json()),
      fetch("/gbdt_backtest.json").then((r) => r.json()),
    ]);
    ar1.value = r1;
    gbdt.value = rg;
    renderMaeChart();
    renderWindowChart();
  } catch (e) {
    console.error("短期回测数据加载失败:", e);
  }
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", resize);
  maeChart?.dispose();
  winChart?.dispose();
});
</script>

<template>
  <div class="short-block">
    <div class="short-sub-title">① 误差随预测天数变化（2024 全年滚动回测：统计 vs 机器学习基线）</div>
    <div ref="maeChartRef" style="width: 100%; height: 300px"></div>

    <div class="short-sub-title">② 真实值 vs 预测值（切换窗口与预测天数，对比两种方法）</div>
    <div class="ctrl-row">
      <div class="ctrl-group">
        <span class="ctrl-label">窗口</span>
        <button
          v-for="(lab, i) in winLabels"
          :key="lab"
          class="ctrl-btn"
          :class="{ active: i === winIdx }"
          @click="winIdx = i; onSwitch()"
        >{{ lab }}</button>
      </div>
      <div class="ctrl-group">
        <span class="ctrl-label">预测</span>
        <button
          v-for="d in DAY_OPTIONS"
          :key="d"
          class="ctrl-btn"
          :class="{ active: d === days }"
          @click="days = d; onSwitch()"
        >{{ d }}天</button>
      </div>
    </div>
    <div ref="winChartRef" style="width: 100%; height: 320px"></div>
  </div>
</template>

<style scoped>
.short-sub-title {
  color: #94a3b8;
  font-size: 13px;
  margin: 8px 0;
}
.ctrl-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: center;
  margin-bottom: 6px;
}
.ctrl-group {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}
.ctrl-label {
  color: #64748b;
  font-size: 12px;
  margin-right: 2px;
}
.ctrl-btn {
  background: rgba(30, 41, 59, 0.8);
  color: #cbd5e1;
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 6px;
  padding: 3px 10px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}
.ctrl-btn:hover {
  border-color: #d85a30;
  color: #f8fafc;
}
.ctrl-btn.active {
  background: #d85a30;
  border-color: #d85a30;
  color: #fff;
}
</style>
