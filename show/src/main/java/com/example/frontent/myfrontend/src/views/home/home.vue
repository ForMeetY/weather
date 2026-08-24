<script setup>
import { ref, onMounted } from "vue";
import {
  Cloudy,
  Share,
  TrendCharts,
  Histogram,
  Warning,
  Cpu,
} from "@element-plus/icons-vue";
import { getKpi } from "@/api/statisticApi";

// KPI 列表响应式数据
const kpiList = ref([
  {
    label: "年均气温（20年均值）",
    value: 0,
    unit: "℃",
    trend: "正在计算...",
    trendClass: "neu",
    color: "#3a8fff",
  },
  {
    label: "极端高温阈值",
    value: 0,
    unit: "℃",
    trend: "正在计算...",
    trendClass: "neu",
    color: "#00f58a",
  },
  {
    label: "极端低温阈值",
    value: 0,
    unit: "℃",
    trend: "正在计算...",
    trendClass: "neu",
    color: "#ff7b45",
  },
  {
    label: "气温日较差均值",
    value: 0,
    unit: "℃",
    trend: "正在计算...",
    trendClass: "neu",
    color: "#c07fff",
  },
]);

const load = async () => {
  try {
    const res = await getKpi();
    if (res && res.data) {
      const d = res.data;
      kpiList.value = [
        {
          label: "年均气温（20年均值）",
          value: d.avgAll ? d.avgAll.toFixed(1) : "0.0",
          unit: "℃",
          trend: "基于20年全量数据",
          trendClass: "neu",
          color: "#3a8fff",
        },
        {
          label: "极端高温阈值",
          value: d.highThreshold ? d.highThreshold.toFixed(1) : "0.0",
          unit: "℃",
          trend: "P95 分位界定",
          trendClass: "up",
          color: "#00f58a",
        },
        {
          label: "极端低温阈值",
          value: d.lowThreshold ? d.lowThreshold.toFixed(1) : "0.0",
          unit: "℃",
          trend: "P05 分位界定",
          trendClass: "dn",
          color: "#ff7b45",
        },
        {
          label: "气温日较差均值",
          value: d.avgRangeAll ? d.avgRangeAll.toFixed(1) : "0.0",
          unit: "℃",
          trend: "大陆性气候特征",
          trendClass: "neu",
          color: "#c07fff",
        },
      ];
    }
  } catch (error) {
    console.error("KPI数据加载失败", error);
  }
};

// 样本量动态计数
const counterDisplay = ref("0");
onMounted(() => {
  load();
  const target = 7305;
  let cur = 0;
  const tick = () => {
    if (cur < target) {
      cur = Math.min(cur + Math.ceil((target - cur) / 12), target);
      counterDisplay.value = cur.toLocaleString();
      requestAnimationFrame(tick);
    }
  };
  setTimeout(tick, 400);
});

// 数据治理链路数据
const chainSteps = [
  { name: "ODS 原始采集", sub: "日增数据入库" },
  { name: "DWD 清洗转换", sub: "缺失值补全 · 格式标准化" },
  { name: "DWS 特征工程", sub: "日较差计算 · 四季维度打标" },
  { name: "ADS 聚合统计", sub: "极端值计算 · 趋势预计算" },
  { name: "可视化看板", sub: "基于 ADS 高效渲染" },
];

// 核心功能导航数据
const funcList = [
  {
    name: "气温趋势分析",
    desc: "年 / 季 / 月三维度 · 20年变化规律",
    route: "/statistic/trend",
    icon: TrendCharts,
    tag: "TREND",
    color: "#3a8fff",
    borderColor: "#1a4a8a",
  },
  {
    name: "极端气温统计",
    desc: "高温 / 低温频次 · 科学阈值界定",
    route: "/statistic/extreme",
    icon: Warning,
    tag: "ALERT",
    color: "#ff7b45",
    borderColor: "#4a2010",
  },
  {
    name: "日较差分布",
    desc: "大陆性气候特征 · 季节差异分析",
    route: "/statistic/diurnal",
    icon: Histogram,
    tag: "DIST",
    color: "#c07fff",
    borderColor: "#3a1050",
  },
  {
    name: "预测建模",
    desc: "时序回归模型 · 未来气温研判",
    route: "/statistic/forecast",
    icon: Cpu,
    tag: "MODEL",
    color: "#00f58a",
    borderColor: "#004020",
  },
];
</script>

