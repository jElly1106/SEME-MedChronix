<template>
  <div class="homePage">
    <TopNavbar />
    <p>这是主页</p>
  </div>
</template>

<script>
import TopNavbar from "@/components/TopNavbar.vue"; // 导入上边栏组件
export default {
  name: "homePage",
  components: {
    TopNavbar,
  },
};
</script>
