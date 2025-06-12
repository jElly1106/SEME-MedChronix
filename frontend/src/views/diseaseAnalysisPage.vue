<template>
  <div class="analysis-page">
    <TopNavbar />
    <div class="analysis-page-container">
      <div class="left-column">
        <!-- 美化后的选择病人按钮 -->
        <button class="select-patient-btn" @click="showModal = true">
          <i class="fas fa-user-plus"></i>
          <span>选择病人</span>
        </button>

        <!-- 弹窗（Modal） -->
        <div v-if="showModal" class="modal">
          <div class="modal-content">
            <!-- 弹窗头部 -->
            <div class="modal-header">
              <h2>筛选病人</h2>
              <span @click="closeModal" class="close">&times;</span>
            </div>

            <!-- 弹窗主体：筛选条件 -->
            <div class="modal-body">
              <!-- 筛选条件 -->
              <div class="filters">
                <label for="strokeType">脑卒中类型：</label>
                <select v-model="selectedStrokeType" id="strokeType">
                  <option value="">-- 全部 --</option>
                  <option
                    v-for="option in strokeTypeOptions"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </option>
                </select>
              </div>

              <div class="filters">
                <label for="icuEntryTimeStart">进入 ICU 时间：</label>
                <div class="time-range">
                  <input
                    type="datetime-local"
                    v-model="icuEntryTimeStart"
                    placeholder="开始时间"
                  />
                  <span>至</span>
                  <input
                    type="datetime-local"
                    v-model="icuEntryTimeEnd"
                    placeholder="结束时间"
                  />
                </div>
              </div>

              <div class="filters">
                <label for="icuExitTimeStart">离开 ICU 时间：</label>
                <div class="time-range">
                  <input
                    type="datetime-local"
                    v-model="icuExitTimeStart"
                    placeholder="开始时间"
                  />
                  <span>至</span>
                  <input
                    type="datetime-local"
                    v-model="icuExitTimeEnd"
                    placeholder="结束时间"
                  />
                </div>
              </div>

              <!-- 病人列表 -->
              <table class="patient-list">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>姓名</th>
                    <th>性别</th>
                    <th>脑卒中类型</th>
                    <th>进入 ICU 时间</th>
                    <th>离开 ICU 时间</th>
                    <th>选择</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="patient in filteredPatients" :key="patient.id">
                    <td>{{ patient.id }}</td>
                    <td>{{ patient.name }}</td>
                    <td>{{ patient.gender }}</td>
                    <td>{{ getStrokeTypeLabel(patient.strokeType) }}</td>
                    <td>{{ patient.icuEntryTime }}</td>
                    <td>{{ patient.icuExitTime }}</td>
                    <td>
                      <input type="checkbox" v-model="patient.isSelected" />
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <!-- 弹窗底部按钮 -->
            <div class="modal-footer">
              <button @click="confirmPatientSelection">确认</button>
            </div>
          </div>
        </div>

        <!-- 左侧两个卡片：一个雷达图，一个词频图 -->
        <div class="card">
          <div class="card-content">
            <RadarChart v-if="isDataReady"
            :selected="radarChartData" />
          </div>
        </div>

        <div class="card">
          <div class="card-content">
            <WordFrequencyChart v-if="isDataReady"
            :wordFrequencyData="wordFrequencyData" />
          </div>
        </div>
      </div>

      <div class="right-column">
        
        <!-- 上半部分 - 图表区域 -->
        <div class="chart-container">
          <ChartComponent
          v-if="isDataReady"
          :patientEventData="patientChartData"
            :clusterData="patientClusterData"
          />
        </div>
        <!-- 下半部分 - 模型解释与 AI 咨询 -->
        <div class="bottom-section">
          <div class="left-half">
            <div class="model-explanation">
              <h3>图表解释</h3>
<<<<<<< HEAD
              <div v-if="chartExplanation" v-html="parseMarkdown(chartExplanation)"></div>