<template>
  <div class="wrap neon-grid-bg">
    <header class="hdr">
      <div class="hdr-left">
        <div class="hdr-icon">
          <el-icon class="cloudy-icon"><Cloudy /></el-icon>
        </div>
        <div>
          <h1 class="title">呼和浩特市气象智能分析平台</h1>
          <div class="subtitle">
            HOHHOT METEOROLOGICAL INTELLIGENCE SYSTEM · 2004–2023
          </div>
        </div>
      </div>
      <div class="hdr-right">
        <div class="status-indicator">
          <span class="status-dot"></span>
          <span class="status-text">系统正常运行</span>
        </div>
        <div class="meta-item">数据年限 <em class="accent">20 年</em></div>
        <div class="meta-item">
          样本量 <em class="accent tabular">{{ counterDisplay }} 条</em>
        </div>
        <div class="meta-item">更新时间 <em class="accent">2026-06-09</em></div>
      </div>
    </header>

    <main class="main-grid">
      <section class="panel chain-panel">
        <div class="panel-title">
          <el-icon><Share /></el-icon>
          <span>数据治理链路</span>
        </div>
        <div class="chain-container">
          <div v-for="(step, i) in chainSteps" :key="i" class="chain-step">
            <div class="step-dot-wrapper">
              <div class="step-dot">{{ i + 1 }}</div>
            </div>
            <div class="step-info">
              <div class="step-name">{{ step.name }}</div>
              <div class="step-sub">{{ step.sub }}</div>
            </div>
          </div>
        </div>
      </section>

      <section class="mid-col">
        <div class="kpi-grid">
          <div
            v-for="kpi in kpiList"
            :key="kpi.label"
            class="kpi-card"
            :style="{ '--accent-color': kpi.color }"
          >
            <div class="kpi-header">
              <span class="kpi-label">{{ kpi.label }}</span>
              <span class="kpi-trend" :class="kpi.trendClass">{{
                kpi.trend
              }}</span>
            </div>
            <div class="kpi-body">
              <span class="kpi-val tabular">{{ kpi.value }}</span>
              <span class="kpi-unit">{{ kpi.unit }}</span>
            </div>
          </div>
        </div>

        <div class="func-grid">
          <router-link
            v-for="fn in funcList"
            :key="fn.name"
            :to="fn.route"
            class="func-card"
            :style="{ '--fn-color': fn.color, '--fn-border': fn.borderColor }"
          >
            <div class="func-icon">
              <el-icon><component :is="fn.icon" /></el-icon>
            </div>
            <div class="func-body">
              <div class="func-name">{{ fn.name }}</div>
              <div class="func-desc">{{ fn.desc }}</div>
            </div>
            <span class="func-badge">{{ fn.tag }}</span>
          </router-link>
        </div>
      </section>
    </main>

    <footer class="bottom-bar">
      <div class="ticker">
        <div class="ticker-item">
          数据范围：<span class="highlight">2004.01.01 → 2023.12.31</span>
        </div>
        <div class="ticker-item">
          覆盖天数：<span class="highlight">7305 天</span>
        </div>
        <div class="ticker-item">
          关键要素：<span class="highlight">最高温 · 最低温 · 平均温</span>
        </div>
        <div class="ticker-item">
          核心维度：<span class="highlight">年 / 季 / 月 级多维聚合</span>
        </div>
      </div>
      <div class="copy">HOHHOT CLIMATE INTELLIGENCE © 2026</div>
    </footer>
  </div>
</template>

<style scoped>
.tabular {
  font-variant-numeric: tabular-nums;
}

.wrap {
  width: 100%;
  height: 100vh;
  padding: 20px 24px;
  background:
    radial-gradient(
      circle at 50% 0%,
      rgba(26, 54, 115, 0.4) 0%,
      transparent 60%
    ),
    linear-gradient(135deg, #070d19 0%, #03060b 100%);
  position: relative;
  color: #e2eaf6;
  font-family:
    "Inter",
    system-ui,
    -apple-system,
    sans-serif;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.neon-grid-bg::before {
  content: "";
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(58, 143, 255, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(58, 143, 255, 0.02) 1px, transparent 1px);
  background-size: 30px 30px;
  pointer-events: none;
  z-index: 0;
}

.hdr {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(58, 143, 255, 0.2);
  margin-bottom: 20px;
  flex-shrink: 0;
  z-index: 1;
}
.hdr-left {
  display: flex;
  align-items: center;
  gap: 16px;
}
.hdr-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(58, 143, 255, 0.1);
  border: 1px solid rgba(58, 143, 255, 0.3);
  box-shadow: 0 0 15px rgba(58, 143, 255, 0.2);
}
.cloudy-icon {
  font-size: 24px;
  color: #3a8fff;
}
.title {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 1px;
  color: #f8fafc;
  margin: 0;
}
.subtitle {
  font-size: 11px;
  letter-spacing: 1.5px;
  color: #64748b;
  margin-top: 4px;
  font-family: monospace;
}

.hdr-right {
  display: flex;
  align-items: center;
  gap: 24px;
  font-size: 13px;
  color: #94a3b8;
}
.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(0, 245, 138, 0.06);
  padding: 4px 10px;
  border-radius: 20px;
  border: 1px solid rgba(0, 245, 138, 0.2);
}
.status-dot {
  width: 8px;
  height: 8px;
  background: #00f58a;
  border-radius: 50%;
  box-shadow: 0 0 8px #00f58a;
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(0, 245, 138, 0.5);
  }
  70% {
    transform: scale(1);
    box-shadow: 0 0 0 6px rgba(0, 245, 138, 0);
  }
  100% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(0, 245, 138, 0);
  }
}
.status-text {
  font-size: 12px;
  color: #00f58a;
  font-weight: 500;
}
.meta-item em.accent {
  font-style: normal;
  color: #f8fafc;
  font-weight: 600;
  margin-left: 4px;
}

