<template>
  <!-- 上边栏 -->
  <div class="top">
    <TopNavbar />
  </div>
  <div class="analysis-page">
    <div class="left-column">
      <!-- 疾病介绍部分 -->
      <div class="card">
        <div class="card-content">
          <!-- 左侧查找图标 -->
          <div class="icon search-icon" @click="filterAction">
            <!-- 这里使用 Font Awesome 的查找图标 -->
            <i class="fa fa-search"></i>
          </div>
          <!-- 输入框 -->
          <input type="text" v-model="searchKey" placeholder="请输入查找内容" />
          <!-- 右侧筛选图标 -->
          <div class="icon filter-icon" @click="togglePopup">
            <!-- 这里使用 Font Awesome 的筛选图标 -->
            <i class="fa fa-filter"></i>
          </div>
        </div>
      </div>

      <!-- 弹出的筛选浮窗 -->
      <div v-if="popupVisible" class="popup-overlay" @click.self="closePopup">
        <div class="popup-content">
          <div class="close-buttons">
            <i class="fa fa-times close-icon" @click="closePopup"></i>
          </div>
          <div class="type">
            <h3>筛选选项</h3>
          </div>
          <!-- 脑卒中类型 -->
          <!-- 脑卒中类型多选 -->
          <div class="type_filter-item">
            <div class="type_header" @click="toggleCollapse">
              <span>脑卒中类型:</span>
              <!-- 使用 Font Awesome 图标来表示收缩状态 -->
              <i
                class="fa"
                :class="{
                  'fa-chevron-down': type_collapsed,
                  'fa-chevron-up': !type_collapsed,
                }"
              ></i>
            </div>
            <!-- 收缩区域内容：复选框部分 -->
            <div class="type-content" v-if="!type_collapsed">
              <div class="checkbox-group">
                <!-- 遍历所有选项，每个选项为一个复选框 -->
                <label
                  v-for="option in strokeOptions"
                  :key="option.value"
                  class="checkbox-label"
                >
                  <input
                    type="checkbox"
                    :value="option.value"
                    v-model="choose_type"
                  />
                  {{ option.label }}
                </label>
              </div>
            </div>
          </div>
          <!-- 进入 ICU 时间 -->
          <div class="filter-item">
            <label>进入 ICU 时间:</label>
            <!-- 这里使用 Element UI 的日期选择组件 -->
            <el-date-picker
              v-model="icuEntryDate"
              type="date"
              placeholder="选择日期"
            >
            </el-date-picker>
          </div>
          <!-- 离开 ICU 时间 -->
          <div class="filter-item">
            <label>离开 ICU 时间:</label>
            <el-date-picker
              v-model="icuExitDate"
              type="date"
              placeholder="选择日期"
            >
            </el-date-picker>
          </div>
          <!-- 操作按钮 -->
          <div class="popup-buttons">
            <button class="reset-btn" @click="resetFilters">重置</button>
            <button class="apply-btn" @click="applyFilters">完成</button>
          </div>
        </div>
      </div>

      <!-- 患者信息列表 -->
      <div class="patient-container">
        <div class="patients-list">
          <div v-for="patient in filteredPatients" :key="patient.id">
            <PatientCard :patient="patient" :onSelect="handleSelect" />
          </div>
        </div>
      </div>
    </div>
    <!-- 左边栏结束 -->
    <div class="right-column">
      <div class="patient-info-container">
        <div v-if="patientDetails" class="patient-sample-info">
          <!-- 病人 ID 和姓名 -->
          <div class="patient-header">
            <h2>
              {{ patientDetails.id }}. {{ patientDetails.name.toUpperCase() }}
            </h2>
          </div>

          <!-- 病人详细信息 -->
          <div class="patient-detail">
            <p>{{ patientDetails.age }}岁</p>
            <span class="separator">|</span>
            <span>{{
              formatIcuDates(
                patientDetails.icuEntryDate,
                patientDetails.icuExitDate
              )
            }}</span>
          </div>

          <!-- 疾病信息 -->
          <div class="disease-info">
            <div
              v-if="patientDetails.medicalHistory.length > 0"
              class="disease-tags"
            >
              <span
                v-for="disease in patientDetails.medicalHistory"
                :key="disease"
                class="disease-tag"
                >{{ disease }}</span
              >
            </div>
            <div v-else>
              <span>该病人无基础病</span>
            </div>
          </div>
          <!-- 突出显示的病情 -->
          <div v-if="patientDetails.strokeType" class="special-condition">
            {{ patientDetails.strokeType }}
          </div>
        </div>
        <!-- 病人基本信息结束 -->
        <!-- 病历记录和CT记录开始 -->
        <div class="record-container">
          <div class="record-type">
            <div class="options">
              <div
                v-if="selectedRecordType === 'caseRecords'"
                class="option1-rectangle"
              ></div>
              <div
                v-if="selectedRecordType === 'ctRecords'"
                class="option2-rectangle"
              ></div>
              <button
                :class="{ selected: selectedRecordType === 'caseRecords' }"
                @click="selectedRecordType = 'caseRecords'"
              >
                病历记录
              </button>
              <button
                :class="{ selected: selectedRecordType === 'ctRecords' }"
                @click="selectedRecordType = 'ctRecords'"
              >
                脑部CT记录
              </button>
            </div>
          </div>
          <!-- 记录类型选择结束 -->

          <!-- 病历记录 -->
          <div v-if="selectedRecordType === 'caseRecords'" class="record-list">
            <div
              v-for="(record, index) in caseRecords"
              :key="index"
              class="record-item"
            >
              <div class="circle">{{ index + 1 }}</div>
              <p>就诊日期：{{ record.visitDate }}</p>
              <button @click="openModal(record)">></button>
            </div>
          </div>
          <!-- 病历记录结束 -->

          <!-- 弹出浮窗 -->
          <div v-if="showModal" class="modal-overlay">
            <div class="modal">
              <div class="modal-header">
                <span class="close-btn" @click="closeModal">X</span>
              </div>
              <div class="modal-body">
                <div class="case-info">
                  <p>病例编号: {{ selectedCase.caseId }}</p>
                  <p>就诊日期: {{ selectedCase.visitDate }}</p>
                  <p>就诊地点: {{ selectedCase.location }}</p>
                  <p>病历详情: {{ selectedCase.details }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <!-- 病人信息结束 -->
      <div class="chart-container">
        <EventTimeline />
      </div>
      <!-- - 下半部分 - 左右两部分 -->
      <div class="bottom-section">
        <!-- 左半部分 - 模型解释 -->
        <div class="left-half">
          <div class="model-explanation">
            <RulesDiagram />
          </div>
        </div>

        <!-- 右半部分 - 聊天框 -->
        <div class="right-half">
          <div class="chat-container">
            <h3>AI咨询</h3>
            <!-- 显示消息 -->
            <div class="messages">
              <div
                v-for="message in chatMessages"
                :class="['message', message.sender]"
                :key="message.id"
              >
                <div class="message-content">
                  <span v-if="message.type === 'image'">
                    <img
                      :src="message.content"
                      alt="User uploaded image"
                      class="uploaded-image"
                    />
                  </span>
                  <span v-else>{{ message.content }}</span>
                </div>
              </div>
            </div>

            <!-- 输入框 -->
            <div class="input-container">
              <!-- 上传按钮（+号图标） -->
              <button class="upload-btn" @click="triggerFileInput">
                <i class="fas fa-plus"></i>
                <!-- 使用Font Awesome的加号图标 -->
              </button>
              <input
                type="file"
                ref="fileInput"
                style="display: none"
                @change="handleFileChange"
              />

              <!-- 显示上传的图片 -->
              <div v-if="uploadedImage" class="uploaded-preview">
                <img
                  :src="uploadedImage"
                  alt="Uploaded Image"
                  class="image-preview"
                />
              </div>

              <textarea
                v-model="userInput"
                placeholder="输入问题..."
                rows="3"
              ></textarea>
              <!-- 提交按钮（右箭头图标） -->
              <button @click="sendMessage" class="submit-btn">
                <i class="fas fa-arrow-right"></i>
                <!-- 使用Font Awesome的右箭头图标 -->
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- 右边栏结束 -->
  </div>
</template>

<script>
import TopNavbar from "@/components/TopNavbar.vue";
import EventTimeline from "@/components/EventTimeline.vue";
import RulesDiagram from "@/components/RulesDiagram.vue";
import PatientCard from "@/components/PatientCard.vue";
import { reactive } from "vue";
export default {
  components: {
    TopNavbar,
    EventTimeline,
    RulesDiagram,
    PatientCard,
  },
  data() {
    return {
      userInput: "",
      selectedFile: null,
      uploadedImage: null, // 存储上传的图片 URL
      chatMessages: [],
      type_collapsed: false,
      popupVisible: false,
      searchKey: "",
      choose_type: [],
      icuEntryDate: null,
      icuExitDate: null,
      selectedStrokeType: "",
      selectedPatient: null,
      visibleDetails: reactive({}),
      selectedRecordType: "caseRecords",
      showModal: false,
      selectedCase: null,
      caseRecords: [
        {
          visitDate: "2024-12-14",
          location: "同济大学嘉定校区卫生所",
          details: "病历详情内容1",
          caseId: "A12345",
        },
        {
          visitDate: "2024-11-11",
          location: "同济大学嘉定校区卫生所",
          details: "病历详情内容2",
          caseId: "A12346",
        },
        {
          visitDate: "2024-05-11",
          location: "同济大学嘉定校区卫生所",
          details: "病历详情内容3",
          caseId: "A12347",
        },
      ],
      patients: [
        {
          id: 1,
          name: "患者1",
          age: 45,
          medicalHistory: ["高血压", "心脏病"],
          strokeType: "缺血性脑卒中",
          icuEntryDate: "2025-01-01",
          icuExitDate: "",
          chartData: [],
        },
        {
          id: 2,
          name: "患者2",
          age: 38,
          medicalHistory: ["糖尿病"],
          strokeType: "出血性脑卒中",
          icuEntryDate: "2025-01-02",
          icuExitDate: "2025-01-10",
          chartData: [],
        },
        {
          id: 3,
          name: "患者3",
          age: 60,
          medicalHistory: [],
          strokeType: "缺血性脑卒中",
          icuEntryDate: "2025-01-03",
          icuExitDate: "",
          chartData: [],
        },
        {
          id: 4,
          name: "患者4",
          age: 45,
          medicalHistory: ["高血压"],
          strokeType: "缺血性脑卒中",
          icuEntryDate: "2025-01-01",
          icuExitDate: "",
          chartData: [],
        },
        {
          id: 5,
          name: "患者5",
          age: 45,
          medicalHistory: ["高血压"],
          strokeType: "缺血性脑卒中",
          icuEntryDate: "2025-01-01",
          icuExitDate: "",
          chartData: [],
        },
        {
          id: 6,
          name: "患者6",
          age: 45,
          medicalHistory: ["高血压"],
          strokeType: "缺血性脑卒中",
          icuEntryDate: "2025-01-01",
          icuExitDate: "",
          chartData: [],
        },
      ],
      strokeOptions: [
        { label: "缺血性脑卒中", value: "0" },
        { label: "出血性脑卒中", value: "1" },
        { label: "短暂性脑缺血发作", value: "2" },
        { label: "其他类型", value: "3" },
      ],
    };
  },
  computed: {
    filteredPatients() {
      return this.selectedStrokeType
        ? this.patients.filter(
            (patient) => patient.strokeType === this.selectedStrokeType
          )
        : this.patients; // 如果没有选择任何类型，显示所有患者
    },
    patientDetails() {
      if (
        this.selectedPatient &&
        this.visibleDetails[this.selectedPatient.id]
      ) {
        // 通过 selectedPatient.id 查找对应的病人
        return this.filteredPatients.find(
          (patient) => patient.id === this.selectedPatient.id
        );
      }
      return null; // 如果没有选中病人，返回 null
    },
  },
  mounted() {
    // 页面加载时初始化病人信息
    this.initializePatient();
  },
  methods: {
    // 触发文件选择框的点击事件
    triggerFileInput() {
      this.$refs.fileInput.click(); // 触发隐藏的文件输入框
    },

    // 处理文件选择
    handleFileChange(event) {
      const file = event.target.files[0];
      if (file) {
        // 创建图片的 URL
        this.uploadedImage = URL.createObjectURL(file);
        this.selectedFile = file;
      }
    },

    // 发送消息
    sendMessage() {
      // 如果用户输入了文本，则先将文本消息添加到聊天记录中
      if (this.userInput.trim()) {
        this.chatMessages.push({
          id: this.chatMessages.length + 1,
          content: this.userInput,
          sender: "user",
          type: "text",
        });
      }

      // 如果存在上传的图片，则调用图片分析接口
      if (this.selectedFile) {
        // 显示一个临时消息表示正在分析图片
        this.chatMessages.push({
          id: this.chatMessages.length + 1,
          content: "正在分析图片，请稍候...",
          sender: "bot",
          type: "text",
        });

        const formData = new FormData();
        formData.append("image", this.selectedFile);

        fetch("http://127.0.0.1:5000/api/llm/image-analysis", {
          method: "POST",
          body: formData,
        })
          .then((response) => response.json())
          .then((data) => {
            // 移除之前“正在分析图片...”的提示
            this.chatMessages = this.chatMessages.filter(
              (message) => message.content !== "正在分析图片，请稍候..."
            );
            // 将图片分析返回的结果添加到聊天记录中
            this.chatMessages.push({
              id: this.chatMessages.length + 1,
              content: data.result, // 假设返回结果在 data.result
              sender: "bot",
              type: "text",
            });
          })
          .catch((error) => {
            console.error("图片分析错误:", error);
            // 移除提示消息
            this.chatMessages = this.chatMessages.filter(
              (message) => message.content !== "正在分析图片，请稍候..."
            );
            this.chatMessages.push({
              id: this.chatMessages.length + 1,
              content: "抱歉，图片分析失败。",
              sender: "bot",
              type: "text",
            });
          });

        // 同时在用户消息中显示上传的图片
        this.chatMessages.push({
          id: this.chatMessages.length + 1,
          content: this.uploadedImage, // 这是通过 URL.createObjectURL() 得到的预览 URL
          sender: "user",
          type: "image",
        });

        // 清空上传的图片预览和 selectedFile
        this.uploadedImage = null;
        this.selectedFile = null;
      } else if (this.userInput.trim()) {
        // 如果没有图片，仅处理文本消息，则调用聊天接口
        // 显示临时等待消息
        this.chatMessages.push({
          id: this.chatMessages.length + 1,
          content: "回答的内容将自动生成...",
          sender: "bot",
          type: "text",
        });

        fetch("http://127.0.0.1:5000/api/llm/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ message: this.userInput }),
        })
          .then((response) => response.json())
          .then((data) => {
            // 移除临时等待消息
            this.chatMessages = this.chatMessages.filter(
              (message) => message.content !== "回答的内容将自动生成..."
            );
            // 添加后端返回的响应
            this.chatMessages.push({
              id: this.chatMessages.length + 1,
              content: data.response,
              sender: "bot",
              type: "text",
            });
          })
          .catch((error) => {
            console.error("聊天接口错误:", error);
            this.chatMessages = this.chatMessages.filter(
              (message) => message.content !== "回答的内容将自动生成..."
            );
            this.chatMessages.push({
              id: this.chatMessages.length + 1,
              content: "抱歉，我无法回答您的问题。",
              sender: "bot",
              type: "text",
            });
          });
      }

      // 清空输入框
      this.userInput = "";
    },
    closeModal() {
      this.showModal = false;
      this.selectedCase = null;
    },
    openModal(record) {
      this.selectedCase = record;
      this.showModal = true;
    },
    formatIcuDates(entryDate, exitDate) {
      // 格式化 ICU 时间
      if (exitDate) {
        return `${entryDate} - ${exitDate}`;
      } else {
        return `${entryDate} - 仍在ICU`;
      }
    },
    initializePatient() {
      if (this.patients.length > 0) {
        const firstPatient = this.patients[0];
        this.selectedPatient = firstPatient;
        this.visibleDetails[firstPatient.id] = true; // 显示第一个病人的详细信息
      }
    },
    toggleDetails(patientId) {
      // 使用 reactive 的方式更新 visibleDetails 状态
      if (this.visibleDetails[patientId]) {
        this.visibleDetails[patientId] = false;
        this.selectedPatient = null; // 清除选中的病人信息
      } else {
        for (let id in this.visibleDetails) {
          if (id !== patientId) {
            this.visibleDetails[id] = false; // 将其他病人的详细信息状态设置为不可见
          }
        }
        this.visibleDetails[patientId] = true;
        // 选择病人并显示右边栏信息
        this.selectedPatient = this.filteredPatients.find(
          (patient) => patient.id === patientId
        );
      }
    },
    isDetailsVisible(patientId) {
      return !!this.visibleDetails[patientId];
    },
    handleSelect(selectedPatient) {
      this.selectedPatient = selectedPatient;
    },
    filterAction() {
      const postData = {
        patientName: this.searchKey,
      };

      // 向后端发送请求，这里假设使用 POST 方法
      axios
        .post("http://your-backend-domain/api/filter", postData)
        .then((response) => {
          console.log("后端返回数据：", response.data);
          this.patients = response.data;
        })
        .catch((error) => {
          console.error("请求后端时出错：", error);
        });
    },
    togglePopup() {
      this.popupVisible = true;
    },
    closePopup() {
      this.popupVisible = false;
    },
    toggleCollapse() {
      this.type_collapsed = !this.type_collapsed;
    },
    resetFilters() {
      this.choose_type = [];
      this.icuEntryDate = null;
      this.icuExitDate = null;
    },
    // 应用筛选器的逻辑
    applyFilters() {
      this.popupVisible = false;
    },
  },
};
</script>

