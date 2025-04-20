<template>
  <div class="register-body">
    <div class="register-window">
      <div class="register-content">
        <p class="register-title">用户注册</p>
        <div class="register-form">
          <form name="myForm">
            <input
              type="email"
              name="email"
              class="register-param"
              v-model="param.email"
              placeholder="用户名"
              required
              @keyup.enter="checkParam()"
            />
            <input
              type="text"
              name="nickname"
              class="register-param"
              v-model="param.nickname"
              placeholder="昵称"
              required
              @keyup.enter="checkParam()"
            />
            <input
              id="pw1"
              type="password"
              name="password1"
              class="register-param"
              v-model="param.password1"
              placeholder="密码"
              required
              @keyup.enter="checkParam()"
            />
            <input
              id="pw2"
              type="password"
              name="password2"
              class="register-param"
              v-model="param.password2"
              placeholder="重复密码"
              required
              @keyup.enter="checkParam()"
            />
            <div class="captcha">
              <input
                type="text"
                name="captcha"
                class="verfi-code-input"
                v-model="param.captcha"
                placeholder="验证码"
                required
                @keyup.enter="checkParam()"
              />
              <a-button
                @click="getCaptcha()"
                :disabled="isButtonDisabled"
                type="primary"
                class="verfi-code-button"
              >
                {{ buttonText }}
              </a-button>
            </div>
            <div class="button-container">
              <a-button
                @click="checkParam()"
                style="width: 90%; margin-top: 10px"
                type="primary"
              >
                注册
              </a-button>
              <a-button
                @click="back2Login()"
                style="width: 90%; margin-bottom: 10px"
                type="dashed"
              >
                返回登录
              </a-button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Axios from "@/utils/axios.js";
import { isEmail } from "validator";

export default {
  data() {
    return {
      param: {
        email: "",
        nickname: "",
        password1: "",
        password2: "",
        captcha: "",
      },
      paramTitle: {
        email: "用户名",
        nickname: "用户昵称",
        password1: "密码",
        password2: "重复密码",
        captcha: "验证码",
      },
      captcha_id: "",
      countdown: 60, // 初始倒计时 60 秒
      isButtonDisabled: false, // 控制按钮是否禁用
      buttonText: "获取验证码", // 按钮显示文本
      timer: null, // 定时器
    };
  },
  created() {
    // 页面加载时检查是否有保存的倒计时
    const savedCountdown = localStorage.getItem("countdown");
    if (savedCountdown) {
      this.countdown = parseInt(savedCountdown);
      if (this.countdown > 0) {
        this.startCountdown();
      }
    }
  },
  methods: {
    async checkParam() {
      for (var i in this.param) {
        if (this.param[i].trim().length == 0)
          return this.$message.error(this.paramTitle[i] + "未填写");
      }

      if (this.param.password1 !== this.param.password2) {
        return this.$message.error("请重新检查，两次输入的密码不一致！");
      } else {
        this.param.userPassword = this.param.password1;
        try {
          const req = {
            email: this.param.email,
            nickname: this.param.nickname,
            password: this.param.password1,
            captcha: this.param.captcha,
            captcha_id: this.param.captcha_id,
          };
          const res = await Axios.post("/user/register", req);
          if (res.success == false) {
            this.$message.error(res.data.message);
          } else {
            this.$message.success(res.data.message);
            this.$router.push({ path: "/login" });
          }
        } catch (error) {
          if (error.response?.data.error) {
            this.$message.error(error.response.data.error);
          } else {
            this.$message.error("网络异常");
          }
        }
      }
    },
    async getCaptcha() {
      if (this.param.email.trim().length == 0) {
        return this.$message.error("邮箱未填写");
      }
      if (!isEmail(this.param.email)) {
        return this.$message.error("邮箱格式错误");
      }
      try {
        const res = await Axios.post("/user/send-captcha", this.param);
        if (res.success == false) {
          this.$message.error(res.data.message);
        } else {
          this.$message.success(res.data.message);
          this.param.captcha_id = res.data.captcha_id;
          this.startCountdown();
        }
        // this.startCountdown();
      } catch (error) {
        if (error.response?.data.error) {
          this.$message.error(error.response.data.error);
        } else {
          console.log(error);
          this.$message.error("网络异常");
        }
      }
    },
    back2Login() {
      this.$router.push({ path: "/login" });
    },
    startCountdown() {
      this.isButtonDisabled = true; // 禁用按钮
      this.timer = setInterval(() => {
        if (this.countdown > 0) {
          this.countdown--;
          this.buttonText = `${this.countdown}秒后重发`; // 更新按钮文本
          // 保存倒计时剩余时间到 localStorage
          localStorage.setItem("countdown", this.countdown);
        } else {
          this.clearCountdown(); // 倒计时结束时清除定时器
        }
      }, 1000);
    },
    clearCountdown() {
      clearInterval(this.timer);
      this.isButtonDisabled = false; // 启用按钮
      this.countdown = 60; // 重置倒计时
      this.buttonText = "获取验证码"; // 重置按钮文本
      // 清除 localStorage 中的倒计时
      localStorage.removeItem("countdown");
    },
  },
};
</script>

<style scoped>
.register-body {
  display: flex;
  justify-content: center;
  background-image: url(../assets/img/bg.jpg);
  height: 100vh;
  width: 100%;
  background-size: cover;
}
.register-window {
  background-color: rgb(255, 255, 255, 0.8);
  width: 600px;
  height: 650px;
  position: relative;
  display: flex;
  border-radius: 10px;
  justify-content: center;
  align-items: center;
  top: 20px;
  margin-top: 70px;
}
.register-content {
  width: 350px;
  height: 700px;
  overflow: hidden;
}
.register-title {
  font: 900 40px bolder;
  margin: 60px 0;
  text-align: center;
  /* 设置字体间距 */
  letter-spacing: 5px;
}
.register-param {
  width: 100%;
  margin-bottom: 20px;
  outline: none;
  border: 0;
  padding: 10px;
  font: 900 16px;
}
.captcha {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.verfi-code-input {
  flex: 1;
  margin-right: 10px;
  width: 100%;
  outline: none;
  border: 0;
  padding: 10px;
  font: 900 16px;
}
.verfi-code-button {
  width: auto;
}

.button-container {
  display: flex;
  flex-direction: column;
  align-items: center; /* 将按钮垂直居中 */
  width: 100%;
  gap: 20px; /* 设置按钮之间的间距 */
}
</style>
