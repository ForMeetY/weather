<script setup>
import { onMounted, ref, watch, onBeforeUnmount } from "vue";
import * as echarts from "echarts";

const props = defineProps({
  data: {
    type: Array,
    default: () => [],
  },
  actualData: {
    type: Array,
    default: () => [],
  },
});

const chartRef = ref(null);
let chart = null;

const renderChart = () => {
  if (!chart || props.data.length === 0) return;

  const actualMap = new Map();
  props.actualData.forEach((item) => {
    if (item.date) {
      actualMap.set(item.date, item.avgTemp);
    }
  });

  const dates = props.data.map((item) => item.ds);
  const yhat = props.data.map((item) => item.yhat);

  const actualValues = dates.map((d) => actualMap.get(d) ?? null);

  chart.setOption({
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "cross",
      },
      formatter(params) {
        const idx = params[0].dataIndex;
        const row = props.data[idx];

        return `
          <b>${row.ds}</b><br/>
          预测值：${row.yhat.toFixed(2)} ℃<br/>
          真实值：${
            actualValues[idx] == null
              ? "-"
              : actualValues[idx].toFixed(2) + " ℃"
          }<br/>
          下界：${row.yhatLower.toFixed(2)} ℃<br/>
          上界：${row.yhatUpper.toFixed(2)} ℃
        `;
      },
    },

    legend: {
      top: 5,
      data: ["预测值", "真实值", "95%置信区间"],
    },

    grid: {
      left: "6%",
      right: "4%",
      bottom: "15%",
      containLabel: true,
    },

    dataZoom: [
      {
        type: "inside",
        start: 0,
        end: 30,
      },
      {
        type: "slider",
        start: 0,
        end: 30,
        bottom: 5,
      },
    ],

    xAxis: {
      type: "category",
      boundaryGap: false,
      data: dates,
      axisLabel: {
        interval: 30,
        formatter(value) {
          const arr = value.split("-");
          return `${parseInt(arr[1])}月${parseInt(arr[2])}日`;
        },
      },
    },

    yAxis: {
      type: "value",
      name: "气温(℃)",
      splitLine: {
        lineStyle: {
          type: "dashed",
        },
      },
    },

    series: [
      // ======== 置信区间 ========
      {
        name: "95%置信区间",
        type: "custom",
        silent: true,
        z: 1,
        renderItem(params, api) {
          const index = params.dataIndex;

          const x = api.coord([index, 0])[0];

          const upper = api.coord([
            index,
            props.data[index].yhatUpper,
          ]);

          const lower = api.coord([
            index,
            props.data[index].yhatLower,
          ]);

          const width =
            api.size([1, 0])[0] * 0.9;

          return {
            type: "rect",
            shape: {
              x: x - width / 2,
              y: upper[1],
              width,
              height: lower[1] - upper[1],
            },
            style: {
              fill: "rgba(133,183,235,0.22)",
            },
          };
        },
        data: dates,
      },

      // ======== 预测值 ========
      {
        name: "预测值",
        type: "line",
        data: yhat,
        smooth: true,
        symbol: "none",
        z: 3,
        lineStyle: {
          width: 2.5,
          color: "#d85a30",
        },
      },

      // ======== 真实值 ========
      {
        name: "真实值",
        type: "line",
        data: actualValues,
        smooth: true,
        symbol: "circle",
        symbolSize: 5,
        z: 4,
        lineStyle: {
          width: 2,
          color: "#5470c6",
        },
        itemStyle: {
          color: "#5470c6",
          borderColor: "#fff",
          borderWidth: 1,
        },
      },
    ],
  });
};

const resize = () => chart?.resize();

onMounted(() => {
  chart = echarts.init(chartRef.value);
  renderChart();
  window.addEventListener("resize", resize);
});

watch(
  () => [props.data, props.actualData],
  renderChart,
  {
    deep: true,
  }
);

onBeforeUnmount(() => {
  window.removeEventListener("resize", resize);
  chart?.dispose();
});
</script>

<template>
  <div
    ref="chartRef"
    style="width: 100%; height: 420px"
  ></div>
</template>