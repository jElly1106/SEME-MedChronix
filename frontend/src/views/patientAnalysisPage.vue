<template>
  <!-- 上边栏 -->
  <TopNavbar />
  <div class="analysis-page" v-if="this.qualificationStatus === 'approved'">
    <div class="left-column">
      <!-- 疾病介绍部分 -->
      <div class="search-filter-bar">
        <!-- 左侧查找图标 -->
        <div class="icon search-icon">
          <i class="fa fa-search"></i>
        </div>
        <!-- 搜索输入框 -->
        <input
          type="text"
          class="search-input"
          placeholder="输入姓名..."
          v-model="searchName"
          @input="handleSearch"
        />
        <!-- 右侧筛选图标 -->
        <div class="icon filter-icon" @click="togglePopup">
          <i class="fa fa-filter"></i>
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
                    :value="option.label"
                    v-model="choose_type"
                  />
                  {{ option.label }}
                </label>
              </div>
            </div>
          </div>
          <!-- 进入 ICU 时间 -->
          <div class="filter-item">
            <label>进入 ICU 时间范围:</label>
            <!-- 将单个日期选择器改为日期范围选择器 -->
            <el-date-picker
              v-model="icuEntryDateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="yyyy-MM-dd"
              value-format="yyyy-MM-dd"
            >
            </el-date-picker>
          </div>
          <!-- 离开 ICU 时间 -->
          <div class="filter-item">
            <label>离开 ICU 时间范围:</label>
            <el-date-picker
              v-model="icuExitDateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="yyyy-MM-dd"
              value-format="yyyy-MM-dd"
            >
            </el-date-picker>
          </div>
          <!-- 操作按钮 -->
          <div class="popup-footer">
            <button class="reset-btn" @click="resetFilters">重置</button>
            <button class="apply-btn" @click="applyFilters" :disabled="loading">
              {{ loading ? "加载中..." : "应用" }}
            </button>
          </div>
        </div>
      </div>

      <!-- 患者信息列表 -->
      <div class="patients-list">
        <div class="patients-header">
          <h3>患者列表</h3>
          <button class="add-patient-btn" @click="openAddModal">
            <i class="fa fa-plus"></i> 添加患者
          </button>
        </div>

        <!-- 在使用 PatientCard 组件的地方 -->
        <PatientCard
          v-for="patient in filteredPatients"
          :key="patient.id"
          :patient="patient"
          :isSelected="selectedPatient && selectedPatient.id === patient.id"
          :onSelect="handleSelect"
          @edit="openEditModal"
          @delete="confirmDelete"
        />
      </div>

      <!-- 删除确认弹窗 -->
      <div v-if="showDeleteModal" class="modal">
        <div class="modal-content">
          <p class="modal-warning">
            <span class="warning-icon">⚠️</span>
            <span>确认删除该病人信息吗？</span>
          </p>
          <div class="buttons">
            <button @click="deletePatient" class="confirm-btn">确认</button>
            <button @click="closeDeleteModal" class="cancel-btn">取消</button>
          </div>
        </div>
      </div>

      <!-- 编辑病人信息表单弹窗 -->
      <div v-if="showEditModal" class="modal">
        <div class="modal-content">
          <h3 class="modal-title">
            {{ isAddingPatient ? "添加新患者" : "修改患者信息" }}
          </h3>
          <form @submit.prevent="submitEdit">
            <label>
              姓名:
              <input v-model="editPatient.name" type="text" required />
            </label>
            <label>
              性别:
              <input v-model="editPatient.gender" type="text" required />
            </label>
            <label>
              年龄:
              <input v-model="editPatient.age" type="number" required />
            </label>
            <label>
              心脏病史:
              <input v-model="editPatient.heartDiseaseHistory" type="text" />
            </label>
            <label>
              糖尿病史:
              <input v-model="editPatient.diabetesHistory" type="text" />
            </label>
            <label>
              高血压史:
              <input v-model="editPatient.hypertensionHistory" type="text" />
            </label>
            <label>
              其他病史:
              <input v-model="editPatient.otherHistory" type="text" />
            </label>
            <label>
              脑卒中类型:
              <input v-model="editPatient.strokeType" type="text" required />
            </label>
            <label>
              入ICU时间:
              <input
                v-model="editPatient.ICUAdmissionTime"
                type="datetime-local"
              />
            </label>
            <label>
              出ICU时间:
              <input
                v-model="editPatient.ICUDischargeTime"
                type="datetime-local"
              />
            </label>
            <div class="buttons">
              <button type="submit" class="confirm-btn">确认</button>
              <button type="button" @click="closeEditModal" class="cancel-btn">
                取消
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
    <!-- 左边栏结束 -->
    <div class="right-column">
      <div class="patient-info-container">
        <div v-if="patientDetails" class="patient-info-card">
          <!-- 左侧：病人基本信息 -->
          <div class="patient-basic-info">
            <div class="patient-avatar">
              <span>{{
                patientDetails.name
                  ? patientDetails.name.charAt(0).toUpperCase()
                  : ""
              }}</span>
            </div>
            <div class="patient-header">
              <h2>
                {{ patientDetails.name.toUpperCase() }}
              </h2>
              <div class="patient-badges">
                <span class="badge gender-badge">{{
                  patientDetails.gender
                }}</span>
                <span class="badge age-badge">{{ patientDetails.age }}岁</span>
              </div>
            </div>
          </div>

          <!-- 中间：住院信息 -->
          <div class="patient-hospital-info">
            <div class="info-item">
              <i class="fa fa-calendar"></i>
              <div class="info-content">
                <span class="info-label">ICU住院时间</span>
                <span class="info-value">{{
                  formatIcuDates(
                    patientDetails.ICUAdmissionTime,
                    patientDetails.ICUDischargeTime
                  )
                }}</span>
              </div>
            </div>
            <div class="info-item">
              <i class="fa fa-heartbeat"></i>
              <div class="info-content">
                <span class="info-label">脑卒中类型</span>
                <span class="info-value stroke-type">{{
                  patientDetails.strokeType
                }}</span>
              </div>
            </div>
          </div>

          <!-- 右侧：病史信息 -->
          <div class="patient-medical-history">
            <h3>病史信息</h3>
            <div class="disease-tags">
              <span
                v-if="patientDetails.heartDiseaseHistory !== '无'"
                class="disease-tag heart-tag"
              >
                <i class="fa fa-heart"></i>
                <span>心脏病史: {{ patientDetails.heartDiseaseHistory }}</span>
              </span>
              <span
                v-if="patientDetails.diabetesHistory !== '无'"
                class="disease-tag diabetes-tag"
              >
                <i class="fa fa-medkit"></i>
                <span>糖尿病史: {{ patientDetails.diabetesHistory }}</span>
              </span>
              <span
                v-if="patientDetails.hypertensionHistory !== '无'"
                class="disease-tag hypertension-tag"
              >
                <i class="fa fa-tachometer"></i>
                <span>高血压史: {{ patientDetails.hypertensionHistory }}</span>
              </span>
              <span
                v-if="patientDetails.otherHistory !== '无'"
                class="disease-tag other-tag"
              >
                <i class="fa fa-stethoscope"></i>
                <span>其他病史: {{ patientDetails.otherHistory }}</span>
              </span>
              <span
                v-if="
                  !patientDetails.heartDiseaseHistory &&
                  !patientDetails.diabetesHistory &&
                  !patientDetails.hypertensionHistory &&
                  !patientDetails.otherHistory
                "
                class="disease-tag no-history"
              >
                <i class="fa fa-check-circle"></i>
                <span>无基础病史</span>
              </span>
            </div>
          </div>
        </div>

        <!-- 无病人信息时显示的占位内容 -->
        <div v-else class="patient-info-placeholder">
          <i class="fa fa-user-circle-o"></i>
          <p>请从左侧选择一位病人查看详细信息</p>
        </div>
      </div>
      <!-- 病人信息结束 -->
      <div class="card-container">
        <!-- 卡片切换按钮 -->
        <div class="card-tabs">
          <button
            :class="['tab-btn', { active: activeCard === 'timeline' }]"
            @click="activeCard = 'timeline'"
          >
            病情发展
          </button>
          <button
            :class="['tab-btn', { active: activeCard === 'rules' }]"
            @click="activeCard = 'rules'"
          >
            模型解释
          </button>
          <button
            :class="['tab-btn', { active: activeCard === 'patientData' }]"
            @click="activeCard = 'patientData'"
          >
            患者数据
          </button>
          <button
            :class="['tab-btn', { active: activeCard === 'caseRecords' }]"
            @click="activeCard = 'caseRecords'"
          >
            病例记录
          </button>
          <button
            :class="['tab-btn', { active: activeCard === 'ct' }]"
            @click="activeCard = 'ct'"
          >
            脑部CT记录
          </button>
          <button
            :class="['tab-btn', { active: activeCard === 'chat' }]"
            @click="activeCard = 'chat'"
          >
            智能问答
          </button>
        </div>

        <!-- 卡片内容 -->
        <div class="card-content">
          <div v-show="activeCard === 'timeline'" class="card-item">
            <EventTimeline
              :patientId="selectedPatient ? selectedPatient.id : null"
            />
          </div>
          <div
            v-show="activeCard === 'rules'"
            class="card-item rules-container"
          >
            <div class="rules-part">
              <h3>规则展示</h3>
              <RulesDiagram
                :selectedPatientId="selectedPatient ? selectedPatient.id : null"
                :key="selectedPatient ? selectedPatient.id : 'no-patient'"
              />
            </div>
            <div class="rules-part">
              <h3>病情发展图表解释</h3>
              <!-- 显示模型解释内容 -->
              <!-- <div v-if="modelExplanation" class="model-explanation">
                <div v-html="renderedExplanation"></div>
              </div>
              <div v-else class="model-explanation-placeholder">
                <p>点击下方按钮生成病情发展解释</p>
                <button
                  @click="generateModelExplanation"
                  class="analysis-btn"
                  :disabled="isGeneratingExplanation"
                >
                  <i class="fa fa-magic" v-if="!isGeneratingExplanation"></i>
                  <i class="fa fa-spinner fa-spin" v-else></i>
                  {{
                    isGeneratingExplanation ? "生成中..." : "生成病情发展解释"
                  }}
                </button>
              </div> -->
            </div>
          </div>

          <!-- 新增的病例记录Tab内容 -->
          <div v-show="activeCard === 'caseRecords'" class="card-item">
            <CaseRecords
              :patientId="selectedPatient ? selectedPatient.id : null"
            />
          </div>

          <!-- 新增的患者数据表格Tab内容 -->
          <div v-show="activeCard === 'patientData'" class="card-item">
            <PatientDataTable
              :patientId="selectedPatient ? selectedPatient.id : null"
            />
          </div>

          <!-- 脑部CT记录Tab内容 -->
          <div v-show="activeCard === 'ct'" class="card-item ct-container">
            <BrainCTRecords
              :patientId="selectedPatient ? selectedPatient.id : null"
            />
          </div>

          <div v-show="activeCard === 'chat'" class="card-item">
            <ChatBox />
          </div>
        </div>
      </div>
    </div>
    <!-- 右边栏结束 -->
  </div>
  <div v-else>
    <UnauthorizedAccess />
  </div>
