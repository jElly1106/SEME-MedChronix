<template>
  <div class="map-container">
    <div class="map-header">
      <h3 class="map-title">全国医院分布</h3>
      <div class="map-subtitle">入驻本系统的医院数量</div>
    </div>
    <div ref="mapEcharts" class="map-echart"></div>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import axios from 'axios';

export default {
  name: "ChinaMap",
  data() {
    return {
      timer: null,
      seriesData: [
      { "name": "天津市", "value": 8 },
      { "name": "北京市", "value": 12 },
      { "name": "上海市", "value": 10 },
      { "name": "河北省", "value": 5 },
      { "name": "山东省", "value": 7 },
      { "name": "山西省", "value": 4 },
      { "name": "辽宁省", "value": 6 },
      { "name": "吉林省", "value": 3 },
      { "name": "黑龙江省", "value": 5 },
      { "name": "江苏省", "value": 9 },
      { "name": "浙江省", "value": 8 },
      { "name": "安徽省", "value": 4 },
      { "name": "福建省", "value": 5 },
      { "name": "江西省", "value": 3 },
      { "name": "河南省", "value": 6 },
      { "name": "湖北省", "value": 7 },
      { "name": "湖南省", "value": 4 },
      { "name": "广东省", "value": 11 },
      { "name": "海南省", "value": 2 },
      { "name": "四川省", "value": 6 },
      { "name": "贵州省", "value": 2 },
      { "name": "云南省", "value": 3 },
      { "name": "陕西省", "value": 4 },
      { "name": "甘肃省", "value": 2 },
      { "name": "青海省", "value": 1 },
      { "name": "新疆维吾尔自治区", "value": 2 },
      { "name": "广西壮族自治区", "value": 3 },
      { "name": "西藏自治区", "value": 1 },
      { "name": "内蒙古自治区", "value": 2 },
      { "name": "宁夏回族自治区", "value": 1 },
      { "name": "重庆市", "value": 5 },
      { "name": "澳门特别行政区", "value": 1 },
      { "name": "香港特别行政区", "value": 2 },
      { "name": "台湾省", "value": 3 }
      ],
      map: null
    }
  },
  mounted() {
    this.initMapEcharts();
    window.addEventListener('resize', this.handleResize);
  },
  beforeUnmount() {
    this.clearTimer();
    window.removeEventListener('resize', this.handleResize);
  },
  methods: {
    handleResize() {
      if (this.map) {
        this.map.resize();
      }
    },
    initMapEcharts() {
      axios.get('/china.json').then(res => {
        // 使用数据注册地图
        echarts.registerMap('china', res.data);
        this.$nextTick(() => {
          // 初始化地图
          this.map = echarts.init(this.$refs['mapEcharts']);
          // 设置基础配置项
          const option = {
            backgroundColor: '#f8f9fa',
            tooltip: {
              trigger: 'item',
              formatter: function (params) {
                return `<div style="font-weight:bold;margin-bottom:5px;">${params.name}</div>
                        <div>入驻医院: <span style="float:right;font-weight:bold;margin-left:15px;">${params.value || 0} 家</span></div>`;
              },
              backgroundColor: 'rgba(255,255,255,0.9)',
              borderColor: '#ddd',
              borderWidth: 1,
              padding: [8, 12],
              textStyle: {
                color: '#333'
              },
              extraCssText: 'box-shadow: 0 3px 10px rgba(0,0,0,0.2); border-radius: 8px;'
            },
            visualMap: {
              min: 0,
              max: 12, // 调整最大值以适应医院数量
              text: ['医院数量多', '医院数量少'],
              realtime: false,
              calculable: true,
              inRange: {
                color: ['#e0f3f8', '#abd9e9', '#74add1', '#4575b4', '#313695']
              },
              textStyle: {
                color: '#333',
                fontSize: 12
              },
              itemWidth: 15,
              itemHeight: 120,
              left: '5%',
              bottom: '10%',
              orient: 'vertical'
            },
            geo: {
              map: 'china',
              roam: true,
              zoom: 1.2,
              scaleLimit: {
                min: 1.0,
                max: 2.0
              },
              itemStyle: {
                areaColor: '#f8f9fa',
                borderColor: '#ccc',
                borderWidth: 0.5
              },
              emphasis: {
                itemStyle: {
                  areaColor: '#e6f7ff',
                  shadowColor: 'rgba(0, 0, 0, 0.3)',
                  shadowBlur: 10
                },
                label: {
                  show: true,
                  color: '#333'
                }
              }
            },
            series: [
              {
                type: 'map',
                map: 'china',
                geoIndex: 0,
                // 允许平移和缩放
                roam: true,
                zoom: 1.2, // 初始倍率为1.2
                scaleLimit: {
                  min: 1.0,
                  max: 2.0
                },
                data: this.seriesData,
                itemStyle: {
                  areaColor: '#f8f9fa',
                  borderColor: '#fff',
                  borderWidth: 1
                },
                emphasis: {
                  itemStyle: {
                    areaColor: '#e6f7ff',
                    shadowColor: 'rgba(0, 0, 0, 0.5)',
                    shadowBlur: 15
                  },
                  label: {
                    show: true,
                    color: '#333',
                    fontSize: 14,
                    fontWeight: 'bold'
                  }
                },
                select: {
                  itemStyle: {
                    areaColor: '#c6e2ff'
                  }
                }
              }
            ]
          };
          this.map.setOption(option);
          this.setTimer();
          let that = this;
          this.map.on('mouseover', { series: 0 }, function () {
            that.clearTimer();
          });
          this.map.on('mouseout', { series: 0 }, function () {
            that.setTimer();
          });
        });
      });
    },
    setTimer() {
      let curIndex = -1;
      this.timer && clearInterval(this.timer);
      this.timer = setInterval(() => {
        const len = this.seriesData.length;
        this.map.dispatchAction({
          type: 'downplay',
          seriesIndex: 0,
          dataIndex: curIndex
        });
        curIndex = (curIndex + 1) % len;
        this.map.dispatchAction({
          type: 'highlight',
          seriesIndex: 0,
          dataIndex: curIndex
        });
        this.map.dispatchAction({
          type: 'showTip',
          seriesIndex: 0,
          dataIndex: curIndex
        });
      }, 2000); // 增加间隔时间，使动画更平滑
    },
    clearTimer() {
      this.timer && clearInterval(this.timer);
    },
  }
}
</script>

<style scoped>
.map-container {
  width: 100%;
  height: 100%;
  min-height: 400px;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
}

.map-container:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  transform: translateY(-3px);
}

.map-header {
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.map-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
  margin-bottom: 5px;
}

.map-subtitle {
  font-size: 14px;
  color: #666;
}

.map-echart {
  flex: 1;
  width: 100%;
  height: calc(100% - 70px); /* 减去标题高度 */
}

@media (max-width: 768px) {
  .map-container {
    min-height: 350px;
  }
  
  .map-title {
    font-size: 16px;
  }
  
  .map-subtitle {
    font-size: 12px;
  }
}
</style>