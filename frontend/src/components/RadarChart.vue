<template>
    <div>
      <!-- Tab navigation for selecting patients -->
      <div class="tab-container" v-if="$props.selected && $props.selected.length > 0">
        <div class="tab-scroll">
          <div 
            v-for="(patient, index) in $props.selected" 
            :key="index" 
            :class="['patient-tab', {'active': selectedPatient === patient.name}]" 
            @click="selectPatient(patient)">
            <span class="patient-name">{{ patient.name }}</span>
          </div>
        </div>
      </div>

      <!-- Radar chart -->
      <div class="radar-chart">
        <canvas ref="radarChart"></canvas>
      </div>
    </div>
  </template>
  
  <script>
  import { onMounted, ref, watch, nextTick } from "vue";
  import Chart from "chart.js/auto";
  
  export default {
    name: "RadarChart",
    props: {
      selected: {
        type: Array,
        required: true,
        default: () => []
      }
    },
    setup(props) {
      const radarChart = ref(null);
      const selectedPatient = ref(null);
      let chartInstance = null;
      
      // 监听数据变化
      watch(() => props.selected, (newValue) => {
        console.log('接收到的 selected 数据:', newValue);
        if (newValue && newValue.length > 0) {
          selectedPatient.value = newValue[0].name;
          
          // 使用 nextTick 确保 DOM 已更新
          nextTick(() => {
            if (chartInstance) {
              // 如果图表已存在，更新数据
              updateChartData(newValue[0].data);
            } else {
              // 如果图表不存在，初始化图表
              initChart();
            }
          });
        }
      }, { immediate: true, deep: true });
  
      const initChart = () => {
        if (!radarChart.value) return;
        
        try {
          const ctx = radarChart.value.getContext("2d");
          
          // 确保数据存在
          if (!props.selected || props.selected.length === 0 || !props.selected[0].data) {
            console.error('No valid data for radar chart');
            return;
          }
          
          const data = {
            labels: ["钠", "钾", "动脉血氧饱和度", "动脉血压", "血糖", "血细胞比容"],
            datasets: [{
              label: "雷达图数据",
              data: props.selected[0].data,
              backgroundColor: "rgba(147, 170, 253, 0.2)",
              borderColor: "rgba(147, 170, 253, 1)",
              borderWidth: 1,
              pointBackgroundColor: "rgba(147, 170, 253, 1)",
            }]
          };

          // 销毁旧图表（如果存在）
          if (chartInstance) {
            chartInstance.destroy();
          }

          chartInstance = new Chart(ctx, {
            type: "radar",
            data: data,
            options: {
              scales: {
                r: {
                  beginAtZero: true,
                },
              },
              responsive: true,
              maintainAspectRatio: false
            },
          });
        } catch (error) {
          console.error('Error initializing chart:', error);
        }
      };

      const updateChartData = (patientData) => {
        if (!chartInstance || !patientData) return;
        
        try {
          chartInstance.data.datasets[0].data = patientData;
          chartInstance.update();
        } catch (error) {
          console.error('Error updating chart:', error);
          // 如果更新失败，尝试重新初始化图表
          initChart();
        }
      };

      const selectPatient = (patient) => {
        if (!patient || !patient.data) return;
        
        selectedPatient.value = patient.name;
        updateChartData(patient.data);
      };

      onMounted(() => {
        // 延迟初始化图表，确保 DOM 已完全渲染
        nextTick(() => {
          if (props.selected && props.selected.length > 0) {
            selectedPatient.value = props.selected[0].name;
            initChart();
          }
        });
      });
  
      return {
        radarChart,
        selectedPatient,
        selectPatient,
      };
    },
  };
  </script>
  
  <style scoped>
  .tab-container {
    margin-bottom: 15px;
    max-width:350px;
    width: 100%;
    overflow: hidden;
    background-color: #f5f7ff;
    border-radius: 8px;
    padding: 8px;
  }
  
  .tab-scroll {
    display: flex;
    overflow-x: auto;
    scrollbar-width: thin;
    scrollbar-color: #93aafd #e5eafc;
    padding-bottom: 5px;
    gap: 8px;
  }
  
  .tab-scroll::-webkit-scrollbar {
    height: 4px;
  }
  
  .tab-scroll::-webkit-scrollbar-track {
    background: #e5eafc;
    border-radius: 10px;
  }
  
  .tab-scroll::-webkit-scrollbar-thumb {
    background-color: #93aafd;
    border-radius: 10px;
  }
  
  .patient-tab {
    flex: 0 0 auto;
    padding: 8px 16px;
    background-color: #fff;
    border: 1px solid #e0e6ff;
    cursor: pointer;
    border-radius: 20px;
    font-weight: 500;
    font-size: 14px;
    transition: all 0.3s ease;
    white-space: nowrap;
    min-width: 40px;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }
  
  .patient-tab.active {
    background-color: #2D5BFF;
    color: white;
    border-color: #2D5BFF;
    box-shadow: 0 2px 8px rgba(45, 91, 255, 0.3);
  }
  
  .patient-tab:hover:not(.active) {
    background-color: #e5eafc;
    transform: translateY(-1px);
  }
  
  .patient-name {
    display: block;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .radar-chart {
    padding: 16px;
    height: 300px;
  }
  </style>
  