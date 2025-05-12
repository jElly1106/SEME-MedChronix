<template>
  <div class="ct-container">
    <div class="ct-left">
      <div class="ct-header">
        <h3>脑部CT记录</h3>
        <div class="ct-actions">
          <button class="ct-add-btn" @click="showAddCTDialog">
            <i class="fa fa-plus"></i> 新增CT
          </button>
          <div class="ct-filter">
            <select v-model="ctFilter" class="ct-select">
              <option value="all">全部记录</option>
              <option value="normal">正常</option>
              <option value="abnormal">异常</option>
            </select>
          </div>
        </div>
      </div>
      <div class="ct-list">
        <div
          v-for="ct in filteredCTRecords"
          :key="ct.id"
          class="ct-list-item"
          :class="{ active: selectedCT && selectedCT.id === ct.id }"
        >
          <div class="ct-list-content" @click="selectCT(ct)">
            <div class="ct-list-date">{{ formatDate(ct.diagnosis_date) }}</div>
            <div class="ct-list-id">ID: {{ ct.id }}</div>
            <div
              :class="[
                'ct-list-status',
                ct.status === 'abnormal' ? 'abnormal' : 'normal',
              ]"
            >
              {{ ct.status === "abnormal" ? "异常" : "正常" }}
            </div>
          </div>
          <div class="ct-list-actions">
            <button class="ct-delete-btn" @click.stop="confirmDeleteCT(ct)">
              <i class="fa fa-trash"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="ct-right">
      <div v-if="selectedCT" class="ct-detail">
        <div class="ct-detail-header">
          <h3>CT详情 ({{ formatDate(selectedCT.diagnosis_date) }})</h3>
          <div
            :class="[
              'ct-detail-status',
              selectedCT.status === 'abnormal' ? 'abnormal' : 'normal',
            ]"
          >
            {{ selectedCT.status === "abnormal" ? "异常" : "正常" }}
          </div>
        </div>

        <div class="ct-content-scroll">
          <div class="ct-image-container">
            <img
              :src="selectedCT.image_url"
              alt="CT扫描图像"
              class="ct-detail-image"
              @error="handleImageError"
            />
          </div>

          <div class="ct-ai-diagnosis">
            <div class="diagnosis-header">
              <h4>AI诊断结果</h4>
              <span class="diagnosis-date">{{
                formatDateTime(selectedCT.diagnosis_date)
              }}</span>
            </div>
            <div class="diagnosis-content">
              <div v-if="selectedCT.ai_diagnosis" v-html="renderedDiagnosis"></div>
              <p v-else>暂无AI诊断结果</p>
              <button
                v-if="!selectedCT.ai_diagnosis && !isAnalyzing"
                class="ct-ai-analyze-btn"
                @click="requestAIDiagnosis"
              >
                获取AI诊断
              </button>
              <div v-if="isAnalyzing" class="analyzing-indicator">
                <div class="spinner"></div>
                <span>AI正在分析图像...</span>
              </div>
            </div>
          </div>
        </div>
      </div>


      <div v-else class="ct-placeholder">
        <div class="placeholder-icon">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="64"
            height="64"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path
              d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
            ></path>
            <circle cx="12" cy="14" r="4"></circle>
            <path d="M14 2v4h4"></path>
          </svg>
        </div>
        <p>请从左侧选择一个CT记录查看详情</p>
      </div>
    </div>
  </div>

  <!-- 新增CT记录弹窗 -->
  <div v-if="showAddDialog" class="ct-dialog-overlay">
    <div class="ct-dialog">
      <div class="ct-dialog-header">
        <h3>新增CT记录</h3>
        <button class="ct-dialog-close" @click="closeAddCTDialog">
          &times;
        </button>
      </div>
      <div class="ct-dialog-body">
        <form @submit.prevent="submitAddCT" class="ct-form">
          <div class="ct-form-group">
            <label>诊断日期</label>
            <input
              type="datetime-local"
              v-model="newCT.diagnosis_date"
              required
              class="ct-input"
            />
          </div>
          <div class="ct-form-group">
            <label>状态</label>
            <select v-model="newCT.status" required class="ct-input">
              <option value="normal">正常</option>
              <option value="abnormal">异常</option>
            </select>
          </div>
          <div class="ct-form-group">
            <label>CT扫描图像</label>
            <input
              type="file"
              @change="handleFileUpload"
              accept="image/*"
              required
              class="ct-input"
            />
          </div>
          <div class="ct-form-actions">
            <button
              type="button"
              class="ct-btn-cancel"
              @click="closeAddCTDialog"
            >
              取消
            </button>
            <button
              type="submit"
              class="ct-btn-submit"
              :disabled="isSubmitting"
            >
              {{ isSubmitting ? "提交中..." : "提交" }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>

  <!-- 删除确认弹窗 -->
  <div v-if="showDeleteConfirm" class="ct-dialog-overlay">
    <div class="ct-dialog ct-dialog-confirm">
      <div class="ct-dialog-header">
        <h3>确认删除</h3>
        <button class="ct-dialog-close" @click="cancelDelete">&times;</button>
      </div>
      <div class="ct-dialog-body">
        <p>确定要删除这条CT记录吗？此操作不可恢复。</p>
        <div class="ct-form-actions">
          <button class="ct-btn-cancel" @click="cancelDelete">取消</button>
          <button
            class="ct-btn-delete"
            @click="deleteCT"
            :disabled="isDeleting"
          >
            {{ isDeleting ? "删除中..." : "确认删除" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Axios from "@/utils/axios";
import { marked } from 'marked'; // 添加这一行，引入marked库

export default {
  name: "BrainCTRecords",
  props: {
    patientId: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      ctFilter: "all",
      selectedCT: null,
      ctRecords: [],
      imageError: false,
      showAddDialog: false,
      showDeleteConfirm: false,
      ctToDelete: null,
      isSubmitting: false,
      isDeleting: false,
      isAnalyzing: false,
      newCT: {
        diagnosis_date: "",
        status: "normal",
        ai_diagnosis: "",
        ct_image: null,
      },
    };
  },
  computed: {
    filteredCTRecords() {
      if (this.ctFilter === "all") {
        return this.ctRecords;
      }
      return this.ctRecords.filter((ct) =>
        this.ctFilter === "normal"
          ? ct.status === "normal"
          : ct.status === "abnormal"
      );
    },
    // 添加这个计算属性，用于渲染Markdown
    renderedDiagnosis() {
      if (!this.selectedCT || !this.selectedCT.ai_diagnosis) {
        return '';
      }
      // 将AI诊断结果转换为HTML
      return marked(this.selectedCT.ai_diagnosis);
    }
  },
  methods: {
    async fetchCTRecords() {
      try {
        this.selectedCT = null;
        const response = await Axios.get(
          `/ct/ct_scans/patient/${this.patientId}`
        );
        console.log("CT记录:", response.data);
        if (response.status === 200) {
          this.ctRecords = response.data.data || [];
          // 默认选中第一条记录
          if (this.ctRecords.length > 0) {
            this.selectCT(this.ctRecords[0]);
            this.$message.success("CT记录加载成功");
          }
        } else {
          console.error("获取CT记录失败:", response.data.message);
        }
      } catch (error) {
        console.error(
          "获取CT记录失败:",
          error.response?.data?.message || error.message
        );
      }
    },
    selectCT(ct) {
      this.selectedCT = JSON.parse(JSON.stringify(ct)); // 创建深拷贝
      this.imageError = false;
      // 向父组件发送选中的CT记录
      this.$emit("ct-selected", ct);
      
      // 先尝试从后端获取诊断结果
      this.fetchCTDiagnosis(ct.id);
    },
    
    // 添加新方法：从后端获取CT诊断结果
    async fetchCTDiagnosis(ctId) {
      try {
        // 显示加载状态
        this.isAnalyzing = true;
        
        // 从后端获取诊断结果
        const response = await Axios.get(`/ct/ct_scans/${ctId}/diagnosis`);
        
        if (response.status === 200) {
          if (response.data.has_diagnosis && response.data.data.ai_diagnosis) {
            // 如果后端已有诊断结果，直接更新本地数据
            this.selectedCT.ai_diagnosis = response.data.data.ai_diagnosis;
            
            // 更新列表中的记录
            const index = this.ctRecords.findIndex(ct => ct.id === ctId);
            if (index !== -1) {
              this.ctRecords[index].ai_diagnosis = response.data.data.ai_diagnosis;
            }
            
            console.log("从后端获取到AI诊断结果");
          } else {
            // 如果后端没有诊断结果，请求大模型分析
            console.log("后端无诊断结果，请求大模型分析");
            await this.requestAIDiagnosis();
          }
        } else {
          // 如果获取失败，尝试请求大模型分析
          console.error("获取诊断结果失败:", response.data.message);
          await this.requestAIDiagnosis();
        }
      } catch (error) {
        console.error("获取诊断结果失败:", error);
        // 如果获取失败，尝试请求大模型分析
        await this.requestAIDiagnosis();
      } finally {
        this.isAnalyzing = false;
      }
    },
    formatDate(dateString) {
      if (!dateString) return "未知日期";
      const date = new Date(dateString);
      date.setHours(date.getHours());
      return new Intl.DateTimeFormat("zh-CN", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        timeZone: "Asia/Shanghai", // 使用中国时区
      }).format(date);
    },
    formatDateTime(dateString) {
      if (!dateString) return "未知时间";
      const date = new Date(dateString);
      date.setHours(date.getHours());
      return new Intl.DateTimeFormat("zh-CN", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        timeZone: "Asia/Shanghai", // 使用中国时区
      }).format(date);
    },
    handleImageError() {
      this.imageError = true;
    },
    // 显示新增CT记录弹窗
    showAddCTDialog() {
      this.showAddDialog = true;
      // 重置表单
      // 创建当前日期对象
      const now = new Date();
      // 格式化为本地时间的YYYY-MM-DDThh:mm格式（datetime-local输入框需要的格式）
      const year = now.getFullYear();
      const month = String(now.getMonth() + 1).padStart(2, "0");
      const day = String(now.getDate()).padStart(2, "0");
      const hours = String(now.getHours()).padStart(2, "0");
      const minutes = String(now.getMinutes()).padStart(2, "0");

      this.newCT = {
        diagnosis_date: `${year}-${month}-${day}T${hours}:${minutes}`,
        status: "normal",
        ai_diagnosis: "",
        ct_image: null,
      };
    },
    // 关闭新增CT记录弹窗
    closeAddCTDialog() {
      this.showAddDialog = false;
    },
    // 处理文件上传
    handleFileUpload(event) {
      this.newCT.ct_image = event.target.files[0];
    },
    // 提交新增CT记录
    async submitAddCT() {
      if (!this.newCT.ct_image) {
        this.$message.error("请选择CT扫描图像");
        return;
      }

      try {
        this.isSubmitting = true;

        // 创建FormData对象
        const formData = new FormData();
        formData.append("patient_id", this.patientId);
        // 创建日期对象并转换为本地时间的ISO字符串
        const diagnosisDate = new Date(this.newCT.diagnosis_date);
        // 获取本地时区的日期时间字符串，添加8小时修正时区差异
        diagnosisDate.setHours(diagnosisDate.getHours() + 8);
        const localISOString = diagnosisDate
          .toISOString()
          .replace("T", " ")
          .slice(0, 19);
        formData.append("diagnosis_date", localISOString);
        if (this.newCT.status === "normal") {
          formData.append("status", "正常");
        } else if (this.newCT.status === "abnormal") {
          formData.append("status", "异常");
        }
        formData.append("ai_diagnosis", this.newCT.ai_diagnosis);
        formData.append("ct_image", this.newCT.ct_image);

        // 发送请求
        const response = await Axios.post("/ct/ct_scans", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });

        if (response.status === 201) {
          this.$message.success("CT记录添加成功");
          this.closeAddCTDialog();
          // 重新获取CT记录列表
          this.fetchCTRecords();
        } else {
          this.$message.error(response.data.message || "添加CT记录失败");
        }
      } catch (error) {
        this.$message.error(error.response?.data?.message || "添加CT记录失败");
        console.error("添加CT记录失败:", error);
      } finally {
        this.isSubmitting = false;
      }
    },
    // 确认删除CT记录
    confirmDeleteCT(ct) {
      this.ctToDelete = ct;
      this.showDeleteConfirm = true;
    },
    // 取消删除
    cancelDelete() {
      this.showDeleteConfirm = false;
      this.ctToDelete = null;
    },
    // 删除CT记录
    async deleteCT() {
      if (!this.ctToDelete) return;

      try {
        this.isDeleting = true;
        const response = await Axios.delete(
          `/ct/ct_scans/${this.ctToDelete.id}`
        );

        if (response.status === 200) {
          this.$message.success("CT记录删除成功");

          // 如果删除的是当前选中的记录，清空选中状态
          if (this.selectedCT && this.selectedCT.id === this.ctToDelete.id) {
            this.selectedCT = null;
          }

          // 从列表中移除该记录
          this.ctRecords = this.ctRecords.filter(
            (ct) => ct.id !== this.ctToDelete.id
          );

          // 如果还有记录，选中第一条
          if (this.ctRecords.length > 0 && !this.selectedCT) {
            this.selectCT(this.ctRecords[0]);
          }

          this.cancelDelete();
        } else {
          this.$message.error(response.data.message || "删除CT记录失败");
        }
      } catch (error) {
        this.$message.error(error.response?.data?.message || "删除CT记录失败");
        console.error("删除CT记录失败:", error);
      } finally {
        this.isDeleting = false;
      }
    },
    // 请求AI诊断 TODO:这里建议后端单独再写一个和大模型的接口，同时更新CT记录,现在是没有更新的
    // 修改AI诊断请求方法
    async requestAIDiagnosis() {
      if (!this.selectedCT || !this.selectedCT.image_url) {
        this.$message.error("无法获取CT图像");
        return;
      }

      try {
        this.isAnalyzing = true;
        this.$message.info("正在进行AI分析，请稍候...");

        // 创建FormData对象
        const formData = new FormData();

        // 处理base64格式的图片
        let imageBlob;
        if (this.selectedCT.image_url.startsWith('data:image')) {
          // 直接从base64字符串创建Blob
          const base64Data = this.selectedCT.image_url.split(',')[1];
          const byteCharacters = atob(base64Data);
          const byteArrays = [];
          
          for (let i = 0; i < byteCharacters.length; i++) {
            byteArrays.push(byteCharacters.charCodeAt(i));
          }
          
          const byteArray = new Uint8Array(byteArrays);
          imageBlob = new Blob([byteArray], { type: 'image/jpeg' });
        } else {
          // 如果不是base64，则通过fetch获取
          const imageResponse = await fetch(this.selectedCT.image_url);
          if (!imageResponse.ok) {
            throw new Error("获取图像失败");
          }
          imageBlob = await imageResponse.blob();
        }

        formData.append("image", imageBlob, "ct_image.jpg");

        // 添加问题文本
        formData.append(
          "question",
          "请分析这张脑部CT扫描图像，识别可能存在的异常情况，并给出专业的医学诊断建议。请以Markdown格式输出，包含标题、发现和建议等部分。"
        );

        // 发送请求到后端API
        const aiResponse = await Axios.post("/llm/multimodal", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
          timeout: 60000, // 增加超时时间到60秒
        });

        if (aiResponse.status === 200) {
          // 修改这里：使用POST或PATCH方法替代PUT方法
          // 根据后端API的实际支持情况选择正确的方法
          const updateResponse = await Axios.post(  // 改为POST方法
            `/ct/ct_scans/${this.selectedCT.id}/update_diagnosis`,  // 可能需要调整路径
            {
              ai_diagnosis: aiResponse.data.result,
            }
          );

          if (updateResponse.status === 200) {
            // 更新本地数据
            this.selectedCT.ai_diagnosis = aiResponse.data.result;

            // 更新列表中的记录
            const index = this.ctRecords.findIndex(
              (ct) => ct.id === this.selectedCT.id
            );
            if (index !== -1) {
              this.ctRecords[index].ai_diagnosis = aiResponse.data.result;
            }

            this.$message.success("AI诊断完成");
          } else {
            this.$message.error("更新CT记录失败");
          }
        } else {
          this.$message.error(aiResponse.data.error || "AI诊断失败");
        }
      } catch (error) {
        console.error("AI诊断请求失败:", error);
        // 添加更详细的错误日志
        if (error.response) {
          console.error("错误响应:", error.response.status, error.response.data);
        }
        this.$message.error(error.response?.data?.error || "AI诊断请求失败");
      } finally {
        this.isAnalyzing = false;
      }
    },
  },
  watch: {
    patientId: {
      immediate: true,
      handler(newVal) {
        if (newVal) {
          this.fetchCTRecords();
        }
      },
    },
  },
};
</script>

