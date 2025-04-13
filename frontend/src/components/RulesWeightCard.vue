<template>
  <div class="rules-weight-card">
    <div class="card-content" ref="chartRef"></div>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'RulesWeightCard',
  mounted() {
    this.initChart()
  },
  methods: {
    initChart() {
      const chartDom = this.$refs.chartRef
      const myChart = echarts.init(chartDom)

      // 定义节点（在每个节点中增加 rules 属性，用于存储相关规则）
      const nodes = [
  {
    name: '⚗️碱储备',
    x: 120,
    y: 50,
    symbol: 'roundRect',
    symbolSize: [60, 30],
    itemStyle: {
      color: '#A8DADC',       // 浅蓝
      borderColor: '#457B9D', // 深蓝
      borderWidth: 2
    },
    label: {
      show: true,
      formatter: '{b}',
      color: '#000000',
      position: 'inside',
      fontSize: 10,
      fontWeight: 'bold',
      align: 'center',
      verticalAlign: 'middle'
    },
    rules: [
      '规则1：碱储备需大于50',
      '规则2：若异常需进一步检测'
    ]
  },
  {
    name: '🧪碳酸盐',
    x: 60,
    y: 90,
    symbol: 'roundRect',
    symbolSize: [60, 30],
    itemStyle: {
      color: '#FFD6A5',       // 柔和橙黄色
      borderColor: '#FFB703', // 明亮橙色
      borderWidth: 2
    },
    label: {
      show: true,
      formatter: '{b}',
      color: '#000000',
      position: 'inside',
      fontSize: 10,
      fontWeight: 'bold',
      align: 'center',
      verticalAlign: 'middle'
    },
    rules: ['规则：碳酸盐浓度正常范围为…']
  },
  {
    name: '➖阴离子间隙',
    x: 100,
    y: 140,
    symbol: 'roundRect',
    symbolSize: [60, 30],
    itemStyle: {
      color: '#BDE0FE',       // 清爽蓝
      borderColor: '#3A86FF', // 鲜明蓝
      borderWidth: 2
    },
    label: {
      show: true,
      formatter: '{b}',
      color: '#000000',
      position: 'inside',
      fontSize: 10,
      fontWeight: 'bold',
      align: 'center',
      verticalAlign: 'middle'
    },
    rules: ['规则：阴离子间隙计算公式…']
  },
  {
    name: '🧂氯',
    x: 170,
    y: 100,
    symbol: 'roundRect',
    symbolSize: [60, 30],
    itemStyle: {
      color: '#FFADAD',       // 淡粉红
      borderColor: '#E63946', // 鲜红
      borderWidth: 2
    },
    label: {
      show: true,
      formatter: '{b}',
      color: '#000000',
      position: 'inside',
      fontSize: 10,
      fontWeight: 'bold',
      align: 'center',
      verticalAlign: 'middle'
    },
    rules: ['规则：氯值异常提示…']
  },
  {
    name: '⚡钠、钾',
    x: 120,
    y: 250,
    symbol: 'roundRect',
    symbolSize: [60, 30],
    itemStyle: {
      color: '#FDFFB6',       // 亮黄色
      borderColor: '#FCA311', // 橙色
      borderWidth: 2
    },
    label: {
      show: true,
      formatter: '{b}',
      color: '#000000',
      position: 'inside',
      fontSize: 10,
      fontWeight: 'bold',
      align: 'center',
      verticalAlign: 'middle'
    },
    rules: ['规则：电解质平衡检测']
  },
  {
    name: '🌡️温度',
    x: 230,
    y: 150,
    symbol: 'roundRect',
    symbolSize: [60, 30],
    itemStyle: {
      color: '#FFB4A2',       // 柔和橙粉
      borderColor: '#E63946', // 鲜红
      borderWidth: 2
    },
    label: {
      show: true,
      formatter: '{b}',
      color: '#000000',
      position: 'inside',
      fontSize: 10,
      fontWeight: 'bold',
      align: 'center',
      verticalAlign: 'middle'
    },
    rules: ['规则：温度超标预警']
  },
  {
    name: '💨呼吸频率',
    x: 270,
    y: 70,
    symbol: 'roundRect',
    symbolSize: [60, 30],
    itemStyle: {
      color: '#C9CCD5',       // 柔和灰蓝
      borderColor: '#6D6875', // 深灰
      borderWidth: 2
    },
    label: {
      show: true,
      formatter: '{b}',
      color: '#000000',
      position: 'inside',
      fontSize: 10,
      fontWeight: 'bold',
      align: 'center',
      verticalAlign: 'middle'
    },
    rules: ['规则：呼吸频率异常时…']
  },
  {
    name: '🫁动脉血氧饱和度',
    x: 270,
    y: 250,
    symbol: 'roundRect',
    symbolSize: [85, 30],
    itemStyle: {
      color: '#B7E4C7',       // 清新绿
      borderColor: '#2B9348', // 深绿
      borderWidth: 2
    },
    label: {
      show: true,
      formatter: '{b}',
      color: '#000000',
      position: 'inside',
      fontSize: 10,
      fontWeight: 'bold',
      align: 'center',
      verticalAlign: 'middle'
    },
    rules: ['规则：血氧饱和度需大于…']
  },
  {
    name: '❤️心率',
    x: 350,
    y: 120,
    symbol: 'roundRect',
    symbolSize: [60, 30],
    itemStyle: {
      color: '#FFC8DD',       // 粉柔
      borderColor: '#D00000', // 鲜红
      borderWidth: 2
    },
    label: {
      show: true,
      formatter: '{b}',
      color: '#000000',
      position: 'inside',
      fontSize: 10,
      fontWeight: 'bold',
      align: 'center',
      verticalAlign: 'middle'
    },
    rules: ['规则：心率维持在60-100之间']
  },
  {
    name: '💨PaCO2',
    x: 380,
    y: 70,
    symbol: 'roundRect',
    symbolSize: [60, 30],
    itemStyle: {
      color: '#FFE066',       // 柔和橙黄
      borderColor: '#F4A261', // 橙色
      borderWidth: 2
    },
    label: {
      show: true,
      formatter: '{b}',
      color: '#000000',
      position: 'inside',
      fontSize: 10,
      fontWeight: 'bold',
      align: 'center',
      verticalAlign: 'middle'
    },
    rules: ['规则：PaCO2正常范围为35-45']
  },
  {
    name: '🫁动脉血氧分压',
    x: 440,
    y: 150,
    symbol: 'roundRect',
    symbolSize: [75, 30],
    itemStyle: {
      color: '#A2D2FF',       // 清爽蓝
      borderColor: '#0077B6', // 深蓝
      borderWidth: 2
    },
    label: {
      show: true,
      formatter: '{b}',
      color: '#000000',
      position: 'inside',
      fontSize: 10,
      fontWeight: 'bold',
      align: 'center',
      verticalAlign: 'middle'
    },
    rules: ['规则：动脉血氧分压监测']
  },
  {
    name: '🩸INR',
    x: 515,
    y: 180,
    symbol: 'roundRect',
    symbolSize: [60, 30],
    itemStyle: {
      color: '#E0BBE4',       // 柔和紫
      borderColor: '#9D4EDD', // 紫色
      borderWidth: 2
    },
    label: {
      show: true,
      formatter: '{b}',
      color: '#000000',
      position: 'inside',
      fontSize: 10,
      fontWeight: 'bold',
      align: 'center',
      verticalAlign: 'middle'
    },
    rules: ['规则：INR超过1.5可能有…']
  },
  {
    name: '🩺动脉血压',
    x: 420,
    y: 250,
    symbol: 'roundRect',
    symbolSize: [60, 30],
    itemStyle: {
      color: '#FFBC42',       // 柔和黄
      borderColor: '#D81159', // 鲜红
      borderWidth: 2
    },
    label: {
      show: true,
      formatter: '{b}',
      color: '#000000',
      position: 'inside',
      fontSize: 10,
      fontWeight: 'bold',
      align: 'center',
      verticalAlign: 'middle'
    },
    rules: ['规则：动脉血压异常提示']
  },
  {
    name: '💤高度昏迷',
    x: 420,
    y: 320,
    symbol: 'roundRect',
    symbolSize: [60, 30],
    itemStyle: {
      color: '#C5C6C7',       // 中性灰
      borderColor: '#1F2833', // 深灰
      borderWidth: 2
    },
    label: {
      show: true,
      formatter: '{b}',
      color: '#000000',
      position: 'inside',
      fontSize: 10,
      fontWeight: 'bold',
      align: 'center',
      verticalAlign: 'middle'
    },
    rules: ['规则：高度昏迷需紧急处理']
  },
  {
    name: '🧪血尿素氮',
    x: 520,
    y: 60,
    symbol: 'roundRect',
    symbolSize: [60, 30],
    itemStyle: {
      color: '#D4A5A5',       // 柔和肉色
      borderColor: '#BF3325', // 深棕红
      borderWidth: 2
    },
    label: {
      show: true,
      formatter: '{b}',
      color: '#000000',
      position: 'inside',
      fontSize: 10,
      fontWeight: 'bold',
      align: 'center',
      verticalAlign: 'middle'
    },
    rules: ['规则：血尿素氮异常提示']
  },
  {
    name: '🧪血糖肌酐',
    x: 550,
    y: 120,
    symbol: 'roundRect',
    symbolSize: [60, 30],
    itemStyle: {
      color: '#A2D2FF',       // 清爽蓝
      borderColor: '#0077B6', // 深蓝
      borderWidth: 2
    },
    label: {
      show: true,
      formatter: '{b}',
      color: '#000000',
      position: 'inside',
      fontSize: 10,
      fontWeight: 'bold',
      align: 'center',
      verticalAlign: 'middle'
    },
    rules: ['规则：血糖肌酐监测']
  },
  {
    name: '🩸血小板',
    x: 630,
    y: 180,
    symbol: 'roundRect',
    symbolSize: [60, 30],
    itemStyle: {
      color: '#FFC8DD',       // 淡粉
      borderColor: '#D00000', // 鲜红
      borderWidth: 2
    },
    label: {
      show: true,
      formatter: '{b}',
      color: '#000000',
      position: 'inside',
      fontSize: 10,
      fontWeight: 'bold',
      align: 'center',
      verticalAlign: 'middle'
    },
    rules: ['规则：血小板异常需关注']
  },
  {
    name: '🍬血糖',
    x: 560,
    y: 250,
    symbol: 'roundRect',
    symbolSize: [60, 30],
    itemStyle: {
      color: '#F6BD60',       // 温暖金黄
      borderColor: '#F4A261', // 橙色
      borderWidth: 2
    },
    label: {
      show: true,
      formatter: '{b}',
      color: '#000000',
      position: 'inside',
      fontSize: 10,
      fontWeight: 'bold',
      align: 'center',
      verticalAlign: 'middle'
    },
    rules: ['规则：血糖控制标准']
  },
  {
    name: '🩸PT',
    x: 730,
    y: 70,
    symbol: 'roundRect',
    symbolSize: [60, 30],
    itemStyle: {
      color: '#C0E218',       // 清新绿
      borderColor: '#8AC926', // 深绿
      borderWidth: 2
    },
    label: {
      show: true,
      formatter: '{b}',
      color: '#000000',
      position: 'inside',
      fontSize: 10,
      fontWeight: 'bold',
      align: 'center',
      verticalAlign: 'middle'
    },
    rules: ['规则：PT监测结果说明']
  },
  {
    name: '🩸PTT',
    x: 770,
    y: 130,
    symbol: 'roundRect',
    symbolSize: [60, 30],
    itemStyle: {
      color: '#A2C523',       // 柔和橄榄绿
      borderColor: '#7B9E3B', // 深橄榄绿
      borderWidth: 2
    },
    label: {
      show: true,
      formatter: '{b}',
      color: '#000000',
      position: 'inside',
      fontSize: 10,
      fontWeight: 'bold',
      align: 'center',
      verticalAlign: 'middle'
    },
    rules: ['规则：PTT异常时…']
  },
  {
    name: '🩸血红蛋白',
    x: 660,
    y: 130,
    symbol: 'roundRect',
    symbolSize: [60, 30],
    itemStyle: {
      color: '#FFADAD',       // 淡粉红
      borderColor: '#E63946', // 鲜红
      borderWidth: 2
    },
    label: {
      show: true,
      formatter: '{b}',
      color: '#000000',
      position: 'inside',
      fontSize: 10,
      fontWeight: 'bold',
      align: 'center',
      verticalAlign: 'middle'
    },
    rules: ['规则：血红蛋白检测标准']
  },
  {
    name: '🦠白细胞',
    x: 740,
    y: 180,
    symbol: 'roundRect',
    symbolSize: [60, 30],
    itemStyle: {
      color: '#D0F4DE',       // 清新绿
      borderColor: '#3C6255', // 深绿
      borderWidth: 2
    },
    label: {
      show: true,
      formatter: '{b}',
      color: '#000000',
      position: 'inside',
      fontSize: 10,
      fontWeight: 'bold',
      align: 'center',
      verticalAlign: 'middle'
    },
    rules: ['规则：白细胞数量异常']
  },
  {
    name: '🩸血细胞比容',
    x: 710,
    y: 250,
    symbol: 'roundRect',
    symbolSize: [60, 30],
    itemStyle: {
      color: '#BDE0FE',       // 清爽蓝
      borderColor: '#3A86FF', // 鲜明蓝
      borderWidth: 2
    },
    label: {
      show: true,
      formatter: '{b}',
      color: '#000000',
      position: 'inside',
      fontSize: 10,
      fontWeight: 'bold',
      align: 'center',
      verticalAlign: 'middle'
    },
    rules: ['规则：血细胞比容计算公式']
  }
]


      // 定义有向边（示例中只使用了一个有向边，其他可根据需要添加）
      const links = [
        { source: '⚗️碱储备', target: '➖阴离子间隙', lineStyle: { curveness: 0.3 } },
        { source: '➖阴离子间隙', target: '⚡钠、钾', lineStyle: { curveness: 0.3 } },
        { source: '🧪碳酸盐', target: '⚡钠、钾', lineStyle: { curveness: -0.3 } },
        { source: '🧂氯', target: '⚡钠、钾', lineStyle: { curveness: 0.3 } },
        { source: '💨呼吸频率', target: '🫁动脉血氧饱和度', lineStyle: { curveness: 0.3 } },
        { source: '🌡️温度', target: '⚡钠、钾', lineStyle: { curveness: 0.3 } },
        { source: '🌡️温度', target: '🫁动脉血氧饱和度', lineStyle: { curveness: 0.3 } },
        { source: '❤️心率', target: '🫁动脉血氧饱和度', lineStyle: { curveness: 0.3 } },
        { source: '❤️心率', target: '🩺动脉血压', lineStyle: { curveness: 0.3 } },
        { source: '💨PaCO2', target: '🫁动脉血氧分压', lineStyle: { curveness: 0.3 } },
        { source: '🫁动脉血氧分压', target: '🩺动脉血压', lineStyle: { curveness: 0.3 } },
        { source: '🩸INR', target: '🩺动脉血压', lineStyle: { curveness: 0.3 } },
        { source: '🩸INR', target: '🍬血糖', lineStyle: { curveness: 0.3 } },
        { source: '🩸INR', target: '🫁动脉血氧饱和度', lineStyle: { curveness: -0.1 } },
        { source: '🧪血糖肌酐', target: '🍬血糖', lineStyle: { curveness: 0.3 } },
        { source: '🧪血尿素氮', target: '🧪血糖肌酐', lineStyle: { curveness: 0.3 } },
        { source: '🍬血糖', target: '💤高度昏迷', lineStyle: { curveness: 0.3 } },
        { source: '🩸血小板', target: '🩸血细胞比容', lineStyle: { curveness: 0.3 } },
        { source: '🩸血红蛋白', target: '🩸血细胞比容', lineStyle: { curveness: 0.2 } },
        { source: '🩸PT', target: '🩸INR', lineStyle: { curveness: -0.1 } },
        { source: '🩸PT', target: '🩸PTT', lineStyle: { curveness: 0.3 } },
        { source: '🩸PTT', target: '🩸血细胞比容', lineStyle: { curveness: 0.6 } },
        { source: '🦠白细胞', target: '🩸血细胞比容', lineStyle: { curveness: 0.3 } },
        { source: '⚡钠、钾', target: '💤高度昏迷', lineStyle: { curveness: -0.3 } },
        { source: '🫁动脉血氧饱和度', target: '💤高度昏迷', lineStyle: { curveness: -0.3 } },
        { source: '🩺动脉血压', target: '💤高度昏迷', lineStyle: { curveness: 0.3 } },
        { source: '🩸血细胞比容', target: '💤高度昏迷', lineStyle: { curveness: 0.3 } },
        
      ] 

      // ECharts 配置
      const option = {
        tooltip: {
          trigger: 'item',
          formatter: function (params) {
            // 如果该节点有 rules 属性，则显示节点名称和规则列表
            if (params.data && params.data.rules) {
              return `<strong>${params.data.name}</strong><br/>${params.data.rules.join('<br/>')}`
            }
            return params.name
          }
        },
        series: [
          {
            name: 'DAG',
            type: 'graph',
            layout: 'none', // 使用手动指定位置
            roam: true,
            draggable: true,
            focusNodeAdjacency: true,
            symbolSize: 60,
            edgeSymbol: ['circle', 'arrow'],
            edgeSymbolSize: [2, 10],
            edgeLabel: {
              show: false,
              fontSize: 10
            },
            data: nodes,
            links: links,
            lineStyle: {
              opacity: 0.9,
              width: 2,
              curveness: 0 // 全局弧度，可在 links 中覆盖
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
.rules-weight-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 16px;
  width: 800px;
  height: 400px;
}

.card-content {
  width: 100%;
  height: calc(100% - 50px);
}
</style>
