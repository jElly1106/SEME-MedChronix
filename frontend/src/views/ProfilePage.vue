<template>
  <div class="profile-page">
    <div class="profile-container">
      <div class="back-button-container">
        <button class="back-button" @click="goBackToSystem">
          <i class="fas fa-arrow-left"></i> 返回系统
        </button>
      </div>
      <div class="page-header">
        <h1>个人信息管理</h1>
      </div>

      <div class="profile-content">
        <!-- 个人基本信息卡片 -->
        <div class="profile-card">
          <div class="card-header">
            <h2>基本信息</h2>
          </div>
          <div class="card-content">
            <div class="profile-avatar">
              <img
                :src="
                  userInfo.avatar ||
                  'https://api.dicebear.com/7.x/avataaars/svg?seed=Doctor123'
                "
                alt="用户头像"
              />
              <input
                type="file"
                ref="avatarInput"
                @change="handleAvatarChange"
                accept="image/*"
                style="display: none"
              />
              <button class="change-avatar-btn" @click="triggerAvatarInput">
                更换头像
              </button>
            </div>

            <div class="profile-details">
              <div class="detail-item">
                <span class="label">姓名:</span>
                <span class="value" v-if="!isEditing">{{ userInfo.name }}</span>
                <input
                  v-else
                  type="text"
                  v-model="editingUserInfo.name"
                  class="edit-input"
                />
              </div>
              <div class="detail-item">
                <span class="label">职称:</span>
                <span class="value" v-if="!isEditing">{{
                  userInfo.title
                }}</span>
                <input
                  v-else
                  type="text"
                  v-model="editingUserInfo.title"
                  class="edit-input"
                />
              </div>
              <div class="detail-item">
                <span class="label">邮箱:</span>
                <span class="value">{{ userInfo.email }}</span>
              </div>
              <div class="detail-item">
                <span class="label">科室:</span>
                <span class="value" v-if="!isEditing">{{
                  userInfo.department
                }}</span>
                <input
                  v-else
                  type="text"
                  v-model="editingUserInfo.department"
                  class="edit-input"
                />
              </div>
              <div class="detail-item">
                <span class="label">医院:</span>
                <span class="value" v-if="!isEditing">{{
                  userInfo.hospital
                }}</span>
                <input
                  v-else
                  type="text"
                  v-model="editingUserInfo.hospital"
                  class="edit-input"
                />
              </div>
              <div class="detail-item">
                <span class="label">资质状态:</span>
                <span class="value status" :class="qualificationStatusClass">{{
                  qualificationStatusText
                }}</span>
              </div>
            </div>
            <div
              class="edit-actions"
              v-if="
                !userInfo.isQualified ||
                userInfo.qualificationStatus !== 'pending'
              "
            >
              <button v-if="!isEditing" @click="startEditing" class="edit-btn">
                编辑信息
              </button>
              <template v-else>
                <button @click="saveUserInfo" class="save-btn">保存</button>
                <button @click="cancelEditing" class="cancel-btn">取消</button>
              </template>
            </div>
          </div>
        </div>

        <!-- 资质验证表单 -->
        <div
          class="qualification-card"
          v-if="
            !userInfo.isQualified || userInfo.qualificationStatus === 'rejected'
          "
        >
          <div class="card-header">
            <h2>资质验证</h2>
            <span
              class="subtitle"
              v-if="userInfo.qualificationStatus === 'rejected'"
              >您的资质申请被拒绝，请重新提交</span
            >
          </div>
          <div class="card-content">
            <form @submit.prevent="submitQualification">
              <div class="form-group">
                <label>医师资格证号</label>
                <input
                  type="text"
                  v-model="qualificationForm.licenseNumber"
                  placeholder="请输入医师资格证号"
                  required
                />
              </div>

              <div class="form-group">
                <label>医师资格证照片</label>
                <div class="upload-area">
                  <div class="preview" v-if="qualificationForm.licenseImage">
                    <img
                      :src="qualificationForm.licenseImage"
                      alt="资格证照片"
                    />
                    <button
                      type="button"
                      class="remove-btn"
                      @click="removeImage('license')"
                    >
                      ×
                    </button>
                  </div>
                  <div class="upload-btn-wrapper" v-else>
                    <button
                      type="button"
                      class="upload-btn"
                      @click="triggerFileInput('license')"
                    >
                      <i class="fas fa-plus"></i>
                      <span>上传照片</span>
                    </button>
                    <input
                      type="file"
                      ref="licenseInput"
                      @change="handleFileChange('license')"
                      accept="image/*"
                      style="display: none"
                    />
                  </div>
                </div>
              </div>

              <div class="form-group">
                <label>医院工作证明</label>
                <div class="upload-area">
                  <div class="preview" v-if="qualificationForm.workProofImage">
                    <img
                      :src="qualificationForm.workProofImage"
                      alt="工作证明照片"
                    />
                    <button
                      type="button"
                      class="remove-btn"
                      @click="removeImage('workProof')"
                    >
                      ×
                    </button>
                  </div>
                  <div class="upload-btn-wrapper" v-else>
                    <button
                      type="button"
                      class="upload-btn"
                      @click="triggerFileInput('workProof')"
                    >
                      <i class="fas fa-plus"></i>
                      <span>上传照片</span>
                    </button>
                    <input
                      type="file"
                      ref="workProofInput"
                      @change="handleFileChange('workProof')"
                      accept="image/*"
                      style="display: none"
                    />
                  </div>
                </div>
              </div>

              <div class="form-group">
                <label>其他补充材料</label>
                <textarea
                  v-model="qualificationForm.additionalInfo"
                  placeholder="请输入其他补充说明（选填）"
                  rows="3"
                  class="additional-info-textarea"
                ></textarea>
              </div>

              <div class="form-actions">
                <button type="submit" class="submit-btn">提交资质验证</button>
              </div>
            </form>
          </div>
        </div>

        <!-- 资质验证状态 -->
        <div
          class="qualification-status-card"
          v-if="userInfo.qualificationStatus === 'pending'"
        >
          <div class="card-header">
            <h2>资质验证状态</h2>
          </div>
          <div class="card-content status-content">
            <div class="status-icon pending">
              <i class="fas fa-clock"></i>
            </div>
            <div class="status-text">
              <h3>资质审核中</h3>
              <p>您的资质验证申请已提交，正在等待管理员审核，请耐心等待。</p>
              <p class="submission-date">
                提交时间: {{ userInfo.qualificationSubmitTime }}
              </p>
            </div>
          </div>
        </div>

        <div
          class="qualification-status-card"
          v-if="userInfo.qualificationStatus === 'approved'"
        >
          <div class="card-header">
            <h2>资质验证状态</h2>
          </div>
          <div class="card-content status-content">
            <div class="status-icon approved">
              <i class="fas fa-check-circle"></i>
            </div>
            <div class="status-text">
              <h3>资质已验证</h3>
              <p>您的医师资质已通过验证，可以使用系统的全部功能。</p>
              <p class="approval-date">
                通过时间: {{ userInfo.qualificationApproveTime }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// import TopNavbar from "@/components/TopNavbar.vue";
import Axios from "@/utils/axios.js";

export default {
  name: "ProfilePage",
  //   components: {
  //     TopNavbar,
  //   },
  data() {
    return {
      isEditing: false,
      userInfo: {
        name: "王医生",
        title: "主治医师",
        email: "doctor@example.com",
        department: "神经内科",
        hospital: "北京协和医院",
        avatar: null,
        isQualified: false,
        qualificationStatus: "initial", // initial, pending, approved, rejected
        qualificationSubmitTime: null,
        qualificationApproveTime: null,
      },
      editingUserInfo: {
        name: "",
        title: "",
        email: "",
        department: "",
        hospital: "",
      },
      qualificationForm: {
        licenseNumber: "",
        licenseImage: null,
        workProofImage: null,
        additionalInfo: "",
      },
    };
  },
  computed: {
    qualificationStatusText() {
      const statusMap = {
        none: "未验证",
        pending: "审核中",
        approved: "已验证",
        rejected: "已拒绝",
      };
      return statusMap[this.userInfo.qualificationStatus] || "未验证";
    },
    qualificationStatusClass() {
      const classMap = {
        none: "status-none",
        pending: "status-pending",
        approved: "status-approved",
        rejected: "status-rejected",
      };
      return classMap[this.userInfo.qualificationStatus] || "status-none";
    },
  },
  mounted() {
    this.fetchUserInfo();

    // 从localStorage获取资质状态
    const savedStatus = localStorage.getItem("qualificationStatus");
    if (savedStatus) {
      this.userInfo.qualificationStatus = "savedStatus"; //savedStatus;
    }
  },
  methods: {
    // 将Base64数据URL转换为Blob对象
    dataURLtoBlob(dataURL) {
      // 提取MIME类型和Base64数据
      const arr = dataURL.split(",");
      const mime = arr[0].match(/:(.*?);/)[1];
      const bstr = atob(arr[1]);
      let n = bstr.length;
      const u8arr = new Uint8Array(n);

      // 将Base64字符串转换为Uint8Array
      while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
      }

      // 创建Blob对象
      return new Blob([u8arr], { type: mime });
    },

    async fetchUserInfo() {
      try {
        // 调用后端API获取用户信息
        const res = await Axios.get("/user/profile", {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        });

        if (res.data) {
          // 更新用户信息
          this.userInfo = {
            name: res.data.nickname,
            email: res.data.email,
            title: res.data.title || this.userInfo.title, // 如果API返回则使用，否则保留现有值
            department: res.data.department || this.userInfo.department, // 如果API返回则使用，否则保留现有值
            hospital: res.data.hospital || this.userInfo.hospital, // 如果API返回则使用，否则保留现有值
            avatar: res.data.avatar,
            isQualified: res.data.is_auth || this.userInfo.isQualified, // 如果API返回则使用，否则保留现有值
            qualificationStatus:
              res.data.qualificationStatus || this.userInfo.qualificationStatus, // 从API获取资质状态
            qualificationSubmitTime: res.data.qualificationSubmitTime,
            qualificationApproveTime: res.data.qualificationApproveTime,
          };
          console.log(
            "qualificationSubmitTime",
            this.userInfo.qualificationSubmitTime
          );
          console.log(
            "qualificationApproveTime",
            this.userInfo.qualificationApproveTime
          );
        }
      } catch (error) {
        this.$message.error("获取用户信息失败");
        console.error(error);
      }
    },
    goBackToSystem() {
      this.$router.push("/diseaseAnalysis");
    },
    startEditing() {
      this.editingUserInfo = { ...this.userInfo };
      this.isEditing = true;
    },
    cancelEditing() {
      this.isEditing = false;
    },
    async saveUserInfo() {
      try {
        // 创建FormData对象保存用户信息
        const formData = new FormData();
        formData.append("nickname", this.editingUserInfo.name);
        formData.append("title", this.editingUserInfo.title);
        formData.append("department", this.editingUserInfo.department);
        formData.append("hospital", this.editingUserInfo.hospital);

        // 调用后端API保存用户信息
        const res = await Axios.post("/user/profile/edit_profile", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        });

        if (res.data && res.data.message) {
          // 更新本地用户信息
          this.userInfo = { ...this.userInfo, ...this.editingUserInfo };
          this.isEditing = false;
          this.$message.success("个人信息已更新");
          // 刷新用户信息
          this.fetchUserInfo();
        } else {
          this.$message.error(res.data.error || "保存个人信息失败");
        }
      } catch (error) {
        this.$message.error(error.response?.data?.error || "保存个人信息失败");
        console.error(error);
      }
    },
    triggerAvatarInput() {
      this.$refs.avatarInput.click();
    },
    handleAvatarChange(event) {
      const file = event.target.files[0];
      if (!file) return;

      // 检查文件类型和大小
      if (!file.type.includes("image/")) {
        this.$message.error("请上传图片文件");
        return;
      }

      if (file.size > 5 * 1024 * 1024) {
        // 5MB限制
        this.$message.error("图片大小不能超过5MB");
        return;
      }

      // 创建预览URL并更新头像
      const reader = new FileReader();
      reader.onload = async (e) => {
        // 创建临时预览
        const previewUrl = e.target.result;

        // 创建FormData对象上传头像
        const formData = new FormData();
        formData.append("avatar", file);

        try {
          // 调用后端API上传头像
          const res = await Axios.post("/user/profile/edit_profile", formData, {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          });

          if (res.data && res.data.message) {
            // 上传成功，更新头像显示
            this.userInfo.avatar = previewUrl;
            this.$message.success("头像已更新");
            // 刷新用户信息以获取服务器上的头像URL
            this.fetchUserInfo();
          } else {
            this.$message.error(res.data.error || "头像上传失败");
          }
        } catch (error) {
          console.error("头像上传错误:", error);
          this.$message.error(
            error.response?.data?.error || "头像上传失败，请重试"
          );
        }
      };
      reader.readAsDataURL(file);
    },
    triggerFileInput(type) {
      if (type === "license") {
        this.$refs.licenseInput.click();
      } else if (type === "workProof") {
        this.$refs.workProofInput.click();
      }
    },
    handleFileChange(type, event) {
      event = event || window.event;
      const file = event.target.files[0];
      if (!file) return;

      // 检查文件类型和大小
      if (!file.type.includes("image/")) {
        this.$message.error("请上传图片文件");
        return;
      }

      if (file.size > 5 * 1024 * 1024) {
        // 5MB限制
        this.$message.error("图片大小不能超过5MB");
        return;
      }

      // 创建预览URL
      const reader = new FileReader();
      reader.onload = (e) => {
        if (type === "license") {
          this.qualificationForm.licenseImage = e.target.result;
        } else if (type === "workProof") {
          this.qualificationForm.workProofImage = e.target.result;
        }
      };
      reader.readAsDataURL(file);
    },
    removeImage(type) {
      if (type === "license") {
        this.qualificationForm.licenseImage = null;
        if (this.$refs.licenseInput) this.$refs.licenseInput.value = "";
      } else if (type === "workProof") {
        this.qualificationForm.workProofImage = null;
        if (this.$refs.workProofInput) this.$refs.workProofInput.value = "";
      }
    },
    async submitQualification() {
      // 验证表单
      if (!this.qualificationForm.licenseNumber) {
        this.$message.error("请输入医师资格证号");
        return;
      }

      if (!this.qualificationForm.licenseImage) {
        this.$message.error("请上传医师资格证照片");
        return;
      }

      if (!this.qualificationForm.workProofImage) {
        this.$message.error("请上传医院工作证明");
        return;
      }

      try {
        // 创建FormData对象保存资质认证信息
        const formData = new FormData();
        formData.append("license_number", this.qualificationForm.licenseNumber);

        // 将Base64图片转换为Blob对象
        const licenseImageBlob = this.dataURLtoBlob(
          this.qualificationForm.licenseImage
        );
        const workProofBlob = this.dataURLtoBlob(
          this.qualificationForm.workProofImage
        );

        formData.append("license_image", licenseImageBlob, "license.jpg");
        formData.append("work_proof", workProofBlob, "work_proof.jpg");

        if (this.qualificationForm.additionalInfo) {
          formData.append(
            "additional_documents",
            this.qualificationForm.additionalInfo
          );
        }

        // 调用后端API提交资质验证
        const response = await Axios.post(
          "/certification/submit_certification",
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          }
        );

        if (response.data) {
          this.$message.success("资质验证申请已提交，请等待审核");
          this.userInfo.qualificationStatus = response.data.qualificationStatus;
          this.userInfo.qualificationSubmitTime =
            response.data.qualificationSubmitTime;
          console.log(
            "qualificationSubmitTime",
            this.userInfo.qualificationSubmitTime
          );
          // 将资质状态保存到localStorage
          localStorage.setItem("qualificationStatus", "pending");
        }
      } catch (error) {
        this.$message.error(error.response?.data?.error || "提交资质验证失败");
        console.error(error);
      }
    },
  },
};
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.profile-container {
  max-width: 1200px;
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

.profile-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 30px;
}

