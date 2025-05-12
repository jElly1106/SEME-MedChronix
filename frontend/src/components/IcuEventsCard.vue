<template>
  <div class="icu-events-card">
    <!-- 标题 -->
    <div class="card-title">ICU 异常事件</div>

    <!-- 搜索 & 筛选栏 -->
    <div class="search-filter-bar">
      <!-- 左侧查找图标 -->
      <div class="icon search-icon" @click="filterAction">
        <i class="fa fa-search"></i>
      </div>
      <!-- 搜索输入框 -->
      <input
        type="text"
        class="search-input"
        placeholder="输入姓名..."
        v-model="searchName"
        @input="handleSearch"
      />
      <!-- 右侧筛选图标 -->
      <div class="icon filter-icon" @click="togglePopup">
        <i class="fa fa-filter"></i>
      </div>
    </div>

    <!-- 患者列表 -->
    <div class="patient-list">
      <!-- 添加空状态提示 -->
      <div v-if="filteredPatients.length === 0" class="empty-state">
        <i class="fa fa-info-circle"></i>
        <p>没有匹配的患者数据</p>
      </div>
      <div
        class="patient-item"
        v-for="(patient, pIndex) in filteredPatients"
        :key="pIndex"
      >
        <!-- 左侧：头像 + 姓名、年龄 -->
        <div class="patient-left">
          <img :src="patient.avatar" alt="avatar" class="avatar" />
          <div class="gray-bar">
            <div class="patient-name">{{ patient.name }}</div>
            <div class="patient-age">年龄: {{ patient.age }}</div>
          </div>
        </div>

        <!-- 右侧：事件蛇形排布 -->
        <div class="patient-right">
          <div
            class="events-container"
            :style="{
              width: calcContainerWidth(getEventCodes(patient).length) + 'px',
              height: calcContainerHeight(getEventCodes(patient).length) + 'px',
            }"
          >
            <!-- 1) 每个事件小矩形 -->
            <div
              v-for="(event, eIndex) in getEventCodes(patient)"
              :key="eIndex"
              class="event-box"
              :style="calcEventBoxStyle(eIndex, getEventCodes(patient).length)"
              :title="getEventName(patient, eIndex)"
            >
              {{ event }}
            </div>

            <!-- 2) SVG 连线，连接所有事件的中心点 -->
            <svg
              class="events-line"
              :width="calcContainerWidth(getEventCodes(patient).length)"
              :height="calcContainerHeight(getEventCodes(patient).length)"
            >
              <polyline
                :points="calcLinePoints(getEventCodes(patient).length)"
                stroke="#999"
                fill="none"
                stroke-width="2"
              />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- 弹出的筛选浮窗 -->
    <div v-if="popupVisible" class="popup-overlay" @click.self="closePopup">
      <div class="popup-content">
        <div class="close-buttons">
          <i class="fa fa-times close-icon" @click="closePopup"></i>
        </div>
        <div class="type">
          <h3>筛选选项</h3>
        </div>
        <!-- 脑卒中类型 -->
        <!-- 脑卒中类型多选 -->
        <div class="type_filter-item">
          <div class="type_header" @click="toggleCollapse">
            <span>脑卒中类型:</span>
            <!-- 使用 Font Awesome 图标来表示收缩状态 -->
            <i
              class="fa"
              :class="{
                'fa-chevron-down': type_collapsed,
                'fa-chevron-up': !type_collapsed,
              }"
            ></i>
          </div>
          <!-- 收缩区域内容：复选框部分 -->
          <div class="type-content" v-if="!type_collapsed">
            <div class="checkbox-group">
              <!-- 遍历所有选项，每个选项为一个复选框 -->
              <label
                v-for="option in strokeOptions"
                :key="option.value"
                class="checkbox-label"
              >
                <input
                  type="checkbox"
                  :value="option.label"
                  v-model="choose_type"
                />
                {{ option.label }}
              </label>
            </div>
          </div>
        </div>
        <!-- 进入 ICU 时间 -->
        <div class="filter-item">
          <label>进入 ICU 时间范围:</label>
          <!-- 将单个日期选择器改为日期范围选择器 -->
          <el-date-picker
            v-model="icuEntryDateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="yyyy-MM-dd"
            value-format="yyyy-MM-dd"
          >
          </el-date-picker>
        </div>
        <!-- 离开 ICU 时间 -->
        <div class="filter-item">
          <label>离开 ICU 时间范围:</label>
          <el-date-picker
            v-model="icuExitDateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="yyyy-MM-dd"
            value-format="yyyy-MM-dd"
          >
          </el-date-picker>
        </div>
        <!-- 操作按钮 -->
        <div class="popup-footer">
          <button class="reset-btn" @click="resetFilters">重置</button>
          <button class="apply-btn" @click="applyFilters" :disabled="loading">
            {{ loading ? '加载中...' : '应用' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Axios from "@/utils/axios";

export default {
  name: "IcuEventsCard",
  props: {
    patients: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      // 原有属性保持不变
      maxCols: 4,
      boxWidth: 50,
      boxHeight: 30,
      rowGap: 5,

      // 新增：搜索关键字
      searchName: "",
      strokeOptions: [
        { label: "缺血性脑卒中", value: "0" },
        { label: "出血性脑卒中", value: "1" },
        { label: "短暂性脑缺血发作", value: "2" },
        { label: "其他类型", value: "3" },
      ],

      choose_type: [],
      popupVisible: false,
      type_collapsed: false,
      // 修改为日期范围
      icuEntryDateRange: null, // [开始日期, 结束日期]
      icuExitDateRange: null,  // [开始日期, 结束日期]

      // 新增：存储筛选后的患者数据
      filteredPatientsData: [],
      // 新增：加载状态
      loading: false,
    };
  },
  computed: {
    filteredPatients() {
      // 如果有筛选后的数据，优先使用筛选后的数据
      const patientsToFilter = this.filteredPatientsData.length > 0 ? 
                              this.filteredPatientsData : this.patients;
      
      // 添加日志，查看筛选前的数据
      console.log('筛选前的数据:', patientsToFilter);
      
      // 按搜索关键字过滤
      const result = patientsToFilter.filter((p) => {
        // 忽略大小写匹配
        return p.name.toLowerCase().includes(this.searchName.toLowerCase());
      });
      
      // 添加日志，查看筛选后的结果
      console.log('最终显示的患者数据:', result);
      
      return result;
    },
  },
  methods: {
    // 新增方法：获取患者的事件代码列表
    getEventCodes(patient) {
      // 如果后端返回了 event_codes 数组，直接使用
      if (patient.event_codes && Array.isArray(patient.event_codes)) {
        return patient.event_codes;
      }
      
      // 如果后端返回了 events 数组但格式是对象，提取事件代码
      if (patient.events && Array.isArray(patient.events)) {
        // 检查 events 是否为对象数组
        if (typeof patient.events[0] === 'object') {
          // 从事件对象中提取事件名称的前4个字符作为代码
          return patient.events.map(event => {
            if (event.name) {
              return event.name.substring(0, 4);
            } else {
              return "未知";
            }
          });
        } else {
          // 如果 events 是字符串数组，直接返回
          return patient.events;
        }
      }
      
      // 默认返回空数组
      return [];
    },
    
    // 新增方法：获取事件的完整名称（用于提示）
    getEventName(patient, index) {
      if (patient.events && Array.isArray(patient.events)) {
        // 检查 events 是否为对象数组
        if (typeof patient.events[0] === 'object' && patient.events[index]) {
          return patient.events[index].name || "未知事件";
        }
      }
      return "事件详情";
    },
    
    // 添加缺失的 handleSearch 方法
    handleSearch() {
      // 搜索功能已在 computed 属性中实现
      // 这里可以添加额外的搜索逻辑
    },
    async applyFilters() {
      try {
        this.loading = true;
        
        // 准备请求数据
        const filterData = {
          status: this.choose_type, // 已经是 label 列表了
        };
        
        // 添加 ICU 入院时间范围（如果有设置）
        if (this.icuEntryDateRange && this.icuEntryDateRange.length === 2) {
          // 设置开始时间
          filterData.in_icu_start = this.formatDateTime(this.icuEntryDateRange[0], true);
          // 设置结束时间
          filterData.in_icu_end = this.formatDateTime(this.icuEntryDateRange[1], false);
        }
        
        // 添加 ICU 出院时间范围（如果有设置）
        if (this.icuExitDateRange && this.icuExitDateRange.length === 2) {
          // 设置开始时间
          filterData.out_icu_start = this.formatDateTime(this.icuExitDateRange[0], true);
          // 设置结束时间
          filterData.out_icu_end = this.formatDateTime(this.icuExitDateRange[1], false);
        }
        
        // 获取 token（假设已存储在 localStorage 中）
        const token = localStorage.getItem('token');
        
        console.log('发送筛选请求数据:', filterData);
        
        // 发送筛选请求
        const response = await Axios.post('/patient/filter', filterData, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        console.log('筛选结果:', response.data);
        
        // 处理返回的患者数据，转换为组件需要的格式
        if (response.data !== undefined) {
          // 即使是空数组也要设置，确保视图更新
          this.filteredPatientsData = Array.isArray(response.data) ? response.data.map(patient => {
            // 从后端获取的患者数据可能需要转换为前端组件需要的格式
            return {
              name: patient.name || '未知姓名',
              age: patient.age || 0,
              avatar: patient.avatar || `https://picsum.photos/seed/patient${patient.id || Math.random()}/200/200`,
              events: patient.events || [],
              event_codes: patient.event_codes || []
            };
          }) : [];
          
          // 添加日志，查看处理后的数据
          console.log('处理后的筛选数据:', this.filteredPatientsData);
          
          // 如果筛选结果为空，可以显示一个提示
          if (this.filteredPatientsData.length === 0) {
            console.log('筛选结果为空，没有匹配的患者');
          }
        }
      } catch (error) {
        console.error('筛选患者数据失败:', error);
        // 可以添加错误处理逻辑，例如显示错误消息
      } finally {
        this.loading = false;
        this.popupVisible = false; // 关闭弹窗
      }
    },
    
    // 修改：重置筛选器的逻辑，同时清空筛选结果
    resetFilters() {
      this.choose_type = [];
      this.icuEntryDateRange = null;
      this.icuExitDateRange = null;
      this.filteredPatientsData = []; // 清空筛选结果，恢复使用 props 传入的数据
    },
    
    // 新增：格式化日期时间为后端需要的格式
    formatDateTime(date, isStartOfDay) {
      if (!date) return null;
      
      // 创建日期对象
      const dateObj = new Date(date);
      
      // 设置时间为当天的开始或结束
      if (isStartOfDay) {
        dateObj.setHours(0, 0, 0, 0);
      } else {
        dateObj.setHours(23, 59, 59, 999);
      }
      
      // 格式化为 YYYY-MM-DD HH:MM:SS
      const year = dateObj.getFullYear();
      const month = String(dateObj.getMonth() + 1).padStart(2, '0');
      const day = String(dateObj.getDate()).padStart(2, '0');
      const hours = String(dateObj.getHours()).padStart(2, '0');
      const minutes = String(dateObj.getMinutes()).padStart(2, '0');
      const seconds = String(dateObj.getSeconds()).padStart(2, '0');
      
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    },
    
    toggleCollapse() {
      this.type_collapsed = !this.type_collapsed;
    },
    closePopup() {
      this.popupVisible = false;
    },
    togglePopup() {
      this.popupVisible = true;
    },
    filterAction() {},

    // 以下为原本的事件蛇形布局方法
    calcContainerWidth() {
      return this.maxCols * this.boxWidth;
    },
    calcContainerHeight(total) {
      const rows = Math.ceil(total / this.maxCols);
      return rows * (this.boxHeight + this.rowGap);
    },
    calcEventBoxStyle(index) {
      const row = Math.floor(index / this.maxCols);
      const col = index % this.maxCols;

      let x;
      if (row % 2 === 0) {
        // 偶数行：左到右
        x = col * this.boxWidth;
      } else {
        // 奇数行：右到左
        x = (this.maxCols - 1 - col) * this.boxWidth;
      }
      const y = row * (this.boxHeight + this.rowGap);

      // 使事件矩形在单元内居中显示
      const actualWidth = 30; // 事件矩形实际宽度
      const actualHeight = 16; // 事件矩形实际高度
      const offsetX = (this.boxWidth - actualWidth) / 2;
      const offsetY = (this.boxHeight - actualHeight) / 2;

      return {
        position: "absolute",
        left: x + offsetX + "px",
        top: y + offsetY + "px",
      };
    },
    calcLinePoints(total) {
      const pointsArr = [];
      for (let i = 0; i < total; i++) {
        const row = Math.floor(i / this.maxCols);
        const col = i % this.maxCols;

        let x;
        if (row % 2 === 0) {
          x = col * this.boxWidth;
        } else {
          x = (this.maxCols - 1 - col) * this.boxWidth;
        }
        const y = row * (this.boxHeight + this.rowGap);

        // 中心点
        const centerX = x + this.boxWidth / 2;
        const centerY = y + this.boxHeight / 2;
        pointsArr.push([centerX, centerY]);
      }
      return pointsArr.map((point) => point.join(",")).join(" ");
    },
  },
};
</script>

<style scoped>
.icu-events-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  width: 300px; /* 你想要的固定宽度 */
  min-height: 360px;
  overflow: auto;
  padding: 16px;
}

/* 标题 */
.card-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #343c6a;
}

