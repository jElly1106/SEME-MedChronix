<template>
  <div class="admin-navbar">
    <div class="navbar-container">
      <!-- 左侧区域 - 网站标识 -->
      <div class="logo-container">
        <img src="@/assets/logo.jpg" alt="MedChronix Logo" class="site-logo" />
        <span class="logo-text">智脉时序 - 管理后台</span>
      </div>

      <!-- 右侧区域 - 导航和用户信息 -->
      <div class="right-section">
        <ul class="nav-links">
          <li
            v-for="item in adminNavItems"
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
              src="https://api.dicebear.com/7.x/avataaars/svg?seed=Admin123"
              alt="Admin Avatar"
              class="user-avatar"
            />
            <div class="avatar-indicator admin"></div>
          </div>

          <!-- 下拉菜单 -->
          <div class="dropdown-menu" v-show="showDropdown">
            <div class="dropdown-header">
              <span class="user-name">{{ userName }}</span>
              <span class="user-role">{{ userRole }}</span>
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
  name: "AdminTopNavbar",
  data() {
    return {
      adminNavItems: [
        { name: "资质认证", path: "/qualification-review" },
        { name: "权限管理", path: "/permission-config" },
        { name: "审计日志", path: "/audit-log" },
      ],
      selected: null,
      showDropdown: false,
      // 用户信息，实际应从用户存储或API获取
      userName: "管理员",
      userRole: "系统管理员",
    };
  },
  created() {
    // 根据当前路径设置初始选中项
    const currentPath = this.$route.path;
    const matchedRoute = this.adminNavItems.find(
      (route) => route.path === currentPath
    );
    if (matchedRoute) {
      this.selected = matchedRoute.name;
    } else {
      this.selected = "资质认证"; // 默认选中项
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
      this.$router.push(this.adminNavItems.find((item) => item.name === name).path); // 跳转到对应的路由
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
      localStorage.removeItem("token");
      localStorage.removeItem("qualificationStatus");
      localStorage.removeItem("isAdmin");
      this.$router.push("/");
    },
  },
};
</script>

<style scoped>
.admin-navbar {
  background-color: #1e293b;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.15);
  position: sticky;
  top: 0;
  z-index: 1000;
  padding: 0;
}

.navbar-container {
  display: flex;
  justify-content: space-between;
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
  filter: brightness(1.2);
}

.logo-text {
  font-size: 24px;
  font-weight: 700;
  color: white;
  letter-spacing: 0.5px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  font-family: "STXingkai", "华文行楷", "FZShuTi", "方正舒体", cursive, sans-serif;
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
  font-size: 15px;
  padding: 10px 25px;
  color: #cbd5e1;
  transition: all 0.3s ease;
  margin: 0 4px;
  font-weight: 500;
}

.nav-links li:hover {
  color: #60a5fa;
}

.nav-links li.selected {
  color: #60a5fa;
  font-weight: 600;
}

/* 添加底部选中指示器 */
.selection-indicator {
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0%;
  height: 3px;
  background-color: #60a5fa;
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
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 2px solid #334155;
  transition: all 0.3s ease;
  background-color: #475569;
}

.avatar-container:hover .user-avatar {
  border-color: #60a5fa;
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
  border: 2px solid #1e293b;
}

.avatar-indicator.admin {
  background-color: #f59e0b;
}

.dropdown-menu {
  position: absolute;
  top: 50px;
  right: 0;
  width: 220px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 5px 25px rgba(0, 0, 0, 0.2);
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
  border-bottom: 1px solid #e2e8f0;
  background-color: #f8fafc;
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
  color: #64748b;
  margin-top: 3px;
}

.dropdown-divider {
  height: 1px;
  background-color: #e2e8f0;
  margin: 5px 0;
}

.dropdown-item {
  padding: 12px 15px;
  cursor: pointer;
  display: flex;
  align-items: center;
  color: #334155;
  transition: all 0.2s ease;
}

.dropdown-item:hover {
  background-color: #f1f5f9;
  color: #3b82f6;
}

.dropdown-icon {
  margin-right: 10px;
  font-size: 16px;
}

.dropdown-item.logout {
  color: #ef4444;
}

.dropdown-item.logout:hover {
  background-color: #fef2f2;
  color: #dc2626;
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