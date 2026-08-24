<template>
  <div class="page-container">
    <TrendByYearChart v-if="trendYear" :trendYear="trendYear" />
    <TrendByMonthChart v-if="trendMonth" :trendMonth="trendMonth" />
    <AnomalyChart v-if="trendYear" :trendYear="trendYear" />
    <HeatmapCalendar v-if="heatmapData" :heatmapData="heatmapData" />
    <Footer />
  </div>
  
</template>

<script setup>
import { ref, onMounted } from "vue";
import { getTrendYear, getTrendMonth } from "@/api/statisticApi";
import TrendByYearChart from "@/components/trendChart/trendByYearChart.vue";
import TrendByMonthChart from "@/components/trendChart/trendByMonth.vue";
import AnomalyChart from "@/components/trendChart/AnomalyChart.vue";
import HeatmapCalendar from "@/components/trendChart/HeatmapCalendar.vue";
import Footer from "@/components/footer.vue";

const trendYear = ref(null);
const trendMonth = ref(null);
const heatmapData = ref(null);

const load = async () => {
  try {
    const resYear = await getTrendYear();
    const resMonth = await getTrendMonth();

    trendYear.value = resYear.data;
    trendMonth.value = resMonth.data;

    // 构造热力图数据
    const matrix = [];
    const years = resYear.data.xaxis;
    const monthTemps = resMonth.data.avgSeries;

    years.forEach((year, yIdx) => {
      for (let mIdx = 0; mIdx < 12; mIdx++) {
        matrix.push([yIdx, mIdx, monthTemps[yIdx * 12 + mIdx]]);
      }
    });

    heatmapData.value = { years: years, matrixData: matrix };
  } catch (e) {
    console.error("加载数据失败", e);
  }
};

onMounted(() => load());
</script>

<style scoped>
.page-container {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
</style>
