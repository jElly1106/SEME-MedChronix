<template>
  <div class="card-container">
    <!-- Tab Header -->
    <div class="tab-header">
      <div
        :class="['tab-item', { active: activeTab === 'age' }]"
        @click="activeTab = 'age'"
      >
        年龄分布
      </div>
      <div
        :class="['tab-item', { active: activeTab === 'gender' }]"
        @click="activeTab = 'gender'"
      >
        性别分布
      </div>
    </div>

    <!-- Tab Content -->
    <div class="tab-content">
      <!-- 当 activeTab === 'age' 时，显示年龄分布图表 -->
      <AgeChart v-if="activeTab === 'age'" :data="ageData" />
      <!-- 当 activeTab === 'gender' 时，显示性别分布图表 -->
      <GenderChart v-else :data="genderData" />
    </div>
  </div>
</template>

<script>
import AgeChart from "@/components/AgeChart.vue";
import GenderChart from "@/components/GenderChart.vue";
import Axios from '@/utils/axios';


export default {
  name: "TabCard",
  components: {
    AgeChart,
    GenderChart,
  },
  data() {
    return {
      activeTab: "age",
      ageData: [],     // 例如：[{ ageRange: '0-20', count: 10 }, ... ]
      genderData: []   // 例如：[{ name: '男', value: 60 }, { name: '女', value: 40 }]
    };
  },
  mounted() {
    this.fetchAgeStats();
    this.fetchGenderStats();
  },
  methods: {
    async fetchAgeStats() {
      try {
        const response = await Axios.get('/patient/age_stats', {
          headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('token')
          }
        });
        // 假设返回的数据形如：{ "0-20": 10, "21-40": 30, "41-60": 50, "60+": 20 }
        const data = response.data;
        this.ageData = Object.keys(data).map(key => ({
          ageRange: key,
          count: data[key]
        }));
      } catch (error) {
        console.error('获取年龄数据失败：', error);
      }
    },
    async fetchGenderStats() {
      try {
        const response = await Axios.get('/patient/gender_stats', {
          headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('token')
          }
        });
        // 假设返回的数据形如：{ "男": 60, "女": 40 }
        const data = response.data;
        this.genderData = Object.keys(data).map(key => ({
          name: key,
          value: data[key]
        }));
      } catch (error) {
        console.error('获取性别数据失败：', error);
      }
    }
  }
};
</script>

<style scoped>
.card-container {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  width: 300px;
  padding: 16px;
  min-height: 300px;
}

/* 顶部选项卡区域 */
.tab-header {
  display: flex;
  justify-content: center; /* 让选项卡居中 */
  border-bottom: 1px solid #ddd;
  margin-bottom: 16px;
}

/* 每个选项卡按钮 */
.tab-item {
  padding: 8px 16px;
  cursor: pointer;
  color: #666;
  transition: background-color 0.2s;
}

.tab-item:hover {
  background-color: #f5f5f5;
}

/* 选中状态 */
.tab-item.active {
  background-color: #e5eafc; /* 选中时背景色 */
  color: #343c6a; /* 选中时文字颜色 */
}

/* 内容区域样式 */
.tab-content {
  padding: 10px;
}
</style>