/* 搜索 & 筛选栏 */
.search-filter-bar {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  /* 可根据需要加上背景或边框 */
}
.icon-search {
  /* 替换成你自己使用的图标库样式或SVG */
  width: 16px;
  height: 16px;
  background: url("data:image/svg+xml;base64,...") no-repeat center / cover;
  margin-right: 6px;
  cursor: pointer;
}
.search-input {
  flex: 1;
  padding: 4px 8px;
  font-size: 14px;
  margin-right: 6px;
}
.icon-filter {
  /* 替换成你自己使用的图标库样式或SVG */
  width: 16px;
  height: 16px;
  background: url("data:image/svg+xml;base64,...") no-repeat center / cover;
  cursor: pointer;
}

/* 患者列表 */
.patient-list {
  max-height: 300px;
}
.patient-item {
  display: flex;
  margin-bottom: 16px;
}

/* 左侧：头像 + 灰色栏 */
.patient-left {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-right: 8px;
}
.avatar {
  width: 50px;
  height: 50px;
  border-radius: 4px;
  object-fit: cover;
  margin-bottom: 4px;
}
.gray-bar {
  width: 80px;
  background-color: #eee;
  border-radius: 4px;
  padding: 4px;
  text-align: center;
}
.patient-name {
  font-weight: bold;
  font-size: 14px;
}
.patient-age {
  font-size: 12px;
  color: #666;
}

