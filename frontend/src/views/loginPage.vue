<template>
  <div class="login-page">
    <!-- 返回首页按钮 -->
   

    <div class="login-container">
      <div class="login-card">
        <h2 class="login-title">用户登录</h2>
        <div class="login-form">
          <div class="form-group">
            <label for="email">邮箱</label>
            <input
              type="text"
              id="email"
              v-model="param.email"
              placeholder="请输入邮箱"
              @keyup.enter="submitForm()"
            />
          </div>
          <div class="form-group">
            <label for="password">密码</label>
            <input
              type="password"
              id="password"
              v-model="param.password"
              placeholder="请输入密码"
              @keyup.enter="submitForm()"
            />
          </div>
          <div class="form-actions">
            <button class="login-btn" @click="submitForm()">登录</button>
          </div>
          <div class="login-footer">
            <p>没有账号? <router-link to="/register">点击注册</router-link></p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Axios from "@/utils/axios.js";

export default {
  // 移除 LoginTopbar 组件
  data() {
    return {
      param: {
        email: "",
        password: "",
      },
      paramTitle: {
        email: "邮箱",
        password: "密码",
      },
    };
  },
  methods: {
    async submitForm() {
      for (var i in this.param) {
        if (this.param[i].trim().length == 0)
          return this.$message.error(this.paramTitle[i] + "未填写");
      }
      try {
        const res = await Axios.post("/user/login", this.param);
        if (res.success == false) {
          this.$message.error(res.data.message);
        } else {
          localStorage.setItem("token", res.data.token);
          localStorage.setItem("user_id", res.data.user_id);

          // 存储用户资质验证状态
          if (res.data.qualificationStatus) {
            localStorage.setItem(
              "qualificationStatus",
              res.data.qualificationStatus
            );
          } else {
            // 如果后端未返回资质状态，默认设为未验证
            localStorage.setItem("qualificationStatus", "none");
          }

          // 存储用户是否为管理员
          if (res.data.isAdmin) {
            localStorage.setItem("isAdmin", res.data.isAdmin);
          }
          if (res.data.isAuth) {
            localStorage.setItem("qualificationStatus", res.data.isAuth);
          }
          this.$message.success(res.data.message);
          this.$router.push({ path: "/diseaseAnalysis" });
        }
      } catch (error) {
        this.$message.error(error.response.data.error);
      }
    },
    goToDashboard() {
      this.$router.push({ path: "/" });
    },
  },
};
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background-color: #e5eafc;
  display: flex;
  flex-direction: column;
  position: relative;
}

/* 新增返回首页按钮样式 */
.back-home-btn {
  position: absolute;
  top: 20px;
  left: 20px;
  background-color: #ffffff;
  color: #2d5bff;
  border: none;
  border-radius: 6px;
  padding: 10px 15px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.back-home-btn:hover {
  background-color: #f0f2f5;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  flex: 1;
  padding: 20px;
}

.login-card {
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px; /* 调整卡片宽度 */
  padding: 30px;
}

.login-title {
  color: #2d5bff;
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 30px;
  text-align: center;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

/* 调整输入框大小和样式 */
.form-group input {
  width: 100%;
  height: 45px; /* 固定高度 */
  padding: 0 15px; /* 调整内边距 */
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 15px;
  transition: border-color 0.3s;
  box-sizing: border-box; /* 确保宽度包含内边距和边框 */
}

.form-group input:focus {
  border-color: #2d5bff;
  outline: none;
  box-shadow: 0 0 0 2px rgba(45, 91, 255, 0.1);
}

.form-actions {
  margin-top: 30px;
}

.login-btn {
  width: 100%;
  background-color: #2d5bff;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 12px;
  height: 45px; /* 固定高度 */
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
}

.login-btn:hover {
  background-color: #1a46e0;
}

.login-footer {
  margin-top: 25px;
  text-align: center;
  color: #666;
}

.login-footer a {
  color: #2d5bff;
  text-decoration: none;
  font-weight: 500;
}

.login-footer a:hover {
  text-decoration: underline;
}
</style>
