<template>
  <div class="chart-container">
    <div class="chart-header">
      <h3 class="chart-title">{{ title }}</h3>
      <div class="chart-actions">
        <div class="year-filter">
          <select v-model="selectedYearRange" @change="updateChart">
            <option value="all">全部年份</option>
            <option value="recent3">近三年</option>
            <option value="recent5">近五年</option>
          </select>
        </div>
      </div>
    </div>

    <!-- 将数据摘要移到图表上方 -->
    <div class="data-summary">
      <div class="summary-item">
        <span class="summary-label">平均致死率:</span>
        <span class="summary-value">{{ averageDeathRate }}</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">城乡差异:</span>
        <span class="summary-value">{{ ruralUrbanDifference }}</span>
      </div>
    </div>

    <div class="chart-inner" ref="chartContainer"></div>
  </div>
</template>

<script>
import * as echarts from "echarts";

export default {
  name: "BarLineChart",
  props: {
    title: {
      type: String,
      default: "中国脑卒中致死率",
    },
  },
  data() {
    return {
      chart: null,
      selectedYearRange: "all",
      // 完整数据集
      allData: {
        years: ["2018", "2019", "2020", "2021", "2022", "2023", "2024"],
        ruralData: [150, 152, 155, 158, 160, 162, 165],
        cityData: [130, 131, 132, 133, 135, 136, 137],
      },
      // 当前显示的数据
      currentData: {
        years: [],
        ruralData: [],
        cityData: [],
        avgData: [],
      },
      // 统计数据
      averageDeathRate: "0",
      ruralUrbanDifference: "0",
    };
  },
  mounted() {
    this.initData();
    //this.initChart();
    this.$nextTick(() => {
      setTimeout(() => {
        this.initChart();
        window.addEventListener("resize", this.handleResize);
      }, 0);
    });
    // 添加延迟调整大小，确保在父容器完全渲染后调整
    //this.$nextTick(() => {
    //  setTimeout(() => {
    //    this.handleResize();
    //  }, 300);
    //});
  },

  updated() {
    // 在组件更新后重新调整大小
    //this.$nextTick(() => {
    //  this.handleResize();
    //});
  },
  beforeUnmount() {
    // 组件销毁前移除事件监听
    window.removeEventListener("resize", this.handleResize);
    if (this.chart) {
      this.chart.dispose();
      this.chart = null;
    }
  },
  methods: {
    initData() {
      // 初始化数据，默认显示全部年份
      this.filterDataByYearRange("all");
    },
    filterDataByYearRange(range) {
      const { years, ruralData, cityData } = this.allData;
      let filteredYears, filteredRuralData, filteredCityData;

      // ... existing code ...

      if (range === "recent3") {
        // 最近3年数据
        filteredYears = years.slice(-3);
        filteredRuralData = ruralData.slice(-3);
        filteredCityData = cityData.slice(-3);
      } else if (range === "recent5") {
        // 最近5年数据
        filteredYears = years.slice(-5);
        filteredRuralData = ruralData.slice(-5);
        filteredCityData = cityData.slice(-5);
      } else {
        // 全部数据
        filteredYears = [...years];
        filteredRuralData = [...ruralData];
        filteredCityData = [...cityData];
      }

      // 计算平均数据
      const filteredAvgData = filteredRuralData.map(
        (val, idx) => (val + filteredCityData[idx]) / 2
      );

      // 更新当前数据
      this.currentData = {
        years: filteredYears,
        ruralData: filteredRuralData,
        cityData: filteredCityData,
        avgData: filteredAvgData,
      };

      // 计算统计数据
      this.calculateStatistics();
    },
    calculateStatistics() {
      // ... existing code ...
      const { ruralData, cityData } = this.currentData;

      // 计算所有数据的平均值
      const allValues = [...ruralData, ...cityData];
      const average =
        allValues.reduce((sum, val) => sum + val, 0) / allValues.length;
      this.averageDeathRate = average.toFixed(1) + " /10万";

      // 计算城乡差异
      const differences = ruralData.map((rural, idx) => rural - cityData[idx]);
      const avgDifference =
        differences.reduce((sum, val) => sum + val, 0) / differences.length;
      this.ruralUrbanDifference = avgDifference.toFixed(1) + " /10万";
    },
    getChartOption() {
      const { years, ruralData, cityData, avgData } = this.currentData;

      // 设置固定的亮色主题
      const textColor = "#333";
      const axisLineColor = "#ccc";
      const splitLineColor = "rgba(0,0,0,0.05)";
      const backgroundColor = "#ffffff";

      // 渐变色配置
      const ruralBarGradient = new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: "#ffd166" },
        { offset: 1, color: "#f9c74f" },
      ]);

      const cityBarGradient = new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: "#a7e9af" },
        { offset: 1, color: "#90be6d" },
      ]);

      return {
        backgroundColor: backgroundColor,
        title: {
          show: false, // 使用自定义标题
        },
        tooltip: {
          trigger: "axis",
          axisPointer: {
            type: "shadow",
            shadowStyle: {
              color: "rgba(0,0,0,0.05)",
            },
          },
          backgroundColor: "rgba(255,255,255,0.9)",
          borderColor: "#ddd",
          borderWidth: 1,
          textStyle: {
            color: textColor,
          },
          formatter: function (params) {
            let result = `<div style="font-weight:bold;margin-bottom:5px;">${params[0].axisValue}年</div>`;

            params.forEach((param) => {
              const marker = `<span style="display:inline-block;margin-right:5px;border-radius:10px;width:10px;height:10px;background-color:${param.color};"></span>`;
              result += `<div>${marker}${param.seriesName}: <span style="float:right;font-weight:bold;margin-left:15px;">${param.value} /10万</span></div>`;
            });

            return result;
          },
          padding: [8, 12],
          extraCssText:
            "box-shadow: 0 3px 10px rgba(0,0,0,0.2); border-radius: 8px;",
        },
        legend: {
          data: ["农村", "城市", "平均"],
          top: 10,
          right: 10,
          itemWidth: 15,
          itemHeight: 10,
          textStyle: {
            color: textColor,
          },
          icon: "roundRect",
        },
        grid: {
          top: 60,
          left: "8%",
          right: "5%",
          bottom: 60,
          containLabel: true,
        },
        // 移除 coordinateSystem 配置
        xAxis: {
          type: "category",
          data: years,
          axisLine: {
            lineStyle: {
              color: axisLineColor,
            },
          },
          axisTick: {
            alignWithLabel: true,
            lineStyle: {
              color: axisLineColor,
            },
          },
          axisLabel: {
            color: textColor,
            fontSize: 12,
            formatter: "{value}年",
          },
        },
        yAxis: {
          type: "value",
          name: "致死率 (/10万)",
          nameTextStyle: {
            color: textColor,
            fontSize: 12,
            padding: [0, 0, 0, 40],
          },
          axisLine: {
            show: true,
            lineStyle: {
              color: axisLineColor,
            },
          },
          axisTick: {
            show: true,
          },
          axisLabel: {
            color: textColor,
          },
          splitLine: {
            lineStyle: {
              color: splitLineColor,
              type: "dashed",
            },
          },
        },
        series: [
          {
            name: "农村",
            type: "bar",
            data: ruralData,
            barWidth: "20%",
            barGap: "30%",
            // 移除所有与极坐标系统相关的配置
            itemStyle: {
              color: ruralBarGradient,
              borderRadius: [4, 4, 0, 0],
            },
            emphasis: {
              itemStyle: {
                color: "#ffba08",
              },
            },
            animationDelay: function (idx) {
              return idx * 100;
            },
          },
          {
            name: "城市",
            type: "bar",
            data: cityData,
            barWidth: "20%",
            // 移除所有与极坐标系统相关的配置
            itemStyle: {
              color: cityBarGradient,
              borderRadius: [4, 4, 0, 0],
            },
            emphasis: {
              itemStyle: {
                color: "#70e000",
              },
            },
            animationDelay: function (idx) {
              return idx * 100 + 50;
            },
          },
          {
            name: "平均",
            type: "line",
            data: avgData,
            // 移除所有与极坐标系统相关的配置
            smooth: true,
            symbol: "circle",
            symbolSize: 8,
            lineStyle: {
              color: "#4361ee",
              width: 3,
              shadowColor: "rgba(0, 0, 0, 0.3)",
              shadowBlur: 10,
              shadowOffsetY: 5,
            },
            itemStyle: {
              color: "#4361ee",
              borderColor: "#fff",
              borderWidth: 2,
            },
            emphasis: {
              scale: true,
              itemStyle: {
                shadowColor: "rgba(0, 0, 0, 0.5)",
                shadowBlur: 10,
              },
            },
            animationDelay: function (idx) {
              return idx * 150 + 100;
            },
          },
        ],
        animationEasing: "elasticOut",
        animationDelayUpdate: function (idx) {
          return idx * 5;
        },
      };
    },
    initChart() {
      try {
        const chartDom = this.$refs.chartContainer;
        if (!chartDom) {
          console.error("Chart container not found");
          return;
        }

        this.chart = echarts.init(chartDom);

        // 使用配置项生成图表
        const option = this.getChartOption();
        this.chart.setOption(option);
        // 添加点击事件
        //this.chart.on("click", this.handleChartClick);
      } catch (error) {
        console.error("Failed to initialize chart:", error);
      }
    },

    updateChart() {
      try {
        // 根据选择的年份范围过滤数据
        this.filterDataByYearRange(this.selectedYearRange);

        // 更新图表 - 使用不同的方式更新图表
        if (this.chart) {
          // 销毁并重新创建图表，避免更新时的冲突
          this.chart.dispose();
          this.chart = null;

          // 重新初始化图表
          this.$nextTick(() => {
            const chartDom = this.$refs.chartContainer;
            if (chartDom) {
              this.chart = echarts.init(chartDom);
              const option = this.getChartOption();
              this.chart.setOption(option);

              // 重新绑定点击事件
              this.chart.on("click", this.handleChartClick);
            }
          });
        }
      } catch (error) {
        console.error("Failed to update chart:", error);
      }
    },
    handleResize() {
      if (this.chart) {
        this.chart.resize();
      }
    },
    handleChartClick(params) {
      // 发出点击事件
      this.$emit("item-click", params);
    },
  },
};
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 100%; /* 保持 100% 高度 */
  min-height: 300px; /* 减小最小高度 */
  max-height: 100%; /* 添加最大高度限制 */
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
}