<style scoped>
.ct-container {
  display: flex;
  gap: 25px;
  height: 100%;
  background-color: #ffffff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.ct-left {
  width: 35%;
  min-width: 280px;
  height: 100%;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #eaecf0;
  background-color: #f9fafb;
}

.ct-right {
  flex: 1;
  height: 100%;
  min-height: 500px;
  padding: 25px;
  background-color: #ffffff;
  display: flex;
  flex-direction: column;
  overflow: hidden; /* 防止内容溢出 */
}

.ct-detail {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.ct-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f0f4f8;
  flex-shrink: 0; /* 防止头部被压缩 */
}

.ct-content-scroll {
  flex: 1;
  overflow-y: auto;
  padding-right: 10px; /* 为滚动条留出空间 */
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 #f1f5f9;
}

.ct-content-scroll::-webkit-scrollbar {
  width: 6px;
}

.ct-content-scroll::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 10px;
}

.ct-content-scroll::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 10px;
}

.ct-image-container {
  margin: 0 auto 5px;
  border-radius: 12px;
  overflow: hidden;
  width: 100%;
  max-width: 500px;
  min-height: 400px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
}

.ct-detail-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
}

.ct-ai-diagnosis {
  background: linear-gradient(to right, #f8fafc, #f1f5f9);
  border-radius: 12px;
  padding: 12px;
  border: 1px solid #e2e8f0;
  margin-bottom: 20px;
}

.ct-header {
  padding: 20px;
  border-bottom: 1px solid #eaecf0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #fff;
}

.ct-header h3 {
  margin: 0;
  color: #2d5bff;
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 0.2px;
}

.ct-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ct-add-btn {
  background-color: #2d5bff;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(45, 91, 255, 0.2);
}

.ct-add-btn:hover {
  background-color: #1a44e4;
  box-shadow: 0 4px 8px rgba(45, 91, 255, 0.3);
}

.ct-filter {
  display: flex;
  align-items: center;
}

.ct-select {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background-color: #fff;
  color: #475569;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.ct-select:focus {
  border-color: #2d5bff;
  outline: none;
  box-shadow: 0 0 0 3px rgba(45, 91, 255, 0.15);
}

.ct-list {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
}

.ct-list-item {
  padding: 16px;
  border-radius: 10px;
  margin-bottom: 12px;
  background: #fff;
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.03);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ct-list-item:hover {
  background: #f8faff;
  transform: translateX(5px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
}

.ct-list-content {
  flex: 1;
  cursor: pointer;
}

.ct-list-item.active {
  background: #f0f5ff;
  border-left: 4px solid #2d5bff;
  box-shadow: 0 4px 12px rgba(45, 91, 255, 0.1);
}

.ct-list-date {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 6px;
  font-size: 16px;
}

.ct-list-id {
  color: #64748b;
  font-size: 13px;
  margin-bottom: 10px;
  font-weight: 500;
}

.ct-list-status {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.3px;
}

.ct-list-status.normal {
  background: #ecfdf5;
  color: #059669;
}

.ct-list-status.abnormal {
  background: #fff1f2;
  color: #e11d48;
}

.diagnosis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.diagnosis-header h4 {
  margin: 0;
  color: #1e293b;
  font-size: 18px;
  font-weight: 600;
}

.diagnosis-date {
  color: #64748b;
  font-size: 13px;
  font-weight: 500;
}

.diagnosis-content {
  color: #334155;
  font-size: 15px;
  line-height: 1.7;
}

.diagnosis-content p {
  margin-top: 0;
}

.ct-placeholder {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #94a3b8;
  text-align: center;
  padding: 40px;
}

.placeholder-icon {
  margin-bottom: 20px;
}

.ct-placeholder p {
  font-size: 16px;
  font-weight: 500;
  max-width: 300px;
}

.ct-detail-status {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.3px;
}

.ct-detail-status.normal {
  background: #ecfdf5;
  color: #059669;
}

.ct-detail-status.abnormal {
  background: #fff1f2;
  color: #e11d48;
}

/* 删除按钮样式 */
.ct-delete-btn {
  background-color: transparent;
  color: #e11d48;
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  opacity: 0.7;
}

.ct-delete-btn:hover {
  background-color: #fff1f2;
  opacity: 1;
}

.ct-list-actions {
  display: flex;
  align-items: center;
}

/* 弹窗样式 */
.ct-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.ct-dialog {
  background-color: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.ct-dialog-confirm {
  max-width: 400px;
}

.ct-dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #eaecf0;
}

.ct-dialog-header h3 {
  margin: 0;
  color: #1e293b;
  font-size: 18px;
  font-weight: 600;
}

.ct-dialog-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #64748b;
  cursor: pointer;
}

.ct-dialog-body {
  padding: 20px;
}

.ct-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.ct-form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ct-form-group label {
  font-weight: 500;
  color: #334155;
  font-size: 14px;
}

.ct-input {
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s;
}

.ct-input:focus {
  border-color: #2d5bff;
  outline: none;
  box-shadow: 0 0 0 3px rgba(45, 91, 255, 0.15);
}

.ct-form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 8px;
}

