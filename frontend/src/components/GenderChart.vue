<template>
  <div class="gender-chart" ref="chartRef" style="width: 100%; height: 250px;"></div>
</template>

<script>
import * as echarts from "echarts";

export default {
  name: "GenderChart",
  props: {
    data: {
      type: Array,
      default: () => ([
        { name: "男", value: 60 },
        { name: "女", value: 40 },
      ]),
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
      }
    }
  },
  methods: {
    initChart() {
      const chartDom = this.$refs.chartRef;
      this.chart = echarts.init(chartDom);
      this.setChartOption(this.data);
      window.addEventListener("resize", this.handleResize);
    },
    setChartOption(data) {
      const option = {
        tooltip: {
          trigger: "item",
        },
        legend: {
          bottom: "0",
          left: "center",
        },
        color: ["#93AAFD", "#2D5BFF"],
        series: [
          {
            name: "性别",
            type: "pie",
            radius: "50%",
            data: data,
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: "rgba(0, 0, 0, 0.5)",
              },
            },
            label: {
              formatter: "{b}",
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
.gender-chart {
  width: 100%;
  /* 可根据需要自定义高度或其他样式 */
}
</style>
