<template>
  <div class="word-frequency-chart" :style="{ transform: 'scale(' + scale + ')' }">
    <!-- 减小画布尺寸 -->
    <canvas ref="wordChart" width="300" height="200"></canvas>
  </div>
</template>

<script>
import { onMounted, ref, nextTick, watch } from "vue";
import WordCloud from "wordcloud";
 
export default {
  name: "WordFrequencyChart",
  props: {
    wordFrequencyData: {
      type: Array,
      default: () => []
    }
  },
  setup(props) {
    const wordChart = ref(null);
    const scale = ref(0.8); // 默认缩放比例为 0.8
    
    // 渲染词云图的函数
    // 渲染词云图的函数
    const renderWordCloud = () => {
      const canvas = wordChart.value;
      if (!canvas) return;
      
      try {
        // 先清除画布内容
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // 固定画布大小，避免动态调整导致的问题
        canvas.width = 300;
        canvas.height = 200;

        // 使用传入的数据或默认数据
        let data = [];
        
        // 检查数据格式并进行转换
        if (props.wordFrequencyData.length > 0) {
          // 判断数据格式：如果第一项是数组，说明是 [词语, 频率] 格式
          if (Array.isArray(props.wordFrequencyData[0])) {
            data = props.wordFrequencyData.map(item => ({
              name: item[0],
              count: item[1] * 2  // 减小放大系数
            }));
          } 
          // 如果第一项有 name 和 count 属性，说明已经是对象格式
          else if (props.wordFrequencyData[0].name && props.wordFrequencyData[0].count !== undefined) {
            data = props.wordFrequencyData.map(item => ({
              name: item.name,
              count: item.count * 2  // 减小放大系数
            }));
          }
        } else {
          // 默认数据
          data = [
            { name: "动脉血压收缩压高", count: 100 },
            { name: "动脉血压舒张压低", count: 90 },
            { name: "呼吸频率高", count: 80 },
            { name: "血氧饱和度低", count: 70 },
            { name: "心率高", count: 110 },
          ];
        }

        console.log("词云图数据:", data);
        
        // 限制数据量，只取前10个词频最高的项
        data = data.sort((a, b) => b.count - a.count).slice(0, 10);
        
        // 转换为 WordCloud 所需的数据格式
        const wordData = data.map(item => [item.name, item.count]);

        // 预先计算布局，然后一次性渲染
        WordCloud(canvas, {
          list: wordData,
          gridSize: 10,           // 增大网格大小
          weightFactor: 3,        // 减小权重因子
          fontFamily: 'Arial',    // 使用更简单的字体
          color: 'random-dark',   // 使用随机深色
          // 或者使用其他内置颜色方案: 'random-light', 'random-dark'
          backgroundColor: '#fff',
          rotateRatio: 0,         // 禁用旋转以提高性能
          drawOutOfBound: false,  // 防止文字超出画布
          shrinkToFit: true,      // 缩小以适应画布
          minSize: 10,            // 设置最小字体大小
          wait: 0,                // 不等待，一次性渲染
          shape: 'circle',        // 使用简单的圆形布局
          clearCanvas: true,      // 确保清除画布
          ellipticity: 1,         // 使用圆形而非椭圆
          drawMask: false,        // 禁用蒙版绘制
          maskColor: 'rgba(0,0,0,0.3)', // 简化蒙版颜色
          maskGapWidth: 0.3,      // 减小蒙版间隙
        });
      } catch (error) {
        console.error("词云图渲染错误:", error);
        // 显示错误信息
        const ctx = canvas.getContext('2d');
        ctx.font = '14px Arial';
        ctx.fillStyle = '#d81e06';
        ctx.textAlign = 'center';
        ctx.fillText('词云图渲染失败', canvas.width / 2, canvas.height / 2);
      }
    };

    // 监听数据变化，使用防抖函数避免频繁渲染
    let debounceTimer = null;
    watch(() => props.wordFrequencyData, () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        renderWordCloud();
      }, 500); // 500ms防抖
    }, { immediate: false, deep: true });

    onMounted(() => {
      // 等待 DOM 渲染完成后初始化
      nextTick(() => {
        console.log("词云图组件挂载完成");
        //renderWordCloud(); // 初始渲染
      });
    });

    return { wordChart, scale };
  },
};
</script>

<style scoped>
.word-frequency-chart {
  width: 300px;   /* 减小画布宽度 */
  height: 200px;  /* 减小画布高度 */
  overflow: hidden;
  margin: 0 auto;
}
</style>