=======
              <!-- <div
                v-if="chartExplanation"
                v-html="parseMarkdown(chartExplanation)"
              ></div>
>>>>>>> parent of 4eedc2b (feat-2026/06/06)
              <div v-else-if="isAnalyzing" class="loading-text">
                <div class="loading-spinner"></div>
                <p>正在分析图表数据，请稍候...</p>
              </div>
              <div v-else>
                <button class="analyze-btn" @click="analyzeChart">
                  <i class="fas fa-chart-line"></i> 点击生成AI分析结果
                </button>
              </div> -->
            </div>
          </div>
          <div class="right-half">
            <ChatBox />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/* eslint-disable */
import TopNavbar from "@/components/TopNavbar.vue";
import { marked } from "marked";
import ChartComponent from "@/components/ChartComponent.vue";
import RadarChart from "@/components/RadarChart.vue";
import WordFrequencyChart from "@/components/WordFrequencyChart.vue";
import ChatBox from "@/components/ChatBox.vue";

import Axios from "@/utils/axios";

export default {
  components: {
    ChartComponent,
    TopNavbar,
    RadarChart,
    WordFrequencyChart,
    ChatBox,
  },
  data() {
    return {
      activePatientIndex: 0,
      showModal: false,
      selectedStrokeType: "",
      icuEntryTimeStart: "",
      icuEntryTimeEnd: "",
      icuExitTimeStart: "",
      icuExitTimeEnd: "",
      selectedPatients: [],
      patients: [],
      radarChartData: [],
      wordFrequencyData: [],
      patientChartData: [],
      patientClusterData: [],
      strokeTypeOptions: [
        { label: "缺血性脑卒中", value: "0" },
        { label: "出血性脑卒中", value: "1" },
        { label: "短暂性脑缺血发作", value: "2" },
        { label: "其他类型", value: "3" },
      ],
      userInput: "",
      selectedFile: null,
      uploadedImage: null, // 存储上传的图片 URL
      chatMessages: [],
      choose_type: [],
      popupVisible: false, // 控制选择病人弹窗显示
      type_collapsed: false,
      isDataReady: false,
      isAnalyzing: false, // 添加分析状态标志
      chartExplanation: null, // 添加图表解释内容
      // 新增部分：患者相关数据及筛选条件
      // 模拟的患者数据，包含 id、姓名、性别、脑卒中类型以及是否选中
    };
  },
  watch: {
    // 监听所有筛选条件的变化
    selectedStrokeType() {
      this.fetchFilteredPatients();
    },
    icuEntryTimeStart() {
      this.fetchFilteredPatients();
    },
    icuEntryTimeEnd() {
      this.fetchFilteredPatients();
    },
    icuExitTimeStart() {
      this.fetchFilteredPatients();
    },
    icuExitTimeEnd() {
      this.fetchFilteredPatients();
    },
  },
  mounted() {
    this.fetchAllPatients();
    //this.resetFilters();
  },
  computed: {
    // 根据 selectedStrokeType 筛选患者，若未选择则返回全部患者
    filteredPatients() {
      let filtered = this.patients;
      if (this.selectedStrokeType) {
        filtered = filtered.filter(
          (patient) => patient.strokeType === this.selectedStrokeType
        );
      }
      return filtered;
    },
  },
  methods: {
    fetchChartDataAsync() {
      if (this.selectedPatients.length === 0) return Promise.resolve();

      // 获取所有选中病人的ID列表
      const patientIds = this.selectedPatients.map((patient) => patient.id);
      console.log("4_9 patientIds", patientIds);
      // 将ID列表作为查询参数传递
      Axios.get(
        `/predict/get_cluster_result?patient_id=${patientIds.join(",")}`
      )
        .then((response) => {
          if (response.data.success) {
            console.log("获取图表数据成功:", response.data);
            this.patientChartData = response.data.patientEventData;
            this.patientClusterData = response.data.clusterData;
          } else {
            console.error("获取图表数据失败:", response.data.message);
          }
        })
        .catch((error) => {
          console.error("获取图表数据请求失败:", error);
        });
    },
    fetchWordFrequencyDataAsync() {
      if (this.selectedPatients.length === 0) return Promise.resolve();

      // 提取所有选中病人的ID
      const patientIds = this.selectedPatients.map((patient) => patient.id);

      // 向后端发送请求获取事件频率数据
      Axios.post("/event/get_events_by_patientsIDList", {
        patient_ids: patientIds,
      })
        .then((response) => {
          console.log("获取词频数据成功:", response.data);

          // 转换数据格式为词云图所需格式
          this.wordFrequencyData = response.data.map((item) => ({
            name: item.event_name,
            count: item.count,
          }));
        })
        .catch((error) => {
          console.error("获取词频数据失败:", error);
          // 如果API请求失败，使用空数组
          this.wordFrequencyData = [];
        });
    },
    fetchRadarChartDataAsync() {
      if (this.selectedPatients.length === 0) return Promise.resolve();

      // 提取所有选中病人的ID
      const patientIds = this.selectedPatients.map((patient) => patient.id);
      console.log("4_8 patientIds", patientIds);
      // 定义需要获取的事件ID
      const eventIds = [1, 2, 3, 4, 5, 6];

      // 向后端发送请求获取最新事件数据
      Axios.post("/patient/get_latest_patient_events", {
        patient_ids: patientIds,
        event_ids: eventIds,
      })
        .then((response) => {
          console.log("获取雷达图数据成功:", response.data);

          // 转换数据格式为雷达图所需格式
          this.radarChartData = this.selectedPatients.map((patient) => {
            const patientData = response.data[patient.id] || {};
            console.log("病人数据", patientData);
            return {
              name: patient.name,
              data: [
                patientData.data[0] || 100,
                patientData.data[1] || 100,
                patientData.data[2] || 100,
                patientData.data[3] || 100,
                patientData.data[4] || 100,
                patientData.data[5] || 100,
              ],
            };
          });
        })
        .catch((error) => {
          console.error("获取雷达图数据失败:", error);
          // 如果API请求失败，使用模拟数据
          //this.initMockRadarChartData();
        });
    },
    closeModal() {
      this.showModal = false;
      // 重置所有筛选条件
      this.selectedStrokeType = "";
      this.icuEntryTimeStart = "";
      this.icuEntryTimeEnd = "";
      this.icuExitTimeStart = "";
      this.icuExitTimeEnd = "";
      // 重新获取所有患者数据
      //this.fetchAllPatients();
    },
    fetchFilteredPatients() {
      // 构建请求参数
      const params = {
        status: this.selectedStrokeType ? [this.selectedStrokeType] : [],
        in_icu_start: this.icuEntryTimeStart
          ? this.icuEntryTimeStart + ":00"
          : null,
        in_icu_end: this.icuEntryTimeEnd ? this.icuEntryTimeEnd + ":00" : null,
        out_icu_start: this.icuExitTimeStart
          ? this.icuExitTimeStart + ":00"
          : null,
        out_icu_end: this.icuExitTimeEnd ? this.icuExitTimeEnd + ":00" : null,
      };

      // 检查是否有筛选条件
      const hasFilters = Object.values(params).some(
        (val) => val !== null && val.length !== 0
      );

      if (hasFilters) {
        Axios.post("/patient/filter", params)
          .then((response) => {
            this.patients = response.data.map((patient) => ({
              id: patient.id,
              name: patient.name,
              gender: patient.gender,
              strokeType: patient.status,
              icuEntryTime: patient.in_icu,
              icuExitTime: patient.out_icu,
              isSelected: false,
            }));
          })
          .catch((error) => {
            console.error("筛选病人失败:", error);
          });
      } else {
        // 如果没有筛选条件，获取所有病人
        this.fetchAllPatients();
      }
    },
    analyzeChart() {
      if (this.patientChartData.length === 0) {
        this.$message.error("请先选择病人并加载图表数据");
        return;
      }
      
      this.isAnalyzing = true; // 设置加载状态为true
      
      // 准备图表数据
      const chartData = {
        patientEventData: this.patientChartData,
        clusterData: this.patientClusterData
      };
      
      // 构建问题文本，包含图表数据的JSON字符串
      const questionText = `这是一张病人病程聚类图以及画该图时使用的数据，每一个节点代表一个病人发生的异常事件，不同颜色的线代表不同的病人，如果线合为一簇则代表从该时刻开始病人属于一个类型，请从专业医生的角度分析为什么这几条事件序列可以聚类成这样的聚类结果包括病人之间的相似性和差异性，提供相关依据，不要太多\n\n图表数据：${JSON.stringify(chartData, null, 2)}`;
      
      // 等待图表完全渲染
      this.$nextTick(() => {
        // 使用html2canvas捕获图表
        import('html2canvas').then(html2canvas => {
          const chartElement = document.querySelector('.chart-container');
          
          if (!chartElement) {
            this.isAnalyzing = false;
            this.$message.error("无法找到图表元素");
            return;
          }
          
          html2canvas.default(chartElement, {
            useCORS: true,
            allowTaint: true,
            scale: 2,
            logging: false
          }).then(canvas => {
            // 将canvas转为blob
            canvas.toBlob(blob => {
              if (!blob) {
                this.isAnalyzing = false;
                this.$message.error("无法生成图表图片");
                return;
              }
              
              console.log("图片生成成功，大小:", blob.size, "字节");
              
              // 创建FormData对象
              const formData = new FormData();
              formData.append('image', blob, 'chart.png');
              formData.append('question', questionText);
              
              // 发送请求到多模态接口
              Axios.post('/llm/multimodal', formData, {
                headers: {
                  'Content-Type': 'multipart/form-data'
                },
                timeout: 120000 // 增加超时时间到2分钟
              })
                .then(response => {
                  console.log("图表解释响应:", response.data);
                  if (response.data && response.data.result) {
                    this.chartExplanation = response.data.result;
                  } else {
                    this.chartExplanation = "服务器返回了空结果，请稍后再试。";
                  }
                  this.isAnalyzing = false; // 请求完成，设置加载状态为false
                })
                .catch(error => {
                  console.error("获取图表解释失败:", error);
                  
                  let errorMessage = "未知错误";
                  if (error.response) {
                    errorMessage = `服务器错误 (${error.response.status}): ${error.response.data.message || error.response.data.error || "请检查服务器日志"}`;
                    console.error("服务器响应:", error.response.data);
                  } else if (error.request) {
                    errorMessage = "服务器未响应，请检查后端服务是否正常运行";
                  } else {
                    errorMessage = `请求错误: ${error.message}`;
                  }
                  
                  this.chartExplanation = `分析图表时发生错误: ${errorMessage}`;
                  this.isAnalyzing = false; // 请求失败，设置加载状态为false
                });
            }, 'image/png', 0.9); // 使用0.9的质量，减小图片大小
          }).catch(error => {
            console.error("生成图表截图失败:", error);
            this.isAnalyzing = false;
            this.chartExplanation = "无法生成图表截图，请稍后再试。";
          });
        }).catch(error => {
          console.error("加载html2canvas失败:", error);
          this.isAnalyzing = false;
          this.chartExplanation = "加载截图工具失败，请刷新页面后再试。";
        });
      });
    },

    // 修改重置筛选器的方法
    resetFilters() {
      this.selectedStrokeType = "";
      this.icuEntryTimeStart = "";
      this.icuEntryTimeEnd = "";
      this.icuExitTimeStart = "";
      this.icuExitTimeEnd = "";
      // 重置后重新获取所有患者
      this.fetchAllPatients();
    },
    async fetchAllPatients() {
      console.log("开始请求获取病人数据:", new Date().toLocaleTimeString());

      try {
        const t0 = performance.now();
        const response = await Axios.get("/patient/all");
        const t1 = performance.now();
        console.log("实际耗时：", t1 - t0);
        //const response = await Axios.get("/patient/all");

        console.log("获取病人数据成功:", response.data);
        console.log("请求完成时间:", new Date().toLocaleTimeString());

        // 暂存数据（避免直接赋给响应式）
        const rawPatients = response.data.map((patient) => ({
          id: patient.id,
          name: patient.name,
          gender: patient.gender,
          strokeType: patient.status,
          icuEntryTime: patient.in_icu,
          icuExitTime: patient.out_icu,
          isSelected: false,
        }));
        console.log("挂载完成时间:", new Date().toLocaleTimeString());
        // 延迟少许时间再挂载组件
        setTimeout(() => {
        console.time("赋值 + 图表加载");
        this.patients = rawPatients;
        this.selectedPatients = rawPatients.slice(0, 1);
        this.patients.forEach((p, idx) => {
          if (idx < 1) p.isSelected = true;
        });
        
        // 延迟加载图表
        //this.fetchRadarChartDataAsync();
        //setTimeout(() => {
        //  this.fetchChartDataAsync();
        //}, 0);
        //setTimeout(() => {
        //  this.fetchWordFrequencyDataAsync();
        //}, 0);
        Promise.all([
          this.fetchRadarChartDataAsync(),
          this.fetchWordFrequencyDataAsync(),
          this.fetchChartDataAsync()
        ]);
        this.isDataReady = true;

        console.timeEnd("赋值 + 图表加载");
      }, 0);

      } catch (error) {
        console.error("获取病人数据失败:", error);
      }
    },
    getStrokeTypeLabel(typeValue) {
      const option = this.strokeTypeOptions.find(
        (opt) => opt.value === typeValue
      );
      return option ? option.label : "未知";
    },
    confirmPatientSelection() {
      // 获取所有选中的病人
      const selectedPatients = this.patients.filter((p) => p.isSelected);
      
      // 检查选中的病人数量是否超过6个
      if (selectedPatients.length > 6) {
        // 使用自定义弹窗或Element UI的消息提示
        this.$message.warning("最多只能选择6个病人进行对比分析");
        return;
      }
      
      this.selectedPatients = selectedPatients; // 更新选中的病人列表
      console.log("已选择的病人:", this.selectedPatients);
      this.showModal = false; // 关闭弹窗
      Promise.all([
        this.fetchRadarChartDataAsync(),
        this.fetchWordFrequencyDataAsync(),
        this.fetchChartDataAsync()
      ]);
    },
    applyFilters() {
      this.popupVisible = false;
    },
    // 重置筛选器的逻辑
    resetFilters() {
      this.choose_type = [];
      this.icuEntryDate = null;
      this.icuExitDate = null;
      this.selectedStrokeType = "";
    },
    // 应用筛选器的逻辑（可根据需要扩展 ICU 时间筛选）
    applyFilters() {
      this.popupVisible = false;
    },
    // 删除操作
    confirmDelete(patient) {
      this.currentPatient = patient;
      this.showDeleteModal = true;
    },
    deletePatient() {
      this.patients = this.patients.filter(
        (p) => p.id !== this.currentPatient.id
      );
      this.closeDeleteModal();
      // 更新 filteredPatients，如有过滤逻辑可在此处理
    },
    closeDeleteModal() {
      this.showDeleteModal = false;
      this.currentPatient = null;
    },
    // 编辑操作
    openEditModal(patient) {
      this.currentPatient = patient;
      // 深拷贝病人数据，防止直接修改原数据
      this.editPatient = JSON.parse(JSON.stringify(patient));
      this.showEditModal = true;
    },
    submitEdit() {
      // eslint-disable-next-line
      const index = this.patients.findIndex(
        (p) => p.id === this.editPatient.id
      );
      // eslint-disable-next-line
      if (index !== -1) {
        // 更新数据（建议在实际项目中调用 API 保存数据）
        // eslint-disable-next-line
        this.$set(this.patients, index, this.editPatient);
      }
      this.closeEditModal();
    },
    closeEditModal() {
      this.showEditModal = false;
      this.currentPatient = null;
      this.editPatient = {};
    },
    toggleCollapse() {
      this.type_collapsed = !this.type_collapsed;
    },
    closePopup() {
      this.popupVisible = false;
    },
    togglePopup() {
      this.popupVisible = true;
    },
    parseMarkdown(text) {
      return marked(text || "");
    },
    handleSelect(patient, isSelected) {
      if (isSelected) {
        this.selectedPatients.push(patient);
      } else {
        this.selectedPatients = this.selectedPatients.filter(
          (p) => p.id !== patient.id
        );
      }
    },
    parseMarkdown(text) {
      return marked(text || "");
    },
  },
};
</script>

