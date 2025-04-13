<template>
  <div class="login-body">
    <div class="left-section">
      <h1 class="logo-title">智脉时序</h1>
      <h2 class="subtitle">基于深度点过程和VLM的脑卒中</h2>
      <h2 class="subtitle">辅助诊断平台</h2>
    </div>
    <div class="right-section">
      <div class="login-window">
        <div class="login-content">
          <p class="login-title">用户登录</p>

          <!-- 登录方式切换 -->
          <div class="login-method">
            <a-button
              @click="toggleLoginMethod('account')"
              :type="loginMethod === 'account' ? 'primary' : 'default'"
              class="login-method-btn"
            >
              账号登录
            </a-button>
            <a-button
              @click="toggleLoginMethod('qr')"
              :type="loginMethod === 'qr' ? 'primary' : 'default'"
              class="login-method-btn"
            >
              扫码登录
            </a-button>
          </div>

          <!-- 账号登录 -->
          <div v-if="loginMethod === 'account'" class="login-form">
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
              <a-button @click="submitForm()" style="width: 100%" type="primary">
                登录
              </a-button>
            </form>
          </div>

          <!-- 扫码登录 -->
          <div v-if="loginMethod === 'qr'" class="qr-login">
            <div class="qr-code">
              <img src="LoginTestQR.png" alt="二维码" />
            </div>
            <p class="qr-text">扫描二维码登录</p>
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
      loginMethod: 'account', // 默认显示账号登录
    };
  },
  methods: {
    toggleLoginMethod(method) {
      this.loginMethod = method;
    },
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
          this.$message.success(res.data.message);
          this.$router.push({ path: "/home" });
        }
      } catch (error) {
        this.$message.error(error.response.data.error);
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
  padding: 0 5%;
}

/* 左侧图标部分 */
.left-section {
  flex: 2;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: flex-start;
  position: absolute;
  left: 0;
  top: 120px;
}

.logo-title {
  position: relative;
  left: 15%;
  font: 900 120px "楷体", serif;
  color: #000;
}

.subtitle {
  position: relative;
  left: 5%;
  font: 600 60px "楷体", serif;
  color: #000;
  margin-top: 5%;
}

/* 右侧登录框部分 */
.right-section {
  flex: 1;
  display: flex;
  justify-content: flex-end;
  padding-right: 10%;
  padding-top: 50px; /* 上边距，避免太紧凑 */
}

.login-window {
  background-color: rgba(255, 255, 255, 0.9);
  width: 350px;
  height: 550px;
  display: flex;
  border-radius: 10px;
  justify-content: center;
  align-items: center;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
}

.login-content {
  width: 100%;
  max-width: 300px;
  height: 450px;
  overflow: hidden;
  padding: 20px;
}

/* 登录框标题 */
.login-title {
  font: 700 40px "楷体", serif;
  margin: 20px 0;
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
  transition: border-color 0.3s;
}

.login-param:focus {
  border-color: #3c4ae8;
}

/* 登录方式切换按钮 */
.login-method {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.login-method-btn {
  width: 48%;
  font-size: 14px;
}

/* 扫码登录部分 */
.qr-login {
  text-align: center;
}

.qr-code {
  margin: 20px 0;
}

.qr-code img {
  width: 180px;
  height: 180px;
}

.qr-text {
  font-size: 18px;
  color: #333;
  margin-top: 10px;
}

/* 登录提示 */
.login-hint {
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
}

.login-hint a {
  color: #3c4ae8;
}
</style>
