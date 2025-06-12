<template>
  <div class="chart-section">
    <div class="chart-wrapper">
      <!-- 刷新按钮放在外层，确保不被 ECharts 覆盖 -->
      <button class="refresh-button" @click="refreshChart">
        <i class="refresh-icon">↻</i>
      </button>
      <!-- 图表容器，供 ECharts 挂载 -->
      <div class="chart-container" ref="chart"></div>
    </div>
  </div>
</template>

<script>
import * as echarts from "echarts"; // 取消注释，导入ECharts

export default {
  name: "ChartComponent",
  props: {
    patientEventData: {
      type: Array,
      default: () => []
    },
    clusterData: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      chartInstance: null,
      resizeTimer: null,
      zoomTimer: null,
    };
  },
  watch: {
    patientEventData: {
      handler(newVal) {
        console.log('patientEventData 发生变化:', newVal);
        this.refreshChart();
      },
      deep: true
    },
    clusterData: {
      handler(newVal) {
        console.log('clusterData 发生变化:', newVal);
        this.refreshChart();
      },
      deep: true
    }
  },
  mounted() {
<<<<<<< HEAD
    try {
      // Wait for DOM to be ready
      this.$nextTick(() => {
        console.log('DOM is ready');
        this.initChart();
      });
    } catch (error) {
      console.error("Error in mounted hook:", error);
    }
    //this.initChart();
=======
    // try {
    //   // Wait for DOM to be ready
    //   this.$nextTick(() => {
    //     console.log("DOM is ready");
    //   });
    // } catch (error) {
    //   console.error("Error in mounted hook:", error);
    // }
    this.initChart();
>>>>>>> parent of 4eedc2b (feat-2026/06/06)
  },
  methods: {
    initChart() {
      // 初始化ECharts实例
      this.chartInstance = echarts.init(this.$refs.chart);
      console.log("卡片内部数据", this.patientEventData);
      console.log("聚类数据", this.clusterData);
<<<<<<< HEAD
      
=======

>>>>>>> parent of 4eedc2b (feat-2026/06/06)
      // 使用传入的数据，如果没有数据则不渲染图表
      if (this.patientEventData.length === 0 || this.clusterData.length === 0) {
        // 显示无数据提示
        this.chartInstance.setOption({
          title: {
<<<<<<< HEAD
            text: '暂无数据',
            left: 'center',
            top: 'center',
            textStyle: {
              color: '#999',
              fontSize: 16
            }
          }
=======
            text: "暂无数据",
            left: "center",
            top: "center",
            textStyle: {
              color: "#999",
              fontSize: 16,
            },
          },
>>>>>>> parent of 4eedc2b (feat-2026/06/06)
        });
        return;
      }

      const chartData = this.patientEventData;
      const clusterData = this.clusterData;
      // 准备数据
      const patientIds = chartData.map((item) => item.patientId);
      const series = chartData.map((patient, index) => {
        // 为每个病人生成不同的颜色，基于基色调的变化
        const color = this.generateColor(index, chartData.length);

        // 准备该病人的所有事件数据点
        const data = [
          // 添加起始点（0时刻）
          {
            value: [0, patientIds.indexOf(patient.patientId) * 1.5],
            itemStyle: { color: color },
            name: "初始状态",
            value_display: 0,
            patientId: patient.patientId,
<<<<<<< HEAD
=======
            realTime: 0,
>>>>>>> parent of 4eedc2b (feat-2026/06/06)
          },
          ...patient.events.map((event) => {
            // 计算同一小时内的事件偏移
            const sameHourEvents = patient.events.filter(
              (e) => e.hour === event.hour
            );
            const hourOffset =
              sameHourEvents.length > 1
                ? (sameHourEvents.indexOf(event) -
                    (sameHourEvents.length - 1) / 2) *
                  0.2
                : 0;

            // 根据事件发生的时间和聚类情况计算Y坐标
            // Y = clusterIndex*patientCount + clustergroup中对应cluster病人的patientId对应的index
            const cluster = clusterData.reduce((closest, current) => {
              return Math.abs(current.hour - event.hour) <
                Math.abs(closest.hour - event.hour)
                ? current
                : closest;
            });
            const clusterIndex = cluster.cluster.findIndex((c) =>
              c.includes(patient.patientId.toLowerCase())
            );
            const patientIndex = cluster.cluster[clusterIndex].findIndex(
              (id) => id === patient.patientId.toLowerCase()
            );
            const yCoord =
              clusterIndex * (patientIds.length * 2) + patientIndex * 1.5;

            return {
              value: [event.hour + hourOffset, yCoord],
              itemStyle: { color: color },
              name: event.name,
              value_display: event.value,
              patientId: patient.patientId,
<<<<<<< HEAD
=======
              realTime: event.hour,
>>>>>>> parent of 4eedc2b (feat-2026/06/06)
            };
          }),
        ];

        return {
          name: patient.patientId,
          type: "scatter",
<<<<<<< HEAD
          symbolSize: 15,          
=======
          symbolSize: 12,
>>>>>>> parent of 4eedc2b (feat-2026/06/06)
          data: data,
          itemStyle: { color: color },
          emphasis: {
            itemStyle: {
              // 鼠标悬停时保持原样式，只是稍微增大点的大小
              color: color,
              borderColor: "#fff",
              borderWidth: 2,
<<<<<<< HEAD
              shadowBlur: 10,
=======
              shadowBlur: 5,
>>>>>>> parent of 4eedc2b (feat-2026/06/06)
              shadowColor: "rgba(0, 0, 0, 0.3)",
            },
            scale: true, // 允许缩放效果
            focus: "none", // 只关注当前数据项
          },
          // 添加连线
          markLine: {
            silent: true, // 使线条不响应鼠标事件
            tooltip: { show: false }, // 明确禁用线条的tooltip
            data: this.generateMarkLines(data),
            lineStyle: { color: color, width: 2 },
            symbol: ["emptyCircle", "emptyCircle"],
          },
        };
      });

      const maxHour =
        chartData.reduce((max, patient) => {
          const maxHourForPatient = Math.max(
            ...patient.events.map((event) => event.hour)
          );
          return Math.max(max, maxHourForPatient);
        }, 0) + 1;
      // 配置图表选项
      const option = {
        tooltip: {
          trigger: "item", // 保持为item，只在数据点上触发
          formatter: function (params) {
            // 只有当params.componentType为'series'且params.seriesType为'scatter'时才显示tooltip
            if (
              params.componentType === "series" &&
              params.seriesType === "scatter"
            ) {
              return `
                <div>
                  <p><strong>病人ID:</strong> ${
                    params.data?.patientId || "未知"
                  }</p>
                  <p><strong>异常事件:</strong> ${
                    params.data?.name || "未知"
                  }</p>
<<<<<<< HEAD
                  <p><strong>严重程度:</strong> ${
                    params.data?.value_display || "未知"
                  }</p>
                  <p><strong>发生时间:</strong> ${
                    Math.round(params.data?.value?.[0]) || "未知"
=======
                  <p><strong>异常值:</strong> ${
                    params.data?.value_display || "未知"
                  }</p>
                  <p><strong>发生时间:</strong> ${
                    Math.round(params.data?.realTime) || "未知"
>>>>>>> parent of 4eedc2b (feat-2026/06/06)
                  }时</p>
                </div>
              `;
            }
            return ""; // 对于非散点的元素（如线），返回空字符串不显示tooltip
          },
          enterable: true, // 允许鼠标进入tooltip
          confine: true, // 将tooltip限制在图表区域内
          position: function (pos) {
            // 自定义tooltip位置，避免遮挡数据点
            return [pos[0] + 10, pos[1] - 10]; // 向右上方偏移
          },
        },
        legend: {
          show: true,
          left: 20,
          top: 20,
          orient: "horizontal",
<<<<<<< HEAD
          selectedMode: false,
=======
          selectedMode: true,
>>>>>>> parent of 4eedc2b (feat-2026/06/06)
          data: patientIds,
          textStyle: {
            color: "#333",
            fontSize: 9,
            fontWeight: 500,
            fontFamily: "'PingFang SC', 'Microsoft YaHei', sans-serif",
          },
          itemWidth: 20,
          itemHeight: 15,
          itemGap: 10,
          padding: [5, 10],
          borderRadius: 4,
          backgroundColor: "rgba(255, 255, 255, 0.9)",
          shadowColor: "rgba(0, 0, 0, 0.1)",
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowOffsetY: 0,
          itemStyle: {
            borderWidth: 0,
          },
          formatter: (name) => `病人 ${name}`,
<<<<<<< HEAD
=======
        },
        toolbox: {
          right: 20,
          top: 20,
          feature: {
            restore: { title: "还原" },
          },
>>>>>>> parent of 4eedc2b (feat-2026/06/06)
        },
        xAxis: {
          type: "value",
          name: "时间（小时）",
          nameLocation: "middle",
          nameGap: 30,
          min: 0,
          max: maxHour,
          splitLine: { show: true },
<<<<<<< HEAD
          // 添加安全处理，确保轴的范围有效
          scale: true,
          axisLabel: {
            formatter: '{value}'
          }
        },
        yAxis: {
          type: "value", 
          show: true,
          name: "病人聚类",
          nameLocation: "middle",
          nameGap: 20,
          // 改进范围计算，避免无效值
          min: function (value) {
            return value.min !== undefined ? Math.floor(value.min - 1) : 0;
          },
          max: function (value) {
            return value.max !== undefined ? Math.ceil(value.max + 1) : 10;
          },
          // 其他配置保持不变
=======
        },
        yAxis: {
          type: "value", // 保持value类型以支持数值坐标
          show: true, // 保持轴的基本结构
          name: "病人聚类", // 轴名称
          nameLocation: "middle",
          nameGap: 20,
          // 范围控制
          min: 0,
          max: function (value) {
            return value.max !== undefined ? Math.ceil(value.max + 1) : 10;
          },
>>>>>>> parent of 4eedc2b (feat-2026/06/06)
          nameTextStyle: {
            fontSize: 13,
            fontWeight: 500,
            color: "#2d5bff",
<<<<<<< HEAD
          },
          axisLine: { show: false },
          axisTick: { show: false },
          axisLabel: { show: false },
          splitLine: { show: false },
=======
          },
          // 隐藏轴线
          axisLine: {
            show: false,
          },
          // 隐藏刻度
          axisTick: {
            show: false,
          },
          // 隐藏标签
          axisLabel: {
            show: false,
          },
          // 隐藏分割线
          splitLine: {
            show: false,
          },
>>>>>>> parent of 4eedc2b (feat-2026/06/06)
        },
        // yAxis: {
        //   type: "category",
        //   show: true,
        //   data: patientIds,
        //   name: "病人ID",
        //   nameLocation: "middle",
        //   nameGap: 50,
        //   nameTextStyle: {
        //     fontSize: 13,
        //     fontWeight: 500,
        //     color: "#2d5bff",
        //   },
        //   axisLine: {
        //     lineStyle: {
        //       color: "#2d5bff",
        //     },
        //   },
        //   axisTick: {
        //     show: true,
        //   },
        //   axisLabel: {
        //     fontSize: 11,
        //     color: "#2d5bff",
        //   },
        // },
        grid: {
          left: "5%",
          right: "5%",
          bottom: "10%",
          top: "15%",
          containLabel: true,
        },
        dataZoom: [
          {
<<<<<<< HEAD
            type: 'inside',
            xAxisIndex: 0,
            filterMode: 'filter',
=======
            type: "inside",
            xAxisIndex: 0, // 只对x轴生效，不影响y轴
            filterMode: "filter",
>>>>>>> parent of 4eedc2b (feat-2026/06/06)
            start: 0,
            end: 100,
            zoomOnMouseWheel: true,
            moveOnMouseMove: true,
            preventDefaultMouseMove: true,
            // 添加安全处理
<<<<<<< HEAD
            rangeMode: ['value', 'value']
          },
          {
            type: 'slider',
            xAxisIndex: 0,
            filterMode: 'filter',
=======
            rangeMode: ["value", "value"],
            // 确保只在x轴方向缩放
            zoomLock: false,
            // yAxisIndex: null, // <-- Remove this line
          },
          {
            type: "slider",
            xAxisIndex: 0, // 只对x轴生效，不影响y轴
            // yAxisIndex: null, // <-- Remove this line
            filterMode: "filter",
>>>>>>> parent of 4eedc2b (feat-2026/06/06)
            height: 20,
            bottom: 10,
            start: 0,
            end: 100,
<<<<<<< HEAD
            handleIcon: 'M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7v-1.2h6.6V24.4z',
            handleSize: '80%',
            showDetail: false,
            // 添加安全处理
            rangeMode: ['value', 'value'],
            minSpan: 1,
            maxSpan: 100
          }
=======
            handleIcon:
              "M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7v-1.2h6.6V24.4z",
            handleSize: "80%",
            showDetail: false,
            // 添加安全处理
            rangeMode: ["value", "value"],
            minSpan: 1,
            maxSpan: 100,
          },
>>>>>>> parent of 4eedc2b (feat-2026/06/06)
        ],
        // brush: {
        //   toolbox: ["rect", "polygon", "keep", "clear"],
        //   throttleType: "debounce",
        //   throttleDelay: 300,
        // },
        // 添加事件处理
        graphic: [],
        series: series.map((s) => ({
          ...s,
          itemStyle: {
            ...s.itemStyle,
            opacity: 1, // 添加默认透明度
          },
        })),
      };

      // 应用配置
      this.chartInstance.setOption(option);
