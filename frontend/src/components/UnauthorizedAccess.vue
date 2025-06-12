<template>
  <div class="unauthorized-page">
    <div class="unauthorized-container">
      <i class="fas fa-lock unauthorized-icon"></i>
      <h2>无权访问</h2>
      <p>您需要完成医师资质验证才能访问此页面</p>
      <router-link to="/profile" class="verify-button"> 前往验证 </router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: "UnauthorizedAccess",
};
</script>

<style scoped>
.unauthorized-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.unauthorized-container {
  text-align: center;
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.unauthorized-icon {
  font-size: 48px;
  color: #ff4d4f;
  margin-bottom: 20px;
}

.unauthorized-container h2 {
  font-size: 24px;
  color: #333;
  margin-bottom: 16px;
}

.unauthorized-container p {
  color: #666;
  margin-bottom: 24px;
}

.verify-button {
  display: inline-block;
  padding: 10px 24px;
  background-color: #2d5bff;
  color: white;
  border-radius: 4px;
  text-decoration: none;
  transition: background-color 0.2s ease;
}

.verify-button:hover {
  background-color: #1a4ae8;
}
</style>
