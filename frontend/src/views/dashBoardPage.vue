<template>
  <TopNavbar />
  <div class="dashboard-page">
    <div class="layout-container">
      <div class="left-side">
        <!-- 左侧内容（TabCard、IcuEventsCard） -->
        <div class="row">
          <TabCard style="width: 300px" />
        </div>
        <div class="row">
          <IcuEventsCard style="width: 300px" :patients="patients" />
        </div>
      </div>

      <!-- 中间较宽区域 -->
      <div class="center-area">
        <HighRiskCard :highRiskPatients="highRiskData" />
        <RulesWeightCard />
        <div class="some-other-content">
          <!-- 你的中间下方内容 -->
        </div>
      </div>

      <!-- 右侧区域，放三个卡片 -->
      <div class="right-side">
        <div class="row">
          <EventFrequencyCard :eventsData="eventsList" />
        </div>
        <div class="row">
          <PredictionAccuracyCard />
        </div>
        <div class="row">
          <RulesListCard />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import TopNavbar from "@/components/TopNavbar.vue";
import TabCard from "@/components/TabCard.vue";
import IcuEventsCard from "@/components/IcuEventsCard.vue";
import HighRiskCard from "@/components/HighRiskCard.vue";
import RulesWeightCard from "@/components/RulesWeightCard.vue";

// 新增导入
import EventFrequencyCard from "@/components/EventFrequencyCard.vue";
import PredictionAccuracyCard from "@/components/PredictionAccuracyCard.vue";
import RulesListCard from "@/components/RulesListCard.vue";

export default {
  name: "dashboardPage",
  components: {
    TopNavbar,
    TabCard,
    IcuEventsCard,
    HighRiskCard,
    RulesWeightCard,
    EventFrequencyCard, // 注册组件
    PredictionAccuracyCard,
    RulesListCard,
  },
  data() {
    return {
      highRiskData: [
        {
          name: "赵六",
          gender: "男",
          basicIllness1: "高血压",
          basicIllness2: "糖尿病",
          basicIllness3: "无",
          predictedTime: "2025-03-15 14:00",
        },
        {
          name: "孙七",
          gender: "女",
          basicIllness1: "心脏病",
          basicIllness2: "无",
          basicIllness3: "哮喘",
          predictedTime: "2025-03-16 09:30",
        },
        {
          name: "周八",
          gender: "男",
          basicIllness1: "高血压",
          basicIllness2: "无",
          basicIllness3: "慢性肾病",
          predictedTime: "2025-03-17 11:45",
        },
      ],
      patients: [
        {
          avatar: "https://picsum.photos/seed/patient1/200/200",
          name: "张伟",
          age: 37,
          events: ["Pneu", "Vanc", "TCO2", "Arte", "AA", "BB"],
        },
        {
          avatar: "https://picsum.photos/seed/patient2/200/200",
          name: "王芳",
          age: 31,
          events: ["Hema", "WBC", "Alka", "CC", "DD"],
        },
        {
          avatar: "https://picsum.photos/seed/patient3/200/200",
          name: "李娜",
          age: 29,
          events: ["Arte", "Ceft", "Hemo", "Mangi", "EE", "FF", "GG"],
        },
        {
          avatar: "https://picsum.photos/seed/patient4/200/200",
          name: "陈强",
          age: 42,
          events: ["XYZ", "ABC", "TTT", "RRR", "UUU", "PPP"],
        },
      ],
      eventsList: [
        { name: "动脉血压收缩压高", count: 412 },
        { name: "动脉血压舒张压低", count: 395 },
        { name: "呼吸频率高", count: 320 },
        { name: "血氧饱和度低", count: 280 },
        { name: "心率高", count: 450 },
        { name: "呼吸频率低", count: 310 },
        { name: "动脉血压平均值低", count: 275 },
        { name: "血红蛋白低", count: 375 },
        { name: "血糖高", count: 290 },
        { name: "凝血酶原时间高", count: 330 },
        { name: "国际标准化比率高", count: 210 },
        { name: "白细胞计数高", count: 265 },
        { name: "动脉氧分压高", count: 300 },
        { name: "血细胞比容低", count: 340 },
        { name: "动脉二氧化碳分压高", count: 360 },
        { name: "动脉二氧化碳分压低", count: 310 },
        { name: "部分凝血活酶时间高", count: 290 },
        { name: "氯离子高", count: 280 },
        { name: "肌酐高", count: 400 },
        { name: "钠高", count: 350 },
        { name: "动脉血压收缩压低", count: 320 },
        { name: "动脉血压舒张压高", count: 300 },
        { name: "动脉血压平均值高", count: 380 },
        { name: "碳酸氢盐低", count: 250 },
        { name: "白细胞计数低", count: 230 },
        { name: "动脉氧分压低", count: 270 },
        { name: "血尿素氮高", count: 360 },
        { name: "碳酸氢盐高", count: 295 },
        { name: "阴离子间隙低", count: 210 },
        { name: "血小板计数低", count: 330 },
        { name: "动脉碱剩余高", count: 310 },
        { name: "氯离子低", count: 290 },
        { name: "华氏体温高", count: 370 },
        { name: "钾低", count: 250 },
        { name: "血小板计数高", count: 340 },
        { name: "心率低", count: 300 },
        { name: "阴离子间隙高", count: 320 },
        { name: "钾高", count: 360 },
        { name: "钠低", count: 280 },
        { name: "肌酐低", count: 310 },
        { name: "血尿素氮低", count: 265 },
        { name: "部分凝血活酶时间低", count: 240 },
        { name: "华氏体温低", count: 230 },
        { name: "凝血酶原时间低", count: 320 },
        { name: "血糖低", count: 290 },
        { name: "血红蛋白高", count: 375 },
        { name: "血细胞比容高", count: 345 },
        { name: "国际标准化比率低", count: 205 },
        { name: "中度到重度", count: 415 },
      ],
    };
  },
};
</script>

<style scoped>
.dashboard-page {
  background-color: #e5eafc;
  min-height: 100vh;
  padding: 16px;
}

.layout-container {
  display: flex;
  gap: 16px;
}

/* 左侧固定宽度 */
.left-side {
  flex: 0 0 300px;
  display: flex;
  flex-direction: column;
}

/* 中间宽度占2份 */
.center-area {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 右侧占1份 */
.right-side {
  flex: 1;
  display: flex;
  flex-direction: column;
}

/* 每行卡片间距 */
.row {
  margin-bottom: 16px;
}
</style>
