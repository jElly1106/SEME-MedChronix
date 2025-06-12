<template>
  <LoginTopbar />
  <div class="dashboard-page">
    <!-- 第一行 -->
    <div class="top-row">
      <!-- 左侧：数字卡片 -->
      <div class="left-cards">
        <StatisticCard
          class="fill-card"
          :value1="2579"
          label1="总数据量"
          icon1="fas fa-chart-bar"
          :value2="688"
          label2="当月数据量"
          icon2="fas fa-chart-bar"
        />
        <StatisticCard
          class="fill-card"
          :value1="634"
          label1="总病人数"
          icon1="fas fa-user-injured"
          :value2="22"
          label2="当月新增病人"
          icon2="fas fa-user-injured"
        />
        <StatisticCard
          class="fill-card"
          :value1="106"
          label1="入驻医院数"
          icon1="fas fa-hospital"
          :value2="235"
          label2="入驻医生数"
          icon2="fas fa-user-md"
        />
      </div>

      <!-- 右侧：中国地图 -->
      <div class="map-container">
        <ChinaMap />
      </div>
    </div>

    <!-- 第二行 -->
    <div class="bottom-row">
      <!-- 图表区域：柱线图和饼状图 -->
      <div class="charts-container">
        <div class="left-chart">
          <BarLineChart />
        </div>
        <div class="right-chart">
          <PieChart v-if="pieChartVisible" />
          <div v-else>PieChart Placeholder</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import StatisticCard from "@/components/StatisticCard.vue";
import ChinaMap from "@/components/ChinaMap.vue";
import BarLineChart from "@/components/BarLineChart.vue";
import PieChart from "@/components/PieChart.vue";
import LoginTopbar from "@/components/LoginTopbar.vue";

export default {
  name: "DashBoardPage",
  components: {
    StatisticCard,
    ChinaMap,
    BarLineChart,
    PieChart,
    LoginTopbar,
  },
  data() {
    return {
      pieChartVisible: true, // 控制 PieChart 是否可见
    };
  },
  mounted() {
    // 添加窗口大小变化监听，确保图表正确渲染
    window.addEventListener("resize", this.handleResize);
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.handleResize);
  },
  methods: {
    handleResize() {
      // 触发子组件中的 resize 方法
      this.$nextTick(() => {
        // 这里可以添加额外的逻辑，如果需要的话
      });
    },
  },
};
</script>

<style scoped>
.dashboard-page {
  height: 100vh;
  display: grid;
  grid-template-rows: 1fr 0.7fr; /* 第一行较大，第二行较小 */
  gap: 20px;
  padding: 10px;
  box-sizing: border-box;
  background-color: #e5eafc;
  overflow: hidden; /* 防止内容溢出 */
}

/* 第一行布局 */
.top-row {
  display: grid;
  grid-template-columns: 1fr 2fr; /* 第一列较窄，第二列较宽 */
  gap: 20px;
  min-height: 0; /* 防止内容溢出 */
}

/* 左侧卡片区域 */
.left-cards {
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 0; /* 防止内容溢出 */
}

.fill-card {
  flex: 1;
}

/* 地图放在右侧 */
.map-container {
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  height: 100%; /* 保证地图填充右侧区域 */
}

/* 第二行图表容器 */
.bottom-row {
  display: flex;
  width: 100%; /* 保证占满整个页面宽度 */
  min-height: 0; /* 防止内容溢出 */
}

/* 图表区域：柱线图和饼状图宽度相同 */
.charts-container {
  display: grid;
  grid-template-columns: 1fr 1fr; /* 两个图表宽度相同 */
  gap: 20px;
  width: 100%;
  height: 100%; /* 确保容器有足够的高度 */
}

.left-chart,
.right-chart {
  width: 100%;
  height: 100%;
  min-height: 0; /* 防止内容溢出 */
}

/* 确保图表组件填充其容器 */
.left-chart > *,
.right-chart > * {
  width: 100%;
  height: 100%;
}
</style>
