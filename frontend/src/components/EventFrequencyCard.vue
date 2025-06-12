<template>
  <div class="event-frequency-card">
    <!-- 卡片标题区 -->
    <div class="card-header">
      <span>异常事件频次</span>
    </div>

    <!-- 搜索框：输入框 + 按钮（带放大镜图标） -->
    <div class="search-box">
      <input type="text" v-model="searchText" placeholder="搜索事件..." />
      <button class="search-btn" @click="handleSearch">
        <!-- 放大镜图标，可使用 iconfont 或 Unicode符号等 -->
        <span class="icon-search">🔍</span>
      </button>
    </div>

    <!-- 事件列表 -->
    <div class="events-list">
      <div class="event-item" v-for="event in filteredEvents" :key="event.name">
        <div class="event-name">
          {{ event.name }}
        </div>
        <div class="bar-container">
          <div
            class="bar"
            :style="{ width: calcBarWidth(event.count) + 'px' }"
          ></div>
        </div>
        <div class="event-count">
          {{ event.count }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "EventFrequencyCard",
  props: {
    eventsData: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      searchText: "",
    };
  },
  computed: {
    filteredEvents() {
      const lowerSearch = this.searchText.toLowerCase();
      return this.eventsData
        .filter((ev) => ev.name.toLowerCase().includes(lowerSearch))
        .sort((a, b) => b.count - a.count);
    },
  },
  methods: {
    handleSearch() {
      // 这里编写点击放大镜后要执行的筛选逻辑
      // 当前示例里已经在 computed 里实现了搜索过滤
      // 你也可以在这里发请求或做更多处理
      console.log("搜索事件：", this.searchText);
    },
    calcBarWidth(count) {
      const maxCount = 500;
      const maxBarWidth = 100;
      const ratio = Math.min(count / maxCount, 1);
      return ratio * maxBarWidth;
    },
  },
};
</script>

<style scoped>
.event-frequency-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  min-height: 280px;
  padding: 16px;
  display: flex;
  flex-direction: column;
}

.card-header {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #343c6a;
}

/* 搜索框布局：让输入框变窄，旁边是一个按钮 */
.search-box {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.search-box input {
  width: 90%; /* 让输入框变窄 */
  padding: 6px 8px;
  border: 1px solid #ddd;
  border-radius: 4px 0 0 4px; /* 左侧圆角 */
  outline: none;
  font-size: 14px;
}

.search-btn {
  width: 10%; /* 让按钮占剩余空间，也可以写固定宽度 */
  background-color: #2d5bff;
  border: 1px solid #2d5bff;
  border-radius: 0 4px 4px 0; /* 右侧圆角 */
  color: #fff;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.search-btn:hover {
  background-color: #1e4ed8; /* 悬停颜色，可根据需求微调 */
}

/* 事件列表 */
.events-list {
  overflow-y: auto;
  max-height: 230px;
}

.event-item {
  display: flex;
  align-items: center;
  padding: 4px 0;
}

.event-name {
  flex: 0 0 150px; /* 调整为150px或更大，根据需求 */
  font-size: 14px;
  color: #333;
  padding-left: 4px;
}

.bar-container {
  flex: 1;
  padding: 0 8px;
  display: flex;
  align-items: center;
}

.bar {
  height: 6px;
  background-color: #2d5bff;
  border-radius: 3px;
}

.event-count {
  width: 40px;
  text-align: right;
  font-size: 14px;
  color: #333;
}

/* 放大镜图标（可换成 iconfont 或 SVG） */
.icon-search {
  font-size: 16px;
}
</style>