<<<<<<< HEAD
      // 记录当前选中的组
      let currentSelectedGroup = null;
      let currentZoomRange = {
        start: 0,
        end: 100
      };
      
      // 使用 dataZoomEnd 事件替代 datazoom 事件，只在缩放操作结束时触发
      this.chartInstance.on('dataZoomEnd', (params) => {
        try {
          // 获取当前的缩放范围，添加安全检查
          if (params && typeof params.start !== 'undefined' && typeof params.end !== 'undefined') {
            currentZoomRange.start = params.start;
            currentZoomRange.end = params.end;
            console.log('图表缩放操作结束:', currentZoomRange.start, currentZoomRange.end);
            
            // 延迟执行重绘，避免频繁重绘
            if (this.zoomTimer) {
              clearTimeout(this.zoomTimer);
            }
            
            this.zoomTimer = setTimeout(() => {
              try {
                console.log('准备更新连线数据');
                
                // 不要尝试更新现有的markLine，而是完全重新绘制图表
                this.refreshChart();
                
              } catch (error) {
                console.error('缩放后更新图表出错:', error);
              }
            }, 300); // 300ms 延迟，避免频繁重绘
          } else {
            console.warn('缩放事件参数无效:', params);
          }
        } catch (error) {
          console.error('处理缩放事件时出错:', error);
        }
      });
