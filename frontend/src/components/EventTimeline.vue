<template>
  <div>
    <div ref="timelineChart" class="timeline-chart"></div>
    <!-- 将预警表格作为独立元素，而不是嵌套在图表内 -->
    <div v-if="showWarningTable" class="warning-table-overlay">
      <div class="warning-table-header">
        <h3>预警事件列表</h3>
        <button class="close-btn" @click="showWarningTable = false">×</button>
      </div>
      <div class="warning-table-content">
        <table>
          <thead>
            <tr>
              <th>预警事件</th>
              <th>风险等级</th>
              <th>预计发生时间</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(event, index) in sortedPredictEvents"
              :key="index"
              :class="getWarningClass(event)"
            >
              <td>
                <span
                  v-for="(type, idx) in event.event_type"
                  :key="idx"
                  class="event-tag"
                  :style="getEventStyle(type)"
                >
                  {{ type }}
                </span>
              </td>
              <td>
                <span class="risk-level" :class="getRiskClass(event)">
                  {{ calculateRiskLevel(event) }}
                </span>
              </td>
              <td>{{ formatDate(event.time) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from "echarts";
import Axios from "@/utils/axios.js";

export default {
  name: "EventTimeline",
  props: {
    patientId: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      // 示例数据，实际使用时应通过props传入
      chart: null,
      showWarningTable: false, // 添加控制表格显示的状态
      realEvents: [],
      predictEvents: [],
      eventData: [],
      predefinedColors: [
        // 使用精简的柔和色调方案
        "#4ecdc4", // 薄荷绿
        "#ff6b6b", // 柔和红
        "#ffe66d", // 柔和黄
        "#7971ea", // 淡紫色
        "#5fa8d3", // 天蓝色
        "#f8961e", // 柔和橙
        "#a5a58d", // 柔和灰绿
        "#b5838d", // 柔和粉紫
        "#277da1", // 柔和蓝
        "#f94144", // 柔和红橙
        "#95d5b2", // 淡绿色
        "#8e9aaf", // 灰蓝色
        "#ffb4a2", // 淡珊瑚色
        "#6b9080", // 深绿色
        "#e5989b", // 淡玫瑰色
        "#b7b7a4", // 灰绿色
        "#83c5be", // 青绿色
        "#006d77", // 深青色
        "#ffddd2", // 淡粉色
        "#e29578", // 柔和橘色
      ],
      colorMap: {},
      theme: {
        backgroundColor: "#ffffff",
        textColor: "#333333",
        axisColor: "#666666",
        splitLineColor: "#eeeeee",
      },
    };
  },
  mounted() {
    this.renderTimelineChart();
    // 添加窗口大小变化的监听，以便图表自适应
    window.addEventListener("resize", this.handleResize);
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.handleResize);
  },
  computed: {
    sortedPredictEvents() {
      return [...this.predictEvents].sort(
        (a, b) => new Date(a.time) - new Date(b.time)
      );
    },
  },
  methods: {
    async initData() {
      // 在获取数据前先销毁现有图表实例
      if (this.chart) {
        this.chart.dispose();
        this.chart = null;
      }

      if (this.patientId) {
        await Promise.all([
          this.fetchEventData(),
          this.fetchEventProbabilities(),
        ]);

        this.colorMap = this.generateColorMap();
        this.renderTimelineChart();
      }
    },
    async fetchEventData() {
      try {
        const response = await Axios.post("/patient/event_full_info", {
          patient_id: this.patientId,
        });
        if (response.status === 200) {
          this.realEvents = response.data.data.actual_events;
          console.log("真实数据为",this.realEvents);
          this.predictEvents = response.data.data.predicted_targets;
          this.$message.success("数据获取成功");
        } else {
          this.$message.error(response.data.message);
        }
      } catch (error) {
        if (error.response?.status === 404 || error.response?.status === 400) {
          this.$message.error(error.response.data.message);
          this.$message.success("数据获取成功");
        } else {
          this.$message.error("发生错误，请稍后再试");
        }
      }
    },

    async fetchEventProbabilities() {
      try {
        const response = await Axios.post("/patient/event_probabilities", {
          patient_id: this.patientId,
        });
        if (response.status === 200) {
          this.eventData = response.data.data;
        } else {
          this.$message.error(response.data.message);
        }
      } catch (error) {
        if (error.response?.status === 404 || error.response?.status === 400) {
          this.$message.error(error.response.data.message);
        } else {
          this.$message.error("发生错误，请稍后再试");
        }
      }
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(
        2,
        "0"
      )}-${String(date.getDate()).padStart(2, "0")}`;
    },
    generateColorMap() {
      // 获取所有不重复的事件类型
      const eventTypes = this.getUniqueEventTypes();
      // 创建一个新的颜色映射对象，保留原有的映射关系
      const newColorMap = { ...this.colorMap };
      // 检查是否有已分配的颜色被使用
      const usedColors = new Set(Object.values(newColorMap));
      // 为每种事件类型分配颜色
      eventTypes.forEach((type, index) => {
        // 如果该类型已经有颜色，则跳过
        if (newColorMap[type]) {
          return;
        }
        // 如果索引在预定义颜色范围内，使用预定义颜色
        if (index < this.predefinedColors.length) {
          // 检查该颜色是否已被使用
          const color = this.predefinedColors[index];
          if (!usedColors.has(color)) {
            newColorMap[type] = color;
            usedColors.add(color);
          } else {
            // 如果已被使用，生成HSL颜色
            let hue = (index * 137.5) % 360;
            let newColor = this.hslToHex(hue, 65, 65);
            // 确保生成的颜色不重复
            let attempts = 0;
            while (usedColors.has(newColor) && attempts < 30) {
              hue = (hue + 37) % 360; // 使用不同的增量以避免重复
              newColor = this.hslToHex(hue, 65, 65);
              attempts++;
            }
            newColorMap[type] = newColor;
            usedColors.add(newColor);
          }
        } else {
          // 生成HSL颜色，确保色相均匀分布
          let hue = (index * 137.5) % 360; // 使用黄金角分割法确保色相分布均匀
          let newColor = this.hslToHex(hue, 65, 65);
          // 确保生成的颜色不重复
          let attempts = 0;
          while (usedColors.has(newColor) && attempts < 30) {
            hue = (hue + 37) % 360;
            newColor = this.hslToHex(hue, 65, 65);
            attempts++;
          }
          newColorMap[type] = newColor;
          usedColors.add(newColor);
        }
      });
      // 更新组件的colorMap
      this.colorMap = newColorMap;
      return this.colorMap;
    },
    // 添加HSL转十六进制颜色的方法
    hslToHex(h, s, l) {
      s /= 100;
      l /= 100;
      const a = s * Math.min(l, 1 - l);
      const f = (n) => {
        const k = (n + h / 30) % 12;
        const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
        return Math.round(255 * color)
          .toString(16)
          .padStart(2, "0");
      };
      return `#${f(0)}${f(8)}${f(4)}`;
    },
    getEventStyle(type) {
      return {
        backgroundColor: this.hexToRgba(this.colorMap[type], 0.2),
        color: this.colorMap[type] || "#333",
        borderColor: this.colorMap[type] || "#333",
      };
    },

    calculateRiskLevel(event) {
      // 获取该时间点的所有事件强度
      const timePoint = this.eventData.find((item) => item.time === event.time);
      if (!timePoint) return "低风险";

      // 计算该时间点所有预警事件类型的最大强度
      let maxProbability = 0;
      event.event_type.forEach((type) => {
        const eventData = timePoint.events.find((e) => e.type === type);
        if (eventData && eventData.probability > maxProbability) {
          maxProbability = eventData.probability;
        }
      });

      // 根据最大强度判断风险等级
      if (maxProbability >= 10) return "高风险";
      if (maxProbability >= 5) return "中风险";
      return "低风险";
    },

    getRiskClass(event) {
      const level = this.calculateRiskLevel(event);
      return {
        "high-risk": level === "高风险",
        "medium-risk": level === "中风险",
        "low-risk": level === "低风险",
      };
    },

    getWarningClass(event) {
      const level = this.calculateRiskLevel(event);
      return {
        "warning-high": level === "高风险",
        "warning-medium": level === "中风险",
        "warning-low": level === "低风险",
      };
    },
    handleResize() {
      if (this.chart) {
        this.chart.resize();
      }
    },
    renderTimelineChart() {
      if (this.chart) {
        this.chart.dispose();
        this.chart = null;
      }
      const chart = echarts.init(this.$refs.timelineChart, null, {
        renderer: "canvas",
      });
      this.chart = chart;
      // 修改图例数据处理
      const legendData = [];
      const eventTypes = this.getUniqueEventTypes();

      // 只为每种事件类型创建一个图例项
      eventTypes.forEach((eventType) => {
        legendData.push({
          name: eventType,
          // 使用事件类型对应的颜色
          itemStyle: {
            color: this.colorMap[eventType],
          },
        });
      });

      const allSeriesNames = [];

      // 区分历史数据和预测数据的时间点
      // const historicalTimePoints = this.eventData.filter(
      //   (item) => item.isHistorical
      // );
      // 我们不再需要单独的futureTimePoints变量，因为我们使用单一的连续线条

      // 获取最后一次观察时间点（历史数据的最后一个点）
      const lastObservationPoint =
        this.realEvents && this.realEvents.length > 0
          ? new Date(
              this.realEvents[this.realEvents.length - 1].time
            ).getTime() : null;
      // 准备每种事件类型的数据系列
      const series = [];

      eventTypes.forEach((eventType) => {
        // 获取该事件类型的所有数据点（包括历史和预测）
        const eventColor = this.colorMap[eventType];
        const allData = this.eventData.map((timePoint) => {
          const event = timePoint.events.find((e) => e.type === eventType);
          return {
            name: timePoint.time,
            value: [
              new Date(timePoint.time).getTime(), // 转换为时间戳
              event ? event.probability : 0,
            ],
            // 标记是否为历史数据
            isHistorical: timePoint.isHistorical,
          };
        });

        // 分别创建历史数据和预测数据的系列
        // 1. 历史数据系列（实线）
        const historicalData = allData.filter((item) => item.isHistorical);
        if (historicalData.length > 0) {
          const seriesName = eventType;
          allSeriesNames.push(seriesName); // 添加到图例名称列表
          series.push({
            name: eventType,
            type: "line",
            smooth: true,
            symbol: "emptyCircle",
            symbolSize: 10,
            sampling: "average",
            animation: true,
            animationDuration: 1000,
            animationEasing: "cubicOut",
            emphasis: {
              focus: [
                "series",
                function (seriesName) {
                  // 如果是预测系列，同时高亮对应的历史系列
                  if (seriesName.includes("(预测)")) {
                    return [seriesName, seriesName.replace(" (预测)", "")];
                  }
                  // 如果是历史系列，同时高亮对应的预测系列
                  return [seriesName, seriesName + " (预测)"];
                },
              ],
              itemStyle: {
                shadowBlur: 10,
                shadowColor: "rgba(0, 0, 0, 0.3)",
              },
            },
            itemStyle: {
              color: eventColor,
              borderWidth: 2,
              borderColor: "#fff",
              shadowBlur: 4,
              shadowColor: "rgba(0, 0, 0, 0.2)",
            },
            lineStyle: {
              width: 2,
              type: "solid",
              shadowBlur: 5,
              shadowColor: "rgba(0, 0, 0, 0.1)",
              shadowOffsetY: 5,
              cap: "round",
            },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                {
                  offset: 0,
                  color: this.hexToRgba(eventColor, 0.7),
                },
                {
                  offset: 1,
                  color: this.hexToRgba(eventColor, 0.05),
                },
              ]),
              shadowBlur: 10,
              shadowColor: "rgba(0, 0, 0, 0.1)",
              opacity: 0.8,
            },
            data: historicalData,
            z: 2, // 确保历史数据在预测数据之上
          });
        }

        // 2. 预测数据系列（虚线）
        const futureData = allData.filter((item) => !item.isHistorical);
        if (futureData.length > 0 && historicalData.length > 0) {
          // 找到最后一个历史数据点
          const lastHistoricalPoint = historicalData[historicalData.length - 1];

          // 创建预测数据数组，包含最后一个历史点和所有预测点
          const predictData = [lastHistoricalPoint, ...futureData];
          const seriesName = eventType + " (预测)";
          allSeriesNames.push(seriesName); // 添加到图例名称列表
          series.push({
            name: eventType + " (预测)",
            type: "line",
            smooth: true,
            symbol: "emptyCircle",
            symbolSize: 8,
            connectNulls: true,
            sampling: "average",
            animation: true,
            animationDuration: 1000,
            animationEasing: "cubicOut",
            emphasis: {
              focus: "series",
              itemStyle: {
                shadowBlur: 10,
                shadowColor: "rgba(0, 0, 0, 0.3)",
              },
            },
            itemStyle: {
              color: eventColor,
              borderWidth: 2,
              borderColor: "#fff",
              shadowBlur: 4,
              shadowColor: "rgba(0, 0, 0, 0.2)",
            },
            lineStyle: {
              width: 2,
              type: "dashed",
              dash: [5, 5],
              shadowBlur: 3,
              shadowColor: "rgba(0, 0, 0, 0.1)",
              cap: "round",
            },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                {
                  offset: 0,
                  color: this.hexToRgba(eventColor, 0.4),
                },
                {
                  offset: 1,
                  color: this.hexToRgba(eventColor, 0.02),
                },
              ]),
              shadowBlur: 8,
              shadowColor: "rgba(0, 0, 0, 0.1)",
              opacity: 0.5,
            },
            // 直接使用预测数据数组，不再进行复杂的映射
            data: predictData,
            z: 1, // 确保预测数据在历史数据之下
          });
        }
      });

      // 添加最后观察时间点的分隔线
      if (lastObservationPoint) {
        series.push({
          name: "最后观察时间",
          type: "line",
          markLine: {
            silent: false,
            symbol: ["none", "none"],
            label: {
              formatter: "最后观察时间",
              position: "middle",
              fontSize: 14,
              fontWeight: "bold",
              color: "#333",
              backgroundColor: "rgba(255, 255, 255, 0.8)",
              padding: [5, 10],
              borderRadius: 4,
              lineHeight: 20,
            },
            lineStyle: {
              type: "dashed", // 修改为虚线
              color: "#999", // 修改为灰色
              width: 2,
              opacity: 0.8,
              cap: "round",
              dashOffset: 5,
              join: "round",
            },
            data: [
              {
                xAxis: lastObservationPoint,
                name: "最后观察时间",
              },
            ],
          },
          data: [],
        });
      }

      // 添加目标事件阈值标记
      const targetEventThresholdSeries = this.prepareTargetEventThreshold();
      series.push(...targetEventThresholdSeries);
      const realEventsSeries = this.prepareRealEventsSeries();
      series.push(...realEventsSeries);

      const option = {
        backgroundColor: this.theme.backgroundColor,
        title: {
          text: "病人病程发展时间线",
          left: "center",
          top: 10,
          textStyle: {
            fontSize: 24,
            fontWeight: "bold",
            fontFamily: "'Microsoft YaHei', sans-serif",
            color: "#333",
            textShadow: "1px 1px 2px rgba(0,0,0,0.1)",
          },
        },
        tooltip: {
          trigger: "axis",
          formatter: function (params) {
            // 确保params是数组
            const paramsArray = Array.isArray(params) ? params : [params];

            // 获取时间点 - 从第一个参数的name获取
            const timePoint = new Date(paramsArray[0].axisValue);
            const formattedDate = `${timePoint.getFullYear()}-${String(
              timePoint.getMonth() + 1
            ).padStart(2, "0")}-${String(timePoint.getDate()).padStart(
              2,
              "0"
            )}`; // TODO:将来可能要进一步细化到小时

            // 创建标题
            let result = `<div style="font-weight:bold;margin-bottom:10px;font-size:16px;color:#333;">${formattedDate}</div>`;

            // 获取所有有效的数据点（排除空值和特殊系列）
            const validParams = paramsArray.filter(
              (p) =>
                p.componentSubType === "line" &&
                p.value !== "-" &&
                p.seriesName !== "最后观察时间" &&
                !p.seriesName.includes("预警") &&
                !p.seriesName.includes("阈值线")
            );

            // 获取真实事件点
            const realEventParams = paramsArray.filter((p) =>
              p.seriesName.includes("真实事件")
            );
            // 获取预测事件点
            const predictEventParams = paramsArray.filter((p) =>
              p.seriesName.includes("预警")
            );

            // 按系列名称分组处理数据
            const groupedParams = {};
            validParams.forEach((param) => {
              const baseName = param.seriesName.replace(" (预测)", "");
              if (!groupedParams[baseName]) {
                groupedParams[baseName] = {};
              }
              // 如果是预测数据且不是最后一组观察数据，放入prediction
              if (
                param.seriesName.includes("(预测)") &&
                !param.value.isHistorical
              ) {
                groupedParams[baseName].prediction = param;
              } else {
                // 其他情况都放入historical
                groupedParams[baseName].historical = param;
              }
            });

            // 遍历分组后的数据，生成tooltip内容
            Object.entries(groupedParams).forEach(([baseName, data]) => {
              // 添加历史数据（如果有）
              if (data.historical) {
                // 从value数组中提取强度值（第二个元素）
                const probability = Array.isArray(data.historical.value)
                  ? data.historical.value[1]
                  : data.historical.value;

                result += `<div style="display:flex;align-items:center;margin:8px 0;">
                    <span style="display:inline-block;width:12px;height:12px;background:${
                      data.historical.color
                    };margin-right:8px;border-radius:50%;"></span>
                    <span style="margin-right:8px;font-size:14px;">${baseName}:</span>
                    <span style="font-weight:bold;font-size:15px;">${
                      typeof probability === "number"
                        ? probability.toFixed(1)
                        : probability
                    }</span>
                  </div>`;
              }

              // 添加预测数据（如果有）
              if (data.prediction) {
                // 从value数组中提取强度值（第二个元素）
                const probability = Array.isArray(data.prediction.value)
                  ? data.prediction.value[1]
                  : data.prediction.value;

                result += `<div style="display:flex;align-items:center;margin:8px 0;">
                    <span style="display:inline-block;width:12px;height:12px;border:1px dashed ${
                      data.prediction.color
                    };margin-right:8px;border-radius:50%;"></span>
                    <span style="margin-right:8px;font-size:14px;">${
                      data.prediction.seriesName
                    }:</span>
                    <span style="font-weight:bold;font-size:15px;">${
                      typeof probability === "number"
                        ? probability.toFixed(1)
                        : probability
                    }</span>
                  </div>`;
              }
            });

            // 添加真实事件信息
            if (realEventParams.length > 0) {
              result += `<div style="margin-top:10px;border-top:1px dashed #ccc;padding-top:8px;">
                  <div style="font-weight:bold;margin-bottom:5px;color:#333;">真实事件:</div>`;

              realEventParams.forEach((param) => {
                const eventType = param.seriesName.replace(" (真实事件)", "");
                result += `<div style="display:flex;align-items:center;margin:5px 0;">
                    <span style="display:inline-block;width:12px;height:12px;background:${param.color};margin-right:8px;border-radius:50%;"></span>
                    <span style="font-size:13px;">${eventType}</span>
                  </div>`;
              });

              result += `</div>`;
            }
            if (predictEventParams.length > 0) {
              result += `<div style="margin-top:10px;border-top:1px dashed #ccc;padding-top:8px;">
                  <div style="font-weight:bold;margin-bottom:5px;color:#333;">预测事件:</div>`;

              predictEventParams.forEach((param) => {
                const eventType = param.seriesName.replace(" (预警)", "");
                result += `<div style="display:flex;align-items:center;margin:5px 0;">
                    <span style="display:inline-block;width:12px;height:12px;background:${param.color};margin-right:8px;border-radius:50%;"></span>
                    <span style="font-size:13px;">${eventType}</span>
                  </div>`;
              });

              result += `</div>`;
            }

            return result;
          },
        },
        legend: {
          data: legendData,
          top: 60,
          type: "scroll",
          padding: [5, 10],
          itemGap: 20,
          borderRadius: 5,
          textStyle: {
            fontSize: 14,
            color: this.theme.textColor,
          },
          itemStyle: {
            borderWidth: 0,
          },
          icon: "roundRect",
          pageIconColor: "#666",
          pageIconInactiveColor: "#aaa",
          pageTextStyle: {
            color: "#666",
          },
          // 默认隐藏预测系列的图例
          selected: eventTypes.reduce((acc, name) => {
            acc[name] = true;
            return acc;
          }, {}),
        },
        grid: {
          left: "3%",
          right: "4%",
          bottom: "8%",
          top: "120px",
          containLabel: true,
        },
        toolbox: {
          right: 20,
          top: 20,
          feature: {
            myWarningTable: {
              show: true,
              title: "预警列表",
              icon: "path://M8,8 L42,8 L42,12 L8,12 Z M8,16 L42,16 L42,20 L8,20 Z M8,24 L42,24 L42,28 L8,28 Z M8,32 L42,32 L42,36 L8,36 Z M8,40 L42,40 L42,44 L8,44 Z",
              onclick: () => {
                this.showWarningTable = !this.showWarningTable;
                // 更新按钮标题
                chart.setOption({
                  toolbox: {
                    feature: {
                      myWarningTable: {
                        title: "预警列表",
                      },
                    },
                  },
                });
              },
            },
            saveAsImage: {
              title: "保存为图片",
              pixelRatio: 2,
            },
            dataZoom: {
              title: { zoom: "区域缩放", back: "还原缩放" },
              icon: {
                zoom: "path://M0,13.5h26.9 M13.5,26.9V0 M32.1,13.5H58V58H13.5 V32.1",
                back: "path://M22,1.4L9.9,13.5l12.3,12.3 M10.3,13.5H54.9v44.6 H10.3v-26",
              },
            },
            restore: { title: "还原" },
          },
          iconStyle: {
            borderColor: "#666",
            borderWidth: 1,
            borderType: "solid",
          },
          emphasis: {
            iconStyle: {
              borderColor: "#333",
            },
          },
        },
        xAxis: {
          type: "time", // 将类型从 category 改为 time
          boundaryGap: false,
          // 移除 data 属性，time 类型不需要预设数据
          axisLabel: {
            formatter: function (value) {
              // 格式化日期显示,精确到小时
              const date = new Date(value);
              return `${date.getMonth() + 1}/${date.getDate()} ${String(
                date.getHours()
              ).padStart(2, "0")}:00`;
            },
            rotate: 45,
            fontSize: 13,
            color: this.theme.axisColor,
            margin: 15,
            fontWeight: "normal",
          },
          axisLine: {
            lineStyle: {
              color: this.theme.axisColor,
              width: 2,
            },
          },
          axisTick: {
            alignWithLabel: true,
            lineStyle: {
              color: this.theme.axisColor,
            },
          },
          splitLine: {
            show: true,
            lineStyle: {
              color: [this.theme.splitLineColor],
              type: "dashed",
              width: 1,
            },
          },
          nameTextStyle: {
            fontSize: 14,
            color: this.theme.textColor,
            padding: [10, 0, 0, 0],
          },
        },
        yAxis: {
          type: "value",
          name: "发生概率",
          nameTextStyle: {
            fontSize: 15,
            color: this.theme.textColor,
            padding: [0, 30, 10, 0],
            fontWeight: "bold",
          },
          axisLabel: {
            fontSize: 13,
            color: this.theme.axisColor,
            margin: 15,
          },
          axisLine: {
            show: true,
            lineStyle: {
              color: this.theme.axisColor,
              width: 2,
            },
          },
          axisTick: {
            show: true,
            lineStyle: {
              color: this.theme.axisColor,
            },
          },
          splitLine: {
            lineStyle: {
              color: [this.theme.splitLineColor],
              type: "dashed",
              width: 1,
            },
          },
          scale: true,
          splitNumber: 5,
        },
        dataZoom: [
          {
            type: "inside",
            start: 0,
            end: 100,
            zoomLock: false,
          },
          {
            start: 0,
            end: 100,
            handleIcon:
              "path://M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z",
            handleSize: "80%",
            handleStyle: {
              color: "#fff",
              shadowBlur: 3,
              shadowColor: "rgba(0, 0, 0, 0.6)",
              shadowOffsetX: 2,
              shadowOffsetY: 2,
            },
            textStyle: {
              color: "#666",
            },
            borderColor: "#ccc",
            backgroundColor: "rgba(240, 240, 240, 0.8)",
            fillerColor: "rgba(220, 220, 220, 0.4)",
            showDetail: true,
            bottom: 20,
          },
        ],
        animation: true,
        animationThreshold: 2000,
        animationDuration: 1000,
        animationEasing: "cubicOut",
        animationDelay: function (idx) {
          return idx * 100;
        },
        series: series,
      };

      // 在chart.setOption(option)之后添加
      chart.setOption(option);

      // 添加图例点击事件处理
      chart.on("legendselectchanged", (params) => {
        const { name, selected } = params;

        // 同时控制历史和预测系列的显示/隐藏
        const updatedSelected = { ...selected };
        updatedSelected[name + " (预测)"] = selected[name]; // 预测系列跟随基本系列的显示状态

        chart.setOption({
          legend: {
            selected: updatedSelected,
          },
        });
      });

      // 添加点击事件
      chart.on("click", (params) => {
        this.$emit("event-click", {
          type: params.seriesName,
          time: params.name,
          value: params.value,
        });
      });
    },

    getUniqueEventTypes() {
      // 获取所有不重复的事件类型
      const types = new Set();
      this.eventData.forEach((timePoint) => {
        timePoint.events.forEach((event) => {
          types.add(event.type);
        });
      });
      return Array.from(types);
    },

    hexToRgba(hex, alpha) {
      // 将十六进制颜色转换为rgba
      const r = parseInt(hex.slice(1, 3), 16);
      const g = parseInt(hex.slice(3, 5), 16);
      const b = parseInt(hex.slice(5, 7), 16);
      return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    },

    // 标注预测事件
    prepareTargetEventThreshold() {
      // 如果没有预测事件数据，则返回空数组
      if (!this.predictEvents || this.predictEvents.length === 0) {
        return [];
      }

      // 创建系列数组，用于存储预警点
      const thresholdSeries = [];

      // 获取所有事件类型
      const eventTypes = this.getUniqueEventTypes();

      // 为每种事件类型创建预警点
      eventTypes.forEach((eventType) => {
        // 收集该事件类型的所有预测事件点
        const eventColor = this.colorMap[eventType];
        const eventPoints = [];

        this.predictEvents.forEach((predictEvent) => {
          // 检查该事件类型是否在当前预测事件中
          if (predictEvent.event_type.includes(eventType)) {
            // 将时间转换为时间戳
            const predictEventTimestamp = new Date(predictEvent.time).getTime();

            // 查找该时间点在eventData中对应的强度值
            const matchingTimePoint = this.eventData.find(
              (item) => item.time === predictEvent.time
            );

            let probability = 0;

            if (matchingTimePoint) {
              // 如果在eventData中找到对应时间点，使用其强度值
              const eventData = matchingTimePoint.events.find(
                (e) => e.type === eventType
              );
              if (eventData) {
                probability = eventData.probability;
              }
            } else {
              // 如果在eventData中找不到对应时间点，使用插值计算强度值
              // 找到最近的前后两个时间点
              const sortedTimePoints = [...this.eventData].sort(
                (a, b) => new Date(a.time) - new Date(b.time)
              );

              const predictEventDate = new Date(predictEvent.time);
              let prevPoint = null;
              let nextPoint = null;

              for (let i = 0; i < sortedTimePoints.length; i++) {
                const currentDate = new Date(sortedTimePoints[i].time);
                if (currentDate <= predictEventDate) {
                  prevPoint = sortedTimePoints[i];
                } else {
                  nextPoint = sortedTimePoints[i];
                  break;
                }
              }

              // 如果找到前后点，进行线性插值
              if (prevPoint && nextPoint) {
                const prevEvent = prevPoint.events.find(
                  (e) => e.type === eventType
                );
                const nextEvent = nextPoint.events.find(
                  (e) => e.type === eventType
                );

                if (prevEvent && nextEvent) {
                  const prevDate = new Date(prevPoint.time);
                  const nextDate = new Date(nextPoint.time);
                  const totalDiff = nextDate - prevDate;
                  const currentDiff = predictEventDate - prevDate;
                  const ratio = currentDiff / totalDiff;

                  probability =
                    prevEvent.probability +
                    ratio * (nextEvent.probability - prevEvent.probability);
                } else if (prevEvent) {
                  probability = prevEvent.probability;
                } else if (nextEvent) {
                  probability = nextEvent.probability;
                }
              } else if (prevPoint) {
                // 如果只有前点，使用前点的强度
                const prevEvent = prevPoint.events.find(
                  (e) => e.type === eventType
                );
                if (prevEvent) {
                  probability = prevEvent.probability;
                }
              } else if (nextPoint) {
                // 如果只有后点，使用后点的强度
                const nextEvent = nextPoint.events.find(
                  (e) => e.type === eventType
                );
                if (nextEvent) {
                  probability = nextEvent.probability;
                }
              }
            }

            // 添加到预警点列表
            eventPoints.push({
              name: predictEvent.time,
              value: [predictEventTimestamp, probability],
              itemStyle: {
                color: eventColor, // 使用事件类型对应的颜色
                borderColor: "#fff",
                borderWidth: 2,
                shadowBlur: 6,
                shadowColor: this.hexToRgba(eventColor, 0.5),
              },
              symbolSize: 20,
            });
          }
        });

        // 如果有该类型的预测事件点，创建一个散点系列
        if (eventPoints.length > 0) {
          const seriesName = `${eventType} (预警)`;
          thresholdSeries.push({
            name: seriesName,
            type: "scatter",
            symbol: "triangle", // 使用三角形标记
            symbolSize: 25,
            data: eventPoints,
            label: {
              show: true,
              formatter: "预警",
              fontSize: 10,
              color: "#fff",
              position: "top",
              backgroundColor: eventColor, // 使用事件类型对应的颜色
            },
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowColor: this.hexToRgba(eventColor, 0.7),
              },
              scale: true,
            },
            itemStyle: {
              color: eventColor, // 使用事件类型对应的颜色
              borderWidth: 2,
              borderColor: "#fff",
              shadowBlur: 4,
              shadowColor: this.hexToRgba(eventColor, 0.5),
            },
            zlevel: 3,
          });
        }
      });

      return thresholdSeries;
    },
    // 标准真实事件
    prepareRealEventsSeries() {
      if (!this.realEvents || this.realEvents.length === 0) {
        return [];
      }

      const realEventsSeries = [];
      const eventTypes = this.getUniqueEventTypes();

      // 为每种事件类型创建一个散点系列
      eventTypes.forEach((eventType) => {
        // 收集该事件类型的所有真实事件点
        const eventPoints = [];

        // 获取事件类型对应的颜色
        const eventColor = this.colorMap[eventType];

        this.realEvents.forEach((realEvent) => {
          // 检查该事件类型是否在当前真实事件中
          if (realEvent.event_type.includes(eventType)) {
            // 将时间转换为时间戳
            const realEventTimestamp = new Date(realEvent.time).getTime();

            // 查找该时间点在eventData中对应的强度值
            const matchingTimePoint = this.eventData.find(
              (item) => item.time === realEvent.time
            );

            if (matchingTimePoint) {
              // 如果在eventData中找到对应时间点，使用其强度值
              const eventData = matchingTimePoint.events.find(
                (e) => e.type === eventType
              );
              if (eventData) {
                eventPoints.push({
                  name: realEvent.time,
                  value: [realEventTimestamp, eventData.probability],
                  itemStyle: {
                    color: this.colorMap[eventType],
                  },
                });
              }
            } else {
              // 如果在eventData中找不到对应时间点，使用插值计算强度值
              // 找到最近的前后两个时间点
              const sortedTimePoints = [...this.eventData].sort(
                (a, b) => new Date(a.time) - new Date(b.time)
              );

              const realEventDate = new Date(realEvent.time);
              let prevPoint = null;
              let nextPoint = null;

              for (let i = 0; i < sortedTimePoints.length; i++) {
                const currentDate = new Date(sortedTimePoints[i].time);
                if (currentDate <= realEventDate) {
                  prevPoint = sortedTimePoints[i];
                } else {
                  nextPoint = sortedTimePoints[i];
                  break;
                }
              }

              let estimatedProbability = 0;

              // 如果找到前后点，进行线性插值
              if (prevPoint && nextPoint) {
                const prevEvent = prevPoint.events.find(
                  (e) => e.type === eventType
                );
                const nextEvent = nextPoint.events.find(
                  (e) => e.type === eventType
                );

                if (prevEvent && nextEvent) {
                  const prevDate = new Date(prevPoint.time);
                  const nextDate = new Date(nextPoint.time);
                  const totalDiff = nextDate - prevDate;
                  const currentDiff = realEventDate - prevDate;
                  const ratio = currentDiff / totalDiff;

                  estimatedProbability =
                    prevEvent.probability +
                    ratio * (nextEvent.probability - prevEvent.probability);
                } else if (prevEvent) {
                  estimatedProbability = prevEvent.probability;
                } else if (nextEvent) {
                  estimatedProbability = nextEvent.probability;
                }
              } else if (prevPoint) {
                // 如果只有前点，使用前点的强度
                const prevEvent = prevPoint.events.find(
                  (e) => e.type === eventType
                );
                if (prevEvent) {
                  estimatedProbability = prevEvent.probability;
                }
              } else if (nextPoint) {
                // 如果只有后点，使用后点的强度
                const nextEvent = nextPoint.events.find(
                  (e) => e.type === eventType
                );
                if (nextEvent) {
                  estimatedProbability = nextEvent.probability;
                }
              }

              // 添加到事件点列表
              eventPoints.push({
                name: realEvent.time,
                value: [realEventTimestamp, estimatedProbability],
                itemStyle: {
                  color: eventColor, // 使用事件类型对应的颜色
                  borderColor: "#fff",
                  borderWidth: 2,
                  shadowBlur: 6,
                  shadowColor: this.hexToRgba(eventColor, 0.5),
                },
              });
            }
          }
        });

        // 如果有该类型的事件点，创建一个散点系列
        if (eventPoints.length > 0) {
          const seriesName = `${eventType} (真实事件)`;
          realEventsSeries.push({
            name: seriesName,
            type: "scatter",
            symbol: "pin", // 使用图钉形状标记
            symbolSize: 30,
            data: eventPoints,
            label: {
              show: true,
              formatter: "实际",
              fontSize: 10,
              color: "#fff",
              position: "top",
              backgroundColor: eventColor, // 使用事件类型对应的颜色
            },
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowColor: this.hexToRgba(eventColor, 0.7),
              },
              scale: true,
            },
            itemStyle: {
              color: eventColor, // 使用事件类型对应的颜色
              borderWidth: 2,
              borderColor: "#fff",
              shadowBlur: 4,
              shadowColor: this.hexToRgba(eventColor, 0.3),
            },
            zlevel: 4, // 确保真实事件点显示在最上层
          });
        }
      });

      return realEventsSeries;
    },
  },
  watch: {
    // 监听patientID的变化，当病人切换时重新获取数据并渲染图表
    patientId: {
      handler(newVal, oldVal) {
        if (newVal !== oldVal && newVal) {
          this.initData();
        }
      },
      immediate: true,
    },
  },
};
</script>

