<template>
  <div class="statistic-card" :class="{ 'hover-effect': enableHover }">
    <div class="card-background"></div>

    <!-- 左组 -->
    <div class="statistic-group">
      <div class="icon-and-text">
        <!-- 图标容器 -->
        <div
          class="icon-container"
          v-if="icon1"
          :style="{ backgroundColor: iconBgColor1 || '#e6f7ff' }"
        >
          <i
            :class="[icon1, 'group-icon']"
            :style="{ color: iconColor1 || '#2f54eb' }"
          ></i>
        </div>
        <!-- 标签和数字纵向排列 -->
        <div class="text-content">
          <div class="card-label">{{ label1 }}</div>
          <div class="card-value" :class="{ 'gradient-text': useGradient }">
            {{ animatedValue1
            }}<span class="unit" v-if="unit1">{{ unit1 }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 分隔线 -->
    <div class="divider" v-if="showDivider"></div>

    <!-- 右组 -->
    <div class="statistic-group">
      <div class="icon-and-text">
        <div
          class="icon-container"
          v-if="icon2"
          :style="{ backgroundColor: iconBgColor2 || '#f6ffed' }"
        >
          <i
            :class="[icon2, 'group-icon']"
            :style="{ color: iconColor2 || '#52c41a' }"
          ></i>
        </div>
        <div class="text-content">
          <div class="card-label">{{ label2 }}</div>
          <div class="card-value" :class="{ 'gradient-text': useGradient }">
            {{ animatedValue2
            }}<span class="unit" v-if="unit2">{{ unit2 }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import "@fortawesome/fontawesome-free/css/all.min.css";

export default {
  name: "StatisticCard",
  props: {
    value1: {
      type: [String, Number],
      default: 0,
    },
    label1: {
      type: String,
      default: "",
    },
    value2: {
      type: [String, Number],
      default: 0,
    },
    label2: {
      type: String,
      default: "",
    },
    /* 图标类名 */
    icon1: {
      type: String,
      default: "",
    },
    icon2: {
      type: String,
      default: "",
    },
    /* 新增属性 */
    iconColor1: {
      type: String,
      default: "",
    },
    iconColor2: {
      type: String,
      default: "",
    },
    iconBgColor1: {
      type: String,
      default: "",
    },
    iconBgColor2: {
      type: String,
      default: "",
    },
    unit1: {
      type: String,
      default: "",
    },
    unit2: {
      type: String,
      default: "",
    },
    useGradient: {
      type: Boolean,
      default: true,
    },
    enableHover: {
      type: Boolean,
      default: true,
    },
    showDivider: {
      type: Boolean,
      default: true,
    },
  },
  data() {
    return {
      animatedValue1: 0,
      animatedValue2: 0,
    };
  },
  mounted() {
    this.animateValue("animatedValue1", this.value1);
    this.animateValue("animatedValue2", this.value2);
  },
  methods: {
    animateValue(targetKey, targetValue) {
      const duration = 1200; // 增加动画时长
      const frameRate = 30; // 每秒帧数
      const totalFrames = Math.round(duration / (1000 / frameRate));
      let frame = 0;
      const startValue = 0;

      // 使用 easeOutQuart 缓动函数使动画更自然
      const easeOutQuart = (t) => 1 - Math.pow(1 - t, 4);

      const counter = setInterval(() => {
        frame++;
        const progress = easeOutQuart(frame / totalFrames);
        this[targetKey] = Math.round(
          startValue + (targetValue - startValue) * progress
        );
        if (frame >= totalFrames) {
          this[targetKey] = targetValue;
          clearInterval(counter);
        }
      }, 1000 / frameRate);
    },
  },
};
</script>

<style scoped>
/* 卡片容器 */
.statistic-card {
  background: linear-gradient(135deg, #ffffff 0%, #f9f9f9 100%);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.05);

  display: flex;
  justify-content: space-around;
  align-items: center;
  position: relative;
  transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
  overflow: hidden;
  border: 1px solid rgba(230, 230, 230, 0.7);
}

/* 卡片背景装饰 */
.card-background {
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200px;
  height: 200px;
  background: radial-gradient(
    circle,
    rgba(47, 84, 235, 0.05) 0%,
    rgba(255, 255, 255, 0) 70%
  );
  border-radius: 50%;
  z-index: 0;
}

/* 悬停效果 */
.hover-effect:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
  border-color: rgba(47, 84, 235, 0.2);
}

/* 两个分组左右并排 */
.statistic-group {
  display: flex;
  align-items: center;
  position: relative;
  z-index: 1;
  flex: 1;
  justify-content: center;
}

/* 分隔线 */
.divider {
  width: 1px;
  height: 70%;
  background: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0),
    rgba(0, 0, 0, 0.1),
    rgba(0, 0, 0, 0)
  );
  margin: 0 10px;
}

/* 
  每个组内部：图标 + (标签 + 数字)
  用 flex 让图标在左边，文字在右边
*/
.icon-and-text {
  display: flex;
  align-items: center;
  gap: 16px; /* 增加图标与文字的间距 */
}

/* 图标容器 */
.icon-container {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.hover-effect:hover .icon-container {
  transform: scale(1.05);
}

/* 图标样式 */
.group-icon {
  font-size: 32px;
  transition: all 0.3s ease;
}

.hover-effect:hover .group-icon {
  transform: scale(1.1);
}

/* 文字容器：标签在上，数字在下 */
.text-content {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.card-label {
  font-size: 16px;
  font-weight: 600;
  color: #666;
  margin-bottom: 6px;
  transition: color 0.3s ease;
}

.hover-effect:hover .card-label {
  color: #333;
}

/* 数字部分 */
.card-value {
  font-size: 38px;
  font-weight: 700;
  letter-spacing: 1px;
  color: #1f1f1f;
  display: flex;
  align-items: baseline;
}

/* 单位样式 */
.unit {
  font-size: 16px;
  font-weight: 500;
  color: #888;
  margin-left: 4px;
}

/* 渐变文字 */
.gradient-text {
  background: linear-gradient(90deg, #2f54eb, #722ed1, #13c2c2, #2f54eb);
  background-size: 300% 300%;
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: gradient-flow 6s ease infinite;
}

/* 让渐变颜色左右来回流动 */
@keyframes gradient-flow {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .statistic-card {
    flex-direction: column;
    padding: 20px;
  }

  .divider {
    width: 80%;
    height: 1px;
    margin: 15px 0;
  }

  .statistic-group {
    width: 100%;
    justify-content: flex-start;
    margin-bottom: 10px;
  }

  .statistic-group:last-child {
    margin-bottom: 0;
  }

  .card-value {
    font-size: 32px;
  }

  .icon-container {
    width: 56px;
    height: 56px;
  }

  .group-icon {
    font-size: 28px;
  }
}
</style>
