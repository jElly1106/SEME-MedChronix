<template>
  <div class="chart-section">
    <div class="chart-wrapper">
      <!-- 刷新按钮放在外层，确保不被 ECharts 覆盖 -->
      <!-- <button class="refresh-button" @click="refreshChart">
        <i class="refresh-icon">↻</i>
      </button> -->
      <!-- 图表容器，供 ECharts 挂载 -->
      <div class="chart-container" ref="chart"></div>
    </div>
  </div>
</template>

<script>
import * as echarts from "echarts";

export default {
  name: "ChartComponent",
  props: {
    patientEventData: {
      type: Array,
      default: () => [],
    },
    clusterData: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      chartInstance: null,
      resizeTimer: null,
    };
  },
  watch: {
    patientEventData: {
      handler() {
        this.refreshChart();
      },
      deep: true,
    },
    clusterData: {
      handler() {
        this.refreshChart();
      },
      deep: true,
    },
  },
  mounted() {
    this.initChart();
  },
  methods: {
    initChart() {
      this.chartInstance = echarts.init(this.$refs.chart);
      console.log("卡片内部数据", this.patientEventData);
      console.log("聚类数据", this.clusterData);

      if (this.patientEventData.length === 0 || this.clusterData.length === 0) {
        this.chartInstance.setOption({
          title: {
            text: "暂无数据",
            left: "center",
            top: "center",
            textStyle: { color: "#999", fontSize: 16 },
          },
        });
        return;
      }

      const chartData = this.patientEventData;
      const clusterData = this.clusterData;
      const patientIds = chartData.map((item) => item.patientId);

      // 聚合同一时间的事件
      const aggregatedData = this.aggregateEventsByTime(chartData);

      // // 生成聚类背景区域 - 修正版本
      // const clusterAreas = this.generateClusterAreas(clusterData, patientIds);

      const series = aggregatedData.map((patient, index) => {
        const color = this.generateDistinctColor(index, aggregatedData.length);

        const data = this.generatePatientDataPoints(
          patient,
          clusterData,
          patientIds
        );

        return {
          name: patient.patientId,
          type: "line",
          symbolSize: 8,
          data: data,
          itemStyle: {
            color: color,
            borderColor: "#fff",
            borderWidth: 2,
          },
          lineStyle: {
            color: color,
            width: 3,
            type: "solid",
            shadowColor: color,
            shadowBlur: 3,
            shadowOffsetY: 1,
          },
          step: false,
          smooth: 0.3,
          emphasis: {
            focus: "series",
            itemStyle: {
              color: color,
              borderColor: "#fff",
              borderWidth: 3,
              shadowBlur: 10,
              shadowColor: "rgba(0, 0, 0, 0.4)",
            },
            lineStyle: {
              width: 6,
              shadowBlur: 10,
              shadowColor: color,
            },
          },
        };
      });
      // 添加聚类背景系列
      const clusterBackgroundSeries = this.generateClusterBackgroundSeries(
        clusterData,
        patientIds
      );
      const maxHour =
        Math.max(
          ...chartData.flatMap((patient) =>
            patient.events.map((event) => event.hour)
          )
        ) + 1;

      const option = {
        tooltip: {
          trigger: "item",
          formatter: (params) => {
            if (params.componentType === "series" && params.data?.events) {
              const events = params.data.events;
              const eventsHtml = events
                .map(
                  (event) =>
                    `<p style="margin: 2px 0;">• ${
                      event.name || "异常事件"
                    }: <span style="color: #2d5bff; font-weight: bold;">${
                      event.value
                    }</span></p>`
                )
                .join("");

              return `
                <div style="max-width: 350px; font-family: Arial, sans-serif;">
                  <p style="margin: 0 0 8px 0;"><strong style="color: #333;">病人ID:</strong> <span style="color: ${
                    params.color
                  }; font-weight: bold;">${params.data.patientId}</span></p>
                  <p style="margin: 0 0 8px 0;"><strong style="color: #333;">时间:</strong> ${Math.round(
                    params.data.realTime
                  )}时</p>
                  <p style="margin: 0 0 8px 0;"><strong style="color: #333;">事件数量:</strong> ${
                    events.length
                  }</p>
                  <div style="max-height: 200px; overflow-y: auto; border-top: 1px solid #eee; padding-top: 8px;">
                    <strong style="color: #333;">事件详情:</strong>
                    ${eventsHtml}
                  </div>
                </div>
              `;
            }
            return "";
          },
          enterable: true,
          confine: true,
          backgroundColor: "rgba(255, 255, 255, 0.95)",
          borderColor: "#ddd",
          borderWidth: 1,
          textStyle: {
            color: "#333",
          },
        },
        legend: {
          show: true,
          left: 20,
          top: 20,
          orient: "horizontal",
          selectedMode: true,
          data: patientIds.map((id, index) => ({
            name: id,
            icon: "circle",
            textStyle: {
              color: this.generateDistinctColor(index, patientIds.length),
            },
          })),
          textStyle: {
            color: "#333",
            fontSize: 11,
            fontWeight: 600,
          },
          formatter: (name) => `病人 ${name}`,
          itemWidth: 25,
          itemHeight: 14,
        },
        toolbox: {
          feature: {
            restore: {
              title: "还原视图",
              icon: "M12,5V1L7,6L12,11V7A6,6 0 0,1 18,13A6,6 0 0,1 12,19A6,6 0 0,1 6,13H4A8,8 0 0,0 12,21A8,8 0 0,0 20,13A8,8 0 0,0 12,5Z",
            },
            dataZoom: {
              title: {
                zoom: "区域缩放",
                back: "还原缩放",
              },
            },
          },
          right: 20,
          top: 20,
          iconStyle: {
            borderColor: "#2d5bff",
          },
          emphasis: {
            iconStyle: {
              borderColor: "#ff6b6b",
            },
          },
        },
        xAxis: {
          type: "value",
          name: "时间（小时）",
          nameLocation: "middle",
          nameGap: 30,
          min: 0,
          max: maxHour,
          splitLine: {
            show: true,
            lineStyle: {
              type: "dashed",
              opacity: 0.5,
              color: "#d0d0d0",
            },
          },
          axisLabel: {
            formatter: "{value}h",
          },
        },
        yAxis: {
          type: "value",
          name: "病人聚类轨迹",
          nameLocation: "middle",
          nameGap: 40,
          min: -2,
          max: function (value) {
            return Math.ceil(value.max + 4);
          },
          splitLine: { show: false },
          axisLabel: { show: false },
          axisTick: { show: false },
          axisLine: { show: false },
        },
        grid: {
          left: "8%",
          right: "5%",
          bottom: "15%",
          top: "18%",
          containLabel: true,
        },
        dataZoom: [
          {
            type: "inside",
            xAxisIndex: 0,
            start: 0,
            end: 100,
            zoomOnMouseWheel: true,
            moveOnMouseMove: true,
            preventDefaultMouseMove: true,
            minSpan: 5,
            maxSpan: 100,
            zoomSensitivity: 0.6,
            moveSensitivity: 1.0,
          },
          {
            type: "slider",
            xAxisIndex: 0,
            start: 0,
            end: 100,
            height: 18,
            bottom: 25,
            backgroundColor: "rgba(45, 91, 255, 0.1)",
            fillerColor: "rgba(45, 91, 255, 0.3)",
            borderColor: "rgba(45, 91, 255, 0.4)",
            borderRadius: 6, // 添加圆角
            handleStyle: {
              color: "#2d5bff",
              borderColor: "#fff",
              borderWidth: 2,
              shadowBlur: 3,
              shadowColor: "rgba(0, 0, 0, 0.3)",
              borderRadius: 8, // 圆角把手
            },
            handleIcon:
              "M3,0 L7,0 C8.1,0 9,0.9 9,2 L9,14 C9,15.1 8.1,16 7,16 L3,16 C1.9,16 1,15.1 1,14 L1,2 C1,0.9 1.9,0 3,0 Z",
            handleSize: "80%", // 调整把手大小
            labelFormatter: function (value) {
              return Math.round(value) + "h";
            },
            showDetail: true,
            showDataShadow: true,
            realtime: true,
            filterMode: "filter",
          },
          {
            type: "inside",
            yAxisIndex: 0,
            start: 0,
            end: 100,
            zoomOnMouseWheel: false,
            moveOnMouseMove: false,
            orient: "vertical",
          },
        ],
        // 修正的聚类背景区域
        // graphic: clusterAreas,
        // series: series,
        series: [...clusterBackgroundSeries, ...series], // 先添加背景系列，再添加数据系列
      };

      this.chartInstance.setOption(option);
      this.setupClusterInteraction(series, clusterData, patientIds);
      this.setupAdvancedInteractions();
      window.addEventListener("resize", this.resizeChart);
    },

    generateDistinctColor(index) {
      // 使用HSL色彩模式生成高对比度的颜色
      const distinctColors = [
        "#E53E3E", // 红色
        "#3182CE", // 蓝色
        "#38A169", // 绿色
        "#D69E2E", // 黄色
        "#805AD5", // 紫色
        "#DD6B20", // 橙色
        "#319795", // 青色
        "#E53E3E", // 粉色
        "#2D3748", // 深灰
        "#0BC5EA", // 天蓝
        "#F56565", // 浅红
        "#48BB78", // 浅绿
        "#ED8936", // 浅橙
        "#9F7AEA", // 浅紫
        "#4FD1C7", // 浅青
      ];

      if (index < distinctColors.length) {
        return distinctColors[index];
      }

      // 如果超出预定义颜色，动态生成
      const hue = (index * 137.508) % 360; // 黄金角度分布
      const saturation = 70 + (index % 3) * 10; // 70-90%
      const lightness = 40 + (index % 4) * 10; // 40-70%

      return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
    },

    // 优化聚类背景颜色，增加更多区分度
    generateClusterBackgroundColor(groupIndex) {
      const backgroundColors = [
        "rgba(229, 62, 62, 0.3)", // 红色系 - 更鲜明
        "rgba(49, 130, 206, 0.3)", // 蓝色系
        "rgba(56, 161, 105, 0.3)", // 绿色系
        "rgba(214, 158, 46, 0.3)", // 黄色系
        "rgba(128, 90, 213, 0.3)", // 紫色系
        "rgba(221, 107, 32, 0.3)", // 橙色系
        "rgba(49, 151, 149, 0.3)", // 青色系
        "rgba(236, 72, 153, 0.3)", // 粉色系
        "rgba(139, 69, 19, 0.3)", // 棕色系
        "rgba(75, 85, 99, 0.3)", // 灰色系
      ];
      return backgroundColors[groupIndex % backgroundColors.length];
    },

    // 设置高级交互功能
    setupAdvancedInteractions() {
      this.chartInstance.on("brushSelected", (params) => {
        console.log("刷选区域:", params);
      });

      this.chartInstance.on("dataZoom", (params) => {
        console.log("缩放事件:", params);
      });

      this.chartInstance.on("dblclick", () => {
        this.chartInstance.dispatchAction({
          type: "dataZoom",
          start: 0,
          end: 100,
        });
      });

      document.addEventListener("keydown", this.handleKeydown);
    },

    handleKeydown(event) {
      if (!this.chartInstance) return;

      const chartContainer = this.$refs.chart;
      if (!chartContainer || !chartContainer.contains(document.activeElement)) {
        return;
      }

      switch (event.key) {
        case "r":
        case "R":
          this.chartInstance.dispatchAction({
            type: "dataZoom",
            start: 0,
            end: 100,
          });
          event.preventDefault();
          break;
        case "ArrowLeft":
          this.shiftView(-10);
          event.preventDefault();
          break;
        case "ArrowRight":
          this.shiftView(10);
          event.preventDefault();
          break;
        case "+":
        case "=":
          this.zoomView(0.8);
          event.preventDefault();
          break;
        case "-":
          this.zoomView(1.2);
          event.preventDefault();
          break;
      }
    },

    shiftView(percent) {
      const option = this.chartInstance.getOption();
      const dataZoom = option.dataZoom[1];
      const start = dataZoom.start;
      const end = dataZoom.end;
      const range = end - start;

      const newStart = Math.max(0, Math.min(100 - range, start + percent));
      const newEnd = newStart + range;

      this.chartInstance.dispatchAction({
        type: "dataZoom",
        start: newStart,
        end: newEnd,
      });
    },

    zoomView(factor) {
      const option = this.chartInstance.getOption();
      const dataZoom = option.dataZoom[1];
      const start = dataZoom.start;
      const end = dataZoom.end;
      const center = (start + end) / 2;
      const currentRange = end - start;
      const newRange = Math.max(5, Math.min(100, currentRange * factor));

      const newStart = Math.max(0, center - newRange / 2);
      const newEnd = Math.min(100, newStart + newRange);

      this.chartInstance.dispatchAction({
        type: "dataZoom",
        start: newStart,
        end: newEnd,
      });
    },

    aggregateEventsByTime(chartData) {
      return chartData.map((patient) => {
        const eventGroups = {};

        patient.events.forEach((event) => {
          const hourKey = Math.round(event.hour * 10) / 10;
          if (!eventGroups[hourKey]) {
            eventGroups[hourKey] = [];
          }
          eventGroups[hourKey].push(event);
        });

        const aggregatedEvents = Object.entries(eventGroups).map(
          ([hour, events]) => ({
            hour: parseFloat(hour),
            events: events,
            value:
              events.reduce((sum, e) => sum + (e.value || 0), 0) /
              events.length,
          })
        );

        return {
          ...patient,
          events: aggregatedEvents.sort((a, b) => a.hour - b.hour),
        };
      });
    },

    generatePatientDataPoints(patient, clusterData, patientIds) {
      const data = [];

      // 获取初始聚类（第一个聚类时间点）
      const initialCluster = clusterData.find(
        (cluster) =>
          cluster.hour === Math.min(...clusterData.map((c) => c.hour))
      );

      // 如果有初始聚类，使用聚类Y坐标；否则使用默认值
      let initialY;
      if (initialCluster) {
        initialY = this.calculateClusterYPosition(
          patient.patientId,
          initialCluster,
          patientIds
        );
      } else {
        initialY = patientIds.indexOf(patient.patientId) * 2;
      }

      // 修正的初始点 - 使用聚类结果
      data.push({
        value: [0, initialY],
        patientId: patient.patientId,
        realTime: 0,
        events: [{ name: "初始状态", value: 0 }],
      });

      patient.events.forEach((eventGroup) => {
        const cluster = this.findClosestCluster(eventGroup.hour, clusterData);
        const yCoord = this.calculateClusterYPosition(
          patient.patientId,
          cluster,
          patientIds
        );

        data.push({
          value: [eventGroup.hour, yCoord],
          patientId: patient.patientId,
          realTime: eventGroup.hour,
          events: eventGroup.events,
        });
      });

      return data;
    },

    findClosestCluster(hour, clusterData) {
      // 找到在当前时间后的聚类中距离当前时间最近的聚类
      const clusterAfterHour = clusterData.filter(
        (cluster) => cluster.hour >= hour
      );
      if (clusterAfterHour.length === 0) {
        // 如果没有找到，则返回最后一个
        return clusterData[clusterData.length - 1];
      }
      return clusterAfterHour.reduce((init, current) => {
        return Math.abs(current.hour - hour) < Math.abs(init.hour - hour)
          ? current
          : init;
      });
    },
    generateClusterBackgroundSeries(clusterData, patientIds) {
      const backgroundSeries = [];

      // 按时间排序聚类数据
      const sortedClusters = [...clusterData].sort((a, b) => a.hour - b.hour);

      sortedClusters.forEach((clusterInfo, clusterIndex) => {
        clusterInfo.cluster.forEach((group, groupIndex) => {
          const yPositions = [];

          group.forEach((patientIdInGroup) => {
            const patientIndex = patientIds.findIndex(
              (id) => id.toLowerCase() === patientIdInGroup.toLowerCase()
            );

            if (patientIndex !== -1) {
              // 修正：使用与calculateClusterYPosition完全相同的计算逻辑
              // 这里需要模拟calculateClusterYPosition的计算过程
              const yCoord = this.calculateClusterYPositionForBackground(
                patientIdInGroup,
                clusterInfo,
                patientIds,
                groupIndex
              );
              yPositions.push(yCoord);
            }
          });

          if (yPositions.length > 0) {
            // 减小Y坐标范围的扩展，使其更贴合实际数据点
            const minY = Math.min(...yPositions) - 1.5;
            const maxY = Math.max(...yPositions) + 1.5;

            // 修正时间范围计算 - 不向后延展
            let startTime, endTime;

            if (clusterIndex === 0) {
              // 第一个聚类，从0开始到当前聚类时间
              startTime = 0;
              endTime = clusterInfo.hour;
            } else {
              // 从上一个聚类时间开始到当前聚类时间
              startTime = sortedClusters[clusterIndex - 1].hour;
              endTime = clusterInfo.hour;
            }

            const clusterColor =
              this.generateClusterBackgroundColor(groupIndex);

            // 创建背景区域系列
            backgroundSeries.push({
              name: `cluster-bg-${clusterIndex}-${groupIndex}`,
              type: "line",
              data: [
                [startTime, minY],
                [startTime, maxY],
                [endTime, maxY],
                [endTime, minY],
                [startTime, minY], // 闭合路径
              ],
              lineStyle: {
                color: clusterColor,
                width: 1.5,
                type: "dashed",
                opacity: 0.4,
              },
              symbol: "none",
              areaStyle: {
                color: clusterColor,
                opacity: 0.15,
              },
              silent: true,
              showInLegend: false,
              z: -2,
            });

            // 在聚类时间点添加分割线 - 调整高度
            backgroundSeries.push({
              name: `cluster-divider-${clusterIndex}-${groupIndex}`,
              type: "line",
              data: [
                [clusterInfo.hour, minY - 0.5], // 从背景区域底部开始
                [clusterInfo.hour, maxY + 0.5], // 到背景区域顶部
              ],
              lineStyle: {
                color: clusterColor,
                width: 2,
                type: "solid",
                opacity: 0.5,
              },
              symbol: "none",
              silent: true,
              showInLegend: false,
              z: -1,
            });

            // 聚类标签 - 调整位置
            backgroundSeries.push({
              name: `cluster-label-${clusterIndex}-${groupIndex}`,
              type: "scatter",
              data: [[clusterInfo.hour, maxY + 0.8]], // 稍微向上偏移
              symbol: "roundRect",
              symbolSize: [30, 16],
              itemStyle: {
                color: clusterColor,
                opacity: 0.8,
              },
              label: {
                show: true,
                position: "inside",
                formatter: `C${groupIndex + 1}`,
                fontSize: 11,
                fontWeight: "700",
                color: "#fff",
                textShadowColor: "rgba(0,0,0,0.3)",
                textShadowBlur: 2,
              },
              silent: true,
              showInLegend: false,
              z: 2,
            });

            // 时间段标签 - 调整位置
            backgroundSeries.push({
              name: `time-label-${clusterIndex}-${groupIndex}`,
              type: "scatter",
              data: [[(startTime + endTime) / 2, minY - 0.8]], // 稍微向下偏移
              symbol: "none",
              label: {
                show: true,
                position: "bottom",
                formatter: `${startTime}h-${endTime}h (${group.length}人)`,
                fontSize: 9,
                fontWeight: "600",
                color: clusterColor,
                backgroundColor: "rgba(255, 255, 255, 0.9)",
                borderColor: clusterColor,
                borderWidth: 1,
                borderRadius: 4,
                padding: [2, 4],
              },
              silent: true,
              showInLegend: false,
              z: 1,
            });
          }
        });
      });

      return backgroundSeries;
    },

    // 新增方法：专门为背景区域计算Y坐标
    calculateClusterYPositionForBackground(
      patientId,
      cluster,
      patientIds,
      expectedGroupIndex
    ) {
      const patientIdLower = patientId.toLowerCase();

      // 直接使用传入的groupIndex，因为我们已经知道这个病人在哪个组
      const group = cluster.cluster[expectedGroupIndex];
      const patientIndex = group.findIndex((id) => id === patientIdLower);

      if (patientIndex !== -1) {
        // 与calculateClusterYPosition使用完全相同的计算公式
        return expectedGroupIndex * (patientIds.length * 2) + patientIndex * 2;
      }

      // 如果找不到，返回默认位置
      return patientIds.indexOf(patientId) * 2;
    },

    // 确保calculateClusterYPosition方法与背景区域计算完全一致
    calculateClusterYPosition(patientId, cluster, patientIds) {
      const patientIdLower = patientId.toLowerCase();

      for (
        let groupIndex = 0;
        groupIndex < cluster.cluster.length;
        groupIndex++
      ) {
        const group = cluster.cluster[groupIndex];
        const patientIndex = group.findIndex((id) => id === patientIdLower);

        if (patientIndex !== -1) {
          // 与背景区域使用相同的计算公式
          return groupIndex * (patientIds.length * 2) + patientIndex * 2;
        }
      }

      // 如果找不到，返回默认位置
      return patientIds.indexOf(patientId) * 2;
    },
    setupClusterInteraction(series, clusterData) {
      let currentSelectedGroup = null;

      this.chartInstance.on("click", (params) => {
        if (params.componentType === "series") {
          const currentPatientId = params.data.patientId;
          const currentHour = Math.floor(params.data.value[0]);

          if (
            currentSelectedGroup &&
            currentSelectedGroup.includes(currentPatientId.toLowerCase())
          ) {
            this.chartInstance.setOption({
              series: series.map((s) => ({
                ...s,
                lineStyle: { ...s.lineStyle, opacity: 1 },
                itemStyle: { ...s.itemStyle, opacity: 1 },
              })),
            });
            currentSelectedGroup = null;
            return;
          }

          const relevantCluster = this.findClosestCluster(
            currentHour,
            clusterData
          );

          if (relevantCluster) {
            let sameClusterPatients = [];

            for (const cluster of relevantCluster.cluster) {
              if (cluster.includes(currentPatientId.toLowerCase())) {
                sameClusterPatients = cluster.map((id) => id.toUpperCase());
                break;
              }
            }

            currentSelectedGroup = sameClusterPatients.map((id) =>
              id.toLowerCase()
            );

            this.chartInstance.setOption({
              series: series.map((s) => ({
                ...s,
                lineStyle: {
                  ...s.lineStyle,
                  opacity: sameClusterPatients.includes(s.name) ? 1 : 0.2,
                },
                itemStyle: {
                  ...s.itemStyle,
                  opacity: sameClusterPatients.includes(s.name) ? 1 : 0.2,
                },
              })),
            });
          }
        }
      });
    },

    refreshChart() {
      if (this.chartInstance) {
        this.chartInstance.dispose();
      }
      this.$nextTick(() => {
        this.initChart();
      });
    },

    resizeChart() {
      if (!this.chartInstance) return;

      if (this.resizeTimer) {
        clearTimeout(this.resizeTimer);
      }

      this.resizeTimer = setTimeout(() => {
        try {
          this.chartInstance.resize();
        } catch (error) {
          console.warn("图表调整大小时出错:", error);
          this.refreshChart();
        }
      }, 100);
    },
  },

  beforeUnmount() {
    window.removeEventListener("resize", this.resizeChart);
    document.removeEventListener("keydown", this.handleKeydown);
    if (this.chartInstance) {
      this.chartInstance.dispose();
    }
  },
};
</script>

