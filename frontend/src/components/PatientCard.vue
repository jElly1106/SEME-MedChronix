<template>
    <div class="patient-card">
      <div class="patient-info">
        <h3>{{ patient.name }} (ID: {{ patient.id }})</h3>
        <p><strong>年龄:</strong> {{ patient.age }}岁</p>
        <p><strong>脑卒中类型:</strong> {{ patient.strokeType }}</p>
      </div>
      <!-- 复选框用于选择病人 -->
      <input type="checkbox" v-model="selected" @change="onSelect" class="checkbox" />
    </div>
  </template>
  
  <script>
  export default {
    props: {
      patient: {
        type: Object,
        required: true,
      },
      onSelect: {
        type: Function,
        required: true, // 向父组件传递选中状态变化的事件
      },
    },
    data() {
      return {
        selected: false, // 控制复选框的选中状态
      };
    },
    watch: {
      // 监听复选框选中状态变化，传递给父组件
      selected(newVal) {
        this.onSelect(this.patient, newVal);
      },
    },
  };
  </script>
  
  <style scoped>
  .patient-card {
    position: relative; /* 使得复选框可以相对于卡片定位 */
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 8px;
    background-color: #fff;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
  }
  
  .patient-info h3 {
    margin: 0;
    font-size: 20px;
    font-weight: bold;
  }
  
  .patient-info p {
    margin: 5px 0;
  }
  
  /* 定位复选框到右上角 */
  .checkbox {
    position: absolute;
    top: 10px;
    right: 10px;
  }
  </style>
  