@media (min-width: 992px) {
  .profile-content {
    grid-template-columns: 1fr 1fr;
  }
}

.profile-card,
.qualification-card,
.qualification-status-card {
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.qualification-card {
  max-height: 600px;
  /* overflow-y: auto; */
  scrollbar-width: thin;
  scrollbar-color: #d0d9ff #f5f7fa;
}

.qualification-card .card-content {
  max-height: 500px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #d0d9ff #f5f7fa;
}

.qualification-card .card-content::-webkit-scrollbar {
  width: 8px;
}

.qualification-card .card-content::-webkit-scrollbar-track {
  background: #f5f7fa;
  border-radius: 4px;
}

.qualification-card .card-content::-webkit-scrollbar-thumb {
  background-color: #d0d9ff;
  border-radius: 4px;
}

.card-header {
  padding: 15px 20px;
  border-bottom: 1px solid #eaedf7;
  background-color: #f9fafd;
}

.card-header h2 {
  margin: 0;
  font-size: 18px;
  color: #333;
  font-weight: 600;
}

.card-header .subtitle {
  font-size: 14px;
  color: #e53935;
  margin-top: 5px;
  display: block;
}

.card-content {
  padding: 20px;
}

/* 个人信息卡片样式 */
.profile-avatar {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
}

.profile-avatar img {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #eaedf7;
  margin-bottom: 10px;
}

.change-avatar-btn {
  background-color: #f5f7ff;
  color: #2d5bff;
  border: 1px solid #d0d9ff;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.change-avatar-btn:hover {
  background-color: #e8edff;
}

.profile-details {
  display: grid;
  grid-template-columns: 1fr;
  gap: 15px;
}

@media (min-width: 576px) {
  .profile-details {
    grid-template-columns: 1fr 1fr;
  }
}

.detail-item {
  display: flex;
  flex-direction: column;
}

.detail-item .label {
  font-size: 14px;
  color: #888;
  margin-bottom: 5px;
}

.detail-item .value {
  font-size: 16px;
  color: #333;
  font-weight: 500;
}

.edit-input {
  width: 80%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.edit-input:focus {
  border-color: #2d5bff;
  outline: none;
}

.edit-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.edit-btn,
.save-btn,
.cancel-btn {
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.edit-btn {
  background-color: #f5f7ff;
  color: #2d5bff;
  border: 1px solid #d0d9ff;
}

.edit-btn:hover {
  background-color: #e8edff;
}

.save-btn {
  background-color: #2d5bff;
  color: white;
  border: none;
}

.save-btn:hover {
  background-color: #1a4ae8;
}

.cancel-btn {
  background-color: #f5f5f5;
  color: #666;
  border: 1px solid #ddd;
}

.cancel-btn:hover {
  background-color: #e8e8e8;
}

.detail-item .status {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
}

.status-none {
  background-color: #f5f5f5;
  color: #757575;
}

.status-pending {
  background-color: #fff8e1;
  color: #ff8f00;
}

.status-approved {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.status-rejected {
  background-color: #ffebee;
  color: #c62828;
}

/* 资质验证表单样式 */
.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #555;
  font-weight: 500;
}

.form-group input[type="text"],
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s ease;
  box-sizing: border-box;
}

.form-group input[type="text"]:focus,
.form-group textarea:focus {
  border-color: #2d5bff;
  outline: none;
}

.upload-area {
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  background-color: #fafafa;
  transition: all 0.2s ease;
}

.upload-area:hover {
  border-color: #2d5bff;
  background-color: #f5f7ff;
}

.upload-btn-wrapper {
  display: inline-block;
}

.upload-btn {
  background-color: #f5f7ff;
  color: #2d5bff;
  border: 1px solid #d0d9ff;
  padding: 10px 15px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s ease;
}

.upload-btn:hover {
  background-color: #e8edff;
}

.preview {
  position: relative;
}

.preview img {
  max-width: 100%;
  max-height: 200px;
  border-radius: 4px;
  border: 1px solid #eaedf7;
}

.remove-btn {
  position: absolute;
  top: -10px;
  right: -10px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: #ff5252;
  color: white;
  border: none;
  font-size: 16px;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.form-actions {
  margin-top: 30px;
  text-align: right;
}
.additional-info-textarea {
  width: 100%;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  line-height: 1.5;
  resize: vertical;
  min-height: 80px;
  padding: 12px 15px;
  transition: all 0.3s ease;
  color: #333;
  background-color: #fff;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
  margin-bottom: 10px;
}

.additional-info-textarea:focus {
  border-color: #2d5bff;
  box-shadow: 0 0 0 2px rgba(45, 91, 255, 0.1);
  outline: none;
}

.additional-info-textarea::placeholder {
  color: #999;
  font-size: 13px;
}

.additional-info-textarea:hover {
  border-color: #2d5bff;
}
.submit-btn {
  background-color: #2d5bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.submit-btn:hover {
  background-color: #1a4ae8;
}

/* 资质状态卡片样式 */
.status-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.status-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.status-icon.pending {
  background-color: #fff8e1;
  color: #ff8f00;
}

.status-icon.approved {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.status-text h3 {
  margin: 0 0 10px 0;
  font-size: 18px;
  font-weight: 600;
}

.status-text p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.submission-date,
.approval-date {
  margin-top: 10px;
  font-size: 13px;
  color: #888;
}
</style>
