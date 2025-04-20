import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus';
import 'element-plus/theme-chalk/index.css'; // 引入样式
import Antd from 'ant-design-vue';
// import 'ant-design-vue/lib/style/index.css';有点bug，找不到这个文件


const app = createApp(App)
app
    .use(router)
    .use(ElementPlus)
    .use(Antd)
    .mount('#app')