.chart-container:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  transform: translateY(-3px); /* 减小悬停时的上移距离 */
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px; /* 减小内边距 */
  border-bottom: 1px solid #f0f0f0;
}

.chart-title {
  font-size: 16px; /* 减小字体大小 */
  font-weight: 600;
  color: #333;
  margin: 0;
}

.chart-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.year-filter select {
  padding: 4px 8px;
  border-radius: 6px;
  border: 1px solid #ddd;
  background-color: #f9f9f9;
  color: #555;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.year-filter select:hover {
  border-color: #bbb;
}

.year-filter select:focus {
  outline: none;
  border-color: #4361ee;
  box-shadow: 0 0 0 2px rgba(67, 97, 238, 0.2);
}

.chart-inner {
  flex: 1;
  width: 100%;
  min-height: 200px; /* 减小图表的最小高度 */
  max-height: calc(100% - 120px); /* 限制图表最大高度，减去头部和摘要的高度 */
  padding: 5px;
  overflow: hidden; /* 防止内容溢出 */
}

/* 移动数据摘要到图表上方 */
.data-summary {
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 8px 15px; /* 减小内边距 */
  background-color: #f9f9f9;
  border-bottom: 1px solid #f0f0f0;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.summary-label {
  font-size: 14px;
  color: #666;
}

.summary-value {
  font-size: 18px;
  font-weight: 600;
  color: #4361ee;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .chart-container {
    min-height: 350px; /* 减小移动端的最小高度 */
  }

  .chart-inner {
    min-height: 180px; /* 减小移动端图表的最小高度 */
  }

  .chart-title {
    font-size: 16px;
  }

  .chart-actions {
    flex-direction: column;
    align-items: flex-end;
    gap: 8px;
  }

  .data-summary {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
}
</style>
