<template>
  <div>
    <div ref="timelineChart" class="timeline-chart"></div>
  </div>
</template>

<script>
import * as echarts from "echarts";

export default {
  name: "EventTimeline",
  props: {
    patientData: {
      type: Array,
      default: () => [],
    },
    // 新增真实事件数据属性
    realEvents: {
      type: Array,
      default: () => [
        {
          time: "2023-01-01",
          event_type: ["发热", "咳嗽"],
        },
        {
          time: "2023-01-02",
          event_type: ["头痛", "乏力"],
        },
        {
          time: "2023-01-05",
          event_type: ["呼吸困难"],
        },
        {
          time: "2023-01-06",
          event_type: ["发热", "呼吸困难", "乏力"],
        },
        {
          time: "2023-01-08",
          event_type: ["咳嗽", "头痛"],
        },
        {
          time: "2023-01-12",
          event_type: ["呼吸困难", "乏力"],
        },
      ],
    },
  },
  data() {
    return {
      // 示例数据，实际使用时应通过props传入
      eventData: [
        // 时间点1 - 已发生的数据
        {
          time: "2023-01-01",
          events: [
            { type: "发热", intensity: 16.5 },
            { type: "咳嗽", intensity: 8.2 },
            { type: "头痛", intensity: 5.1 },
            { type: "呼吸困难", intensity: 3.0 },
            { type: "乏力", intensity: 4.5 },
          ],
          isHistorical: true,
        },
        // 时间点2
        {
          time: "2023-01-02",
          events: [
            { type: "发热", intensity: 15.0 },
            { type: "咳嗽", intensity: 9.5 },
            { type: "头痛", intensity: 4.8 },
            { type: "呼吸困难", intensity: 4.2 },
            { type: "乏力", intensity: 6.0 },
          ],
          isHistorical: true,
        },
        // 时间点3
        {
          time: "2023-01-04",
          events: [
            { type: "发热", intensity: 10.2 },
            { type: "咳嗽", intensity: 12.5 },
            { type: "头痛", intensity: 3.0 },
            { type: "呼吸困难", intensity: 5.5 },
            { type: "乏力", intensity: 7.2 },
          ],
          isHistorical: true,
        },
        // 时间点4
        {
          time: "2023-01-07",
          events: [
            { type: "发热", intensity: 5.8 },
            { type: "咳嗽", intensity: 9.3 },
            { type: "头痛", intensity: 8.5 },
            { type: "呼吸困难", intensity: 6.8 },
            { type: "乏力", intensity: 8.0 },
          ],
          isHistorical: true,
        },
        // 时间点5
        {
          time: "2023-01-10",
          events: [
            { type: "发热", intensity: 4.2 },
            { type: "咳嗽", intensity: 6.5 },
            { type: "头痛", intensity: 4.0 },
            { type: "呼吸困难", intensity: 8.5 },
            { type: "乏力", intensity: 6.5 },
          ],
          isHistorical: true,
        },
        // 时间点6
        {
          time: "2023-01-11",
          events: [
            { type: "发热", intensity: 2.1 },
            { type: "咳嗽", intensity: 4.5 },
            { type: "头痛", intensity: 2.5 },
            { type: "呼吸困难", intensity: 12.0 },
            { type: "乏力", intensity: 5.8 },
          ],
          isHistorical: true,
        },
        // 时间点7
        {
          time: "2023-01-13",
          events: [
            { type: "发热", intensity: 0.8 },
            { type: "咳嗽", intensity: 1.2 },
            { type: "头痛", intensity: 0.5 },
            { type: "呼吸困难", intensity: 7.5 },
            { type: "乏力", intensity: 7.0 },
          ],
          isHistorical: true,
        },
        // 未来预测数据
        {
          time: "2023-01-15",
          events: [
            { type: "发热", intensity: 0.5 },
            { type: "咳嗽", intensity: 0.8 },
            { type: "头痛", intensity: 0.3 },
            { type: "呼吸困难", intensity: 9.2 },
            { type: "乏力", intensity: 6.5 },
          ],
          isHistorical: false,
        },
        {
          time: "2023-01-17",
          events: [
            { type: "发热", intensity: 0.2 },
            { type: "咳嗽", intensity: 0.5 },
            { type: "头痛", intensity: 0.1 },
            { type: "呼吸困难", intensity: 11.5 },
            { type: "乏力", intensity: 5.8 },
          ],
          isHistorical: false,
        },
        {
          time: "2023-01-19",
          events: [
            { type: "发热", intensity: 0.1 },
            { type: "咳嗽", intensity: 0.3 },
            { type: "头痛", intensity: 0.0 },
            { type: "呼吸困难", intensity: 13.8 },
            { type: "乏力", intensity: 4.2 },
          ],
          isHistorical: false,
        },
      ],
      colorMap: {
        发热: "#FF4560",
        咳嗽: "#00E396",
        头痛: "#775DD0",
        呼吸困难: "#FEB019",
        乏力: "#008FFB",
      },
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
  methods: {
    handleResize() {
      if (this.chart) {
        this.chart.resize();
      }
    },
    renderTimelineChart() {
      const chart = echarts.init(this.$refs.timelineChart, null, {
        renderer: "canvas",
      });
      this.chart = chart;

      // 获取所有事件类型
      const eventTypes = this.getUniqueEventTypes();

      // 准备时间轴数据
      const timeData = this.eventData.map((item) => item.time);

      // 区分历史数据和预测数据的时间点
      const historicalTimePoints = this.eventData.filter(
        (item) => item.isHistorical
      );
      // 我们不再需要单独的futureTimePoints变量，因为我们使用单一的连续线条

      // 获取最后一次观察时间点（历史数据的最后一个点）
      const lastObservationPoint =
        historicalTimePoints.length > 0
          ? historicalTimePoints[historicalTimePoints.length - 1].time
          : null;

      // 准备每种事件类型的数据系列
      const series = [];

      eventTypes.forEach((eventType) => {
        // 获取该事件类型的所有数据点（包括历史和预测）
        const allData = this.eventData.map((timePoint) => {
          const event = timePoint.events.find((e) => e.type === eventType);
          return {
            name: timePoint.time,
            value: event ? event.intensity : 0,
            // 标记是否为历史数据
            isHistorical: timePoint.isHistorical,
          };
        });

        // 分别创建历史数据和预测数据的系列
        // 1. 历史数据系列（实线）
        const historicalData = allData.filter((item) => item.isHistorical);
        if (historicalData.length > 0) {
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
              color: this.colorMap[eventType] || this.getRandomColor(),
              borderWidth: 2,
              borderColor: "#fff",
              shadowBlur: 4,
              shadowColor: "rgba(0, 0, 0, 0.2)",
            },
            lineStyle: {
              width: 4,
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
                  color: this.hexToRgba(
                    this.colorMap[eventType] || this.getRandomColor(),
                    0.7
                  ),
                },
                {
                  offset: 1,
                  color: this.hexToRgba(
                    this.colorMap[eventType] || this.getRandomColor(),
                    0.05
                  ),
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

          // 创建一个新的数据数组，只包含从最后观察点开始的数据
          // 为了确保连续性，我们需要将最后一个历史数据点添加为第一个点
          const predictData = [];

          // 添加最后一个历史数据点作为起始点
          predictData.push(lastHistoricalPoint);

          // 添加所有未来数据点
          futureData.forEach((point) => {
            predictData.push(point);
          });

          // 创建一个连接点数组，用于控制线条的显示
          // 只在最后历史点和第一个预测点之间显示线条
          const connectNulls = [];
          timeData.forEach((time) => {
            // 如果是最后历史点或未来点，则连接
            if (
              time === lastHistoricalPoint.name ||
              futureData.some((p) => p.name === time)
            ) {
              connectNulls.push(true);
            } else {
              // 其他点设为null，不显示线条
              connectNulls.push(false);
            }
          });

          series.push({
            name: eventType + " (预测)",
            type: "line",
            smooth: true,
            symbol: "emptyCircle",
            symbolSize: 8,
            connectNulls: true, // 确保空值点不连接
            sampling: "average",
            animation: true,
            animationDuration: 1000,
            animationEasing: "cubicOut",
            // 预测数据系列的 emphasis 配置
            emphasis: {
              focus: "series",
              itemStyle: {
                shadowBlur: 10,
                shadowColor: "rgba(0, 0, 0, 0.3)",
              },
            },
            itemStyle: {
              color: this.colorMap[eventType] || this.getRandomColor(),
              borderWidth: 2,
              borderColor: "#fff",
              shadowBlur: 4,
              shadowColor: "rgba(0, 0, 0, 0.2)",
            },
            lineStyle: {
              width: 3,
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
                  color: this.hexToRgba(
                    this.colorMap[eventType] || this.getRandomColor(),
                    0.4
                  ),
                },
                {
                  offset: 1,
                  color: this.hexToRgba(
                    this.colorMap[eventType] || this.getRandomColor(),
                    0.02
                  ),
                },
              ]),
              shadowBlur: 8,
              shadowColor: "rgba(0, 0, 0, 0.1)",
              opacity: 0.5,
            },
            // 使用完整的时间轴数据，但只在特定点显示数据
            data: timeData.map((time) => {
              // 如果是最后历史点或未来点，则显示实际数据
              if (time === lastHistoricalPoint.name) {
                return lastHistoricalPoint;
              }

              // 如果是未来点，显示对应数据
              const futurePoint = futureData.find((p) => p.name === time);
              if (futurePoint) {
                return futurePoint;
              }

              // 其他点返回空值，不显示
              return {
                name: time,
                value: "-",
                symbolSize: 0,
              };
            }),
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
            // 获取时间点
            const timePoint = paramsArray[0].axisValue;

            // 创建标题
            let result = `<div style="font-weight:bold;margin-bottom:10px;font-size:16px;color:#333;">${timePoint}</div>`;

            // 获取所有有效的数据点（排除空值和特殊系列）
            const validParams = paramsArray.filter(
              (p) =>
                p.componentSubType === "line" &&
                p.value !== "-" &&
                p.seriesName !== "最后观察时间" &&
                !p.seriesName.includes("预警") &&
                !p.seriesName.includes("真实事件")
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
                result += `<div style="display:flex;align-items:center;margin:8px 0;">
                  <span style="display:inline-block;width:12px;height:12px;background:${
                    data.historical.color
                  };margin-right:8px;border-radius:50%;"></span>
                  <span style="margin-right:8px;font-size:14px;">${baseName}:</span>
                  <span style="font-weight:bold;font-size:15px;">${
                    typeof data.historical.value === "number"
                      ? data.historical.value.toFixed(1)
                      : data.historical.value
                  }</span>
                </div>`;
              }

              // 添加预测数据（如果有）
              if (data.prediction) {
                result += `<div style="display:flex;align-items:center;margin:8px 0;">
                  <span style="display:inline-block;width:12px;height:12px;border:1px dashed ${
                    data.prediction.color
                  };margin-right:8px;border-radius:50%;"></span>
                  <span style="margin-right:8px;font-size:14px;">${
                    data.prediction.seriesName
                  }:</span>
                  <span style="font-weight:bold;font-size:15px;">${
                    typeof data.prediction.value === "number"
                      ? data.prediction.value.toFixed(1)
                      : data.prediction.value
                  }</span>
                </div>`;
              }
            });

            return result;
          },
          // ... 其他 tooltip 配置保持不变
          backgroundColor: "rgba(255, 255, 255, 0.95)",
          borderColor: "rgba(0, 0, 0, 0.1)",
          borderWidth: 1,
          textStyle: {
            color: "#333",
            fontSize: 14,
          },
          padding: 15,
          extraCssText:
            "box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15); border-radius: 8px;",
          axisPointer: {
            type: "line",
            lineStyle: {
              color: "rgba(0, 0, 0, 0.2)",
              width: 1,
              type: "dashed",
            },
            label: {
              backgroundColor: "#6a7985",
            },
            animation: true,
          },
          // 自定义tooltip内容，只显示鼠标所在曲线的数据
        },
        legend: {
          data: [...eventTypes],
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
          selected: {
            ...eventTypes.reduce((acc, type) => {
              acc[type] = true;
              return acc;
            }, {}),
          },
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
            dataView: {
              title: "数据视图",
              // readOnly: true,
              lang: ["数据视图", "关闭", "刷新"],
            },
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
          type: "category",
          boundaryGap: false,
          data: timeData,
          axisLabel: {
            rotate: 45,
            fontSize: 13,
            color: this.theme.axisColor,
            formatter: function (value) {
              return value;
            },
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
          name: "条件强度",
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

    getRandomColor() {
      // 生成随机颜色
      return "#" + Math.floor(Math.random() * 16777215).toString(16);
    },

    hexToRgba(hex, alpha) {
      // 将十六进制颜色转换为rgba
      const r = parseInt(hex.slice(1, 3), 16);
      const g = parseInt(hex.slice(3, 5), 16);
      const b = parseInt(hex.slice(5, 7), 16);
      return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    },

    prepareTargetEventThreshold() {
      // 选择呼吸困难作为目标事件
      const targetEventType = "呼吸困难";
      const thresholdValue = 10; // 设置阈值为10

      // 找出所有预测数据中的目标事件
      const futureData = this.eventData.filter((item) => !item.isHistorical);

      // 找出预测数据中超过阈值的点
      const thresholdPoints = [];

      futureData.forEach((timePoint) => {
        const targetEvent = timePoint.events.find(
          (e) => e.type === targetEventType
        );
        if (targetEvent && targetEvent.intensity >= thresholdValue) {
          thresholdPoints.push({
            name: timePoint.time,
            // 修改这里：使用[x, y]格式明确指定坐标
            value: [timePoint.time, targetEvent.intensity],
            itemStyle: {
              color: "#FF0000", // 红色标记
            },
            symbolSize: 20,
          });
        }
      });

      // 创建系列数组，包含阈值线和预警点
      const thresholdSeries = [];

      // 添加阈值横线
      thresholdSeries.push({
        name: `${targetEventType} (阈值线)`,
        type: "line",
        markLine: {
          silent: true,
          symbol: ["none", "none"],
          label: {
            formatter: `预警阈值: ${thresholdValue}`,
            position: "start",
            fontSize: 12,
            fontWeight: "bold",
            color: "#FF0000",
            backgroundColor: "rgba(255, 255, 255, 0.8)",
            padding: [3, 8],
            borderRadius: 4,
          },
          lineStyle: {
            type: "dashed",
            color: "#FF0000",
            width: 2,
            opacity: 0.3,
          },
          data: [
            {
              yAxis: thresholdValue,
              name: "预警阈值",
            },
          ],
        },
        data: [],
        zlevel: 2,
      });

      // 如果有超过阈值的点，创建一个特殊的标记系列
      if (thresholdPoints.length > 0) {
        thresholdSeries.push({
          name: `${targetEventType} (预警)`,
          type: "scatter",
          symbol: "triangle", // 使用三角形标记
          symbolSize: 25,
          data: thresholdPoints,
          label: {
            show: true,
            formatter: "预警",
            fontSize: 10,
            color: "#fff",
            position: "top",
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: "rgba(255, 0, 0, 0.5)",
            },
            scale: true,
          },
          itemStyle: {
            borderWidth: 2,
            borderColor: "#fff",
            shadowBlur: 4,
            shadowColor: "rgba(255, 0, 0, 0.5)",
          },
          zlevel: 3,
        });
      }

      return thresholdSeries;
    },
    // 添加新函数：准备真实事件数据系列
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

        this.realEvents.forEach((realEvent) => {
          // 检查该事件类型是否在当前真实事件中
          if (realEvent.event_type.includes(eventType)) {
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
                  value: [realEvent.time, eventData.intensity],
                  itemStyle: {
                    color: this.colorMap[eventType] || this.getRandomColor(),
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

              let estimatedIntensity = 0;

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

                  estimatedIntensity =
                    prevEvent.intensity +
                    ratio * (nextEvent.intensity - prevEvent.intensity);
                } else if (prevEvent) {
                  estimatedIntensity = prevEvent.intensity;
                } else if (nextEvent) {
                  estimatedIntensity = nextEvent.intensity;
                }
              } else if (prevPoint) {
                // 如果只有前点，使用前点的强度
                const prevEvent = prevPoint.events.find(
                  (e) => e.type === eventType
                );
                if (prevEvent) {
                  estimatedIntensity = prevEvent.intensity;
                }
              } else if (nextPoint) {
                // 如果只有后点，使用后点的强度
                const nextEvent = nextPoint.events.find(
                  (e) => e.type === eventType
                );
                if (nextEvent) {
                  estimatedIntensity = nextEvent.intensity;
                }
              }

              // 添加到事件点列表
              eventPoints.push({
                name: realEvent.time,
                value: [realEvent.time, estimatedIntensity],
                itemStyle: {
                  color: this.colorMap[eventType] || this.getRandomColor(),
                },
              });
            }
          }
        });

        // 如果有该类型的事件点，创建一个散点系列
        if (eventPoints.length > 0) {
          realEventsSeries.push({
            name: `${eventType} (真实事件)`,
            type: "scatter",
            symbol: "pin", // 使用图钉形状标记
            symbolSize: 30,
            data: eventPoints,
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowColor: "rgba(0, 0, 0, 0.5)",
              },
              scale: true,
            },
            itemStyle: {
              borderWidth: 2,
              borderColor: "#fff",
              shadowBlur: 4,
              shadowColor: "rgba(0, 0, 0, 0.3)",
            },
            zlevel: 4, // 确保真实事件点显示在最上层
          });
        }
      });

      return realEventsSeries;
    },
  },
  watch: {
    patientData: {
      handler(newVal) {
        if (newVal && newVal.length > 0) {
          this.eventData = newVal;
          this.renderTimelineChart();
        }
      },
      deep: true,
    },
    realEvents: {
      handler() {
        this.renderTimelineChart();
      },
      deep: true,
    },
  },
};
</script>

<style scoped>
.timeline-chart {
  width: 100%;
  height: 380px;
  /* padding: 20px; */
  border-radius: 12px;
  background: #ffffff;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  margin: 15px 0;
}

.timeline-chart:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

/* 响应式设计 */
@media screen and (max-width: 768px) {
  .timeline-chart {
    height: 40vh;
    /* padding: 15px; */
  }
}

@media screen and (max-width: 480px) {
  .timeline-chart {
    height: 35vh;
    /* padding: 10px; */
  }
}
</style>