=======
      // 监听 legend 选择变化，隐藏时清空 markLine
      this.chartInstance.on("legendselectchanged", (params) => {
        const selected = params.selected;
        const newSeries = series.map((s) => {
          if (!selected[s.name]) {
            // 被隐藏时，清空 markLine
            return {
              ...s,
              markLine: {
                ...s.markLine,
                data: [],
              },
            };
          }
          // 显示时恢复 markLine
          return s;
        });
        this.chartInstance.setOption({
          series: newSeries,
        });
      });

      //记录当前选中的组
      let currentSelectedGroup = null;

>>>>>>> parent of 4eedc2b (feat-2026/06/06)
      // 添加点击事件处理
      this.chartInstance.on("click", (params) => {
        if (
          params.componentType === "series" &&
          params.seriesType === "scatter"
        ) {
          const currentPatientId = params.data.patientId;
          const currentHour = Math.floor(params.data.value[0]);

          // 如果点击的是当前已选中组的病人，则恢复所有病人的显示状态
          if (
            currentSelectedGroup &&
            currentSelectedGroup.includes(currentPatientId.toLowerCase())
          ) {
            // 恢复所有点和线的透明度
            this.chartInstance.setOption({
              series: series.map((s) => ({
                ...s,
                itemStyle: { ...s.itemStyle, opacity: 1 },
                markLine: {
                  ...s.markLine,
                  lineStyle: {
                    ...s.markLine.lineStyle,
                    opacity: 1,
                  },
                },
              })),
            });
            currentSelectedGroup = null;
            return;
          }

          // 找到当前时间点最近的聚类信息
          let relevantCluster = null;
          let maxHour = -1;

          for (const clusterInfo of clusterData) {
            if (clusterInfo.hour <= currentHour && clusterInfo.hour > maxHour) {
              relevantCluster = clusterInfo;
              maxHour = clusterInfo.hour;
            }
          }

          if (relevantCluster) {
            // 找到当前病人所在的聚类组
            let sameClusterPatients = [];

            for (const cluster of relevantCluster.cluster) {
              if (cluster.includes(currentPatientId.toLowerCase())) {
                sameClusterPatients = cluster.map((id) => id.toUpperCase());
                break;
              }
            }

            // 更新当前选中的组
            currentSelectedGroup = sameClusterPatients.map((id) =>
              id.toLowerCase()
            );

            // 设置非同组病人的点和线的透明度
            this.chartInstance.setOption({
              series: series.map((s) => ({
                ...s,
                itemStyle: {
                  ...s.itemStyle,
                  opacity: sameClusterPatients.includes(s.name) ? 1 : 0.1,
                },
                markLine: {
                  ...s.markLine,
                  lineStyle: {
                    ...s.markLine.lineStyle,
                    opacity: sameClusterPatients.includes(s.name) ? 1 : 0.1,
                  },
                },
              })),
            });
          }
        }
      });

      // 移除原有的mouseover和mouseout事件
      this.chartInstance.off("mouseover");
      this.chartInstance.off("mouseout");
      // 响应窗口大小变化
      window.addEventListener("resize", this.resizeChart);
    },

    // 生成连接同一病人的所有点的标记线，在聚类点添加垂直线段
