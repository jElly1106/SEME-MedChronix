<template>
  <div class="analysis-page">
    <!-- <div class="top-column"></div> -->
    <TopNavbar />
    <div class="analysis-page-container">
      <div class="left-column">
        <div class="card">
          <div class="card-content">
            <!-- 左侧查找图标 -->
            <div class="icon search-icon" @click="filterAction">
              <!-- 这里使用 Font Awesome 的查找图标 -->
              <i class="fa fa-search"></i>
            </div>
            <!-- 输入框 -->
            <input
              type="text"
              v-model="searchKey"
              placeholder="请输入查找内容"
            />
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
        <div class="patients-list">
          <div v-for="patient in filteredPatients" :key="patient.id">
            <PatientCard :patient="patient" :onSelect="handleSelect" />
          </div>
        </div>
      </div>

      <div class="right-column">
        <!-- 上半部分 - 图表区域 -->
        <div class="chart-container">
          <ChartComponent />
        </div>

        <!-- 下半部分 - 左右两部分 -->
        <div class="bottom-section">
          <!-- 左半部分 - 模型解释 -->
          <div class="left-half">
            <div class="model-explanation">
              <h3>图表解释</h3>
              <p>模型的解释内容将在这里展示。</p>
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
                    <!-- 如果是文本，使用 v-html 渲染解析后的 Markdown -->
                    <div v-else v-html="parseMarkdown(message.content)"></div>
                  </div>
                </div>
              </div>

              <!-- 输入框 -->
              <div class="input-container">
                <!-- 如果有上传的图片，则显示在上方 -->
                <div v-if="uploadedImage" class="uploaded-preview">
                  <img
                    :src="uploadedImage"
                    alt="Uploaded Image"
                    class="image-preview"
                  />
                  <!-- 关闭按钮 -->
                  <button class="close-preview-btn" @click="removeImage">
                    <i class="fas fa-times"></i>
                  </button>
                </div>

                <div class="input-row">
                  <!-- 上传按钮（+号图标） -->
                  <button class="upload-btn" @click="triggerFileInput">
                    <i class="fas fa-plus"></i>
                  </button>
                  <!-- 隐藏的文件选择框 -->
                  <input
                    type="file"
                    ref="fileInput"
                    @change="handleFileChange"
                  />

                  <!-- 文本输入框 -->
                  <textarea
                    v-model="userInput"
                    placeholder="输入问题..."
                    rows="3"
                  ></textarea>

                  <!-- 提交按钮（右箭头图标） -->
                  <button @click="sendMessage" class="submit-btn">
                    <i class="fas fa-arrow-right"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import PatientCard from "@/components/PatientCard.vue";
import TopNavbar from "@/components/TopNavbar.vue";
import { marked } from "marked";
import ChartComponent from "@/components/ChartComponent.vue";

// import ChartComponent from "@/components/ChartComponent.vue";

