<template>
  <div class="review-page">
    <AdminTopNavbar />
    <div class="review-container">
      <div class="back-button-container">
      </div>
      <div class="page-header">
        <h1>资质审核管理</h1>
      </div>

      <div class="review-content">
        <!-- 左侧：申请列表 -->
        <div class="applications-list">
          <div class="list-header">
            <h2>待审核申请</h2>
            <div class="filter-controls">
              <select v-model="statusFilter" class="status-filter">
                <option value="all">全部状态</option>
                <option value="pending">待审核</option>
                <option value="approved">已通过</option>
                <option value="rejected">已拒绝</option>
              </select>
              <div class="search-box">
                <input
                  type="text"
                  v-model="searchQuery"
                  placeholder="搜索姓名..."
                />
                <i class="fas fa-search"></i>
              </div>
            </div>
          </div>

          <div class="applications">
            <div
              v-for="application in filteredApplications"
              :key="application.id"
              class="application-item"
              :class="{
                selected:
                  selectedApplication &&
                  selectedApplication.id === application.id,
                [application.status]: true,
              }"
              @click="selectApplication(application)"
            >
              <div class="application-info">
                <div class="applicant-name">{{ application.name }}</div>
                <div class="applicant-details">
                  <span class="hospital">{{ application.hospital }}</span>
                  <span class="department">{{ application.department }}</span>
                </div>
                <div class="application-date">
                  {{ formatDate(application.submitTime) }}
                </div>
              </div>
              <div class="status-badge" :class="application.status">
                {{
                  application.status === "pending"
                    ? "待审核"
                    : application.status === "approved"
                    ? "已通过"
                    : "已拒绝"
                }}
              </div>
            </div>

            <div v-if="filteredApplications.length === 0" class="no-results">
              没有找到符合条件的申请
            </div>
          </div>
        </div>

        <!-- 右侧：申请详情 -->
        <div class="application-details" v-if="selectedApplication">
          <div class="details-header">
            <h2>申请详情</h2>
            <div class="status-indicator" :class="selectedApplication.status">
              {{
                selectedApplication.status === "pending"
                  ? "待审核"
                  : selectedApplication.status === "approved"
                  ? "已通过"
                  : "已拒绝"
              }}
            </div>
          </div>

          <div class="details-content">
            <!-- 申请人基本信息 -->
            <div class="applicant-info-card">
              <h3>申请人信息</h3>
              <div class="info-grid">
                <div class="info-item">
                  <span class="label">姓名</span>
                  <span class="value">{{ selectedApplication.name }}</span>
                </div>
                <div class="info-item">
                  <span class="label">职称</span>
                  <span class="value">{{ selectedApplication.title }}</span>
                </div>
                <div class="info-item">
                  <span class="label">邮箱</span>
                  <span class="value">{{ selectedApplication.email }}</span>
                </div>
                <div class="info-item">
                  <span class="label">医院</span>
                  <span class="value">{{ selectedApplication.hospital }}</span>
                </div>
                <div class="info-item">
                  <span class="label">科室</span>
                  <span class="value">{{
                    selectedApplication.department
                  }}</span>
                </div>
                <div class="info-item">
                  <span class="label">申请时间</span>
                  <span class="value">{{
                    formatDate(selectedApplication.submitTime)
                  }}</span>
                </div>
              </div>
            </div>

            <!-- 资质证明材料 -->
            <div class="qualification-materials">
              <h3>资质证明材料</h3>

              <div class="material-item">
                <div class="material-header">
                  <h4>医师执业证书</h4>
                </div>
                <div class="material-content">
                  <div class="license-number">
                    <span class="label">证书编号:</span>
                    <span class="value">{{
                      selectedApplication.licenseNumber
                    }}</span>
                  </div>
                  <div class="license-image">
                    <img
                      :src="selectedApplication.licenseImage"
                      alt="医师执业证书"
                      @click="enlargeImage(selectedApplication.licenseImage)"
                    />
                    <div class="image-caption">点击查看大图</div>
                  </div>
                </div>
              </div>

              <div class="material-item">
                <div class="material-header">
                  <h4>医院工作证明</h4>
                </div>
                <div class="material-content">
                  <div class="work-proof-image">
                    <img
                      :src="selectedApplication.workProofImage"
                      alt="医院工作证明"
                      @click="enlargeImage(selectedApplication.workProofImage)"
                    />
                    <div class="image-caption">点击查看大图</div>
                  </div>
                </div>
              </div>

              <div
                class="material-item"
                v-if="selectedApplication.additionalInfo"
              >
                <div class="material-header">
                  <h4>补充说明</h4>
                </div>
                <div class="material-content">
                  <div class="additional-info">
                    {{ selectedApplication.additionalInfo }}
                  </div>
                </div>
              </div>
            </div>

            <!-- 审核操作区域 -->
            <div
              class="review-actions"
              v-if="selectedApplication.status === 'pending'"
            >
              <h3>审核操作</h3>
              <div class="review-form">
                <div class="form-group">
                  <label>审核意见</label>
                  <textarea
                    v-model="reviewComment"
                    placeholder="请输入审核意见（可选）"
                    rows="3"
                  ></textarea>
                </div>
                <div class="action-buttons">
                  <button class="approve-btn" @click="approveApplication">
                    通过申请
                  </button>
                  <button class="reject-btn" @click="rejectApplication">
                    拒绝申请
                  </button>
                </div>
              </div>
            </div>

            <!-- 已审核信息 -->
            <div
              class="review-result"
              :class="selectedApplication.status"
              v-if="selectedApplication.status !== 'pending'"
            >
              <h3>审核结果</h3>
              <div class="result-info">
                <div class="info-item">
                  <span class="label">审核人</span>
                  <span class="value">{{ selectedApplication.reviewer }}</span>
                </div>
                <div class="info-item">
                  <span class="label">审核时间</span>
                  <span class="value">{{
                    formatDate(selectedApplication.reviewTime)
                  }}</span>
                </div>
                <div class="info-item" v-if="selectedApplication.reviewComment">
                  <span class="label">审核意见</span>
                  <span class="value">{{
                    selectedApplication.reviewComment
                  }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：未选择申请时的提示 -->
        <div class="no-selection" v-else>
          <div class="no-selection-content">
            <i class="fas fa-clipboard-list"></i>
            <p>请从左侧列表选择一个申请进行审核</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 图片放大查看 -->
    <div
      class="enlarged-image-container"
      v-if="enlargedImage"
      @click="closeEnlargedImage"
    >
      <div class="enlarged-image-wrapper">
        <img :src="enlargedImage" alt="放大查看" />
        <button class="close-button" @click="closeEnlargedImage">×</button>
      </div>
    </div>
  </div>
</template>

<script>
// import TopNavbar from "@/components/TopNavbar.vue";
import Axios from "@/utils/axios.js";
import AdminTopNavbar from '@/components/AdminTopNavbar.vue';
export default {
  name: "QualificationReviewPage",
  components: {
    AdminTopNavbar
  },
  //   components: {
  //     TopNavbar,
  //   },
  data() {
    return {
      applications: [],
      selectedApplication: null,
      statusFilter: "all",
      searchQuery: "",
      reviewComment: "",
      enlargedImage: null,
    };
  },
  computed: {
    filteredApplications() {
      let filtered = [...this.applications];

      // 按状态筛选
      if (this.statusFilter !== "all") {
        filtered = filtered.filter((app) => app.status === this.statusFilter);
      }

      // 按姓名搜索
      if (this.searchQuery.trim() !== "") {
        const query = this.searchQuery.toLowerCase().trim();
        filtered = filtered.filter((app) =>
          app.name.toLowerCase().includes(query)
        );
      }

      return filtered;
    },
  },
  mounted() {
    // 页面加载时获取所有认证申请
    this.fetchAllCertifications();
  },
  methods: {
    selectApplication(application) {
      // 选择申请时获取详细信息
      this.getCertificationDetail(application.id);
      this.reviewComment = ""; // 清空审核意见
    },
    formatDate(dateString) {
      if (!dateString) return "";
      const date = new Date(dateString);
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(
        2,
        "0"
      )}-${String(date.getDate()).padStart(2, "0")} ${String(
        date.getHours()
      ).padStart(2, "0")}:${String(date.getMinutes()).padStart(2, "0")}`;
    },
    enlargeImage(imageUrl) {
      this.enlargedImage = imageUrl;
    },
    closeEnlargedImage() {
      this.enlargedImage = null;
    },
    // 获取所有资质认证申请
    async fetchAllCertifications() {
      try {
        const response = await Axios.get(
          "/certification/get_all_certifications",
          {
            params: {
              status:
                this.statusFilter !== "all" ? this.statusFilter : undefined,
            },
          }
        );

        if (response.data) {
          // 处理返回的认证列表数据
          this.applications = response.data.map((cert) => ({
            id: cert.id,
            name: cert.user_nickname || "未知用户",
            title: cert.title || "",
            email: cert.user_email || "未知邮箱",
            hospital: cert.hospital || "",
            department: cert.department || "",
            licenseNumber: cert.license_number,
            licenseImage: cert.license_image,
            workProofImage: cert.work_proof,
            additionalInfo: cert.additional_documents || "",
            submitTime: cert.created_at,
            status:
              cert.is_approved === null
                ? "pending"
                : cert.is_approved === true
                ? "approved"
                : "rejected",
            reviewer: cert.reviewer_nickname || "",
            reviewTime: cert.review_date,
            reviewComment: cert.review_comment || "",
            userId: cert.user_id,
          }));
        }
      } catch (error) {
        console.error("获取认证申请列表失败:", error);
        this.$message.error("获取认证申请列表失败");
      }
    },
    // 获取认证详情
    async getCertificationDetail(certificationId) {
      try {
        const response = await Axios.get(
          `/certification/get_certification_detail/${certificationId}`
        );

        if (response.data) {
          // 更新选中的申请详情
          const cert = response.data;
          this.selectedApplication = {
            id: cert.id,
            name: cert.applicant_nickname || "未知用户",
            title: cert.title || "",
            email: cert.applicant_email || "未知邮箱",
            hospital: cert.hospital || "",
            department: cert.department || "",
            licenseNumber: cert.license_number,
            licenseImage: cert.license_image,
            workProofImage: cert.work_proof,
            additionalInfo: cert.additional_documents || "",
            submitTime: cert.created_at,
            status:
              cert.is_approved === null
                ? "pending"
                : cert.is_approved === true
                ? "approved"
                : "rejected",
            reviewer: cert.reviewer_nickname || "",
            reviewTime: cert.review_date,
            reviewComment: cert.review_comment || "",
            userId: cert.user_id,
          };
        }
      } catch (error) {
        console.error("获取认证详情失败:", error);
        this.$message.error("获取认证详情失败");
      }
    },
    // 审核认证申请 - 通过
    async approveApplication() {
      if (!this.selectedApplication) return;

      try {
        // 调用审核API
        const response = await Axios.post(
          `/certification/review_certification/${this.selectedApplication.id}`,
          {
            is_approved: true,
            review_comment: this.reviewComment,
          }
        );

        if (response.data && response.data.message) {
          // 更新申请状态为已通过
          this.selectedApplication.status = "approved";
          this.selectedApplication.reviewer = "管理员"; // 实际会从后端返回
          this.selectedApplication.reviewTime = new Date().toISOString();
          this.selectedApplication.reviewComment = this.reviewComment;

          // 更新列表中的状态
          const index = this.applications.findIndex(
            (app) => app.id === this.selectedApplication.id
          );
          if (index !== -1) {
            this.applications[index].status = "approved";
            this.applications[index].reviewer =
              this.selectedApplication.reviewer;
            this.applications[index].reviewTime =
              this.selectedApplication.reviewTime;
            this.applications[index].reviewComment =
              this.selectedApplication.reviewComment;
          }

          this.$message.success("已通过该医师的资质验证申请");

          // 刷新认证列表
          this.fetchAllCertifications();
        }
      } catch (error) {
        console.error("审核认证失败:", error);
        this.$message.error(error.response?.data?.error || "审核认证失败");
      }
    },
    // 审核认证申请 - 拒绝
    async rejectApplication() {
      if (!this.selectedApplication) return;

      try {
        // 调用审核API
        const response = await Axios.post(
          `/certification/review_certification/${this.selectedApplication.id}`,
          {
            is_approved: false,
            review_comment: this.reviewComment,
          }
        );

        if (response.data && response.data.message) {
          // 更新申请状态为已拒绝
          this.selectedApplication.status = "rejected";
          this.selectedApplication.reviewer = "管理员"; // 实际会从后端返回
          this.selectedApplication.reviewTime = new Date().toISOString();
          this.selectedApplication.reviewComment = this.reviewComment;

          // 更新列表中的状态
          const index = this.applications.findIndex(
            (app) => app.id === this.selectedApplication.id
          );
          if (index !== -1) {
            this.applications[index].status = "rejected";
            this.applications[index].reviewer =
              this.selectedApplication.reviewer;
            this.applications[index].reviewTime =
              this.selectedApplication.reviewTime;
            this.applications[index].reviewComment =
              this.selectedApplication.reviewComment;
          }

          this.$message.success("已拒绝该医师的资质验证申请");

          // 刷新认证列表
          this.fetchAllCertifications();
        }
      } catch (error) {
        console.error("审核认证失败:", error);
        this.$message.error(error.response?.data?.error || "审核认证失败");
      }
    },
  },
};
</script>

<style scoped>
.review-page {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.review-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 30px 20px;
}
.back-button-container {
  margin-bottom: 20px;
}
.back-button {
  display: flex;
  align-items: center;
  background-color: #f5f7ff;
  color: #2d5bff;
  border: 1px solid #d0d9ff;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.back-button:hover {
  background-color: #e8edff;
}

.back-button i {
  margin-right: 8px;
}
.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 28px;
  color: #333;
  font-weight: 600;
}

.review-content {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 30px;
}

@media (max-width: 992px) {
  .review-content {
    grid-template-columns: 1fr;
  }
}

/* 左侧申请列表样式 */
.applications-list {
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  height: calc(100vh - 200px);
  display: flex;
  flex-direction: column;
}

.list-header {
  padding: 20px;
  border-bottom: 1px solid #eaedf7;
}

.list-header h2 {
  font-size: 18px;
  color: #333;
  margin-bottom: 15px;
}

.filter-controls {
  display: flex;
  gap: 10px;
}

.status-filter {
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  color: #606266;
  background-color: white;
  outline: none;
}

.search-box {
  position: relative;
  flex: 1;
  /* 添加右侧内边距防止内容超出 */
  padding-right: 10px;
}

.search-box input {
  width: 100%;
  padding: 10px 36px 10px 16px;
  border: 2px solid #e6e8f1;
  border-radius: 8px;
  font-size: 14px;
  color: #2c3e50;
  outline: none;
  background-color: #f8f9fc;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
  /* 添加盒模型设置确保宽度包含padding和border */
  box-sizing: border-box;
}

/* .search-box input:hover {
  border-color: #d0d9ff;
  background-color: #ffffff;
} */

.search-box input:focus {
  border-color: #2d5bff;
  background-color: #ffffff;
  box-shadow: 0 0 0 3px rgba(45, 91, 255, 0.1);
}

.search-box i {
  position: absolute;
  right: 24px; /* 调整图标位置,考虑search-box的padding */
  top: 50%;
  transform: translateY(-50%);
  color: #8c8c8c;
  font-size: 16px;
  transition: all 0.3s ease;
}

.search-box:hover i {
  color: #2d5bff;
}
.applications {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.application-item {
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #eaedf7;
}

.application-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.application-item.selected {
  background-color: #f0f7ff;
  border-color: #409eff;
}

.application-info {
  margin-bottom: 10px;
}

.applicant-name {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin-bottom: 5px;
}

.applicant-details {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.application-date {
  font-size: 12px;
  color: #909399;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.pending {
  background-color: #fff7e6;
  color: #d48806;
}

.status-badge.approved {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.status-badge.rejected {
  background-color: #ffebee;
  color: #c62828;
}

/* 右侧详情样式 */
.application-details {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  height: calc(100vh - 200px);
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}

.status-indicator {
  display: inline-flex;
  align-items: center;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  position: relative;
  overflow: hidden;
}

.status-indicator::before {
  content: "";
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 8px;
  animation: pulse 2s infinite;
}

.status-indicator.pending {
  background-color: #ffa500;
  color: white;
}

.status-indicator.pending::before {
  background-color: white;
}

.status-indicator.approved {
  background-color: #42b983;
  color: white;
}

.status-indicator.approved::before {
  background-color: white;
}

.status-indicator.rejected {
  background-color: #ff4757;
  color: white;
}

.status-indicator.rejected::before {
  background-color: white;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.4);
  }
  70% {
    box-shadow: 0 0 0 6px rgba(255, 255, 255, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(255, 255, 255, 0);
  }
}

.details-header {
  padding: 24px;
  border-bottom: 1px solid #eaedf7;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f9fafc;
  border-top-left-radius: 12px;
  border-top-right-radius: 12px;
}

.details-header h2 {
  font-size: 20px;
  color: #2c3e50;
  font-weight: 600;
}

.details-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  scrollbar-width: thin;
  scrollbar-color: #d0d9ff transparent;
}

.details-content::-webkit-scrollbar {
  width: 6px;
}

.details-content::-webkit-scrollbar-track {
  background: transparent;
}

.details-content::-webkit-scrollbar-thumb {
  background-color: #d0d9ff;
  border-radius: 6px;
}

.applicant-info-card,
.qualification-materials,
.review-actions,
.review-result {
  margin-bottom: 30px;
  background-color: #ffffff;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 20px;
  transition: all 0.3s ease;
  border-left: 4px solid;
  border-left-color: #d0d9ff;
}

.review-result.approved {
  border-left-color: #42b983;
}

.review-result.rejected {
  border-left-color: #ff4757;
}

h3 {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 18px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eaedf7;
  position: relative;
}

h3::after {
  content: "";
  position: absolute;
  bottom: -1px;
  left: 0;
  width: 60px;
  height: 3px;
  background-color: #2d5bff;
  border-radius: 3px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.info-item {
  display: flex;
  flex-direction: column;
  background-color: #f9fafc;
  padding: 12px 16px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.info-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgbargba(0, 0, 0, 0.05);
}

.info-item .label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
  font-weight: 500;
}

.info-item .value {
  font-size: 16px;
  color: #2c3e50;
  font-weight: 500;
}

.material-item {
  background-color: #ffffff;
  border-radius: 10px;
  margin-bottom: 24px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgbargba(0, 0, 0, 0.05);
  border: 1px solid #eaedf7;
  transition: all 0.3s ease;
}

.material-item:hover {
  box-shadow: 0 4px 16px rgbargba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.material-header {
  padding: 14px 18px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #eaedf7;
  display: flex;
  align-items: center;
}

.material-header h4 {
  font-size: 16px;
  color: #2c3e50;
  margin: 0;
  font-weight: 600;
}

.material-content {
  padding: 18px;
}

.license-number {
  margin-bottom: 10px;
}

.license-image,
.work-proof-image {
  margin-top: 16px;
  position: relative;
  overflow: hidden;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.license-image img,
.work-proof-image img {
  max-width: 100%;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: block;
}

.license-image img:hover,
.work-proof-image img:hover {
  transform: scale(1.03);
}

.image-caption {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: rgba(0, 0, 0, 0.6);
  color: white;
  padding: 8px 12px;
  font-size: 13px;
  text-align: center;
  transform: translateY(100%);
  transition: transform 0.3s ease;
}

.license-image:hover .image-caption,
.work-proof-image:hover .image-caption {
  transform: translateY(0);
}

.additional-info {
  white-space: pre-wrap;
  color: #666;
  line-height: 1.5;
}

.review-form {
  background-color: #f9fafc;
  border-radius: 10px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  margin-bottom: 10px;
  color: #2c3e50;
  font-weight: 500;
  font-size: 15px;
}

textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  resize: vertical;
  min-height: 100px;
  font-size: 14px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
}

textarea:focus {
  border-color: #2d5bff;
  box-shadow: 0 0 0 2px rgba(45, 91, 255, 0.1);
  outline: none;
}

.action-buttons {
  display: flex;
  gap: 20px;
}

.approve-btn,
.reject-btn {
  flex: 1;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8pxrgba (0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
}

.approve-btn {
  background-color: #2d5bff;
  color: white;
  position: relative;
  overflow: hidden;
}

.approve-btn:hover {
  background-color: #1a42ff;
  transform: translateY(-2px);
}

.approve-btn:active {
  transform: translateY(0);
}

.approve-btn::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    to right,
    transparent,
    rgba(255, 255, 255, 0.2),
    transparent
  );
  transform: translateX(-100%);
}

.approve-btn:hover::before {
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  100% {
    transform: translateX(100%);
  }
}

.reject-btn {
  background-color: #ff4757;
  color: white;
  position: relative;
  overflow: hidden;
}

.reject-btn:hover {
  background-color: #e03444;
  transform: translateY(-2px);
}

.reject-btn:active {
  transform: translateY(0);
}

.reject-btn::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    to right,
    transparent,
    rgba(255, 255, 255, 0.2),
    transparent
  );
  transform: translateX(-100%);
}

.reject-btn:hover::before {
  animation: shimmer 1.5s infinite;
}

.no-selection {
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  height: calc(100vh - 200px);
  display: flex;
  align-items: center;
  justify-content: center;
}

.no-selection-content {
  text-align: center;
  color: #909399;
}

.no-selection-content i {
  font-size: 48px;
  margin-bottom: 15px;
}

/* 图片放大查看 */
.enlarged-image-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.enlarged-image-wrapper {
  position: relative;
  max-width: 90%;
  max-height: 90vh;
  box-shadow: 0 5px 30px rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  overflow: hidden;
  animation: scaleIn 0.3s ease;
}

@keyframes scaleIn {
  from {
    transform: scale(0.9);
  }
  to {
    transform: scale(1);
  }
}

.enlarged-image-wrapper img {
  max-width: 100%;
  max-height: 90vh;
  object-fit: contain;
  display: block;
}

.close-button {
  position: absolute;
  top: 15px;
  right: 15px;
  background-color: rgba(0, 0, 0, 0.5);
  border: none;
  color: white;
  font-size: 24px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.close-button:hover {
  background-color: rgba(255, 255, 255, 0.2);
  transform: rotate(90deg);
}
</style>
