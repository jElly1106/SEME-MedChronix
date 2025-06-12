<template>
  <div class="prediction-accuracy-card">
    <div class="card-header">疾病事件预测正确率</div>
    <div class="card-content">
      <!-- 圆形背景，居中显示动态数字 -->
      <div class="circle-container">
        <div class="circle">
          <!-- 显示动态数字 + '%' -->
          <div class="accuracy-text">
            {{ displayValue }}<span class="percent-sign">%</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "PredictionAccuracyCard",
  data() {
    return {
      displayValue: 0, // 当前显示的数值
      targetValue: 98, // 最终想显示的预测正确率（比如 98）
      duration: 2000, // 动画时长，单位毫秒
      startTime: null, // 动画开始时间
      animationFrameId: null,
    };
  },
  mounted() {
    this.startAnimation();
  },
  // Vue 3 中使用 beforeUnmount
  beforeUnmount() {
    // 组件卸载前，清除动画帧
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
    }
  },
  methods: {
    startAnimation() {
      this.startTime = performance.now();
      // 用箭头函数来传递 now
      this.animationFrameId = requestAnimationFrame((now) => this.animate(now));
    },
    animate(now) {
      if (!this.startTime) this.startTime = now;
      const elapsed = now - this.startTime;
      let progress = elapsed / this.duration;
      if (progress > 1) progress = 1;

      const currentValue = Math.floor(this.targetValue * progress);
      this.displayValue = currentValue;

      if (progress < 1) {
        this.animationFrameId = requestAnimationFrame((t) => this.animate(t));
      }
    },
  },
};
</script>

<style scoped>
.prediction-accuracy-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  min-height: 150px;
  padding: 16px;
}

.card-header {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #343c6a;
}

.card-content {
  min-height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 圆形背景容器，让它居中 */
.circle-container {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 圆形 */
.circle {
  width: 130px;
  height: 130px;
  background: radial-gradient(circle, #ebf2ff 30%, #e5eafc 100%);
  border-radius: 50%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 数字文本 */
.accuracy-text {
  font-size: 36px;
  font-weight: bold;
  color: #343c6a;
}

/* 如果你想要百分号小一些，可以单独设置 */
.percent-sign {
  font-size: 24px;
  margin-left: 4px;
}
</style>
