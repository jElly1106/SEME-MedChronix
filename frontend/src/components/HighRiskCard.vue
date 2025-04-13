<template>
  <div class="high-risk-card">
    <div class="card-header">高风险病人</div>
    <table class="risk-table">
      <thead>
        <tr>
          <th>姓名</th>
          <th>性别</th>
          <th>基础病1</th>
          <th>基础病2</th>
          <th>基础病3</th>
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
          <td>{{ patient.predictedTime }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  name: 'HighRiskCard',
  props: {
    // 从外部传入的高风险病人数据
    highRiskPatients: {
      type: Array,
      default: () => []
    }
  }
}
</script>

<style scoped>
.high-risk-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 16px;
  width: 800px; /* 根据需要调整宽度 */
  height: 400px; /* 固定高度 */
}

.card-header {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #343C6A;
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
  background-color: #2D5BFF;
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
