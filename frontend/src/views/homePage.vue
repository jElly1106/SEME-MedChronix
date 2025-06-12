<template>
  <TopNavbar />
  <div class="dashboard-page" v-if="this.qualificationStatus === 'approved'">
    <div class="layout-container">
      <div class="left-side">
        <!-- 左侧内容（TabCard、IcuEventsCard） -->
        <!-- <div class="row"> -->
        <TabCard style="width: 300px" />
        <!-- </div>
        <div class="row"> -->
        <IcuEventsCard style="width: 300px" :patients="patients" />
        <!-- </div> -->
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
          <RulesListCard />
        </div>
      </div>
    </div>
  </div>
  <div v-else>
    <UnauthorizedAccess />
  </div>
</template>

<script>
import TopNavbar from "@/components/TopNavbar.vue";
import TabCard from "@/components/TabCard.vue";
import IcuEventsCard from "@/components/IcuEventsCard.vue";
import HighRiskCard from "@/components/HighRiskCard.vue";
import RulesWeightCard from "@/components/RulesWeightCard.vue";
import UnauthorizedAccess from "@/components/UnauthorizedAccess.vue";
// 新增导入
import EventFrequencyCard from "@/components/EventFrequencyCard.vue";
import RulesListCard from "@/components/RulesListCard.vue";

import Axios from "@/utils/axios";

export default {
  name: "homePage",
  components: {
    TopNavbar,
    TabCard,
    IcuEventsCard,
    HighRiskCard,
    RulesWeightCard,
    EventFrequencyCard, // 注册组件
    RulesListCard,
    UnauthorizedAccess,
  },
  data() {
    return {
      qualificationStatus: "approved", //localStorage.getItem("qualificationStatus"), //用户资质验证状态
      highRiskData: [],
      patients: [],
      eventsList: [], 
    };
  },
  mounted() {
    // 组件挂载后获取患者数据
    this.fetchPatients();
    // 添加获取事件列表数据的方法调用
    this.fetchEventsData();
    // 获取高风险患者数据
    this.fetchHighRiskPatients();
  },
  methods: {
    async fetchPatients() {
      try {
        // 获取 token（假设您已经存储在 localStorage 中）
        const token = localStorage.getItem('token');
        
        // 发送请求获取患者数据
        const response = await Axios.get('/patient/details', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        // 更新患者数据
        if (response.data && Array.isArray(response.data)) {
          this.patients = response.data;
        }
      } catch (error) {
        console.error('获取患者数据失败:', error);
        // 如果API请求失败，使用硬编码的测试数据
        this.patients = [
          {
            avatar: "https://picsum.photos/seed/patient1/200/200",
            name: "张伟",
            age: 37,
            events: ["Pneu", "Vanc", "TCO2", "Arte", "AA", "BB"],
          },
          // ... 其他测试数据
        ];
      }
    },
    // 新增方法：获取事件列表数据
    async fetchEventsData() {
      try {
        // 获取 token
        const token = localStorage.getItem('token');
        
        // 发送请求获取事件数据
        const response = await Axios.get('/event/get_num_of_events', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        // 检查响应数据
        if (response.data && Array.isArray(response.data)) {
          // 将后端返回的数据格式转换为组件需要的格式
          this.eventsList = response.data.map(item => ({
            name: item.event_name,
            count: item.count
          }));
          
          console.log('成功获取事件列表数据:', this.eventsList);
        } else {
          console.error('事件数据格式不正确:', response.data);
        }
      } catch (error) {
        console.error('获取事件列表数据失败:', error);
        // 如果API请求失败，可以使用默认的硬编码数据（可选）
        this.eventsList = [
          { name: "动脉血压收缩压高", count: 412 },
          { name: "动脉血压舒张压低", count: 395 },
          // ... 可以保留几个作为备用
        ];
      }
    },
    // 新增方法：获取高风险患者数据
    async fetchHighRiskPatients() {
      try {
        // 获取 token
        const token = localStorage.getItem('token');
        
        // 发送请求获取高风险患者数据
        const response = await Axios.get('/patient/top_predictions', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        // 检查响应数据
        if (response.data && response.data.data && Array.isArray(response.data.data)) {
          // 将后端返回的数据格式转换为组件需要的格式
          this.highRiskData = response.data.data.map(patient => ({
            name: patient.name,
            gender: patient.gender,
            basicIllness1: patient.heart_history || '无',
            basicIllness2: patient.diabete_history || '无',
            basicIllness3: patient.Eh_history || '无',
            predictedTime: patient.prediction_time || '未知'
          }));
          
          console.log('成功获取高风险患者数据:', this.highRiskData);
        } else {
          console.error('高风险患者数据格式不正确:', response.data);
          // 如果数据格式不正确，使用默认数据
          this.setDefaultHighRiskData();
        }
      } catch (error) {
        console.error('获取高风险患者数据失败:', error);
        // 如果API请求失败，使用默认数据
        this.setDefaultHighRiskData();
      }
    },
    
    // 设置默认的高风险患者数据（作为备用）
    setDefaultHighRiskData() {
      this.highRiskData = [
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
      ];
    }
  }
};
</script>

<style scoped>
.dashboard-page {
  background-color: #e5eafc;
  height: 100%;
  padding: 16px;
  padding-bottom: 0px;
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
  /* height: 88vh; */
  gap: 16px;
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