<style scoped>
.timeline-chart {
  width: 100%;
  height: 100%;
  min-height: 500px;
  border-radius: 15px;
  background: #ffffff;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  position: relative; /* 添加相对定位，作为表格的定位参考 */
}

/* 表格覆盖层样式 */
.warning-table-overlay {
  position: absolute;
  top: 60px;
  right: 20px;
  width: 450px;
  max-height: 70%;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 100;
  overflow: hidden;
  animation: slideIn 0.3s ease-in-out;
  border: 1px solid #e0e0e0;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.warning-table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  background: #f5f7fa;
  border-bottom: 1px solid #e0e0e0;
}

.warning-table-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  color: #666;
  cursor: pointer;
  padding: 0 5px;
  line-height: 1;
}

.close-btn:hover {
  color: #333;
}

.warning-table-content {
  padding: 10px;
  max-height: calc(100% - 50px);
  overflow-y: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

th {
  background: #f5f7fa;
  color: #606266;
  font-weight: 600;
  padding: 8px 12px;
  text-align: left;
  border-bottom: 2px solid #ebeef5;
  position: sticky;
  top: 0;
  z-index: 1;
}

td {
  padding: 6px 12px;
  border-bottom: 1px solid #ebeef5;
  vertical-align: middle;
}

.event-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.event-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
}

.risk-level {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
  font-size: 12px;
  text-align: center;
  min-width: 60px;
}

.high-risk {
  background-color: #ff4560;
  color: white;
}

.medium-risk {
  background-color: #ff9f40;
  color: white;
}

.low-risk {
  background-color: #4bc0c0;
  color: white;
}

/* 添加行高亮效果 */
.warning-high {
  background-color: rgba(255, 69, 96, 0.05);
}

.warning-high:hover {
  background-color: rgba(255, 69, 96, 0.1);
}

.warning-medium {
  background-color: rgba(255, 159, 64, 0.05);
}

.warning-medium:hover {
  background-color: rgba(255, 159, 64, 0.1);
}

.warning-low {
  background-color: rgba(75, 192, 192, 0.05);
}

.warning-low:hover {
  background-color: rgba(75, 192, 192, 0.1);
}
</style>
