<template>
  <div
    class="age-chart"
    ref="chartRef"
    style="width: 100%; height: 250px"
  ></div>
</template>

<script>
import * as echarts from "echarts";

export default {
  name: "AgeChart",
  props: {
    data: {
      type: Array,
      default: () => [
        { ageRange: "0-20", count: 10 },
        { ageRange: "21-40", count: 30 },
        { ageRange: "41-60", count: 50 },
        { ageRange: "60+", count: 20 },
      ],
    },
  },
  data() {
    return {
      chart: null,
    };
  },
  mounted() {
    this.initChart();
  },
  watch: {
    data: {
      deep: true,
      handler(newVal) {
        this.updateChart(newVal);
      },
    },
  },
  methods: {
    initChart() {
      const chartDom = this.$refs.chartRef;
      this.chart = echarts.init(chartDom);
      this.setChartOption(this.data);
      window.addEventListener("resize", this.handleResize);
    },
    setChartOption(data) {
      const xData = data.map((item) => item.ageRange);
      const yData = data.map((item) => item.count);
      const option = {
        tooltip: {
          trigger: "axis",
        },
        xAxis: {
          type: "category",
          data: xData,
        },
        yAxis: {
          type: "value",
        },
        series: [
          {
            data: yData,
            type: "bar",
            barWidth: "40%",
            itemStyle: {
              color: "#2D5BFF",
            },
          },
        ],
      };
      this.chart.setOption(option);
    },
    updateChart(newData) {
      if (this.chart) {
        this.setChartOption(newData);
      }
    },
    handleResize() {
      if (this.chart) {
        this.chart.resize();
      }
    },
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.handleResize);
    if (this.chart) {
      this.chart.dispose();
      this.chart = null;
    }
  },
};
</script>

<style scoped>
.age-chart {
  /* 可根据需要自定义样式 */
}
</style>
