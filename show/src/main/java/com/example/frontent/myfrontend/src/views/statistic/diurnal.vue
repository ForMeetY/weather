<script setup>
import StackedAreaChart from "@/components/distributionChart/stackedAreaChart.vue";
import Footer from "@/components/footer.vue";
import { ref, onMounted } from "vue";
import {
  getDiurnalDeviation,
  getSeasonalDeviation,
  getScatterChart,
  getMonthlyDeviationLine,
} from "@/api/statisticApi";

import ScatterChart from "@/components/distributionChart/scatterChart.vue";
import LineChart from "@/components/distributionChart/lineChart.vue";


const diurnalData = ref([]);
const seasonalBoxData = ref([]);
const scatterData = ref([]);
const monthlyLineData = ref([]);
const load = async () => {
  const res = await getDiurnalDeviation();
  diurnalData.value = res.data;
  console.log("日差温度统计分析:", diurnalData.value);
  const seasonalRes = await getSeasonalDeviation();
  const seasonalData = seasonalRes.data;
  console.log("日差季节分布箱线图:", seasonalData);
  seasonalBoxData.value = seasonalData;
  const scatterRes = await getScatterChart();
  scatterData.value = scatterRes.data;
  console.log("日差与平均气温散点图:", scatterData.value);
  monthlyLineData.value = await getMonthlyDeviationLine();
  console.log("月度平均日较差:", monthlyLineData.value);
};
onMounted(async () => {
  load();
});
</script>

<template>
  <div>
    <LineChart
      v-if="monthlyLineData.data"
      :data="monthlyLineData.data"
      style="flex: 1"
    />
    <StackedAreaChart
      v-if="diurnalData.length > 0"
      :data="diurnalData"
      style="flex: 1"
    />

    <ScatterChart
      v-if="scatterData.length > 0"
      :data="scatterData"
      style="flex: 1"
    />

    <Footer />
  </div>
</template>

<style scoped>
h1 {
  color: white;
}
</style>
