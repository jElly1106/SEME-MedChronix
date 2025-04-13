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
  data() {
    return {
      // 扩充后的示例数据，一个病人在同一小时可能发生多个异常事件
      mockChartData: [
        {
          patientId: "P1",
          events: [
            { hour: 1, value: 10, name: "心率过快" },
            { hour: 3, value: 15, name: "血压偏高" },
            { hour: 3, value: 12, name: "呼吸急促" },
            { hour: 6, value: 18, name: "发热" },
            { hour: 6, value: 14, name: "心率不齐" },
            { hour: 8, value: 20, name: "血压偏高" },
          ],
        },
        {
          patientId: "P2",
          events: [
            { hour: 2, value: 8, name: "心率不齐" },
            { hour: 4, value: 12, name: "呼吸急促" },
            { hour: 5, value: 15, name: "心率过快" },
            { hour: 7, value: 16, name: "血氧偏低" },
            { hour: 9, value: 20, name: "发热" },
            { hour: 9, value: 18, name: "低血压" },
          ],
        },
        {
          patientId: "P3",
          events: [
            { hour: 1, value: 9, name: "心率过快" },
            { hour: 3, value: 11, name: "呼吸急促" },
            { hour: 5, value: 5, name: "低血压" },
            { hour: 7, value: 13, name: "发热" },
            { hour: 8, value: 16, name: "血氧偏低" },
          ],
        },
        {
          patientId: "P4",
          events: [
            { hour: 1, value: 7, name: "心率过快" },
            { hour: 1, value: 9, name: "呼吸急促" },
            { hour: 2, value: 11, name: "血压偏低" },
            { hour: 4, value: 14, name: "血压偏高" },
            { hour: 6, value: 17, name: "发热" },
            { hour: 8, value: 19, name: "心率不齐" },
          ],
        },
        {
          patientId: "P5",
          events: [
            { hour: 2, value: 10, name: "血氧偏低" },
            { hour: 4, value: 13, name: "心率过快" },
            { hour: 5, value: 16, name: "发热" },
            { hour: 7, value: 18, name: "血压偏高" },
            { hour: 9, value: 15, name: "呼吸急促" },
          ],
        },
        {
          patientId: "P6",
          events: [
            { hour: 1, value: 8, name: "呼吸急促" },
            { hour: 3, value: 12, name: "心率不齐" },
            { hour: 5, value: 15, name: "血压偏低" },
            { hour: 6, value: 17, name: "发热" },
            { hour: 8, value: 20, name: "血氧偏低" },
            { hour: 9, value: 14, name: "心率过快" },
          ],
        },
        {
          patientId: "P7",
          events: [
            { hour: 2, value: 11, name: "血压偏高" },
            { hour: 4, value: 14, name: "心率过快" },
            { hour: 6, value: 16, name: "呼吸急促" },
            { hour: 7, value: 19, name: "发热" },
            { hour: 9, value: 17, name: "血氧偏低" },
          ],
        },
        {
          patientId: "P8",
          events: [
            { hour: 1, value: 9, name: "血压偏低" },
            { hour: 3, value: 13, name: "心率不齐" },
            { hour: 5, value: 15, name: "发热" },
            { hour: 7, value: 18, name: "血氧偏低" },
            { hour: 8, value: 16, name: "呼吸急促" },
            { hour: 9, value: 20, name: "心率过快" },
          ],
        },
      ],
      clustergroup: [
        {
          hour: 0,
          cluster: [["p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8"]],
        },
        {
          hour: 2,
          cluster: [
            ["p1", "p3", "p6"],
            ["p2", "p4", "p8"],
            ["p5", "p7"],
          ],
        },
        {
          hour: 4,
          cluster: [
            ["p1", "p4", "p7"],
            ["p2", "p5"],
            ["p3", "p6", "p8"],
          ],
        },
        {
          hour: 6,
          cluster: [
            ["p2", "p4", "p6"],
            ["p1", "p5", "p7"],
            ["p3", "p8"],
          ],
        },
        {
          hour: 8,
          cluster: [
            ["p3", "p5"],
            ["p2", "p6", "p1"],
            ["p4", "p7", "p8"],
          ],
        },
      ],

      chartInstance: null,
      resizeTimer: null,
    };
  },
  mounted() {
    this.initChart();
  },
  methods: {
    initChart() {
      // 初始化ECharts实例
      this.chartInstance = echarts.init(this.$refs.chart);

      // 准备数据
      const patientIds = this.mockChartData.map((item) => item.patientId);
      const series = this.mockChartData.map((patient, index) => {
        // 为每个病人生成不同的颜色，基于基色调的变化
        const color = this.generateColor(index, this.mockChartData.length);

        // 准备该病人的所有事件数据点
        const data = [
          // 添加起始点（0时刻）
          {
            value: [0, patientIds.indexOf(patient.patientId) * 1.5],
            itemStyle: { color: color },
            name: "初始状态",
            value_display: 0,
            patientId: patient.patientId,
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
            const cluster = this.clustergroup.reduce((closest, current) => {
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
            };
          }),
        ];

        return {
          name: patient.patientId,
          type: "scatter",
          symbolSize: 15,
          data: data,
          itemStyle: { color: color },
          emphasis: {
            itemStyle: {
              // 鼠标悬停时保持原样式，只是稍微增大点的大小
              color: color,
              borderColor: "#fff",
              borderWidth: 2,
              shadowBlur: 10,
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
        this.mockChartData.reduce((max, patient) => {
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
                  <p><strong>严重程度:</strong> ${
                    params.data?.value_display || "未知"
                  }</p>
                  <p><strong>发生时间:</strong> ${
                    Math.round(params.data?.value?.[0]) || "未知"
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
          selectedMode: false,
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
        },
        xAxis: {
          type: "value",
          name: "时间（小时）",
          nameLocation: "middle",
          nameGap: 30,
          min: 0,
          max: maxHour,
          splitLine: { show: true },
        },
        yAxis: {
          type: "value", // 保持value类型以支持数值坐标
          show: true, // 保持轴的基本结构
          name: "病人聚类", // 轴名称
          nameLocation: "middle",
          nameGap: 20,
          // 范围控制
          min: function (value) {
            return Math.floor(value.min - 1);
          },
          max: function (value) {
            return Math.ceil(value.max + 1);
          },
          nameTextStyle: {
            fontSize: 13,
            fontWeight: 500,
            color: "#2d5bff",
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
          // 添加这一行，隐藏分割线
          splitLine: {
            show: false,
          },
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
      // 记录当前选中的组
      let currentSelectedGroup = null;

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

          for (const clusterInfo of this.clustergroup) {
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
    generateMarkLines(data) {
      if (data.length <= 1) return [];

      // 按时间排序
      const sortedData = [...data].sort((a, b) => a.value[0] - b.value[0]);

      // 获取所有聚类时间点
      const clusterTimes = this.clustergroup.map((c) => c.hour);

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

        const startTime = Math.round(startPoint.value[0]);
        const endTime = Math.round(endPoint.value[0]);

        // 检查这两个点之间是否有聚类时间点
        const betweenClusterTimes = clusterTimes
          .filter((time) => time >= startTime && time <= endTime)
          .sort((a, b) => a - b);

        if (betweenClusterTimes.length === 0) {
          // 如果没有聚类时间点，直接连接（使用正确格式）
          lines.push([
            { coord: startPoint.value, lineStyle: { type: "solid", width: 5 } },
            { coord: endPoint.value, lineStyle: { type: "solid", width: 5 } },
          ]);
        } else {
          // 如果有聚类时间点，添加垂直过渡
          let lastPoint = startPoint;

          // 对每个中间的聚类时间点，创建两个点形成垂直线段
          for (const clusterTime of betweenClusterTimes) {
            // 获取该时间点对应的聚类
            const cluster = this.clustergroup.find(
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
            const patientIds = this.mockChartData.map((item) => item.patientId);
            const yCoord =
              clusterIndex * (patientIds.length * 2) + patientIndex * 1.5;
            // 添加到上一个点到聚类时间点的水平线段（粗实线）
            lines.push([
              {
                coord: lastPoint.value,
                lineStyle: { type: "solid", width: 5 },
              },
              {
                coord: [clusterTime, lastPoint.value[1]],
                lineStyle: { type: "solid", width: 5 },
              },
            ]);

            // 添加垂直过渡线段（虚线）
            lines.push([
              {
                coord: [clusterTime, lastPoint.value[1]],
                lineStyle: { type: "dashed", width: 2 },
              },
              {
                coord: [clusterTime, yCoord],
                lineStyle: { type: "dashed", width: 2 },
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
            { coord: lastPoint.value, lineStyle: { type: "solid", width: 5 } },
            { coord: endPoint.value, lineStyle: { type: "solid", width: 5 } },
          ]);
        }
      }

      return lines;
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

  // 确保在组件销毁时清理资源
  beforeUnmount() {
    // 组件销毁前移除事件监听
    window.removeEventListener("resize", this.resizeChart);
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
