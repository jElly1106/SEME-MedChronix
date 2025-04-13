/* eslint-disable */
/** 该文件为路由配置文件，用于配置路由信息 */
import { createRouter, createWebHashHistory } from 'vue-router'
import homePage from '@/views/homePage.vue'
import loginPage from '@/views/loginPage.vue'
import registerPage from '@/views/registerPage.vue'
import diseaseAnalysisPage from '@/views/diseaseAnalysisPage.vue'; // 假设这个是你疾病分析页面的路径
import patientAnalysisPage from '@/views/patientAnalysisPage.vue'; // 假设这个是你患者分析页面的路径
import DashBoardPage from '@/views/dashBoardPage.vue';


// TODO 转到admin由login页面决定
const router = createRouter({
    history: createWebHashHistory(),
    routes: [
        {
            path: '/',
            redirect: '/login'
        },
        {
            path: '/home',
            name: 'home',
            component: DashBoardPage,
            meta: {
                requiresAuth: true
            }
        },
        {
            path: '/login',
            name: 'Login',
            component: loginPage,
            //props: { type: 'login' }
        },
        {
            path: '/register',
            name: 'Register',
            component: registerPage,
        },
        {
            path: '/diseaseAnalysis',
            name: 'DiseaseAnalysis',
            component: diseaseAnalysisPage,
        },
        {
            path: '/patientAnalysis',
            name: 'patientAnalysis',
            component: patientAnalysisPage,

        },
    ]
})

// 全局路由前置守卫,最后加，要不无法正常使用
// router.beforeEach((to, from, next) => {
//     const token = localStorage.getItem('token'); // 获取 token

//     if (to.meta.requiresAuth && !token) {
//         // 如果目标路由需要登录权限，且没有 token，跳转到登录页
//         next({ path: '/login' });
//     } else {
//         // 如果有 token 或目标路由不需要权限，继续导航
//         next();
//     }
// });

export default router