.main-grid {
  display: grid;
  grid-template-columns: 340px 1fr;
  gap: 20px;
  flex: 1;
  min-height: 0;
  z-index: 1;
}

.panel {
  background: rgba(10, 20, 42, 0.4);
  border: 1px solid rgba(58, 143, 255, 0.15);
  border-radius: 16px;
  backdrop-filter: blur(16px);
  padding: 24px;
  display: flex;
  flex-direction: column;
}
.panel-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 15px;
  font-weight: 600;
  color: #3a8fff;
  letter-spacing: 1px;
  margin-bottom: 24px;
}
.chain-container {
  flex: 1;
  overflow-y: auto;
  padding-right: 4px;
}
.chain-step {
  display: flex;
  gap: 18px;
  position: relative;
  padding-bottom: 24px;
}
.chain-step:not(:last-child)::after {
  content: "";
  position: absolute;
  left: 16px;
  top: 32px;
  width: 2px;
  height: calc(100% - 24px);
  background: linear-gradient(
    180deg,
    rgba(58, 143, 255, 0.4) 0%,
    rgba(58, 143, 255, 0.05) 100%
  );
}
.step-dot-wrapper {
  position: relative;
  z-index: 2;
}
.step-dot {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #0f1c3f;
  border: 2px solid rgba(58, 143, 255, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  color: #3a8fff;
  box-shadow: 0 0 10px rgba(58, 143, 255, 0.1);
}
.chain-step:hover .step-dot {
  border-color: #00f58a;
  color: #00f58a;
  box-shadow: 0 0 15px rgba(0, 245, 138, 0.4);
}
.step-name {
  font-size: 14px;
  font-weight: 600;
  color: #f1f5f9;
}
.step-sub {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
}

.mid-col {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
  justify-content: space-between;
}
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.kpi-card {
  background: rgba(15, 23, 42, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 14px;
  padding: 20px;
  position: relative;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.kpi-card::before {
  content: "";
  position: absolute;
  left: 0;
  top: 20px;
  bottom: 20px;
  width: 3px;
  background: var(--accent-color);
  border-radius: 0 4px 4px 0;
  box-shadow: 0 0 10px var(--accent-color);
}
.kpi-card:hover {
  background: rgba(30, 41, 59, 0.5);
  border-color: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}
.kpi-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.kpi-label {
  font-size: 13px;
  color: #94a3b8;
  font-weight: 500;
}
.kpi-trend {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 600;
}
.up {
  background: rgba(0, 245, 138, 0.1);
  color: #00f58a;
}
.dn {
  background: rgba(255, 123, 69, 0.1);
  color: #ff7b45;
}
.neu {
  background: rgba(192, 127, 255, 0.1);
  color: #c07fff;
}

.kpi-body {
  display: flex;
  align-items: baseline;
}
.kpi-val {
  font-size: 32px;
  font-weight: 700;
  color: #f8fafc;
}
.kpi-unit {
  font-size: 16px;
  color: #64748b;
  margin-left: 4px;
  font-weight: 500;
}

.func-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  flex: 1;
}
.func-card {
  background: rgba(15, 23, 42, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.03);
  border-radius: 14px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  position: relative;
  text-decoration: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.func-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  border: 1px solid var(--fn-border);
  background: rgba(15, 23, 42, 0.6);
  color: var(--fn-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  transition: all 0.3s;
}
.func-card:hover {
  background: rgba(30, 41, 59, 0.4);
  border-color: rgba(58, 143, 255, 0.3);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
}
.func-card:hover .func-icon {
  transform: scale(1.05);
  box-shadow: 0 0 15px var(--fn-color);
  background: var(--fn-color);
  color: #070d19;
}
.func-name {
  font-size: 15px;
  font-weight: 600;
  color: #f1f5f9;
}
.func-desc {
  font-size: 12px;
  color: #64748b;
  margin-top: 6px;
  line-height: 1.5;
}
.func-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  font-size: 10px;
  font-weight: 700;
  font-family: monospace;
  padding: 2px 6px;
  border-radius: 4px;
}

.bottom-bar {
  margin-top: auto;
  padding: 14px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  background: rgba(7, 13, 25, 0.8);
  backdrop-filter: blur(12px);
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #475569;
  flex-shrink: 0;
  z-index: 1;
}
.ticker {
  display: flex;
  gap: 32px;
}
.ticker-item {
  display: flex;
  align-items: center;
}
.highlight {
  color: #94a3b8;
  font-weight: 500;
  margin-left: 4px;
}
.copy {
  font-weight: 500;
  letter-spacing: 0.5px;
  color: #475569;
}
</style>