<<<<<<< HEAD
    generateMarkLines(data) {
      console.log('===== generateMarkLines 方法被调用 =====');
      if (!data || data.length <= 1) return [];
      console.log('生成连线数据，数据点数量:', data.length);

      try {
        // 按时间排序
        const sortedData = [...data].sort((a, b) => a.value[0] - b.value[0]);

        // 获取所有聚类时间点
        const clusterTimes = this.clusterData.map((c) => c.hour);
        console.log('聚类时间点:', clusterTimes);

        // 生成连线数据
        const lines = [];

        for (let i = 0; i < sortedData.length - 1; i++) {
          const startPoint = sortedData[i];
          const endPoint = sortedData[i + 1];
          
          // 更严格的数据验证
          if (
            !startPoint || !endPoint || 
            !startPoint.value || !endPoint.value ||
            !Array.isArray(startPoint.value) || !Array.isArray(endPoint.value) ||
            startPoint.value.length < 2 || endPoint.value.length < 2 ||
            isNaN(startPoint.value[0]) || isNaN(startPoint.value[1]) ||
            isNaN(endPoint.value[0]) || isNaN(endPoint.value[1])
          ) {
            console.warn('跳过无效的数据点:', startPoint, endPoint);
            continue;
          }

          // 确保坐标值是数字类型
          const startCoord = [+startPoint.value[0], +startPoint.value[1]];
          const endCoord = [+endPoint.value[0], +endPoint.value[1]];

          const startTime = Math.round(startPoint.value[0]);
          const endTime = Math.round(endPoint.value[0]);

          // 检查这两个点之间是否有聚类时间点
          const betweenClusterTimes = clusterTimes
            .filter((time) => time > startTime && time < endTime)
            .sort((a, b) => a - b);

          if (betweenClusterTimes.length === 0) {
            // 如果没有聚类时间点，直接连接
            lines.push([
              { coord: startCoord, lineStyle: { type: "solid", width: 2 } },
              { coord: endCoord, lineStyle: { type: "solid", width: 2 } },
            ]);
          } else {
            // 如果有聚类时间点，添加垂直过渡
            let lastPoint = { ...startPoint, value: startCoord };

            // 对每个中间的聚类时间点，创建两个点形成垂直线段
            for (const clusterTime of betweenClusterTimes) {
              // 获取该时间点对应的聚类
              const cluster = this.clusterData.find(
                (c) => c.hour === clusterTime
              );
              if (!cluster) {
                console.warn('找不到时间点对应的聚类:', clusterTime);
                continue;
              }

              // 找到患者在该聚类中的位置
              const patientId = startPoint.patientId.toLowerCase();
              const clusterIndex = cluster.cluster.findIndex((c) =>
                c.includes(patientId)
              );
              if (clusterIndex === -1) {
                console.warn('找不到患者在聚类中的位置:', patientId, clusterTime);
                continue; // 防止找不到聚类
              }

              const patientIndex = cluster.cluster[clusterIndex].findIndex(
                (id) => id === patientId
              );
              if (patientIndex === -1) {
                console.warn('找不到患者在聚类组中的索引:', patientId, clusterIndex);
                continue; // 防止找不到患者
              }

              // 计算Y坐标
              const patientIds = this.patientEventData.map((item) => item.patientId);
              const yCoord =
                clusterIndex * (patientIds.length * 2) + patientIndex * 1.5;
                
              // 验证坐标有效性
              if (isNaN(yCoord)) {
                console.warn('计算出的Y坐标无效:', yCoord);
                continue;
              }
              
              // 添加到上一个点到聚类时间点的水平线段
              lines.push([
                {
                  coord: [+lastPoint.value[0], +lastPoint.value[1]],
                  lineStyle: { type: "solid", width: 2 },
                },
                {
                  coord: [+clusterTime, +lastPoint.value[1]],
                  lineStyle: { type: "solid", width: 2 },
                },
              ]);

              // 添加垂直过渡线段
              lines.push([
                {
                  coord: [+clusterTime, +lastPoint.value[1]],
                  lineStyle: { type: "dashed", width: 1 },
                },
                {
                  coord: [+clusterTime, +yCoord],
                  lineStyle: { type: "dashed", width: 1 },
                },
              ]);

              // 更新最后一个点
              lastPoint = {
                value: [+clusterTime, +yCoord],
                patientId: startPoint.patientId,
              };
            }

            // 添加最后一段线段到终点
            lines.push([
              { coord: [+lastPoint.value[0], +lastPoint.value[1]], lineStyle: { type: "solid", width: 2 } },
              { coord: endCoord, lineStyle: { type: "solid", width: 2 } },
            ]);
          }
        }

        // 最终验证所有线条数据
        // 最终验证所有线条数据
        const validLines = lines.filter(line => {
          if (!Array.isArray(line) || line.length !== 2) {
            console.warn('无效的线条数据格式:', line);
            return false;
          }
          const [start, end] = line;
          const isValid = (
            start && end && 
            start.coord && end.coord && 
            Array.isArray(start.coord) && Array.isArray(end.coord) &&
            start.coord.length === 2 && end.coord.length === 2 &&
            !isNaN(start.coord[0]) && !isNaN(start.coord[1]) &&
            !isNaN(end.coord[0]) && !isNaN(end.coord[1]) &&
            isFinite(start.coord[0]) && isFinite(start.coord[1]) &&
            isFinite(end.coord[0]) && isFinite(end.coord[1])
          );
          if (!isValid) {
            console.warn('无效的线条坐标:', start, end);
          }
          return isValid;
        });
        
        // 检查坐标范围，防止极端值导致缩放问题
        let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
        
        validLines.forEach(line => {
          const [start, end] = line;
          minX = Math.min(minX, start.coord[0], end.coord[0]);
          maxX = Math.max(maxX, start.coord[0], end.coord[0]);
          minY = Math.min(minY, start.coord[1], end.coord[1]);
          maxY = Math.max(maxY, start.coord[1], end.coord[1]);
        });
        
        // 如果范围异常，记录警告并返回空数组
        if (!isFinite(minX) || !isFinite(maxX) || !isFinite(minY) || !isFinite(maxY) ||
            maxX - minX <= 0 || maxY - minY <= 0) {
          console.warn('连线坐标范围异常:', { minX, maxX, minY, maxY });
          return [];
        }
        
        console.log(`生成连线完成，有效线条数量: ${validLines.length}/${lines.length}`);
        console.log('线条示例:', validLines.slice(0, 2)); // 只显示前两个线条作为示例
        console.log('坐标范围:', { minX, maxX, minY, maxY });
        return validLines;
        // return validLines;
      } catch (error) {
        console.error('生成连线时发生错误:', error);
        return []; // 出错时返回空数组，避免图表崩溃
      }
=======
    // 生成连接同一病人的所有点的标记线，在聚类点添加垂直线段
    generateMarkLines(data) {
      if (data.length <= 1) return [];

      // 按时间排序
      const sortedData = [...data].sort((a, b) => a.value[0] - b.value[0]);

      // 获取所有聚类时间点
      const clusterTimes = this.clusterData.map((c) => c.hour);

      // 生成连线数据
      const lines = [];

      for (let i = 0; i < sortedData.length - 1; i++) {
        const startPoint = sortedData[i];
        const endPoint = sortedData[i + 1];
        if (
          !startPoint.value ||
          !endPoint.value ||
          !Array.isArray(startPoint.value) ||
          !Array.isArray(endPoint.value) ||
          startPoint.value.length < 2 ||
          endPoint.value.length < 2
        ) {
          continue;
        }

        const startTime = Math.round(startPoint.realTime);
        const endTime = Math.round(endPoint.realTime);

        // 检查这两个点之间是否有聚类时间点
        const betweenClusterTimes = clusterTimes
          .filter((time) => time >= startTime && time <= endTime)
          .sort((a, b) => a - b);

        if (betweenClusterTimes.length === 0) {
          // 如果没有聚类时间点，直接连接（使用正确格式）
          lines.push([
            { coord: startPoint.value, lineStyle: { type: "solid", width: 2 } },
            { coord: endPoint.value, lineStyle: { type: "solid", width: 2 } },
          ]);
        } else {
          // 如果有聚类时间点，添加垂直过渡
          let lastPoint = startPoint;

          // 对每个中间的聚类时间点，创建两个点形成垂直线段
          for (const clusterTime of betweenClusterTimes) {
            // 获取该时间点对应的聚类
            const cluster = this.clusterData.find(
              (c) => c.hour === clusterTime
            );
            if (!cluster) continue;

            // 找到患者在该聚类中的位置
            const patientId = startPoint.patientId.toLowerCase();
            const clusterIndex = cluster.cluster.findIndex((c) =>
              c.includes(patientId)
            );
            if (clusterIndex === -1) continue; // 防止找不到聚类

            const patientIndex = cluster.cluster[clusterIndex].findIndex(
              (id) => id === patientId
            );
            if (patientIndex === -1) continue; // 防止找不到患者

            // 计算Y坐标
            const patientIds = this.patientEventData.map(
              (item) => item.patientId
            );
            const yCoord =
              clusterIndex * (patientIds.length * 2) + patientIndex * 1.5;
            // 添加到上一个点到聚类时间点的水平线段（粗实线）
            lines.push([
              {
                coord: lastPoint.value,
                lineStyle: { type: "solid", width: 2 },
              },
              {
                coord: [clusterTime, lastPoint.value[1]],
                lineStyle: { type: "solid", width: 2 },
              },
            ]);

            // 添加垂直过渡线段（虚线）
            lines.push([
              {
                coord: [clusterTime, lastPoint.value[1]],
                lineStyle: { type: "dashed", width: 1 },
              },
              {
                coord: [clusterTime, yCoord],
                lineStyle: { type: "dashed", width: 1 },
              },
            ]);

            // 更新最后一个点
            lastPoint = {
              value: [clusterTime, yCoord],
              patientId: startPoint.patientId,
            };
          }

          // 添加最后一段线段到终点（粗实线）
          lines.push([
            { coord: lastPoint.value, lineStyle: { type: "solid", width: 2 } },
            { coord: endPoint.value, lineStyle: { type: "solid", width: 2 } },
          ]);
        }
      }

      return lines;
>>>>>>> parent of 4eedc2b (feat-2026/06/06)
    },
    generateColor(index, total) {
      // 基准颜色 #2d5bff
      const baseColor = {
        r: 0x2d,
        g: 0x5b,
        b: 0xff,
      };

      // 计算色相偏移量，确保颜色分布均匀
      const hueOffset = (360 / total) * index;

      // 将RGB转换为HSL
      const rgbToHsl = (r, g, b) => {
        r /= 255;
        g /= 255;
        b /= 255;
        const max = Math.max(r, g, b);
        const min = Math.min(r, g, b);
        let h,
          s,
          l = (max + min) / 2;

        if (max === min) {
          h = s = 0;
        } else {
          const d = max - min;
          s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
          switch (max) {
            case r:
              h = (g - b) / d + (g < b ? 6 : 0);
              break;
            case g:
              h = (b - r) / d + 2;
              break;
            case b:
              h = (r - g) / d + 4;
              break;
          }
          h /= 6;
        }
        return [h * 360, s * 100, l * 100];
      };

      // 将HSL转换回RGB
      const hslToRgb = (h, s, l) => {
        h /= 360;
        s /= 100;
        l /= 100;
        let r, g, b;

        if (s === 0) {
          r = g = b = l;
        } else {
          const hue2rgb = (p, q, t) => {
            if (t < 0) t += 1;
            if (t > 1) t -= 1;
            if (t < 1 / 6) return p + (q - p) * 6 * t;
            if (t < 1 / 2) return q;
            if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
            return p;
          };

          const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
          const p = 2 * l - q;
          r = hue2rgb(p, q, h + 1 / 3);
          g = hue2rgb(p, q, h);
          b = hue2rgb(p, q, h - 1 / 3);
        }

        return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)];
      };

      // 获取基准颜色的HSL值
      const [baseH, baseS, baseL] = rgbToHsl(
        baseColor.r,
        baseColor.g,
        baseColor.b
      );

      // 基于基准颜色生成新的颜色
      const newH = (baseH + hueOffset) % 360;
      const [r, g, b] = hslToRgb(newH, baseS, baseL);

      // 转换为16进制颜色代码
      return `#${r.toString(16).padStart(2, "0")}${g
        .toString(16)
        .padStart(2, "0")}${b.toString(16).padStart(2, "0")}`;
    },

    refreshChart() {
<<<<<<< HEAD
      console.log('开始刷新图表');
      // 保存当前的缩放范围和选中状态
      let savedZoomRange = null;
      // let savedSelectedGroup = null;
      
      if (this.chartInstance) {
        try {
          // 获取当前图表的选项
          const option = this.chartInstance.getOption();
          
          // 保存缩放范围
          if (option.dataZoom && option.dataZoom.length > 0) {
            savedZoomRange = {
              start: option.dataZoom[0].start,
              end: option.dataZoom[0].end
            };
            console.log('保存当前缩放范围:', savedZoomRange);
          }
          
          // 销毁当前图表实例
          this.chartInstance.dispose();
        } catch (error) {
          console.error('保存图表状态时出错:', error);
        }
      }
      
      // 重新初始化图表
      this.$nextTick(() => {
        console.log('重新初始化图表，将重新生成连线');
        this.initChart();
        
        // 如果有保存的缩放范围，恢复它
        if (savedZoomRange && this.chartInstance) {
          setTimeout(() => {
            console.log('恢复缩放范围:', savedZoomRange);
            this.chartInstance.setOption({
              dataZoom: [
                {
                  start: savedZoomRange.start,
                  end: savedZoomRange.end
                },
                {
                  start: savedZoomRange.start,
                  end: savedZoomRange.end
                }
              ]
            });
          }, 200); // 增加延迟，确保图表已完全初始化
        }
      });
    }
  },