/* 右侧：事件蛇形排布 */
.patient-right {
  flex: 1; /* 占满剩余空间 */
}
.events-container {
  position: relative;
  border-radius: 4px;
  background-color: #fff;
}
.event-box {
  width: 40px;
  height: 16px;
  background-color: #f0f0f0;
  border: 1px solid #ccc;
  border-radius: 4px;
  text-align: center;
  line-height: 16px;
  font-size: 8px;
  color: #333;
  position: absolute;
  z-index: 1;
}
.events-line {
  position: absolute;
  top: 0;
  left: 0;
}
.icon {
  cursor: pointer;
  padding: 5px;
  font-size: 20px;
  color: #333;
}
.search-icon {
  margin-right: 10px;
}
.filter-icon {
  margin-left: auto;
}

/*浮窗*/
.popup-overlay {
  position: fixed;
  top: 200px;
  left: 300px;
  width: 500px;
  height: 450px;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.popup-content {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  min-width: 320px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  top: 200px;
  left: 300px;
  width: 500px;
  height: 450px;
}

.type h3 {
  margin: -20px auto 20px 0;
  text-align: center;
  color: #0e0f0f;
  border-bottom: 2px solid #585555;
  padding-bottom: 10px;
}
.type_header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 30px; /* 增大内边距，使间距变大 */
  color: rgb(5, 5, 5); /* 设置文字颜色 */
  cursor: pointer; /* 设置光标为手形 */
  border-radius: 4px; /* 边角圆滑 */
  font-size: 18px; /* 增大字体大小 */
  font-weight: bold; /* 设置文字加粗 */
}