<style scoped>
.analysis-page {
  display: flex;
  justify-content: space-between;
  color: #0f0f10;
}

/* 左边列样式 */
.left-column {
  width: 20%;
  padding: 5px;
  height: 800px;
}
.left-column h3 {
  margin-bottom: 15px;
  font-size: 20px;
  font-weight: 600;
}
.card {
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 10px;
  align-items: center;
  max-width: 500px;
  margin: 20px auto 20px 0;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  width: 300px;
}
.card-content {
  display: flex;
  align-items: center;
  width: 100%;
}

.icon {
  cursor: pointer;
  padding: 5px;
  font-size: 20px;
  color: #333;
}
.search-icon {
  margin-right: 10px;
}

.filter-icon {
  margin-left: auto;
}
input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 16px;
}

.popup-overlay {
  position: fixed;
  top: 200px;
  left: 300px;
  width: 500px;
  height: 450px;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.popup-content {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  min-width: 320px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  top: 200px;
  left: 300px;
  width: 500px;
  height: 450px;
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

.checkbox-group {
  display: flex;
  flex-wrap: wrap; /* 允许换行 */
}
.checkbox-label {
  width: 50%; /* 每个标签占一行的一半 */
  box-sizing: border-box; /* 防止内边距影响宽度 */
  margin-bottom: 10px; /* 每行下方间距 */
}
.filter-item {
  margin-bottom: 15px; /* 增大项之间的间距 */
  display: flex;
  flex-direction: column;
}

.filter-item label {
  display: flex;
  padding: 10px; /* 增加标签内的内边距 */
  font-size: 18px; /* 增大字体大小 */
  font-weight: bold; /* 设置文字加粗 */
  margin-bottom: 15px; /* 增大标签之间的间距 */
}

.filter-item select,
.filter-item .el-date-picker {
  /* 如果需要，可添加宽度等样式 */
  width: 100%;
}

.popup-buttons {
  display: flex;
  justify-content: space-between; /* 两个按钮之间的间距 */
  margin-top: 20px;
}

button {
  border: none;
  border-radius: 50px; /* 圆角按钮 */
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
}

.reset-btn {
  background-color: white;
  color: #333;
  border: 1px solid #ccc;
  width: 48%; /* 控制按钮宽度 */
}

.apply-btn {
  background-color: #6c68c6; /* 按钮背景色为黄色 */
  color: white;
  width: 48%; /* 控制按钮宽度 */
}
.close-buttons {
  position: flex;
  cursor: pointer;
}

.patient-container {
  margin-bottom: 15px;

  height: 100%;
  padding: auto;
  width: 100%;
}
.patients-list {
  background-color: #e4dcdc;
  font-family: Arial, sans-serif;
  border-radius: 8px;
  padding: 10px;
  height: 100%;
  max-width: 300px;
  margin: 0 -3px;
  color: #0e0f0f;
  overflow-x: hidden; /* 隐藏水平滚动条 */
  overflow-y: auto; /* 显示垂直滚动条 */
}
.patient-id {
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background-color: #f2f6fc;
  border: 1px solid #dde1f0;
  border-radius: 8px;
  font-size: 16px;
  font-weight: bold;
}

.patient-id-text {
  color: #4b6cb7;
}

.patient-card {
  margin-top: 10px;
  padding: 15px;
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.patient-card p {
  margin: 5px 0;
}

.patient-card > div {
  background-color: #eef2f7;
  padding: 10px;
  border-radius: 4px;
}

.patient-id:hover {
  background-color: #e1efff;
}

.patient-id span {
  font-size: 18px;
}
/* 左边列样式结束 */
.right-column {
  width: 80%;
  padding: 5px;
  height: 800px;
}

.patient-info-container {
  flex: 1;
  padding: 10px;
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  height: 17%;
  border: 1px solid black;
  border-radius: 10px;
}

.patient-sample-info {
  margin-top: 2px;
  padding: 2px;
  background-color: #f9f9f9;
  border-radius: 10px;
  position: relative;
  height: 15%;
  width: 49%;
  background-color: linear-gradient(145deg, #ffffff, #e8ebf7);
}

.patient-header {
  display: flex;
  justify-content: space-between;
  margin-top: 2px; /* 设置与父容器上边框的距离为 20px */
  margin-left: 20px;
}

.patient-header h2 {
  font-size: 25px;
  font-weight: bold;
  position: absolute;
  top: -25px;
  left: 15px;
}

.patient-detail {
  position: absolute;
  top: 33px;
  left: 15px;
  display: flex; /* 使用Flexbox进行水平排列 */
  align-items: center; /* 垂直居中对齐 */
}

.patient-detail p {
  margin: 0 10px; /* 给左右的<p>添加间距 */
}

.separator {
  margin: 0 10px; /* 给|两边添加间距 */
}

.disease-info {
  margin-top: 20px;
  margin-left: 20px;
}

.disease-tags {
  display: flex;
  flex-wrap: wrap;
}

.disease-tag {
  margin-top: 35px;
  padding: 5px 10px;
  background-color: #e0e0e0;
  border-radius: 20px;
  font-size: 14px;
  color: #333;
  transition: transform 0.3s ease; /* 只对 transform 添加过渡效果 */
}

.disease-tag:hover {
  transform: scale(1.1); /* 鼠标悬停时，标签放大 10% */
  cursor: pointer; /* 鼠标悬停时变成手形 */
}

.special-condition {
  background-color: #add8e6; /* 浅蓝色背景 */
  color: #1e3a8a; /* 深蓝色文字 */
  padding: 10px 20px; /* 内边距，调整矩形的大小 */
  border-radius: 5px; /* 可选：为矩形添加轻微的圆角 */
  font-size: 18px; /* 文字大小 */
  font-weight: bold; /* 文字加粗 */
  text-align: center;
  display: inline-block; /* 使元素为内联块级元素 */
  position: absolute; /* 使元素相对于父容器定位 */
  top: 25px;
  left: 300px; /* 可以根据需要调整位置 */
}

.special-condition:hover {
  transform: scale(1.03); /* 鼠标悬停时，标签放大 10% */
  cursor: pointer; /* 鼠标悬停时变成手形 */
}

/*病历列表样式 */
.record-container {
  border-radius: 10px;
  width: 49%;
  left: -90px;
  height: 10%;
}
.options {
  display: flex;
  justify-content: flex-start; /* 使选项卡按钮靠右排列 */
  gap: 20px; /* 在按钮之间增加间距，可以调整为需要的间距 */
  border-bottom: 1px solid #e0e0e0; /* 下方灰色分隔线 */
  position: relative;
  margin-top: -15px;
}

.options button {
  background: none;
  border: none;
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
  color: #333;
  outline: none;
  position: relative;
  transition: color 0.3s;
}

.options button:hover {
  transform: scale(1.1); /* 鼠标悬停时，标签放大 10% */
}

.option1-rectangle {
  position: absolute; /* 使矩形相对于父容器定位 */
  top: 40px; /* 设置距离父容器顶部 0 像素 */
  left: 30px; /* 设置距离父容器左边 0 像素 */
  width: 45px; /* 矩形宽度 */
  height: 5px; /* 矩形高度 */
  background-color: rgb(85, 0, 255); /* 矩形背景颜色为橙色 */
}

.option2-rectangle {
  position: absolute; /* 使矩形相对于父容器定位 */
  top: 40px; /* 设置距离父容器顶部 0 像素 */
  left: 160px; /* 设置距离父容器左边 0 像素 */
  width: 45px; /* 矩形宽度 */
  height: 5px; /* 矩形高度 */
  background-color: rgb(85, 0, 255); /* 矩形背景颜色为橙色 */
}

.record-list {
  margin-top: 20px;
  display: flex;
  flex-wrap: nowrap; /* 禁止换行 */
  gap: 20px; /* 控制记录项之间的间距 */
  overflow-x: auto; /* 添加水平滚动条 */
  padding-bottom: 45px; /* 防止滚动条遮挡内容 */
  height: 20px;
  overflow-y: hidden; /* 禁用垂直滚动条 */
}

.record-item {
  background-color: #f0f0f0;
  padding: -15px;
  border-radius: 10px;
  width: 250px; /* 控制记录项宽度 */
  text-align: center;
  display: flex;
  height: 50px;
  flex-shrink: 0; /* 防止记录项被压缩 */
}

.record-item button {
  margin-top: 10px;
}
.circle {
  width: 30px; /* 圆形的宽度 */
  height: 30px; /* 圆形的高度 */
  background-color: rgb(85, 0, 255); /* 橙色背景 */
  color: white; /* 文字颜色 */
  font-size: 16px; /* 文字大小 */
  font-weight: bold; /* 文字加粗 */
  border-radius: 50%; /* 让元素变为圆形 */
  display: flex;
  justify-content: center; /* 水平居中 */
  align-items: center; /* 垂直居中 */
}
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal {
  background-color: white;
  padding: 20px;
  width: 400px;
  border-radius: 10px;
}

.modal-header {
  display: flex;
  justify-content: flex-end;
}

.close-btn {
  font-size: 20px;
  cursor: pointer;
}

.case-info p {
  margin: 5px 0;
}
.chart-section {
  margin-bottom: 20px;
}

.bottom-section {
  display: flex;
  justify-content: space-between;
}

.left-half {
  width: 48%;
  padding: 10px;
}
.model-explanation {
  border-radius: 10px;
  border: 1px solid #423535;
}
.right-half {
  padding: 10px;
  width: 48%;
  height: 300px; /* 增加咨询区域的高度 */
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}
.chart-container {
  /* 图表容器样式 */
  border-radius: 10px;
  height: 50%;
  background: linear-gradient(145deg, #ffffff, #f0f0f0);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  padding: 15px;
  border: 1px solid #e0e0e0;
}

/* 聊天框整体 */
.chat-container {
  background-color: #f7f7f7;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden; /* 禁止聊天框内部的滚动 */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
.uploaded-preview {
  margin-top: 10px;
  text-align: center;
}

.image-preview {
  max-width: 200px;
  max-height: 150px;
  object-fit: cover;
  border-radius: 8px;
}

/* 消息容器 */
.messages {
  flex: 1; /* 让消息区域占满剩余空间 */
  overflow-y: auto; /* 使消息区域可滚动 */
  padding-right: 10px; /* 防止滚动条挡住内容 */
}

/* 每条消息的样式 */
.message {
  margin-bottom: 20px;
  display: flex;
  flex-direction: row;
  align-items: flex-start;
}

/* 医生消息和大模型消息的样式 */
.message.user {
  justify-content: flex-end; /* 医生消息靠右 */
}

.message.bot {
  justify-content: flex-start; /* 大模型消息靠左 */
}

.message .message-content {
  max-width: 70%;
  padding: 10px 15px;
  border-radius: 10px;
  font-size: 14px;
}

.message.user .message-content {
  background-color: #c6d2fd;
  color: black;
}

.message.bot .message-content {
  background-color: #e5eafc;
  color: black;
  text-align: left;
}

/* 输入框固定底部 */
.input-container {
  display: flex;
  flex-direction: row;
  align-items: center;

  background-color: #ffffff;
  border-radius: 8px;
  position: sticky;
  bottom: 0;
  width: 100%;
  z-index: 10; /* 保证输入框在最上面 */
}

/* 上传按钮样式 */
.upload-btn {
  font-size: 18px;
  padding: 5px 10px;
  background-color: #93aafd;
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  margin-right: 10px;
}

/* 隐藏的文件选择框 */
.input-container input[type="file"] {
  display: none;
}

/* 输入框样式 */
.input-container textarea {
  width: 75%; /* 调整输入框的宽度 */
  padding: 10px;
  border: 1px solid #93aafd;
  border-radius: 8px;
  font-size: 14px;
}

/* 提交按钮样式 */
.input-container button {
  background-color: #2d5bff;
  color: white;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  margin-left: 10px;
  border: none;
}

.input-container button:hover {
  background-color: #93aafd;
}
</style>
