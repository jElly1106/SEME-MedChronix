<template>
  <div class="register-page">
    <!-- 返回首页按钮 -->
    <button class="back-home-btn" @click="goToDashboard()">
      <i class="fa fa-arrow-left"></i> 返回首页
    </button>

    <div class="register-container">
      <div class="register-card">
        <h2 class="register-title">用户注册</h2>
        <div class="register-form">
          <div class="form-group">
            <label for="email">邮箱</label>
            <input
              type="email"
              id="email"
              v-model="param.email"
              placeholder="请输入邮箱"
              @keyup.enter="checkParam()"
            />
          </div>
          <!-- 其他表单项保持不变 -->
          <div class="form-group">
            <label for="nickname">姓名</label>
            <input
              type="text"
              id="nickname"
              v-model="param.nickname"
              placeholder="请输入姓名"
              @keyup.enter="checkParam()"
            />
          </div>
          <div class="form-group">
            <label for="password1">密码</label>
            <input
              type="password"
              id="password1"
              v-model="param.password1"
              placeholder="请输入密码"
              @keyup.enter="checkParam()"
            />
          </div>
          <div class="form-group">
            <label for="password2">确认密码</label>
            <input
              type="password"
              id="password2"
              v-model="param.password2"
              placeholder="请再次输入密码"
              @keyup.enter="checkParam()"
            />
          </div>
          <div class="form-group captcha-group">
            <label for="captcha">验证码</label>
            <div class="captcha-input">
              <input
                type="text"
                id="captcha"
                v-model="param.captcha"
                placeholder="请输入验证码"
                @keyup.enter="checkParam()"
              />
              <button
                class="captcha-btn"
                @click="getCaptcha()"
                :disabled="isButtonDisabled"
              >
                {{ buttonText }}
              </button>
            </div>
          </div>
          <div class="form-actions">
            <button class="register-btn" @click="checkParam()">注册</button>
            <button class="login-btn" @click="back2Login()">返回登录</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Axios from "@/utils/axios.js";
import { isEmail } from "validator";

export default {
  // 移除 LoginTopbar 组件
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
        nickname: "姓名",
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
    goToDashboard() {
      this.$router.push({ path: "/" });
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
.register-page {
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

.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  flex: 1;
  padding: 20px;
}

.register-card {
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 450px; /* 调整卡片宽度 */
  padding: 30px;
}

.register-title {
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

.captcha-group {
  margin-bottom: 25px;
}

.captcha-input {
  display: flex;
  gap: 10px;
}

.captcha-input input {
  flex: 1;
}

.captcha-btn {
  background-color: #2d5bff;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0 15px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s;
  white-space: nowrap;
  min-width: 110px; /* 确保按钮有足够宽度 */
}

.captcha-btn:hover:not(:disabled) {
  background-color: #1a46e0;
}

.captcha-btn:disabled {
  background-color: #a0aec0;
  cursor: not-allowed;
}

.form-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 20px;
}

.register-btn {
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

.register-btn:hover {
  background-color: #1a46e0;
}

.login-btn {
  background-color: #f0f2f5;
  color: #333;
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
  background-color: #e1e4e8;
}
</style>