=======
      // 销毁当前图表实例
      if (this.chartInstance) {
        this.chartInstance.dispose();
      }
      // 重新初始化图表
      this.$nextTick(() => {
        this.initChart();
      });
    },

    // 修复 resizeChart 方法
    resizeChart() {
      if (!this.chartInstance) return;

      try {
        // 创建一个延迟，确保DOM已完全调整大小
        if (this.resizeTimer) {
          clearTimeout(this.resizeTimer);
        }

        this.resizeTimer = setTimeout(() => {
          // 先尝试普通的 resize
          try {
            this.chartInstance.resize();
          } catch (error) {
            console.warn("图表调整大小时出错，尝试重新初始化:", error);
            // 如果 resize 失败，尝试完全重新创建图表
            this.chartInstance.dispose();
            this.chartInstance = null;
            this.$nextTick(() => {
              this.initChart();
            });
          }
        }, 100); // 添加200ms延迟，避免频繁调整
      } catch (error) {
        console.error("resizeChart 错误:", error);
      }
    },
  },

>>>>>>> parent of 4eedc2b (feat-2026/06/06)
  // 确保在组件销毁时清理资源
  beforeUnmount() {
    // 组件销毁前移除事件监听
    window.removeEventListener("resize", this.resizeChart);
<<<<<<< HEAD
    // 清理计时器
    if (this.resizeTimer) {
      clearTimeout(this.resizeTimer);
    }
    if (this.zoomTimer) {
      clearTimeout(this.zoomTimer);
    }
=======
>>>>>>> parent of 4eedc2b (feat-2026/06/06)
    // 销毁图表实例
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
