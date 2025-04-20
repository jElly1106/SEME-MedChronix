<template>
    <div class="navbar">
      <ul>
        <li 
          v-for="item in items" 
          :key="item.name"
          :class="{'selected': selected === item.name}" 
          @click="selectItem(item.name)">
          {{ item.name }}
        </li>
      </ul>
    </div>
  </template>
  
  <script>
  export default {
    name: "TopNavbar",
    data() {
      return {
        items: [
          { name: '病人详情' },
          { name: '总体概览' },
          { name: '疾病分析' }
        ],
        selected: null
      };
    },
    methods: {
      selectItem(name) {
        this.selected = name;  // 更新选中的项
      }
    }
  };
  </script>
  
  <style scoped>
  .navbar {
    background-color: white;
    padding: 10px 0;
  }
  
  .navbar ul {
    list-style-type: none;
    display: flex;
    justify-content: flex-end; /* 右对齐 */
    margin: 0;
    padding: 0;
  }
  
  .navbar li {
    cursor: pointer;
    font-size: 16px;
    padding: 10px 20px;
    color: #2D5BFF; /* 默认蓝色 */
    transition: all 0.3s ease;
  }
  
  .navbar li.selected {
    background-color: #2D5BFF; /* 选中时底色 */
    color: white; /* 选中时文字颜色变为白色 */
  }
  </style>
  