</template>

<script>
import TopNavbar from "@/components/TopNavbar.vue";
import EventTimeline from "@/components/EventTimeline.vue";
import RulesDiagram from "@/components/RulesDiagram.vue";
import PatientCard from "@/components/PatientCard.vue";
import CaseRecords from "@/components/CaseRecords.vue";
import UnauthorizedAccess from "@/components/UnauthorizedAccess.vue";
import ChatBox from "@/components/ChatBox.vue";
import BrainCTRecords from "@/components/BrainCTRecords.vue";
import PatientDataTable from "@/components/PatientDataTable.vue";
import { reactive } from "vue";
import { marked } from "marked"; // 添加这一行，引入marked库

import Axios from "@/utils/axios"; // 确保导入Axios
export default {
  components: {
    TopNavbar,
    EventTimeline,
    RulesDiagram,
    PatientCard,
    UnauthorizedAccess,
    CaseRecords,
    ChatBox,
    BrainCTRecords,
    PatientDataTable,
  },
  data() {
    return {
      qualificationStatus: "approved", //localStorage.getItem("qualificationStatus"),
      activeCard: "timeline", // 可选值：'timeline', 'rules', 'chat', 'ct', 'caseRecords'
      selectedRecordIndex: null,
      editRecord: false,
      editingRecord: null,
      caseRecords: [],
      userInput: "",
      selectedFile: null,
      uploadedImage: null, // 存储上传的图片 URL
      chatMessages: [],
      type_collapsed: false,
      searchKey: "",
      choose_type: [],
      selectedStrokeType: "",
      icuEntryTimeStart: "",
      icuEntryTimeEnd: "",
      icuExitTimeStart: "",
      icuExitTimeEnd: "",
      selectedPatient: null,
      visibleDetails: reactive({}),
      selectedRecordType: "caseRecords",
      selectedCase: null,
      ctFilter: "all",
      selectedCT: null,
      ctRecords: [],
      patients: [],
      strokeOptions: [
        { label: "缺血性脑卒中", value: "0" },
        { label: "出血性脑卒中", value: "1" },
        { label: "短暂性脑缺血发作", value: "2" },
        { label: "其他类型", value: "3" },
      ],
      showDeleteModal: false,
      showEditModal: false,
      isAddingPatient: false, // 添加这个标记，用于区分是添加还是编辑
      currentPatient: null,
      editPatient: {}, // 用于编辑的临时数据
      searchName: "", // 添加搜索名称变量
      popupVisible: false, // 添加弹窗可见性变量
      loading: false, // 添加加载状态变量
      filteredPatientsData: [], // 添加筛选后的患者数据数组
      modelExplanation: null,
      isGeneratingExplanation: false,
    };
  },
  computed: {
    // 根据 selectedStrokeType 筛选患者，若未选择则返回全部患者
    filteredPatients() {
      // 如果有筛选后的数据，优先使用筛选后的数据
      const patientsToFilter =
        this.filteredPatientsData.length > 0
          ? this.filteredPatientsData
          : this.patients;

      // 添加日志，查看筛选前的数据
      console.log("筛选前的数据:", patientsToFilter);

      // 按搜索关键字过滤
      const result = patientsToFilter.filter((p) => {
        // 忽略大小写匹配
        return p.name.toLowerCase().includes(this.searchName.toLowerCase());
      });

      // 添加日志，查看筛选后的结果
      console.log("最终显示的患者数据:", result);

      return result;
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
    renderedExplanation() {
      if (!this.modelExplanation) {
        return "";
      }
      // 将模型解释结果转换为HTML
      try {
        console.log("计算属性中的 modelExplanation:", this.modelExplanation);
        const html = marked(this.modelExplanation);
        console.log("计算属性生成的 HTML:", html);
        return html;
      } catch (error) {
        console.error("Markdown 渲染错误:", error);
        return `<p style="color: red;">Markdown 渲染错误: ${error.message}</p>`;
      }
    },
  },
  mounted() {
    // 页面加载时初始化病人信息
    this.initializePatient();

    // Initialize the first case record if available
    if (this.caseRecords && this.caseRecords.length > 0) {
      this.selectedRecordIndex = 0;
    }
    // 调用获取患者数据的方法
    this.fetchPatients();
  },
  methods: {
    // 生成模型解释
    async generateModelExplanation() {
      if (!this.selectedPatient || this.isGeneratingExplanation) {
        console.log("未选择病人或正在生成中，无法继续");
        return;
      }

      console.log("开始生成病情发展解释...");
      this.isGeneratingExplanation = true;

      try {
        // 先切换到病情发展卡片，确保它被渲染出来
        const originalCard = this.activeCard;
        console.log("当前卡片:", originalCard, "切换到病情发展卡片");
        this.activeCard = "timeline";

        // 等待DOM更新和组件渲染完成
        await this.$nextTick();
        console.log("等待组件渲染...");
        await new Promise((resolve) => setTimeout(resolve, 1500)); // 增加等待时间

        // 获取病情发展卡片元素
        console.log("尝试获取病情发展卡片元素...");
        const timelineElement = document.querySelector(".card-item");

        if (!timelineElement) {
          throw new Error("无法找到病情发展卡片元素");
        }

        console.log("找到病情发展卡片元素:", timelineElement);
        console.log(
          "元素尺寸:",
          timelineElement.offsetWidth,
          "x",
          timelineElement.offsetHeight
        );

        if (
          timelineElement.offsetWidth === 0 ||
          timelineElement.offsetHeight === 0
        ) {
          throw new Error("病情发展卡片元素尺寸为0");
        }

        // 动态导入 html2canvas
        const html2canvasModule = await import("html2canvas");
        const html2canvas = html2canvasModule.default;

        // 使用html2canvas捕获DOM元素为图片
        console.log("开始捕获图表为图片...");
        const canvas = await html2canvas(timelineElement, {
          scale: 2,
          useCORS: true,
          allowTaint: true,
          logging: true, // 启用html2canvas的日志
        });

        console.log(
          "图片捕获成功，canvas尺寸:",
          canvas.width,
          "x",
          canvas.height
        );

        // 将canvas转为blob
        const blob = await new Promise((resolve) => {
          canvas.toBlob(resolve, "image/png");
        });

        if (!blob) {
          throw new Error("图像转换为blob失败");
        }

        console.log("图像转换为blob成功，大小:", blob.size, "字节");

        // 准备发送到后端的数据
        const formData = new FormData();
        formData.append("image", blob, "timeline.png");
        formData.append(
          "question",
          "请你根据该图撰写一段综合性临床报告摘要，说明患者的症状演变、预测预警及相应干预建议，便于多学科会诊时使用"
        );

        // 发送请求到后端
        console.log("发送请求到后端...");
        const response = await Axios.post("/llm/multimodal", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
          timeout: 60000,
        });

        console.log("收到后端响应:", response);

        // 切换回模型解释卡片
        this.activeCard = "rules";

        // 显示返回的结果
        console.log("原始响应数据:", response.data.result);
        this.modelExplanation = response.data.result;
        console.log("设置的 modelExplanation:", this.modelExplanation);
        console.log("渲染后的 HTML:", marked(this.modelExplanation));
      } catch (error) {
        console.error("生成病情发展解释失败:", error);

        let errorMessage = "未知错误";
        if (error.response) {
          console.error(
            "服务器响应错误:",
            error.response.status,
            error.response.data
          );
          errorMessage = `服务器错误 (${error.response.status}): ${
            error.response.data.error || "请检查服务器日志"
          }`;
        } else if (error.request) {
          console.error("服务器未响应:", error.request);
          errorMessage = "服务器未响应，请检查后端服务是否正常运行";
        } else {
          console.error("请求错误:", error.message);
          errorMessage = `请求错误: ${error.message}`;
        }

        // 显示错误信息
        alert(`生成病情发展解释失败: ${errorMessage}`);
        this.modelExplanation = `<p class="error-message">生成病情发展解释失败: ${errorMessage}</p>`;
      } finally {
        this.isGeneratingExplanation = false;
      }
    },
    // 解析Markdown文本为HTML
    parseMarkdown(text) {
      // 如果已经引入了marked库
      if (window.marked) {
        return window.marked(text || "");
      }
      // 如果没有引入marked库，可以使用简单的替换
      return (text || "")
        .replace(/\n/g, "<br>")
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/\*(.*?)\*/g, "<em>$1</em>");
    },
    handleSelect(patient) {
      console.log("选中病人:", patient);

      // 先清空选中状态，确保触发变化
      this.selectedPatient = null;
      this.activeCard = "timeline";

      // 使用 nextTick 确保 DOM 更新后再设置新的选中病人
      this.$nextTick(() => {
        // 设置当前选中病人
        this.selectedPatient = patient;
        // 设置该病人的详情为可见
        this.visibleDetails = { [patient.id]: true };

        console.log("当前选中病人ID:", this.selectedPatient.id);
      });
    },
    async fetchPatients() {
      try {
        // 获取 token（假设已经存储在 localStorage 中）
        const token = localStorage.getItem("token");

        // 发送请求获取患者数据
        const response = await Axios.get("/patient/details", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        // 检查响应数据
        if (response.data && Array.isArray(response.data)) {
          // 将后端返回的数据格式转换为组件需要的格式
          this.patients = response.data.map((patient) => ({
            id: patient.id || Math.random(), // 如果后端没有返回id，生成一个随机id
            name: patient.name,
            age: patient.age,
            gender: patient.gender || "未知", // 后端可能没有返回性别
            heartDiseaseHistory: patient.heart_history || "无",
            diabetesHistory: patient.diabete_history || "无",
            hypertensionHistory: patient.EH_history || "无",
            otherHistory: patient.other_history || "无",
            strokeType: patient.status || "未知",
            ICUAdmissionTime: patient.in_icu
              ? patient.in_icu.substring(0, 16)
              : null,
            ICUDischargeTime: patient.out_icu
              ? patient.out_icu.substring(0, 16)
              : null,
            events: patient.events || [],
            event_codes: patient.event_codes || [],
            avatar: patient.avatar,
          }));

          console.log("成功获取患者数据:", this.patients);
        } else {
          console.error("患者数据格式不正确:", response.data);
          // 如果数据格式不正确，可以使用默认数据
          this.setDefaultPatients();
        }
      } catch (error) {
        console.error("获取患者数据失败:", error);
        // 如果API请求失败，使用默认数据
        this.setDefaultPatients();
      }
    },

    // 设置默认的患者数据（作为备用）
    setDefaultPatients() {
      this.patients = [
        {
          id: 1,
          name: "张三",
          age: 60,
          gender: "男",
          heartDiseaseHistory: "无",
          diabetesHistory: "有",
          hypertensionHistory: "有",
          otherHistory: "无",
          strokeType: "缺血性",
          ICUAdmissionTime: "2025-03-15T08:00",
          ICUDischargeTime: "2025-03-20T16:00",
        },
        {
          id: 2,
          name: "李四",
          age: 65,
          gender: "女",
          heartDiseaseHistory: "有",
          diabetesHistory: "无",
          hypertensionHistory: "有",
          otherHistory: "哮喘",
          strokeType: "出血性",
          ICUAdmissionTime: "2025-03-10T09:30",
          ICUDischargeTime: "2025-03-18T14:30",
        },
      ];
    },
    // 添加缺失的handleSearch方法
    handleSearch() {
      // 简单的搜索实现，可以根据需要扩展
      console.log("搜索关键词:", this.searchName);
      // 搜索逻辑已在computed.filteredPatients中实现
    },
    confirmPatientSelection() {
      this.selectedPatients = this.patients.filter((p) => p.isSelected); // 更新选中的病人列表
      console.log("已选择的病人:", this.selectedPatients);
      this.showModal = false; // 关闭弹窗
    },
    // 重置筛选器的逻辑
    async applyFilters() {
      try {
        this.loading = true;

        // 准备请求数据
        const filterData = {
          status: this.choose_type, // 已经是 label 列表了
        };

        // 添加 ICU 入院时间范围（如果有设置）
        if (this.icuEntryDateRange && this.icuEntryDateRange.length === 2) {
          // 设置开始时间
          filterData.in_icu_start = this.formatDateTime(
            this.icuEntryDateRange[0],
            true
          );
          // 设置结束时间
          filterData.in_icu_end = this.formatDateTime(
            this.icuEntryDateRange[1],
            false
          );
        }

        // 添加 ICU 出院时间范围（如果有设置）
        if (this.icuExitDateRange && this.icuExitDateRange.length === 2) {
          // 设置开始时间
          filterData.out_icu_start = this.formatDateTime(
            this.icuExitDateRange[0],
            true
          );
          // 设置结束时间
          filterData.out_icu_end = this.formatDateTime(
            this.icuExitDateRange[1],
            false
          );
        }

        // 获取 token（假设已存储在 localStorage 中）
        const token = localStorage.getItem("token");

        console.log("发送筛选请求数据:", filterData);

        // 发送筛选请求
        const response = await Axios.post("/patient/filter", filterData, {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        });

        console.log("筛选结果:", response.data);

        // 处理返回的患者数据，转换为组件需要的格式
        if (response.data !== undefined) {
          // 即使是空数组也要设置，确保视图更新
          this.filteredPatientsData = Array.isArray(response.data)
            ? response.data.map((patient) => {
                // 完整映射所有必要的字段
                return {
                  id: patient.id || Math.random(), // 如果后端没有返回id，生成一个随机id
                  name: patient.name || "未知姓名",
                  age: patient.age || 0,
                  gender: patient.gender || "未知",
                  heartDiseaseHistory: patient.heart_history || "无",
                  diabetesHistory: patient.diabete_history || "无",
                  hypertensionHistory: patient.EH_history || "无",
                  otherHistory: patient.other_history || "无",
                  strokeType: patient.status || "未知",
                  ICUAdmissionTime: patient.in_icu
                    ? patient.in_icu.substring(0, 16)
                    : null,
                  ICUDischargeTime: patient.out_icu
                    ? patient.out_icu.substring(0, 16)
                    : null,
                  events: patient.events || [],
                  event_codes: patient.event_codes || [],
                  avatar:
                    patient.avatar ||
                    `https://picsum.photos/seed/patient${
                      patient.id || Math.random()
                    }/200/200`,
                };
              })
            : [];

          // 添加日志，查看处理后的数据
          console.log("处理后的筛选数据:", this.filteredPatientsData);

          // 如果筛选结果为空，可以显示一个提示
          if (this.filteredPatientsData.length === 0) {
            console.log("筛选结果为空，没有匹配的患者");
          }
        }
      } catch (error) {
        console.error("筛选患者数据失败:", error);
        // 可以添加错误处理逻辑，例如显示错误消息
      } finally {
        this.loading = false;
        this.popupVisible = false; // 关闭弹窗
      }
    },

    // 修改：重置筛选器的逻辑，同时清空筛选结果
    resetFilters() {
      this.choose_type = [];
      this.icuEntryDateRange = null;
      this.icuExitDateRange = null;
      this.filteredPatientsData = []; // 清空筛选结果，恢复使用 props 传入的数据
    },

    // 新增：格式化日期时间为后端需要的格式
    formatDateTime(date, isStartOfDay) {
      if (!date) return null;

      // 创建日期对象
      const dateObj = new Date(date);

      // 设置时间为当天的开始或结束
      if (isStartOfDay) {
        dateObj.setHours(0, 0, 0, 0);
      } else {
        dateObj.setHours(23, 59, 59, 999);
      }

      // 格式化为 YYYY-MM-DD HH:MM:SS
      const year = dateObj.getFullYear();
      const month = String(dateObj.getMonth() + 1).padStart(2, "0");
      const day = String(dateObj.getDate()).padStart(2, "0");
      const hours = String(dateObj.getHours()).padStart(2, "0");
      const minutes = String(dateObj.getMinutes()).padStart(2, "0");
      const seconds = String(dateObj.getSeconds()).padStart(2, "0");

      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
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

    // 删除操作
    confirmDelete(patient) {
      this.currentPatient = patient;
      this.showDeleteModal = true;
    },
    async deletePatient() {
      try {
        // 获取 token
        const token = localStorage.getItem("token");

        // 调用后端删除接口
        const response = await Axios.delete(
          `/patient/delete/${this.currentPatient.id}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        console.log("删除患者成功:", response.data);

        // 删除成功后，从前端列表中移除该患者
        this.patients = this.patients.filter(
          (p) => p.id !== this.currentPatient.id
        );

        // 关闭删除确认弹窗
        this.closeDeleteModal();

        // 可以添加成功提示
        this.$message && this.$message.success("删除患者成功");
      } catch (error) {
        console.error("删除患者失败:", error);

        // 显示错误提示
        this.$message &&
          this.$message.error(
            `删除患者失败: ${error.response?.data?.error || error.message}`
          );
      }
    },
    closeDeleteModal() {
      this.showDeleteModal = false;
      this.currentPatient = null;
    },
    openAddModal() {
      this.isAddingPatient = true;
      // 创建一个空的病人对象
      this.editPatient = {
        id: this.generateNewId(),
        name: "",
        age: "",
        gender: "",
        heartDiseaseHistory: "无",
        diabetesHistory: "无",
        hypertensionHistory: "无",
        otherHistory: "无",
        strokeType: "",
        ICUAdmissionTime: "",
        ICUDischargeTime: "",
      };
      this.showEditModal = true;
    },

    // 打开编辑病人弹窗
    openEditModal(patient) {
      this.isAddingPatient = false;
      this.currentPatient = patient;
      // 深拷贝病人数据，防止直接修改原数据
      this.editPatient = JSON.parse(JSON.stringify(patient));
      this.showEditModal = true;
    },

    // 提交编辑或添加
    async submitEdit() {
      try {
        // 获取 token
        const token = localStorage.getItem("token");

        if (this.isAddingPatient) {
          // 添加新患者
          // 准备请求数据
          const patientData = {
            name: this.editPatient.name,
            gender: this.editPatient.gender,
            age: parseInt(this.editPatient.age),
            heart_history: this.editPatient.heartDiseaseHistory || "无",
            diabete_history: this.editPatient.diabetesHistory || "无",
            Eh_history: this.editPatient.hypertensionHistory || "无",
            other_history: this.editPatient.otherHistory || "无",
            status: this.editPatient.strokeType,
            desease: "脑卒中", // 默认疾病名称，可以根据需要修改
            in_icu: this.formatDateTimeForBackend(
              this.editPatient.ICUAdmissionTime
            ),
            out_icu: this.formatDateTimeForBackend(
              this.editPatient.ICUDischargeTime
            ),
          };

          console.log("发送添加患者请求:", patientData);

          // 发送添加患者请求
          const response = await Axios.post("/patient/add", patientData, {
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
          });

          console.log("添加患者成功:", response.data);

          // 添加成功后刷新患者列表
          this.fetchPatients();
          this.closeEditModal();

          // 显示成功提示
          this.$message.success("添加患者成功");
        } else {
          // 修改现有患者
          // 准备请求数据
          const patientData = {
            name: this.editPatient.name,
            gender: this.editPatient.gender,
            age: parseInt(this.editPatient.age),
            heart_history: this.editPatient.heartDiseaseHistory || "无",
            diabete_history: this.editPatient.diabetesHistory || "无",
            Eh_history: this.editPatient.hypertensionHistory || "无",
            other_history: this.editPatient.otherHistory || "无",
            status: this.editPatient.strokeType,
            in_icu: this.formatDateTimeForBackend(
              this.editPatient.ICUAdmissionTime
            ),
            out_icu: this.formatDateTimeForBackend(
              this.editPatient.ICUDischargeTime
            ),
          };

          console.log("发送修改患者请求:", patientData);

          // 发送修改患者请求
          const response = await Axios.put(
            `/patient/update/${this.editPatient.id}`,
            patientData,
            {
              headers: {
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json",
              },
            }
          );

          console.log("修改患者成功:", response.data);

          // 修改成功后刷新患者列表
          this.fetchPatients();
          this.closeEditModal();

          // 显示成功提示
          this.$message.success("修改患者信息成功");
        }
      } catch (error) {
        console.error("操作失败:", error);
        // 显示错误提示
        this.$message.error(
          `操作失败: ${error.response?.data?.error || error.message}`
        );
      }
    },
    // 添加一个辅助方法，用于格式化日期时间为后端需要的格式
    formatDateTimeForBackend(dateTimeString) {
      if (!dateTimeString) return null;

      // 将 "2025-03-15T08:00" 格式转换为 "2025-03-15 08:00:00" 格式
      const date = new Date(dateTimeString);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, "0");
      const day = String(date.getDate()).padStart(2, "0");
      const hours = String(date.getHours()).padStart(2, "0");
      const minutes = String(date.getMinutes()).padStart(2, "0");

      return `${year}-${month}-${day} ${hours}:${minutes}:00`;
    },
    // 关闭编辑弹窗
    closeEditModal() {
      this.showEditModal = false;
      this.currentPatient = null;
      this.editPatient = {};
      this.isAddingPatient = false;
    },
    generateNewId() {
      // 找出当前最大ID，然后+1
      const maxId = Math.max(...this.patients.map((p) => p.id), 0);
      return maxId + 1;
    },
    // 发送消息
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

        // 清空所有病人的可见状态
        for (let id in this.visibleDetails) {
          this.visibleDetails[id] = false;
        }

        // 设置第一个病人为选中状态
        this.selectedPatient = firstPatient;
        this.visibleDetails[firstPatient.id] = true; // 显示第一个病人的详细信息
      }
    },
    toggleDetails(patientId) {
      // 清空所有病人的可见状态
      for (let id in this.visibleDetails) {
        this.visibleDetails[id] = false;
      }

      // 设置当前选中病人的详情为可见
      this.visibleDetails[patientId] = true;

      // 选择病人并显示右边栏信息
      this.selectedPatient = this.filteredPatients.find(
        (patient) => patient.id === patientId
      );

      if (this.selectedPatient) {
        this.icuEntryDate = this.selectedPatient.ICUAdmissionTime;
        this.icuExitDate = this.selectedPatient.ICUDischargeTime;
      }
    },
    isDetailsVisible(patientId) {
      return !!this.visibleDetails[patientId];
    },
    // 在 methods 部分添加或修改 handleSelect 方法
    selectCT(ct) {
      this.selectedCT = ct;
    },
  },
};
</script>

<style scoped>
.analysis-page {
  display: flex;
  height: 88vh;
  margin-top: 8px;
  justify-content: space-between;
  color: #0f0f10;
  padding: 0 8px;
}

/* 左边列样式 */
.left-column {
  width: 20%;
  padding: 5px;
  height: 100%;
  overflow: hidden;
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
/* 搜索 & 筛选栏 */
.search-filter-bar {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  /* 可根据需要加上背景或边框 */
}
.icon-search {
  /* 替换成你自己使用的图标库样式或SVG */
  width: 16px;
  height: 16px;
  background: url("data:image/svg+xml;base64,...") no-repeat center / cover;
  margin-right: 6px;
  cursor: pointer;
}
.search-input {
  flex: 1;
  padding: 4px 8px;
  font-size: 14px;
  margin-right: 6px;
}
.icon-filter {
  /* 替换成你自己使用的图标库样式或SVG */
  width: 16px;
  height: 16px;
  background: url("data:image/svg+xml;base64,...") no-repeat center / cover;
  cursor: pointer;
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
  background-color: #e5eafc;
  font-family: Arial, sans-serif;
  border-radius: 12px;
  padding: 15px;
  height: calc(100% - 80px);
  max-width: 300px;
  margin: 0 -3px;
  color: #0e0f0f;
  overflow-x: hidden;
  overflow-y: auto;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.patients-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e9ecef;
}

.patients-header h3 {
  margin: 0;
  color: #2d5bff;
  font-size: 18px;
  font-weight: 600;
}

.add-patient-btn {
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

.add-patient-btn:hover {
  background-color: #1a46e0;
}

/* 左边列样式结束 */
.right-column {
  width: 80%;
  padding: 5px;
  height: 100%;
  overflow: hidden;
}

.patient-info-container {
  flex: 1;
  padding: 0;
  display: flex;
  height: 17%;
  border-radius: 12px;
  background: #ffffff;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  margin-bottom: 15px;
}

.patient-info-card {
  display: flex;
  width: 100%;
  height: 100%;
}

/* 左侧：病人基本信息 */
.patient-basic-info {
  width: 25%;
  padding: 15px;
  display: flex;
  align-items: center;
  border-right: 1px solid #f0f0f0;
}

.patient-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2d5bff, #7597ff);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  box-shadow: 0 4px 10px rgba(45, 91, 255, 0.3);
}

.patient-avatar span {
  color: white;
  font-size: 24px;
  font-weight: bold;
}

.patient-header {
  display: flex;
  flex-direction: column;
}

.patient-header h2 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.patient-badges {
  display: flex;
  gap: 8px;
}

.badge {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.gender-badge {
  background-color: #e7f5ff;
  color: #1c7ed6;
}

.age-badge {
  background-color: #fff3bf;
  color: #e67700;
}

/* 中间：住院信息 */
.patient-hospital-info {
  width: 35%;
  padding: 15px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  border-right: 1px solid #f0f0f0;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.info-item i {
  font-size: 18px;
  color: #2d5bff;
  margin-right: 12px;
  width: 20px;
  text-align: center;
}

.info-content {
  display: flex;
  flex-direction: column;
}

.info-label {
  font-size: 12px;
  color: #6c757d;
  margin-bottom: 2px;
}

.info-value {
  font-size: 14px;
  font-weight: 500;
  color: #343a40;
}

.stroke-type {
  color: #e03131;
  font-weight: 600;
}

/* 右侧：病史信息 */
.patient-medical-history {
  flex: 1;
  padding: 15px;
  display: flex;
  flex-direction: column;
}

.patient-medical-history h3 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.disease-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.disease-tag {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  display: flex;
  align-items: center;
  transition: transform 0.2s ease;
}

.disease-tag i {
  margin-right: 6px;
}

.disease-tag:hover {
  transform: translateY(-2px);
}

.heart-tag {
  background-color: #ffe3e3;
  color: #e03131;
}

.diabetes-tag {
  background-color: #e3fafc;
  color: #0c8599;
}

.hypertension-tag {
  background-color: #e5dbff;
  color: #6741d9;
}

.other-tag {
  background-color: #f1f3f5;
  color: #495057;
}

.no-history {
  background-color: #ebfbee;
  color: #2b8a3e;
}

/* 无病人信息时的占位样式 */
.patient-info-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #adb5bd;
}

.patient-info-placeholder i {
  font-size: 40px;
  margin-bottom: 10px;
}

.patient-info-placeholder p {
  font-size: 15px;
}

/* 堆叠卡片容器样式 */
.card-container {
  margin-top: 20px;
  border: none;
  border-radius: 16px;
  background: #fff;
  height: 90%;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.card-tabs {
  display: flex;
  background: linear-gradient(to right, #e5eafc, #f0f3ff);
  padding: 18px 20px 0;
  border-bottom: 2px solid rgba(45, 91, 255, 0.1);
  border-radius: 12px 12px 0 0;
  position: relative;
  box-shadow: 0 -4px 12px rgba(45, 91, 255, 0.05);

  /* 添加内部光晕效果 */
  &::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(
      to bottom,
      rgba(255, 255, 255, 0.2),
      transparent
    );
    border-radius: 12px 12px 0 0;
    pointer-events: none;
  }
}

.tab-btn {
  padding: 12px 24px;
  border: none;
  background: none;
  cursor: pointer;
  margin-right: 8px;
  border-radius: 10px 10px 0 0;
  transition: all 0.3s ease;
  color: #6c757d;
  font-weight: 500;
  font-size: 15px;
}

.tab-btn.active {
  background: #fff;
  color: #2d5bff;
  border: 1px solid #e9ecef;
  border-bottom: none;
  box-shadow: 0 -4px 10px rgba(0, 0, 0, 0.03);
}

.tab-btn:hover:not(.active) {
  color: #2d5bff;
  background: rgba(45, 91, 255, 0.05);
}

.card-content {
  height: 80%;
  overflow: hidden;
  position: relative;
}

.card-item {
  padding: 25px;
  height: 100%;
  position: absolute;
  width: 100%;
  top: 0;
  left: 0;
  box-sizing: border-box;
  overflow-y: auto;
}

/* 美化规则容器 */
.rules-container {
  display: flex;
  gap: 25px;
  height: 100%;
  padding: 25px;
}

.rules-part {
  flex: 1;
  height: 100%;
  border-radius: 12px;
  background: #f8f9fa;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
  position: relative;
}

.rules-part h3 {
  margin: 0 0 20px 0;
  color: #2d5bff;
  font-size: 18px;
  font-weight: 600;
}

.case-records {
  height: calc(100% - 40px);
  overflow-y: auto;
  padding-right: 5px;
}

.case-record-item {
  background: white;
  border-radius: 10px;
  padding: 18px;
  margin-bottom: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  border-left: 3px solid transparent;
}

.case-record-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.08);
  border-left: 3px solid #2d5bff;
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

.record-number {
  color: #2d5bff;
  font-weight: 600;
}

.record-date {
  color: #666;
  font-size: 0.9em;
}

.record-body {
  color: #333;
}

.record-location {
  font-weight: 500;
  margin-bottom: 5px;
}

.record-details {
  color: #666;
  font-size: 0.95em;
  line-height: 1.5;
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

/* 美化滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 4px;
  transition: all 0.3s ease;
}

::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

/* 针对特定容器的滚动条样式 */
.patients-list::-webkit-scrollbar,
.record-list::-webkit-scrollbar,
.card-content::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.patients-list::-webkit-scrollbar-thumb,
.record-list::-webkit-scrollbar-thumb,
.card-content::-webkit-scrollbar-thumb {
  background: #2d5bff40;
}

.patients-list::-webkit-scrollbar-thumb:hover,
.record-list::-webkit-scrollbar-thumb:hover,
.card-content::-webkit-scrollbar-thumb:hover {
  background: #2d5bff80;
}

/* 添加模型解释按钮样式 */
.analysis-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background-color: #2d5bff;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 10px 16px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.analysis-btn:hover {
  background-color: #2d5bff;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.analysis-btn:disabled {
  background-color: #bfbfbf;
  cursor: not-allowed;
  box-shadow: none;
}

.model-explanation {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 16px;
  margin-top: 16px;
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #eaeaea;
}

/* Markdown 渲染样式 */
.model-explanation :deep(h1),
.model-explanation :deep(h2),
.model-explanation :deep(h3),
.model-explanation :deep(h4),
.model-explanation :deep(h5),
.model-explanation :deep(h6) {
  margin-top: 16px;
  margin-bottom: 8px;
  color: #333;
}

.model-explanation :deep(p) {
  margin-bottom: 12px;
  line-height: 1.6;
}

.model-explanation :deep(ul),
.model-explanation :deep(ol) {
  margin-bottom: 12px;
  padding-left: 24px;
}

.model-explanation :deep(li) {
  margin-bottom: 4px;
}

.model-explanation :deep(code) {
  background-color: #f0f0f0;
  padding: 2px 4px;
  border-radius: 4px;
  font-family: monospace;
}

.model-explanation :deep(pre) {
  background-color: #f0f0f0;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
  margin-bottom: 12px;
}

.model-explanation :deep(blockquote) {
  border-left: 4px solid #ddd;
  padding-left: 16px;
  margin-left: 0;
  margin-right: 0;
  color: #666;
}

.model-explanation :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin-bottom: 12px;
}

.model-explanation :deep(th),
.model-explanation :deep(td) {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

.model-explanation :deep(th) {
  background-color: #f2f2f2;
}

.model-explanation-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px;
  background-color: #f9f9f9;
  border-radius: 8px;
  margin-top: 16px;
  border: 1px dashed #d9d9d9;
}

.model-explanation-placeholder p {
  margin-bottom: 16px;
  color: #666;
}
</style>