export default {
  components: {
    PatientCard,
    ChartComponent,
    TopNavbar,
  },
  data() {
    return {
      strokeOptions: [
        { label: "缺血性脑卒中", value: "0" },
        { label: "出血性脑卒中", value: "1" },
        { label: "短暂性脑缺血发作", value: "2" },
        { label: "其他类型", value: "3" },
      ],
      strokeTypes: ["缺血性脑卒中", "出血性脑卒中", "混合型脑卒中"],
      genderTypes: ["男", "女"],
      selectedGender: "",
      selectedStrokeType: "",
      patients: [
        {
          id: 1,
          name: "患者1",
          age: 45,
          medicalHistory: "高血压",
          strokeType: "缺血性脑卒中",
          icuEntryDate: "2025-01-01",
          icuExitDate: "",
          chartData: [],
        },
        {
          id: 2,
          name: "患者2",
          age: 38,
          medicalHistory: "糖尿病",
          strokeType: "出血性脑卒中",
          icuEntryDate: "2025-01-02",
          icuExitDate: "2025-01-10",
          chartData: [],
        },
        {
          id: 3,
          name: "患者3",
          age: 60,
          medicalHistory: "无",
          strokeType: "缺血性脑卒中",
          icuEntryDate: "2025-01-03",
          icuExitDate: "",
          chartData: [],
        },
        {
          id: 4,
          name: "患者4",
          age: 45,
          medicalHistory: "高血压",
          strokeType: "缺血性脑卒中",
          icuEntryDate: "2025-01-01",
          icuExitDate: "",
          chartData: [],
        },
        {
          id: 5,
          name: "患者5",
          age: 45,
          medicalHistory: "高血压",
          strokeType: "缺血性脑卒中",
          icuEntryDate: "2025-01-01",
          icuExitDate: "",
          chartData: [],
        },
        {
          id: 6,
          name: "患者6",
          age: 45,
          medicalHistory: "高血压",
          strokeType: "缺血性脑卒中",
          icuEntryDate: "2025-01-01",
          icuExitDate: "",
          chartData: [],
        },
      ],
      selectedPatients: [],
      userInput: "",
      selectedFile: null,
      uploadedImage: null, // 存储上传的图片 URL
      chatMessages: [],
      choose_type: [],
      popupVisible: false,
      type_collapsed: false,
      icuEntryDate: null,
      icuExitDate: null,
    };
  },
  computed: {
    filteredPatients() {
      if (this.selectedStrokeType) {
        return this.patients.filter(
          (patient) => patient.strokeType === this.selectedStrokeType
        );
      }
      return this.patients; // 如果没有选择任何类型，显示所有患者
    },
  },
  methods: {
    // 重置筛选器的逻辑
    resetFilters() {
      this.choose_type = [];
      this.icuEntryDate = null;
      this.icuExitDate = null;
    },
    // 应用筛选器的逻辑
    applyFilters() {
      this.popupVisible = false;
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
    parseMarkdown(text) {
      // 如果 text 为空或不是字符串，可自行处理
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
    removeImage() {
      this.uploadedImage = null;
      // 同时清空 file input 的值，防止重复选取相同文件时不触发 change
      this.$refs.fileInput.value = "";
      this.selectedFile = null;
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
  },
};
</script>

<style scoped>
.analysis-page {
  width: 100%;
  height: 100vh;
}
.analysis-page-container {
  display: flex;
  justify-content: space-between;
}

.left-column {
  width: 20%;
  padding: 5px;
  height: 90vh;
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

/* 搜索栏卡片 */
.card {
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 10px;
  align-items: center;
  max-width: 500px;
  margin: 20px auto 20px 0;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  width: 100%;
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
/*浮窗*/
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

.patients-list {
  margin: -10px auto 0px 0;
  overflow-y: auto;
  padding: 10px;
  background-color: #c6d2fd; /* 设置背景为蓝色 */
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  width: 100%;
  height: 90%;
}

.patient-card {
  background-color: white; /* 白色背景 */
  color: black; /* 文字颜色为黑色 */
  padding: 20px;
  margin: 10px 0;
  border-radius: 10px;
  font-size: 16px;
  font-family: "Arial", sans-serif;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.patient-card:hover {
  background-color: #f1f1f1; /* Hover时的背景颜色 */
  cursor: pointer;
  transform: translateY(-5px);
}

.patient-card h4 {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 10px;
}

.patient-card .info {
  font-size: 14px;
  line-height: 1.6;
}

.patient-card .info span {
  font-weight: 600;
  color: #333; /* 字体颜色设为黑色 */
}

.patient-card .info p {
  margin: 5px 0;
  font-size: 14px;
  color: #333;
}

.patient-card .button {
  text-align: right;
  margin-top: 15px;
}

.patient-card .button button {
  background-color: #2d5bff;
  border: none;
  color: white;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
}

.patient-card .button button:hover {
  background-color: #93aafd;
}

/* 修改复选框大小 */
input[type="checkbox"] {
  transform: scale(1.5); /* 增大复选框 */
  margin: 5px;
}

.right-column {
  width: 75%;
  padding: 20px;
  height: 90vh;
}

.chart-container {
  height: 50vh;
  border-radius: 8px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.bottom-section {
  display: flex;
  padding: 20px;
  border: 4px solid #aaa; /* 加粗边框 */
  border-radius: 15px; /* 圆角边框 */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); /* 细腻阴影 */
  background-color: #fff;
  height: 35vh;
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

/* 消息区域调整，确保留出足够空间给输入框 */
.messages {
  flex: 1;
  overflow-y: auto;
  padding-right: 10px;
  padding-bottom: 60px; /* 增加底部内边距，为固定定位的输入框留出空间 */
}

/* 每条消息的样式 */
.message {
  margin-bottom: 10px;
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
  max-width: 80%;
  padding: 0px 10px;
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
.uploaded-image {
  max-width: 100%;
  border-radius: 5px;
}

/* 输入框固定底部 */
/* 外层容器 - 垂直布局，图片预览在上，输入行在下 */
.input-container {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  background-color: #ffffff;
  border: 1px solid #f0f0f0;
  border-radius: 30px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 10px 15px;
  position: absolute; /* 改为绝对定位，避免在flex布局中被压缩 */
  bottom: 10px; /* 距离底部10px */
  left: 50%; /* 水平居中 */
  transform: translateX(-50%); /* 水平居中 */
  width: 90%; /* 宽度占90% */
  z-index: 10;
  min-height: 56px; /* 设置最小高度确保不会被压得太扁 */
}

/* 输入行样式调整 */
.input-row {
  display: flex;
  align-items: center;
  min-height: 36px; /* 确保最小高度 */
}

/* 文本输入框调整 */
.input-row textarea {
  flex: 1;
  min-height: 36px;
  border: none;
  outline: none;
  resize: none;
  background-color: transparent;
  font-size: 16px;
  color: #333;
  padding: 5px 0; /* 增加上下内边距 */
  margin-right: 10px;
  line-height: 1.4; /* 改善多行文本的行间距 */
}

/* 上传预览区域调整 */
.uploaded-preview {
  position: relative;
  display: flex;
  align-items: center;
  margin-bottom: 8px; /* 与输入行保持间距 */
}

.image-preview {
  position: relative;
  display: block;
  width: 40px; /* 稍微加大图片预览 */
  height: 40px;
  border-radius: 5px;
  object-fit: cover;
  margin-right: 5px;
}

/* 关闭按钮 - 右上角 */
.close-preview-btn {
  position: relative;
  top: -20px;
  right: 10px; /* 改为右上角位置，更符合常规设计 */
  width: 20px; /* 增加尺寸 */
  height: 20px; /* 增加尺寸 */
  background-color: #ff4757; /* 更醒目的红色 */
  color: #fff;
  border: 2px solid #fff; /* 添加白色边框增强立体感 */
  border-radius: 50%;
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3); /* 增强阴影 */
  z-index: 11; /* 确保在最上层 */
  transition: all 0.2s ease; /* 平滑过渡效果 */
  padding: 0; /* 重置内边距 */
  line-height: 1; /* 确保内容垂直居中 */
}

/* 悬停时变亮一些 */
.close-preview-btn:hover {
  background-color: #999;
}

/* 输入行（+号按钮、文本域、发送按钮）并排 */
.input-row {
  display: flex;
  align-items: center;
}

/* “+”号上传按钮 - 圆形 */
.upload-btn {
  width: 36px;
  height: 36px;
  background-color: #93aafd;
  color: #ffffff;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  margin-right: 10px; /* 与文本域拉开距离 */
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

/* 隐藏的文件选择框 */
.input-container input[type="file"] {
  display: none;
}

/* 文本输入框 - 占据剩余空间，简洁无边框 */
.input-row textarea {
  flex: 1; /* 撑满剩余宽度 */
  min-height: 36px; /* 保证与按钮等高 */
  border: none;
  outline: none;
  resize: none; /* 禁止拖拽缩放 */
  background-color: transparent;
  font-size: 16px;
  color: #333;
  padding: 0;
  margin-right: 10px; /* 与发送按钮拉开距离 */
}

/* 占位文字颜色 */
.input-row textarea::placeholder {
  color: #aaa;
}

/* 发送按钮（右箭头图标） - 圆形 */
.submit-btn {
  width: 36px;
  height: 36px;
  background-color: #2d5bff;
  color: #ffffff;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  transition: background-color 0.3s ease;
}

/* 悬停时颜色变浅 */
.submit-btn:hover {
  background-color: #93aafd;
}
</style>
