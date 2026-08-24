<script setup>  
import { getPrediction, getActualData } from '@/api/statisticApi'
import { onMounted, ref } from 'vue'
const forecastData = ref([])
const actualData = ref([])
const load = async () => {
    const res = await getPrediction()
    forecastData.value = res.data
    console.log("预报温度统计分析:", res.data)
    console.log("预报温度统计分析:", forecastData.value)
    const actualRes = await getActualData()
    actualData.value = actualRes.data
    console.log("真实数据2024:", actualRes.data)
    console.log("真实数据2024:", actualData.value)
}

onMounted(async () => {
    load()
})


</script>

<template>
  <div class="dashboard-wrapper">
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="label">MAE (平均绝对误差)</div>
        <div class="value">3.18 <small>℃</small></div>
      </div>
      <div class="metric-card">
        <div class="label">RMSE (均方根误差)</div>
        <div class="value">4.03 <small>℃</small></div>
      </div>
      <div class="metric-card">
        <div class="label">置信区间覆盖率</div>
        <div class="value">92.61 <small>%</small></div>
      </div>
    </div>

    <div class="chart-card">
      <linearChart 
        v-if="forecastData.length > 0 && actualData.length > 0" 
        :data="forecastData"
        :actualData="actualData"
      />
    </div>
  </div>
</template>

<style scoped>
.dashboard-wrapper {
  padding: 20px;
  background-color: #0f172a; /*深蓝黑 */
  border-radius: 12px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 25px;
}

.metric-card {
  background: rgba(30, 41, 59, 0.7); 
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 24px;
  border-radius: 12px;
  text-align: center;
  transition: background 0.3s;
}

.metric-card:hover {
  background: rgba(51, 65, 85, 0.9);
}

.label {
  font-size: 13px;
  color: #94a3b8; 
  margin-bottom: 10px;
}

.value {
  font-size: 28px;
  font-weight: 700;
  color: #f8fafc; 
}

.value small {
  font-size: 14px;
  color: #64748b;
}

.chart-card {
  background: #1e293b;
  padding: 20px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}
</style>