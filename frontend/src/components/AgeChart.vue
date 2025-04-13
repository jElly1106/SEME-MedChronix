<template>
    <div class="age-chart" ref="chartRef" style="width: 100%; height: 250px;"></div>
  </template>
  
  <script>
  import * as echarts from 'echarts'
  
  export default {
    name: 'AgeChart',
    props: {
      data: {
        type: Array,
        default: () => ([
          { ageRange: '0-20', count: 10 },
          { ageRange: '21-40', count: 30 },
          { ageRange: '41-60', count: 50 },
          { ageRange: '60+', count: 20 }
        ])
      }
    },
    mounted() {
      this.initChart()
    },
    methods: {
      initChart() {
        const chartDom = this.$refs.chartRef
        const myChart = echarts.init(chartDom)
  
        // 准备 xAxis, series 所需的数据
        const xData = this.data.map(item => item.ageRange)
        const yData = this.data.map(item => item.count)
  
        const option = {
          tooltip: {
            trigger: 'axis'
          },
          xAxis: {
            type: 'category',
            data: xData
          },
          yAxis: {
            type: 'value'
          },
          series: [
            {
              data: yData,
              type: 'bar',
              barWidth: '40%',
              itemStyle: {
                color: '#2D5BFF'
              }
            }
          ]
        }
  
        myChart.setOption(option)
        window.addEventListener('resize', () => {
          myChart.resize()
        })
      }
    }
  }
  </script>
  
  <style scoped>
  .age-chart {
    /* 这里的宽高可以按需调整或用父级容器控制 */
  }
  </style>
  