.ct-btn-cancel {
  padding: 8px 16px;
  background-color: #f1f5f9;
  color: #475569;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.ct-btn-cancel:hover {
  background-color: #e2e8f0;
}

.ct-btn-submit {
  padding: 8px 16px;
  background-color: #2d5bff;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.ct-btn-submit:hover {
  background-color: #1a44e4;
}

.ct-btn-submit:disabled {
  background-color: #94a3b8;
  cursor: not-allowed;
}

.ct-btn-delete {
  padding: 8px 16px;
  background-color: #e11d48;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.ct-btn-delete:hover {
  background-color: #be123c;
}

.ct-btn-delete:disabled {
  background-color: #f43f5e;
  opacity: 0.7;
  cursor: not-allowed;
}

.ct-ai-analyze-btn {
  padding: 8px 16px;
  background-color: #2d5bff;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 10px;
  display: inline-block;
}

.ct-ai-analyze-btn:hover {
  background-color: #1a44e4;
}

.ct-ai-analyze-btn:disabled {
  background-color: #94a3b8;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .ct-container {
    flex-direction: column;
    height: auto;
  }

  .ct-left {
    width: 100%;
    min-width: auto;
    max-height: 300px;
    border-right: none;
    border-bottom: 1px solid #eaecf0;
  }

  .ct-right {
    min-height: 500px;
    padding: 20px;
  }

  .ct-content-scroll {
    padding-right: 5px;
  }

  .ct-image-container {
    min-height: 300px;
    margin-bottom: 20px;
  }

  .ct-dialog {
    width: 95%;
    max-height: 90vh;
    overflow-y: auto;
  }

  .ct-actions {
    flex-direction: column;
    align-items: flex-end;
    gap: 8px;
  }
}

/* 添加Markdown渲染样式 */
.diagnosis-content :deep(h1) {
  font-size: 1.5em;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
  color: #1e293b;
}

.diagnosis-content :deep(h2) {
  font-size: 1.3em;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
  color: #334155;
}

.diagnosis-content :deep(h3) {
  font-size: 1.1em;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
  color: #475569;
}

.diagnosis-content :deep(ul), .diagnosis-content :deep(ol) {
  padding-left: 1.5em;
  margin: 0.5em 0;
}

.diagnosis-content :deep(li) {
  margin-bottom: 0.3em;
}

.diagnosis-content :deep(p) {
  margin: 0.5em 0;
}

.diagnosis-content :deep(strong) {
  font-weight: 600;
  color: #1e293b;
}

.diagnosis-content :deep(em) {
  font-style: italic;
}

.diagnosis-content :deep(blockquote) {
  border-left: 3px solid #cbd5e1;
  padding-left: 1em;
  margin: 0.5em 0;
  color: #64748b;
}
</style>
