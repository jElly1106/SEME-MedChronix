<template>
  <div class="navbar">
    <div class="navbar-container">
      <!-- 左侧区域 - 网站标识 -->
      <div class="logo-container">
        <img src="@/assets/logo.jpg" alt="MedChronix Logo" class="site-logo" />
        <span class="logo-text">MedChronix</span>
      </div>

      <!-- 右侧区域 - 导航和用户信息 -->
      <div class="right-section">
        <ul class="nav-links">
          <li
            v-for="item in items"
            :key="item.name"
            :class="{ selected: selected === item.name }"
            @click="selectItem(item.name)"
          >
            <span>{{ item.name }}</span>
            <div class="selection-indicator"></div>
          </li>
        </ul>

        <!-- 添加用户头像和下拉菜单 -->
        <div class="user-profile" ref="userProfileRef">
          <div class="avatar-container" @click="toggleDropdown">
            <img
              src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix"
              alt="User Avatar"
              class="user-avatar"
            />
            <div class="avatar-indicator"></div>
          </div>

          <!-- 下拉菜单 -->
          <div class="dropdown-menu" v-show="showDropdown">
            <div class="dropdown-header">
              <span class="user-name">王医生</span>
              <span class="user-role">主治医师</span>
            </div>
            <div class="dropdown-divider"></div>
            <div class="dropdown-item" @click="goToUserProfile">
              <i class="dropdown-icon">👤</i>
              个人信息管理
            </div>
            <div class="dropdown-item logout" @click="logout">
              <i class="dropdown-icon">🚪</i>
              退出登录
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "TopNavbar",
  data() {
    return {
      items: [{ name: "总体概览" }, { name: "疾病分析" }, { name: "病人详情" }],
      routers: [
        { name: "总体概览", path: "/home" },
        { name: "疾病分析", path: "/diseaseAnalysis" },
        { name: "病人详情", path: "/patientAnalysis" },
      ],
      selected: null,
      showDropdown: false,
    };
  },
  created() {
    // 根据当前路径设置初始选中项
    const currentPath = this.$route.path;
    const matchedRoute = this.routers.find(
      (route) => route.path === currentPath
    );
    if (matchedRoute) {
      this.selected = matchedRoute.name;
    } else {
      this.selected = "总体概览"; // 默认选中项
    }
  },
  mounted() {
    // 点击页面其他区域关闭下拉菜单
    document.addEventListener("click", this.handleClickOutside);
  },
  beforeUnmount() {
    document.removeEventListener("click", this.handleClickOutside);
  },
  methods: {
    selectItem(name) {
      this.selected = name; // 更新选中的项
      this.$router.push(this.routers.find((item) => item.name === name).path); // 跳转到对应的路由
    },
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
    goToUserProfile() {
      this.$router.push("/profile");
      this.showDropdown = false;
    },
    logout() {
      // 执行登出逻辑
      this.$message.success("已退出登录");
      // 通常会删除存储的 token，并跳转到登录页面
      // localStorage.removeItem('token');
      this.$router.push("/login");
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
  height: 70px;
}

/* 左侧区域 */
.logo-container {
  display: flex;
  align-items: center;
}

.site-logo {
  height: 40px;
  margin-right: 12px;
  transition: transform 0.3s ease;
}

.site-logo:hover {
  transform: scale(1.05);
}

.logo-text {
  font-size: 20px;
  font-weight: 600;
  color: #2d5bff;
  letter-spacing: 0.5px;
}

/* 右侧区域 */
.right-section {
  display: flex;
  align-items: center;
}

.nav-links {
  list-style-type: none;
  display: flex;
  margin: 0;
  padding: 0;
}

.nav-links li {
  position: relative;
  cursor: pointer;
  font-size: 16px;
  padding: 10px 25px;
  color: #505a6e; /* 默认深灰色 */
  transition: all 0.3s ease;
  margin: 0 4px;
  font-weight: 500;
}

.nav-links li:hover {
  color: #2d5bff;
}

.nav-links li.selected {
  color: #2d5bff;
  font-weight: 600;
}

/* 添加底部选中指示器 */
.selection-indicator {
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0%;
  height: 3px;
  background-color: #2d5bff;
  transition: all 0.3s ease;
  opacity: 0;
  border-radius: 2px;
}

.nav-links li.selected .selection-indicator {
  width: 100%;
  opacity: 1;
}

.nav-links li:hover .selection-indicator {
  width: 100%;
  opacity: 0.5;
}

/* 用户头像和下拉菜单样式 */
.user-profile {
  position: relative;
  margin-left: 20px;
}

.avatar-container {
  cursor: pointer;
  position: relative;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid #eaedf7;
  transition: all 0.3s ease;
  background-color: #f5f7ff;
}

.avatar-container:hover .user-avatar {
  border-color: #2d5bff;
  transform: scale(1.05);
}

.avatar-indicator {
  position: absolute;
  bottom: 2px;
  right: 0;
  width: 10px;
  height: 10px;
  background-color: #4caf50;
  border-radius: 50%;
  border: 2px solid white;
}

.dropdown-menu {
  position: absolute;
  top: 55px;
  right: 0;
  width: 220px;
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

.dropdown-header {
  padding: 15px;
  border-bottom: 1px solid #eaedf7;
  background-color: #f9fafd;
  display: flex;
  flex-direction: column;
}

.user-name {
  font-weight: 600;
  font-size: 16px;
  color: #333;
}

.user-role {
  font-size: 13px;
  color: #888;
  margin-top: 3px;
}

.dropdown-divider {
  height: 1px;
  background-color: #eaedf7;
  margin: 5px 0;
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

.dropdown-item.logout {
  color: #e53935;
}

.dropdown-item.logout:hover {
  background-color: #fff5f5;
  color: #d32f2f;
}

/* 添加响应式设计 */
@media (max-width: 768px) {
  .logo-text {
    font-size: 18px;
  }

  .nav-links li {
    padding: 10px 15px;
    font-size: 14px;
  }

  .user-avatar {
    width: 35px;
    height: 35px;
  }

  .dropdown-menu {
    width: 200px;
  }
}
</style>