<style scoped>
.analysis-page {
  background-color: #e5eafc;
  width: 100%;
  height: 100vh;
}
.analysis-page-container {
  display: flex;
  justify-content: space-between;
  height: 90vh;
}

.left-column {
  width: 25%;
  padding: 10px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between; /* 保证两张卡片之间有间隔 */
}

.left-column h3 {
  margin-bottom: 15px;
  font-size: 20px;
  font-weight: 600;
}

.right-column h3 {
  margin-bottom: 15px;
  font-size: 20px;
  font-weight: 600;
  color: #2d5bff;
}

.type h3 {
  margin: -20px auto 20px 0;
  text-align: center;
  color: #0e0f0f;
  border-bottom: 2px solid #585555;
  padding-bottom: 10px;
}
.type_header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 30px; /* 增大内边距，使间距变大 */
  color: rgb(5, 5, 5); /* 设置文字颜色 */
  cursor: pointer; /* 设置光标为手形 */
  border-radius: 4px; /* 边角圆滑 */
  font-size: 18px; /* 增大字体大小 */
  font-weight: bold; /* 设置文字加粗 */
}

.popup-buttons {
  display: flex;
  justify-content: space-between; /* 两个按钮之间的间距 */
  margin-top: 20px;
}

.right-column {
  width: 75%;
  padding: 10px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.chart-container {
  height: 50vh;
  border-radius: 15px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #fff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); /* 细腻阴影 */
}

.bottom-section {
  display: flex;
  padding: 20px;
  border-radius: 15px; /* 圆角边框 */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); /* 细腻阴影 */
  background-color: #fff;
  height: 50vh;
  margin-top: 10px;
}

