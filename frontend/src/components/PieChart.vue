<template>
  <div class="chart-container">
    <div class="chart-header">
      <h3 class="chart-title">脑卒中致病危险因素</h3>
    </div>
    <div class="pie-chart" ref="chartRef"></div>
  </div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  name: "PieChart",
  data() {
    return {
      chart: null,
      chartData: [],
      isInitialized: false
    }
  },
  mounted() {
    this.prepareData();
    
    // 添加窗口大小变化监听
    window.addEventListener('resize', this.handleResize);
    
    // 确保DOM已经渲染完成后再初始化图表
    this.$nextTick(() => {
      this.initChart();
      
      // 添加延迟调整大小，确保在父容器完全渲染后调整
      setTimeout(() => {
        this.handleResize();
      }, 300);
    });
  },
  updated() {
    // 在组件更新后重新调整大小
    this.$nextTick(() => {
      this.handleResize();
    });
  },
  beforeUnmount() {
    // 组件销毁前移除事件监听
    window.removeEventListener('resize', this.handleResize);
    if (this.chart) {
      this.chart.dispose();
      this.chart = null;
    }
  },
  methods: {
    prepareData() {
      // 构造数据
      const realData = [
        { value: 20, name: '饮食' },
        { value: 18, name: '高血压' },
        { value: 15, name: '吸烟' },
        { value: 12, name: '血脂异常' },
        { value: 10, name: '空气污染' },
        { value: 8,  name: '糖尿病' },
        { value: 5,  name: '肥胖' },
        { value: 12, name: '运动不足' }
      ];

      // 按照 value 的降序排列
      realData.sort((a, b) => b.value - a.value);

      // 直接使用真实数据，不添加占位数据
      this.chartData = realData;
    },
    getChartOption() {
      const textColor = '#333';
      const backgroundColor = '#ffffff';
      
      // 颜色方案
      const colors = [
        '#ff6b6b', // 饮食
        '#ff8c42', // 高血压
        '#f72585', // 吸烟
        '#ffa62b', // 血脂异常
        '#ffcb47', // 空气污染
        '#06d6a0', // 糖尿病
        '#1b9aaa', // 肥胖
        '#4361ee', // 运动不足
      ];
      
      return {
        backgroundColor: backgroundColor,
        title: {
          show: false // 使用自定义标题
        },
        tooltip: {
          trigger: 'item',
          formatter: (params) => {
            return `<div style="font-weight:bold;margin-bottom:5px;">${params.name}</div>` +
                   `<div>数值: <span style="font-weight:bold;float:right;margin-left:10px;">${params.value}</span></div>`;
          },
          backgroundColor: 'rgba(255,255,255,0.9)',
          borderColor: '#ddd',
          borderWidth: 1,
          padding: [8, 12],
          textStyle: {
            color: textColor
          },
          extraCssText: 'box-shadow: 0 3px 10px rgba(0,0,0,0.2); border-radius: 8px;'
        },
        legend: {
          orient: 'horizontal',
          bottom: 20, // 增加底部距离，避免与饼图重叠
          itemWidth: 12,
          itemHeight: 12,
          itemGap: 15, // 减小图例项之间的间距
          textStyle: {
            color: textColor,
            fontSize: 12
          },
          icon: 'circle'
        },
        color: colors,
        series: [
          {
            name: '脑卒中致病危险因素',
            type: 'pie',
            radius: ['30%', '65%'], // 减小饼图大小
            center: ['50%', '45%'], // 将饼图中心点向上移动
            avoidLabelOverlap: true,
            roseType: 'radius', // 使用玫瑰图模式，让扇形呈现阶梯状
            itemStyle: {
              borderRadius: 6,
              borderColor: backgroundColor,
              borderWidth: 2,
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.2)'
            },
            label: {
              show: true,
              position: 'outside',
              formatter: '{b}', // 只显示名称，不显示百分比
              color: textColor,
              fontSize: 12, // 减小标签字体大小
              fontWeight: 'bold',
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
              borderRadius: 4,
              padding: [3, 5], // 减小标签内边距
              alignTo: 'edge',
              edgeDistance: '10%'
            },
            labelLine: {
              length: 10, // 减小引导线长度
              length2: 15, // 减小引导线第二段长度
              smooth: true,
              lineStyle: {
                width: 1.5,
                type: 'solid'
              }
            },
            emphasis: {
              scale: true,
              scaleSize: 10,
              itemStyle: {
                shadowBlur: 20,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              },
              label: {
                fontSize: 14, // 减小强调时的字体大小
                fontWeight: 'bold'
              }
            },
            data: this.chartData,
            animationType: 'scale',
            animationEasing: 'elasticOut',
            animationDelay: function () {
              return Math.random() * 200 + 300;
            }
          }
        ]
      };
    },
    initChart() {
      // 确保DOM元素存在
      if (!this.$refs.chartRef) {
        console.error('Chart container not found');
        return;
      }
      
      try {
        // 初始化 ECharts 实例
        if (!this.chart) {
          this.chart = echarts.init(this.$refs.chartRef, null, {
            renderer: 'canvas'
          });
        }
        
        // 使用配置项生成图表
        const option = this.getChartOption();
        this.chart.setOption(option, true);
        
        // 添加点击事件
        this.chart.on('click', this.handleChartClick);
        
        this.isInitialized = true;
      } catch (error) {
        console.error('Failed to initialize chart:', error);
      }
    },
    handleResize() {
      if (this.chart) {
        this.chart.resize();
      }
    },
    handleChartClick(params) {
      // 发出点击事件
      this.$emit('item-click', params);
    }
  }
}
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 100%;
  min-height: 300px; /* 减小最小高度 */
  max-height: 100%; /* 添加最大高度限制 */
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.chart-container:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  transform: translateY(-3px); /* 减小悬停时的上移距离 */
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px; /* 减小内边距 */
  border-bottom: 1px solid #f0f0f0;
}

.chart-title {
  font-size: 16px; /* 减小字体大小 */
  font-weight: 600;
  color: #333;
  margin: 0;
}

.pie-chart {
  flex: 1;
  width: 100%;
  min-height: 250px; /* 减小图表的最小高度 */
  max-height: calc(100% - 50px); /* 限制图表最大高度，减去头部高度 */
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden; /* 防止内容溢出 */
}

/* 响应式调整 */
@media (max-width: 768px) {
  .chart-container {
    min-height: 300px; /* 减小移动端的最小高度 */
  }
  
  .pie-chart {
    min-height: 250px; /* 减小移动端图表的最小高度 */
  }
  
  .chart-title {
    font-size: 14px; /* 进一步减小移动端的字体大小 */
  }
}
</style>