.checkbox-group {
  display: flex;
  flex-wrap: wrap; /* 允许换行 */
}
.checkbox-label {
  width: 50%; /* 每个标签占一行的一半 */
  box-sizing: border-box; /* 防止内边距影响宽度 */
  margin-bottom: 10px; /* 每行下方间距 */
}
.filter-item {
  margin-bottom: 15px; /* 增大项之间的间距 */
  display: flex;
  flex-direction: column;
}

.filter-item label {
  display: flex;
  padding: 10px; /* 增加标签内的内边距 */
  font-size: 18px; /* 增大字体大小 */
  font-weight: bold; /* 设置文字加粗 */
  margin-bottom: 15px; /* 增大标签之间的间距 */
}

.filter-item select,
/* 日期范围选择器样式 */
.filter-item .el-date-editor--daterange {
  width: 100%;
}

.popup-buttons {
  display: flex;
  justify-content: space-between; /* 两个按钮之间的间距 */
  margin-top: 20px;
}

button {
  border: none;
  border-radius: 50px; /* 圆角按钮 */
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
}

.reset-btn {
  background-color: white;
  color: #333;
  border: 1px solid #ccc;
  width: 48%; /* 控制按钮宽度 */
}

.apply-btn {
  background-color: #6c68c6; /* 按钮背景色为黄色 */
  color: white;
  width: 48%; /* 控制按钮宽度 */
}
.close-buttons {
  position: flex;
  cursor: pointer;
}

/* 加载状态按钮样式 */
.apply-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

/* 可以添加一个加载指示器 */
.loading-indicator {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(0, 0, 0, 0.1);
  border-top-color: #333;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 8px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}


</style>
