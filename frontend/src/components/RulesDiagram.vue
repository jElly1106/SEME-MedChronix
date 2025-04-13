<template>
  <div ref="chart" style="width: 600px; height: 300px"></div>
</template>

<script>
import * as echarts from "echarts";

export default {
  name: "EchartsFloatingGraph",
  data() {
    return {
      chart: null,
    };
  },
  mounted() {
    this.initChart();
    window.addEventListener("resize", this.resizeChart);
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.resizeChart);
    if (this.chart) {
      this.chart.dispose();
    }
  },
  methods: {
    initChart() {
      this.chart = echarts.init(this.$refs.chart);

      // 定义节点数据：中心节点和多个规则节点
      const nodes = [
        {
          id: 0,
          name: "目标事件",
          symbolSize: 70,
          draggable: true,
          category: 0,
          description: "这是目标事件的信息",
        },
        {
          id: 1,
          name: "规则1",
          symbolSize: 50,
          draggable: true,
          category: 1,
          description: "这是规则1的详细描述。",
          time: "2025-03-15 10:00",
        },
        {
          id: 2,
          name: "规则2",
          symbolSize: 50,
          draggable: true,
          category: 1,
          description: "这是规则2的详细描述。",
          time: "2025-03-15 11:00",
        },
        {
          id: 3,
          name: "规则3",
          symbolSize: 50,
          draggable: true,
          category: 1,
          description: "这是规则3的详细描述。",
          time: "2025-03-15 12:00",
        },
        {
          id: 4,
          name: "规则4",
          symbolSize: 50,
          draggable: true,
          category: 1,
          description: "这是规则4的详细描述。",
          time: "2025-03-15 13:00",
        },
        {
          id: 5,
          name: "规则5",
          symbolSize: 50,
          draggable: true,
          category: 1,
          description: "这是规则5的详细描述。",
          time: "2025-03-15 14:00",
        },
        {
          id: 6,
          name: "规则6",
          symbolSize: 50,
          draggable: true,
          category: 1,
          description: "这是规则6的详细描述。",
          time: "2025-03-15 15:00",
        },
      ];

      // 定义连线：中心节点（id:0）与每个规则节点连接
      const links = [];
      for (let i = 1; i <= 6; i++) {
        links.push({
          source: 0,
          target: i,
          lineStyle: {
            color: "rgba(0, 0, 0, 0.6)",
            width: 2,
            type: "dashed", // 虚线效果
            curveness: 0.2, // 曲线弯曲程度
            shadowColor: "rgba(0, 0, 0, 0.3)",
            shadowBlur: 4,
            shadowOffsetX: 2,
            shadowOffsetY: 2,
          },
        });
      }

      // 配置项
      const option = {
        graphic: [
          {
            type: "text",
            left: 10, // 距离左边 10px
            top: 10, // 距离顶部 10px
            style: {
              text: "规则展示",
              fill: "#000", // 文本颜色
              font: "bold 16px Arial",
            },
          },
        ],
        tooltip: {
          formatter: function (params) {
            if (params.dataType === "node") {
              if (params.data.category === 1) {
                return `
                    <div>
                      <strong>${params.data.name}</strong><br/>
                      描述：${params.data.description}<br/>
                      时间：${params.data.time}
                    </div>
                  `;
              } else {
                return `<div><strong>${params.data.name}</strong><br/>${params.data.description}</div>`;
              }
            }
          },
        },
        legend: [
          {
            data: ["目标事件", "规则"],
          },
        ],
        series: [
          {
            name: "规则图",
            type: "graph",
            layout: "force",
            roam: true, // 允许拖拽和缩放
            force: {
              repulsion: 300,
              edgeLength: [100, 200],
            },
            label: {
              show: true,
              position: "inside",
              fontSize: 14,
            },
            // 添加类别配置，用于 legend 和节点样式区分
            categories: [{ name: "目标事件" }, { name: "规则" }],
            data: nodes,
            links: links,
            lineStyle: {
              color: "#000",
              width: 2,
            },
          },
        ],
      };

      this.chart.setOption(option);
    },
    resizeChart() {
      if (this.chart) {
        this.chart.resize();
      }
    },
  },
};
</script>

<style scoped>
/* 如有需要可进一步调整图表容器的样式 */
</style>