<style scoped>
.chart-section h3 {
  margin-bottom: 15px;
  font-size: 22px;
  font-weight: 600;
  color: #2d5bff;
  text-shadow: 0 1px 2px rgba(45, 91, 255, 0.1);
}

.chart-wrapper {
  position: relative;
  width: 100%;
  height: 95%;
}

.chart-container {
  width: 100%;
  height: 100%;
  background: linear-gradient(145deg, #ffffff, #f5f7ff);
  border-radius: 16px;
  box-shadow: 0 10px 20px rgba(45, 91, 255, 0.05),
    0 6px 6px rgba(45, 91, 255, 0.1), inset 0 -2px 5px rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(45, 91, 255, 0.1);
  backdrop-filter: blur(5px);
  transition: all 0.3s ease;
}

.chart-container:hover {
  box-shadow: 0 15px 30px rgba(45, 91, 255, 0.1),
    0 8px 8px rgba(45, 91, 255, 0.15), inset 0 -2px 5px rgba(255, 255, 255, 0.8);
  transform: translateY(-2px);
}

.chart-container > div {
  width: 100%;
  height: 100%;
  padding: 20px;
}

.refresh-button {
  position: absolute;
  top: 15px;
  right: 15px;
  z-index: 100;
  width: 34px;
  height: 34px;
  border-radius: 17px;
  background: linear-gradient(145deg, #ffffff, #f0f3fa);
  border: 1px solid rgba(45, 91, 255, 0.15);
  box-shadow: 0 3px 6px rgba(45, 91, 255, 0.1);
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: all 0.2s ease;
}

.refresh-button:hover {
  transform: rotate(15deg);
  box-shadow: 0 5px 10px rgba(45, 91, 255, 0.2);
  background: linear-gradient(145deg, #f5f7ff, #ffffff);
}

.refresh-button:active {
  transform: rotate(30deg) scale(0.95);
}

.refresh-icon {
  color: #2d5bff;
  font-size: 18px;
  font-weight: bold;
  font-style: normal;
}
</style>
