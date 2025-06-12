<template>
  <div class="high-risk-card">
    <div class="card-header">高危病人</div>
    <table class="risk-table">
      <thead>
        <tr>
          <th>姓名</th>
          <th>性别</th>
          <th>心脏病</th>
          <th>糖尿病</th>
          <th>高血压</th>
          <th>预测时间</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(patient, index) in highRiskPatients" :key="index">
          <td>{{ patient.name }}</td>
          <td>{{ patient.gender }}</td>
          <td>{{ patient.basicIllness1 }}</td>
          <td>{{ patient.basicIllness2 }}</td>
          <td>{{ patient.basicIllness3 }}</td>
          <td>{{ formatDateTime(patient.predictedTime) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  name: "HighRiskCard",
  props: {
    // 从外部传入的高风险病人数据
    highRiskPatients: {
      type: Array,
      default: () => [],
    },
  },
  methods: {
    formatDateTime(dateTimeStr) {
      if (!dateTimeStr) return '未知';
      
      try {
        const date = new Date(dateTimeStr);
        
        // 检查日期是否有效
        if (isNaN(date.getTime())) {
          return dateTimeStr; // 如果无法解析，则返回原始字符串
        }
        
        // 格式化为 YYYY-MM-DD HH:MM 格式
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        
        return `${year}-${month}-${day} ${hours}:${minutes}`;
      } catch (error) {
        console.error('日期格式化错误:', error);
        return dateTimeStr; // 发生错误时返回原始字符串
      }
    }
  }
};
</script>

<style scoped>
.high-risk-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 16px;
  width: 800px; /* 根据需要调整宽度 */
  min-height: 350px; /* 固定高度 */
}

.card-header {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #343c6a;
}

.risk-table {
  width: 100%;
  border-collapse: collapse;
  overflow: hidden;
  border-radius: 8px;
}

.risk-table th,
.risk-table td {
  border: 1px solid #ddd;
  padding: 12px;
  text-align: center;
}

.risk-table th {
  background-color: #2d5bff;
  color: #fff;
  font-weight: 600;
}

.risk-table tbody tr:nth-child(even) {
  background-color: #f9f9f9;
}

.risk-table tbody tr:hover {
  background-color: #f1faff;
}
</style>
