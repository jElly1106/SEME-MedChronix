<template>
  <div class="patient-data-table-container">
    <div class="table-header">
      <h3>患者数据表格</h3>
      <div class="table-actions">
        <button class="refresh-btn" @click="fetchPatientData">
          <i class="fa fa-refresh"></i> 刷新数据
        </button>
      </div>
    </div>

    <div class="table-content">
      <table v-if="patientData.length > 0" class="data-table">
        <thead>
          <tr>
            <th v-for="(column, index) in tableColumns" :key="index">
              {{ column.label }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, rowIndex) in patientData" :key="rowIndex">
            <td v-for="(column, colIndex) in tableColumns" :key="colIndex">
              {{ row[column.key] || "-" }}
            </td>
          </tr>
        </tbody>
      </table>

      <div v-else class="no-data-placeholder">
        <div class="placeholder-icon">
          <i class="fa fa-table"></i>
        </div>
        <p v-if="loading">正在加载数据...</p>
        <p v-else>暂无患者数据</p>
        <button v-if="!loading" class="load-btn" @click="fetchPatientData">
          加载数据
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import Axios from "@/utils/axios";

export default {
  name: "PatientDataTable",
  props: {
    patientId: {
      type: [Number, String],
      required: true,
    },
  },
  data() {
    return {
      patientData: [],
      loading: false,
      error: null,
      tableColumns: [
        { key: "recordTime", label: "记录时间" },
        { key: "eventName", label: "事件名" },
        { key: "value", label: "指标值" },
        { key: "normalRange", label: "正常范围值" },
      ],
    };
  },
  watch: {
    // 监听patientId的变化，当病人ID变化时重新获取数据
    patientId: {
      immediate: false,
      async handler(newPatientId, oldPatientId) {
        console.log("病人ID变化:", oldPatientId, "->", newPatientId);
        if (newPatientId && newPatientId !== oldPatientId) {
          await this.fetchPatientData();
        }
      },
    },
  },
  async created() {
    console.log(
      "PatientDataTable组件初始化，接收到的patientId:",
      this.patientId
    );
    // 初始化时获取数据
    await this.fetchPatientData();
  },
  methods: {
    async fetchPatientData() {
      if (!this.patientId) {
        console.error("未找到病人ID，无法获取数据");
        return;
      }

      this.loading = true;
      this.error = null;

      try {
        console.log(`尝试获取病人ID为 ${this.patientId} 的数据表格信息`);

        // 获取token
        const token = localStorage.getItem("token");
        if (!token) {
          console.error("未找到token");
          this.error = "未授权，请重新登录";
          this.patientData = this.getDefaultData();
          return;
        }

        // 调用后端接口获取患者数据
        const response = await Axios.get(
          `/patient/data_table/${this.patientId}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        console.log("API返回的原始数据:", response.data);

        // 检查响应状态
        if (response.data && response.data.code === 200) {
          // 格式化数据
          this.patientData = this.formatTableData(response.data.data);
          // 如果是高度昏迷事件，其值为：目标事件
          if (response.data.data && response.data.data.length > 0) {
            this.patientData = this.patientData.map((item) => {
              if (item.eventName === "高度昏迷") {
                return {
                  ...item,
                  value: "目标事件",
                };
              }
              return item;
            });
          }
        } else {
          console.warn("后端返回的数据格式不正确或为空");
          this.patientData = this.getDefaultData();
        }
      } catch (error) {
        console.error("获取患者数据表格失败:", error);
        this.error = `获取数据失败: ${error.message}`;
        this.patientData = this.getDefaultData();
      } finally {
        this.loading = false;
      }
    },

    formatTableData(data) {
      // 如果数据为空，返回空数组
      if (!data || data.length === 0) {
        return [];
      }

      // 格式化数据为表格所需格式
      return data.map((item) => ({
        recordTime: item.record_time || "-",
        eventName: item.event_name || "-",
        value:
          item.value !== null && item.value !== undefined ? item.value : "-",
        normalRange: item.normal_range || "-",
      }));
    },

    formatDate(dateString) {
      if (!dateString) return "-";

      try {
        // 处理多种可能的日期格式
        if (dateString.includes("T")) {
          // ISO格式: 2025-04-06T00:00:00.000000
          return dateString.split("T")[0];
        } else if (dateString.includes(" ")) {
          // 数据库格式: 2025-04-06 00:00:00.000000
          return dateString.split(" ")[0];
        }
        return dateString;
      } catch (error) {
        console.error("日期格式化错误:", error);
        return dateString;
      }
    },

    getDefaultData() {
      // 返回默认数据，用于API调用失败时显示
      return []; // 修改为空数组，不再显示默认数据
    },
  },
};
</script>

<style scoped>
.patient-data-table-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e9ecef;
}

.table-header h3 {
  margin: 0;
  color: #2d5bff;
  font-size: 18px;
  font-weight: 600;
}

.table-actions {
  display: flex;
  gap: 10px;
}

.refresh-btn {
  background-color: #2d5bff;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 6px 12px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  gap: 5px;
}

.refresh-btn:hover {
  background-color: #1a46e0;
}

.table-content {
  flex: 1;
  padding: 16px;
  overflow: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.data-table th,
.data-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
}

.data-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #495057;
}

.data-table tr:hover {
  background-color: #f1f3f9;
}

.no-data-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: #6c757d;
}

.placeholder-icon {
  font-size: 48px;
  margin-bottom: 16px;
  color: #adb5bd;
}

.load-btn {
  margin-top: 16px;
  background-color: #2d5bff;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.load-btn:hover {
  background-color: #1a46e0;
}
</style>
