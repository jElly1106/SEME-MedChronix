<template>
  <div class="navbar">
    <div class="navbar-container">
      <!-- 左侧区域 - 网站标识 -->
      <div class="logo-container">
        <img src="../assets/logo.png" alt="MedChronix Logo" class="site-logo" />
        <span class="logo-text">智脉时序</span>
      </div>

      <!-- 右侧区域 - 用户信息 -->
      <div class="right-section">
        <!-- 添加用户头像和下拉菜单 -->
        <div class="user-profile" ref="userProfileRef">
          <div class="avatar-container" @click="toggleDropdown">
            <img
              src="https://api.dicebear.com/7.x/identicon/svg?seed=Guest"
              alt="User Avatar"
              class="user-avatar"
            />
            <span class="login-text">登录/注册</span>
          </div>

          <!-- 下拉菜单 -->
          <div class="dropdown-menu" v-show="showDropdown">
            <div class="dropdown-item" @click="goToLogin">
              <i class="dropdown-icon">🔑</i>
              登录
            </div>
            <div class="dropdown-item" @click="goToRegister">
              <i class="dropdown-icon">📝</i>
              注册
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "LoginTopbar",
  data() {
    return {
      showDropdown: false,
    };
  },
  mounted() {
    // 点击页面其他区域关闭下拉菜单
    document.addEventListener("click", this.handleClickOutside);
  },
  beforeUnmount() {
    document.removeEventListener("click", this.handleClickOutside);
  },
  methods: {
    toggleDropdown() {
      this.showDropdown = !this.showDropdown;
    },
    handleClickOutside(event) {
      if (
        this.$refs.userProfileRef &&
        !this.$refs.userProfileRef.contains(event.target)
      ) {
        this.showDropdown = false;
      }
    },
    goToLogin() {
      this.$router.push("/login");
      this.showDropdown = false;
    },
    goToRegister() {
      this.$router.push("/register");
      this.showDropdown = false;
    },
  },
};
</script>

<style scoped>
.navbar {
  background-color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 1000;
  padding: 0;
}

.navbar-container {
  display: flex;
  justify-content: space-between; /* 两端对齐 */
  align-items: center;
  width: 95%;
  margin: 0 auto;
  padding: 0 20px;
  height: 8vh;
}

/* 左侧区域 */
.logo-container {
  display: flex;
  align-items: center;
}

.site-logo {
  height: 36px;
  margin-right: 10px;
  transition: transform 0.3s ease;
}

.logo-text {
  font-size: 30px;
  font-weight: 700;
  color: #2d5bff;
  letter-spacing: 0.5px;
  text-shadow: 0 2px 4px rgba(45, 91, 255, 0.15);
  font-family: "STXingkai", "华文行楷", "FZShuTi", "方正舒体", cursive,
    sans-serif;
  position: relative;
  background: linear-gradient(135deg, #2d5bff 0%, #7597ff 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
/* 右侧区域 */
.right-section {
  display: flex;
  align-items: center;
}

/* 用户头像和下拉菜单样式 */
.user-profile {
  position: relative;
  margin-left: 20px;
}

.avatar-container {
  cursor: pointer;
  position: relative;
  display: flex;
  align-items: center;
}

.login-text {
  margin-left: 8px;
  font-size: 14px;
  color: #505a6e;
  font-weight: 500;
  transition: color 0.3s ease;
}

.avatar-container:hover .login-text {
  color: #2d5bff;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 2px solid #eaedf7;
  transition: all 0.3s ease;
  background-color: #f5f7ff;
}

.avatar-container:hover .user-avatar {
  border-color: #2d5bff;
  transform: scale(1.05);
}

.dropdown-menu {
  position: absolute;
  top: 50px;
  right: 0;
  width: 180px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 5px 25px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  overflow: hidden;
  animation: dropdown-fade 0.2s ease;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

@keyframes dropdown-fade {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-item {
  padding: 12px 15px;
  cursor: pointer;
  display: flex;
  align-items: center;
  color: #505a6e;
  transition: all 0.2s ease;
}

.dropdown-item:hover {
  background-color: #f5f7ff;
  color: #2d5bff;
}

.dropdown-icon {
  margin-right: 10px;
  font-size: 16px;
}

/* 添加响应式设计 */
@media (max-width: 768px) {
  .logo-text {
    font-size: 18px;
  }

  .login-text {
    font-size: 13px;
  }

  .user-avatar {
    width: 32px;
    height: 32px;
  }

  .dropdown-menu {
    width: 160px;
  }
}
</style>
