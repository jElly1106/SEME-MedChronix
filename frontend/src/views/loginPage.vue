<template>
  <div class="login-body">
    <div class="left-section">
      <!-- 左侧的“智脉时序”图标 -->
      <h1 class="logo-title">智脉时序</h1>
      <h2 class="subtitle">基于深度点过程和VLM的脑卒中</h2>
      <h2 class="subtitle">辅助诊断平台</h2>
    </div>
    <div class="right-section">
      <div class="login-window">
        <div class="login-content">
          <p class="login-title">用户登录</p>
          <div class="login-form">
            <form>
              <input
                type="text"
                name="email"
                class="login-param"
                placeholder="邮箱"
                required
                v-model="param.email"
                @keyup.enter="submitForm()"
              />

              <input
                type="password"
                name="password"
                class="login-param"
                placeholder="密码"
                required
                v-model="param.password"
                @keyup.enter="submitForm()"
              />
              <a-button
                @click="submitForm()"
                style="width: 100%"
                type="primary"
              >
                登录
              </a-button>
            </form>
          </div>
          <div class="login-hint">
            没有账号?
            <router-link to="/register">点击注册</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Axios from "@/utils/axios.js";
export default {
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

          // 普通用户跳转到首页或其他页面
          this.$router.push('/diseaseAnalysis');
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
  },
};
</script>

<style scoped>
/* 主体布局 */
.login-body {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100vh;
  width: 100%;
  background-image: url(../assets/img/bg.jpg);
  background-size: cover;
}

/* 左侧图标部分 */
.left-section {
  flex: 2;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: left;
  position: absolute;
  left: 0;
  top: 120px;
}

.logo-title {
  position: relative;
  left: 15%;
  font: 900 120px "楷体", serif;
  /* color: #3c4ae8; */
  color: #000;
}
.subtitle {
  position: relative;
  left: 5%;
  font: 600 60px "楷体", serif;
  /* color: #3c4ae8; */
  color: #000;
  margin-top: 5%;
}
/* 右侧登录框部分 */
.right-section {
  flex: 1;
  display: flex;
  justify-content: flex-end;
  padding-right: 10%; /* 控制右侧边距 */
}

.login-window {
  background-color: rgba(255, 255, 255, 0.8);
  width: 350px;
  height: 550px;
  display: flex;
  border-radius: 10px;
  justify-content: center;
  align-items: center;
}

.login-content {
  width: 300px;
  height: 450px;
  overflow: hidden;
}

/* 登录框标题 */
.login-title {
  font: 700 40px "楷体", serif;
  margin: 60px 0;
  text-align: center;
  letter-spacing: 5px;
}

/* 输入框样式 */
.login-param {
  width: 100%;
  margin-bottom: 20px;
  outline: none;
  border: 1px solid #ccc;
  border-radius: 5px;
  padding: 10px;
  font-size: 16px;
}

/* 登录提示 */
.login-hint {
  margin: 23px;
  text-align: center;
}
</style>
