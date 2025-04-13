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
        <AgeChart v-if="activeTab === 'age'" />
        <!-- 当 activeTab === 'gender' 时，显示性别分布图表 -->
        <GenderChart v-else-if="activeTab === 'gender'" />
      </div>
    </div>
  </template>
  
  <script>
  import AgeChart from '@/components/AgeChart.vue'
  import GenderChart from '@/components/GenderChart.vue'
  
  export default {
    name: 'TabCard',
    components: {
      AgeChart,
      GenderChart
    },
    data() {
      return {
        // 默认展示哪个图表，随意设置，默认 'age' 或 'gender'
        activeTab: 'age'
      }
    }
  }
  </script>
  
  <style scoped>
  .card-container {
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    width: 300px; /* 你想要多宽就多宽 */
    padding: 16px;
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
    background-color: #E5EAFC; /* 选中时背景色 */
    color: #343C6A;            /* 选中时文字颜色 */
  }
  
  /* 内容区域 */
  .tab-content {
    /* 这里放切换后的图表组件 */
  }
  </style>
  