/* 左侧区域设置为1份 */
.left-half {
  flex: 1;
  padding: 10px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  height: 95%;
}

.right-half {
  flex: 1;
  padding: 10px;
  border-left: 1px solid #ddd; /* 竖线分隔 */
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  height: 95%;
}

.model-explanation {
  background-color: #c6d2fd;
  padding-left: 10px;
  border-radius: 8px;
  height: 100%;
  max-height:360px;
  overflow: auto;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.chat-container {
  background-color: #f7f7f7;
  border-radius: 8px;
  padding-left: 10px;
  padding-bottom: 15px; /* 增加底部内边距，为输入框留出空间 */
  display: flex;
  flex-direction: column;
  height: 100%;
  flex: 1;
  overflow: auto;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  position: relative; /* 为内部绝对定位元素提供参照 */
}

/* 定义配色变量 */
:root {
  --color-primary: #2d5bff;
  --color-secondary: #93aafd;
  --color-tertiary: #c6d2fd;
  --color-light: #e5eafc;
}

/* 弹窗遮罩层 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
}

/* 弹窗内容 */
.modal-content {
  background-color: #fff;
  border: 2px solid var(--color-light);
  border-radius: 12px;
  padding: 24px 32px;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  animation: fadeIn 0.3s ease-out;
}

/* 标题样式 */
.modal-title {
  margin-bottom: 16px;
  color: #2d5bff;
  font-size: 1.2rem;
  font-weight: bold;
}

/* 警告文字及动画 */
.modal-warning {
  margin-bottom: 16px;
  color: #000;
  font-size: 1.1rem;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 8px;
}
.warning-icon {
  display: inline-block;
  animation: pulse 1.5s infinite;
}

/* 输入框样式 */
.modal-content input[type="text"],
.modal-content input[type="number"],
.modal-content input[type="datetime-local"] {
  width: 100%;
  padding: 8px 10px;
  margin: 8px 0;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
  transition: border-color 0.3s;
}
.modal-content input:focus {
  border-color: var(--color-secondary);
  outline: none;
}

/* 标签样式 */
.modal-content label {
  color: #333;
  display: block;
  margin-bottom: 8px;
  font-size: 0.95rem;
}

/* 按钮容器 */
.buttons {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 按钮样式，按你给出的风格 */
.cancel-btn {
  background-color: #fff !important;
  border: 1px solid #2d5bff !important;
  color: #2d5bff !important;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 5px;
}

/* 确认类按钮 */
.confirm-btn {
  background-color: #2d5bff !important;
  border: 1px solid #2d5bff !important;
  color: #fff !important;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 5px;
}
.cancel-btn:hover {
  background-color: var(--color-tertiary);
}

.confirm-btn:hover {
  background-color: var(--color-secondary);
}

/* 渐显动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 警告标识动画：脉冲效果 */
@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
  }
}

