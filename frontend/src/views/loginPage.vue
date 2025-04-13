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
  // methods: {
  //   async submitForm() {
  //     // 跳过对邮箱和密码的填写检查，直接跳转到疾病分析页面
  //     // if (this.param.email.trim().length === 0 || this.param.password.trim().length === 0) {
  //     //   return this.$message.error("邮箱或密码未填写");
  //     // }

  //     // 直接跳转到疾病分析页面
  //     this.$router.push({ path: "/diseaseAnalysis" });
  //   },
  // },
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
