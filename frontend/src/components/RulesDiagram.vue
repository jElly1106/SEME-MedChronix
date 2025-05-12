<template>
  <div class="rules-diagram-container">
    <!-- 无规则数据提示 -->
    <div v-if="noRules" class="no-rules-message">
      <i class="fa fa-info-circle" style="color: #2d5bff"></i>
      <span>暂无与该病人有关的规则</span>
    </div>
    <div ref="chart" class="patient-rules"></div>
  </div>
</template>

<script>
import * as echarts from "echarts";
import Axios from "axios";

export default {
  props: {
    selectedPatientId: {
      type: [Number, String],
      default: null,
    },
  },
  data() {
    return {
      chart: null,
      nodes: [],
      links: [],
      noRules: false,
    };
  },
  watch: {
    // 监听 selectedPatientId 变化，当病人ID变化时重新获取规则
    selectedPatientId: {
      immediate: true, // 添加这一行，确保组件创建时就执行一次
      handler(newVal) {
        console.log("RulesDiagram 接收到新的病人ID:", newVal);
        if (newVal) {
          this.fetchPatientRules(newVal);
        } else {
          // 如果没有选中病人，可以清空图表或显示默认内容
          this.nodes = [];
          this.links = [];
          this.noRules = false;
          this.updateChart();
        }
      },
    },
  },
  mounted() {
    // 在组件挂载时初始化图表
    if (this.selectedPatientId) {
      this.initChart();
    }
  },
  beforeUnmount() {
    // 在组件卸载前销毁图表
    if (this.chart) {
      this.chart.dispose();
      this.chart = null;
    }
  },
  methods: {
    initChart() {
      this.chart = echarts.init(this.$refs.chart);

      // 初始化空图表
      const option = {
        graphic: [
          {
            type: "text",
            left: 10,
            top: 10,
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
            roam: true,
            force: {
              repulsion: 300,
              edgeLength: [100, 200],
            },
            label: {
              show: true,
              position: "inside",
              fontSize: 14,
            },
            categories: [{ name: "目标事件" }, { name: "规则" }],
            data: this.nodes,
            links: this.links,
            lineStyle: {
              color: "#000",
              width: 2,
            },
          },
        ],
      };

      this.chart.setOption(option);
    },
    // 更新图表数据
    updateChart() {
      if (!this.chart) return;

      const option = {
        series: [
          {
            data: this.nodes,
            links: this.links,
          },
        ],
      };

      this.chart.setOption(option);
    },
    resizeChart() {
      if (this.chart) {
        // 添加延迟以确保容器尺寸已更新
        setTimeout(() => {
          this.chart.resize();
        }, 100);
      }
    },
    async fetchPatientRules(patientId) {
      try {
        console.log("获取病人规则，病人ID:", patientId);

        // 获取 token
        const token = localStorage.getItem("token");

        // 调用后端接口获取病人相关的规则 127.0.0.1:5000
        const response = await Axios.get(
          `http://47.97.48.128/api/rule/get_rules_by_patient`,
          {
            params: { patient_id: patientId },
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        console.log("获取病人规则成功:", response.data);

        // 检查是否有规则数据
        if (!Array.isArray(response.data) || response.data.length === 0) {
          // 没有规则数据，显示提示信息
          this.noRules = true;
          this.nodes = [];
          this.links = [];
          this.updateChart();
          return;
        }

        // 有规则数据，隐藏提示信息
        this.noRules = false;

        // 将后端返回的规则数据转换为图表所需的节点格式
        this.nodes = [
          {
            id: 0,
            name: "目标事件",
            symbolSize: 70,
            draggable: true,
            category: 0,
            description: "这是目标事件的信息",
          },
        ];

        // 将每个规则添加为节点
        if (Array.isArray(response.data)) {
          response.data.forEach((rule, index) => {
            this.nodes.push({
              id: index + 1,
              name: `规则${index + 1}`,
              symbolSize: 50,
              draggable: true,
              category: 1,
              description: rule.rule_content || "规则详情",
              time: new Date().toISOString().slice(0, 16).replace("T", " "),
            });
          });
        }

        // 生成连接线数据
        this.links = [];
        for (let i = 1; i < this.nodes.length; i++) {
          this.links.push({
            source: i,
            target: 0,
            lineStyle: {
              color: "rgba(0, 0, 0, 0.6)",
              width: 2,
              type: "dashed",
              curveness: 0.2,
              shadowColor: "rgba(0, 0, 0, 0.3)",
              shadowBlur: 4,
              shadowOffsetX: 2,
              shadowOffsetY: 2,
            },
          });
        }

        // 更新图表
        this.updateChart();
      } catch (error) {
        console.error("获取病人规则失败:", error);
        // 显示错误提示
        this.$message &&
          this.$message.error(
            `获取病人规则失败: ${error.response?.data?.error || error.message}`
          );
        // 显示无规则提示
        this.noRules = true;
        this.nodes = [];
        this.links = [];
        this.updateChart();
      }
    },
  },
};
</script>

<style scoped>
.rules-diagram-container {
  position: relative;
  width: 100%;
  height: 500px;
}

.patient-rules {
  width: 550px;
  /* height: 100%; */
  height: 500px; /* 添加最小高度 */
}

.no-rules-message {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: #f5f5f5;
  padding: 15px 25px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  z-index: 10;
  font-size: 16px;
  color: #666;
}

.no-rules-message i {
  font-size: 20px;
  margin-right: 10px;
  color: #1890ff;
}
</style>