.card-header {
  font-size: 18px;
  font-weight: bold;
  color: #2d5bff;
  margin-bottom: 12px;
}

.left-column .card {
  background-color: white;
  border: 1px solid #ddd; /* Border color */
  border-radius: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); /* Shadow effect */
  padding: 16px;
  margin-bottom: 10px; /* Adjust margin between cards */
  /* Remove fixed height for responsive design */
}

.left-column .card:first-child {
  flex: 2; /* First card takes more space */
}

.left-column .card:last-child {
  flex: 1; /* Second card takes less space */
  /* 允许内容滚动，防止撑大 */
  display: flex;
  justify-content: center; /* 水平居中 */
  align-items: center; /* 垂直居中 */
  height: 100vh; /* 占满整个视口高度 */
}

/* 选择病人按钮样式 */
.select-patient-btn {
  margin-bottom: 8px;
  padding: 10px 20px;
  border: none;
  background: linear-gradient(135deg, #2d5bff, #93aafd);
  color: #fff;
  border-radius: 50px;
  cursor: pointer;
  font-weight: 600;
  font-size: 15px;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 4px 15px rgba(45, 91, 255, 0.3);
  transition: all 0.3s ease;
  width: 100%;
  max-width: 200px;
}

.select-patient-btn i {
  font-size: 16px;
}

.select-patient-btn:hover {
  background: linear-gradient(135deg, #1a48e6, #7b97ff);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(45, 91, 255, 0.4);
}

.select-patient-btn:active {
  transform: translateY(1px);
  box-shadow: 0 2px 10px rgba(45, 91, 255, 0.3);
}
.modal {
  position: fixed;
  z-index: 9999;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  overflow: auto;
  background-color: rgba(0, 0, 0, 0.5); /* 半透明背景 */
}
.modal h2 {
  color: #2d5bff;
}

.modal-content {
  background-color: white;
  margin: 5% auto;
  padding: 20px;
  width: 70%;
  max-width: 900px;
  border-radius: 16px;
  max-height: 80vh; /* 最大高度为屏幕高度的 80% */
  overflow-y: auto; /* 使主体内容可滚动 */
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.close {
  font-size: 30px;
  cursor: pointer;
}

.filters {
  margin-bottom: 10px;
}

.filters label {
  font-weight: bold;
  margin-right: 10px;
  color: #2d5bff; /* 主题色 */
}

.time-range {
  display: flex;
  align-items: center;
}

.time-range input {
  margin-right: 10px; /* 调整输入框之间的间距 */
}

.time-range span {
  margin: 0 5px; /* 控制“至”字的间距 */
}

.filters label {
  font-weight: bold;
  margin-right: 10px;
}

.filters select,
.filters input {
  padding: 5px;
  margin-top: 5px;
  border-radius: 5px;
  border: 1px solid #ccc;
}

.patient-list {
  width: 100%;
  border-collapse: collapse;
}
.patient-list th {
  color: #2d5bff; /* 主题色背景 */
}

.patient-list th,
.patient-list td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

.modal-footer {
  text-align: right;
}

.modal-footer button {
  margin-top: 20px;
  padding: 10px 20px;
  background-color: #2d5bff;
  color: white;
  border: none;
  border-radius: 16px;
  cursor: pointer;
}

.modal-footer button:hover {
  background-color: #93aafd;
}

/* 分析图表按钮样式 */
.analyze-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: linear-gradient(135deg, #2d5bff, #93aafd);
  color: white;
  border: none;
  border-radius: 50px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(45, 91, 255, 0.3);
  margin: 20px auto;
}

.analyze-btn:hover {
  background: linear-gradient(135deg, #1a48e6, #7b97ff);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(45, 91, 255, 0.4);
}

.analyze-btn:active {
  transform: translateY(1px);
  box-shadow: 0 2px 10px rgba(45, 91, 255, 0.3);
}

/* 加载动画样式 */
.loading-text {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(45, 91, 255, 0.2);
  border-radius: 50%;
  border-top-color: #2d5bff;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Markdown 渲染样式 */
.model-explanation :deep(h1),
.model-explanation :deep(h2),
.model-explanation :deep(h3) {
  color: #2d5bff;
  margin-top: 16px;
  margin-bottom: 8px;
}

.model-explanation :deep(p) {
  margin-bottom: 12px;
  line-height: 1.6;
}

.model-explanation :deep(ul),
.model-explanation :deep(ol) {
  padding-left: 20px;
  margin-bottom: 12px;
}

.model-explanation :deep(li) {
  margin-bottom: 6px;
}

.model-explanation :deep(blockquote) {
  border-left: 4px solid #93aafd;
  padding-left: 16px;
  margin: 12px 0;
  color: #555;
}

.model-explanation :deep(code) {
  background-color: #f0f2ff;
  padding: 2px 4px;
  border-radius: 4px;
  font-family: monospace;
}

/* 美化提醒弹窗 */
.alert-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
}

.alert-content {
  background-color: white;
  border-radius: 16px;
  padding: 24px;
  width: 400px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  text-align: center;
  animation: fadeInUp 0.3s ease-out;
}

.alert-icon {
  font-size: 48px;
  color: #2d5bff;
  margin-bottom: 16px;
}

.alert-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin-bottom: 12px;
}

.alert-message {
  font-size: 16px;
  color: #666;
  margin-bottom: 24px;
}

.alert-button {
  background: linear-gradient(135deg, #2d5bff, #93aafd);
  color: white;
  border: none;
  border-radius: 50px;
  padding: 10px 24px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.alert-button:hover {
  background: linear-gradient(135deg, #1a48e6, #7b97ff);
  transform: translateY(-2px);
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 加载动画样式 */
.loading-text {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(45, 91, 255, 0.2);
  border-radius: 50%;
  border-top-color: #2d5bff;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Markdown 渲染样式 */
.model-explanation :deep(h1),
.model-explanation :deep(h2),
.model-explanation :deep(h3) {
  color: #2d5bff;
  margin-top: 16px;
  margin-bottom: 8px;
}

.model-explanation :deep(p) {
  margin-bottom: 12px;
  line-height: 1.6;
}

.model-explanation :deep(ul),
.model-explanation :deep(ol) {
  padding-left: 20px;
  margin-bottom: 12px;
}

.model-explanation :deep(li) {
  margin-bottom: 6px;
}

.model-explanation :deep(blockquote) {
  border-left: 4px solid #93aafd;
  padding-left: 16px;
  margin: 12px 0;
  color: #555;
}

.model-explanation :deep(code) {
  background-color: #f0f2ff;
  padding: 2px 4px;
  border-radius: 4px;
  font-family: monospace;
}

</style>
