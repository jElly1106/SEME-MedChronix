<template>
  <div class="login-page">
    <!-- 返回首页按钮 -->
    <button class="back-home-btn" @click="goToDashboard()">
      <i class="fa fa-arrow-left"></i> 返回首页
    </button>

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
import { ElMessage } from 'element-plus';



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
      try {
        // 简单的表单验证
        if (!this.param.email) {
          ElMessage.error('请输入邮箱');
          return;
        }
        if (!this.param.password) {
          ElMessage.error('请输入密码');
          return;
        }
        
        // 显示加载状态
        this.loading = true;
        
        // 发送登录请求
        const response = await Axios.post('/user/login', {
          email: this.param.email,
          password: this.param.password
        });
        
        // 确保 response 存在且有 data 属性
        if (response && response.data) {
          // 处理登录成功
          localStorage.setItem('token', response.data.token);
          localStorage.setItem('qualificationStatus', response.data.qualificationStatus);
          localStorage.setItem('isAdmin', response.data.is_admin);

          if (response.data.role === 'admin') {
            // 管理员用户直接跳转到资质认证页面
            this.$router.push('/qualification-review');
          } else {
            // 普通用户跳转到首页或其他页面
            this.$router.push('/home');
          }
          
          ElMessage.success('登录成功');
          
        } else {
          // 响应存在但没有预期的数据
          ElMessage.error('登录失败：服务器响应异常');
          console.error('登录响应异常:', response);
        }
      } catch (error) {
        // 处理错误
        if (error.response && error.response.data) {
          // 服务器返回了错误信息
          ElMessage.error(`登录失败：${error.response.data.message || '未知错误'}`);
        } else if (error.message) {
          // 请求过程中发生错误
          ElMessage.error(`登录失败：${error.message}`);
        } else {
          // 其他未知错误
          ElMessage.error('登录失败：网络错误或服务器无响应');
        }
        console.error('登录错误:', error);
      } finally {
        // 无论成功或失败，都关闭加载状态
        this.loading = false;
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
