<template>
  <div class="icu-events-card">
    <!-- 标题 -->
    <div class="card-title">ICU 异常事件</div>

    <!-- 搜索 & 筛选栏 -->
    <div class="search-filter-bar">
      <!-- 左侧查找图标 -->
      <div class="icon search-icon" @click="filterAction">
        <!-- 这里使用 Font Awesome 的查找图标 -->
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
        <!-- 这里使用 Font Awesome 的筛选图标 -->
        <i class="fa fa-filter"></i>
      </div>
    </div>

    <!-- 患者列表 -->
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
            width: calcContainerWidth(patient.events.length) + 'px',
            height: calcContainerHeight(patient.events.length) + 'px'
          }"
        >
          <!-- 1) 每个事件小矩形 -->
          <div
            v-for="(event, eIndex) in patient.events"
            :key="eIndex"
            class="event-box"
            :style="calcEventBoxStyle(eIndex, patient.events.length)"
          >
            {{ event }}
          </div>

          <!-- 2) SVG 连线，连接所有事件的中心点 -->
          <svg
            class="events-line"
            :width="calcContainerWidth(patient.events.length)"
            :height="calcContainerHeight(patient.events.length)"
          >
            <polyline
              :points="calcLinePoints(patient.events.length)"
              stroke="#999"
              fill="none"
              stroke-width="2"
            />
          </svg>
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
                      :value="option.value"
                      v-model="choose_type"
                    />
                    {{ option.label }}
                  </label>
                </div>
              </div>
            </div>
            <!-- 进入 ICU 时间 -->
            <div class="filter-item">
              <label>进入 ICU 时间:</label>
              <!-- 这里使用 Element UI 的日期选择组件 -->
              <el-date-picker
                v-model="icuEntryDate"
                type="date"
                placeholder="选择日期"
              >
              </el-date-picker>
            </div>
            <!-- 离开 ICU 时间 -->
            <div class="filter-item">
              <label>离开 ICU 时间:</label>
              <el-date-picker
                v-model="icuExitDate"
                type="date"
                placeholder="选择日期"
              >
              </el-date-picker>
            </div>
            <!-- 操作按钮 -->
            <div class="popup-buttons">
              <button class="reset-btn" @click="resetFilters">重置</button>
              <button class="apply-btn" @click="applyFilters">完成</button>
            </div>
          </div>
        </div>
  </div>
</template>

<script>
export default {
  name: 'IcuEventsCard',
  props: {
    patients: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      
      // 原有属性
      maxCols: 4,
      boxWidth: 50,
      boxHeight: 30,
      rowGap: 5,

      // 新增：搜索关键字
      searchName: '',
      strokeOptions: [
        { label: "缺血性脑卒中", value: "0" },
        { label: "出血性脑卒中", value: "1" },
        { label: "短暂性脑缺血发作", value: "2" },
        { label: "其他类型", value: "3" },
      ],

      choose_type: [],
      popupVisible: false,
      type_collapsed: false,
      icuEntryDate: null,
      icuExitDate: null,
    }
  },
  computed: {
    filteredPatients() {
      // 先按搜索关键字过滤
      let result = this.patients.filter(p => {
        // 忽略大小写匹配
        return p.name.toLowerCase().includes(this.searchName.toLowerCase())
      })

      // 这里可以结合弹窗内的筛选条件做进一步过滤
      // 比如 strokeTypes、icuEnter、icuLeave 等
      // 如果没有被勾选任何类型，说明不限制类型
      // 如果勾选了某些类型，则只保留这些类型
      // 下面仅演示搜索功能，具体逻辑按需实现

      return result
    }
  },
  methods: {
    // 重置筛选器的逻辑
    resetFilters() {
      this.choose_type = [];
      this.icuEntryDate = null;
      this.icuExitDate = null;
    },
    // 应用筛选器的逻辑
    applyFilters() {
      this.popupVisible = false;
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
    filterAction() {
    
    },

    // 以下为原本的事件蛇形布局方法
    calcContainerWidth() {
      return this.maxCols * this.boxWidth
    },
    calcContainerHeight(total) {
      const rows = Math.ceil(total / this.maxCols)
      return rows * (this.boxHeight + this.rowGap)
    },
    calcEventBoxStyle(index) {
      const row = Math.floor(index / this.maxCols)
      const col = index % this.maxCols

      let x;
      if (row % 2 === 0) {
        // 偶数行：左到右
        x = col * this.boxWidth
      } else {
        // 奇数行：右到左
        x = (this.maxCols - 1 - col) * this.boxWidth
      }
      const y = row * (this.boxHeight + this.rowGap)
      
      // 使事件矩形在单元内居中显示
      const actualWidth = 30;  // 事件矩形实际宽度
      const actualHeight = 16; // 事件矩形实际高度
      const offsetX = (this.boxWidth - actualWidth) / 2;
      const offsetY = (this.boxHeight - actualHeight) / 2;

      return {
        position: 'absolute',
        left: (x + offsetX) + 'px',
        top: (y + offsetY) + 'px'
      }
    },
    calcLinePoints(total) {
      const pointsArr = []
      for (let i = 0; i < total; i++) {
        const row = Math.floor(i / this.maxCols)
        const col = i % this.maxCols

        let x
        if (row % 2 === 0) {
          x = col * this.boxWidth
        } else {
          x = (this.maxCols - 1 - col) * this.boxWidth
        }
        const y = row * (this.boxHeight + this.rowGap)

        // 中心点
        const centerX = x + this.boxWidth / 2
        const centerY = y + this.boxHeight / 2
        pointsArr.push([centerX, centerY])
      }
      return pointsArr.map(point => point.join(',')).join(' ')
    }
  }
}
</script>

<style scoped>
.icu-events-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  width: 300px; /* 你想要的固定宽度 */
  height: 500px; /* 你想要的固定高度 */
  overflow: auto;
  padding: 16px;
}

/* 标题 */
.card-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #343C6A;
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
  background: url('data:image/svg+xml;base64,...') no-repeat center / cover;
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
  background: url('data:image/svg+xml;base64,...') no-repeat center / cover;
  cursor: pointer;
}

/* 患者列表 */
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
  width: 30px;
  height: 16px;
  background-color: #f0f0f0;
  border: 1px solid #ccc;
  border-radius: 4px;
  text-align: center;
  line-height: 16px;
  font-size: 10px;
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
.filter-item .el-date-picker {
  /* 如果需要，可添加宽度等样式 */
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
</style>
