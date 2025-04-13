<template>
    <div class="gender-chart" ref="chartRef" style="width: 100%; height: 250px;"></div>
  </template>
  
  <script>
  import * as echarts from 'echarts'
  
  export default {
    name: 'GenderChart',
    props: {
      // 可以通过 props 传递数据
      data: {
        type: Array,
        default: () => ([
          { name: '男', value: 60 },
          { name: '女', value: 40 }
        ])
      }
    },
    mounted() {
      this.initChart()
    },
    methods: {
      initChart() {
        // 1. 获取 DOM 容器
        const chartDom = this.$refs.chartRef
        // 2. 初始化 ECharts 实例
        const myChart = echarts.init(chartDom)
        // 3. 配置项
        const option = {
          tooltip: {
            trigger: 'item'
          },
          legend: {
            bottom: '0',
            left: 'center'
          },
          color: ['#93AAFD', '#2D5BFF'],
          series: [
            {
              name: '性别',
              type: 'pie',
              radius: '50%',
              data: this.data,
              emphasis: {
                itemStyle: {
                  shadowBlur: 10,
                  shadowOffsetX: 0,
                  shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
              },
              label: {
                formatter: '{b}'
              }
            }
          ]
        }
        // 4. 设置配置
        myChart.setOption(option)
  
        // 5. 自适应监听
        window.addEventListener('resize', () => {
          myChart.resize()
        })
      }
    }
  }
  </script>
  
  <style scoped>
  .gender-chart {
    /* 这里的宽高可以按需调整或用父级容器控制 */
  }
  </style>
  