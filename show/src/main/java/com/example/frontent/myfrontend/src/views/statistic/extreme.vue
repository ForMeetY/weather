<script setup>
import { onMounted, ref, computed } from "vue";
import { getExtremeWeather } from "@/api/statisticApi";
import stackChart from "@/components/extremeChart/stackChart.vue";
import roseChart from "@/components/extremeChart/roseChart.vue";
import areaChart from "@/components/extremeChart/areaChart.vue";
import {
  getSeasonalExtremeWeather,
  getYearlyDeviation,
  getMonthlyDeviation,   // 👈 需要后端提供按月接口，见下方说明
} from "@/api/statisticApi";
import bubbleChart from "@/components/extremeChart/bubblechart.vue";
import Footer from "@/components/footer.vue";

const extremeWeather = ref({});
const seasonalData = ref([]);
const yearIntensity = ref({});
const monthIntensity = ref({});
const loading = ref(true);
const granularity = ref("year");



const currentIntensity = computed(() =>
  granularity.value === "month"
    ? monthIntensity.value
    : yearIntensity.value
);
console.log("currentIntensity.value:",currentIntensity.value);
const load = async () => {
  try {
    const res = await getExtremeWeather();
    extremeWeather.value = res.data;

    const roseData = await getSeasonalExtremeWeather();
    seasonalData.value = roseData.data;

    const yearData = await getYearlyDeviation();
    yearIntensity.value = yearData.data;

    const monthData = await getMonthlyDeviation();  // 按月接口
    monthIntensity.value = monthData.data;

    console.log("2. granularity:", granularity.value);
    console.log("3. currentIntensity:", currentIntensity.value);
  } finally {
    loading.value = false;
  }
};

onMounted(() => load());


</script>

<template>
  <div>
    <div v-if="loading">加载中...</div>
    <stackChart v-else-if="extremeWeather.xaxis" :data="extremeWeather" />

    <!-- 玫瑰图 + 气泡图并排 -->
    <div v-if="seasonalData.length > 0" style="display: flex; gap: 16px">
      <roseChart :data="seasonalData" style="flex: 1" />
      <bubbleChart :data="seasonalData" style="flex: 1" />
    </div>

    <!-- 面积组合图 + 粒度切换 -->
    <div v-if="currentIntensity.xaxis">
      <div class="granularity-selector">
        <span class="label">时间粒度：</span>
        <div class="tab-group">
          <button 
            :class="['tab-btn', { active: granularity === 'year' }]" 
            @click="granularity = 'year'"
          >按年</button>
          <button 
            :class="['tab-btn', { active: granularity === 'month' }]" 
            @click="granularity = 'month'"
          >按月</button>
        </div>
      </div>
      <areaChart :currentIntensity="currentIntensity" style="flex: 1" />
    </div>
    <Footer />
  </div>
</template>

<style scoped>
.granularity-selector {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  padding-left: 4px;
}
.label {
  color: #94a3b8;
  font-size: 14px;
  margin-right: 12px;
}
.tab-group {
  display: flex;
  background: rgba(30, 41, 59, 0.5);
  border-radius: 6px;
  padding: 2px;
  border: 1px solid #334155;
}
.tab-btn {
  padding: 4px 16px;
  border: none;
  background: transparent;
  color: #94a3b8;
  cursor: pointer;
  border-radius: 4px;
  font-size: 13px;
  transition: all 0.2s ease;
}
.tab-btn.active {
  background: #3b82f6;
  color: #fff;
}
</style>