/* eslint-disable */
/** 该文件为路由配置文件，用于配置路由信息 */
import { createRouter, createWebHashHistory } from 'vue-router'
import homePage from '@/views/homePage.vue'
import loginPage from '@/views/loginPage.vue'
import registerPage from '@/views/registerPage.vue'
import diseaseAnalysisPage from '@/views/diseaseAnalysisPage.vue'; // 假设这个是你疾病分析页面的路径
import patientAnalysisPage from '@/views/patientAnalysisPage.vue'; // 假设这个是你患者分析页面的路径
import DashBoardPage from '@/views/dashBoardPage.vue';
import ProfilePage from '@/views/ProfilePage.vue'; // 个人信息管理页面
import QualificationReviewPage from '@/views/QualificationReviewPage.vue'; // 资质审核页面
import permissionConfigPage from '@/views/permissionConfigPage.vue';
import auditLogPage from '@/views/auditLogPage.vue';

// TODO 转到admin由login页面决定
const router = createRouter({
    history: createWebHashHistory(),
    routes: [
        {
            path: '/',
            redirect: '/dashBoardPage'
        },
        {
            path: '/dashBoardPage',
            name: 'dashBoardPage',
            component: DashBoardPage,
            meta: {
                requiresAuth: true,
                requiresQualification: true // 需要资质验证
            }
        },
        {
            path: '/login',
            name: 'Login',
            component: loginPage,
            //props: { type: 'login' }
        },
        {
            path:'/home',
            name:'Home',
            component:homePage,
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
            meta: {
                requiresAuth: true,
                requiresQualification: true // 需要资质验证
            }
        },
        {
            path: '/patientAnalysis',
            name: 'patientAnalysis',
            component: patientAnalysisPage,
            meta: {
                requiresAuth: true,
                requiresQualification: true // 需要资质验证
            }
        },
        {
            path: '/profile',
            name: 'Profile',
            component: ProfilePage,
            meta: {
                requiresAuth: true
            }
        },
        {
            path: '/qualification-review',
            name: 'QualificationReview',
            component: QualificationReviewPage,
            meta: {
                requiresAuth: true,
                requiresAdmin: true // 需要管理员权限
            }
        },
        {
            path: '/permission-config',
            name: 'PermissionConfig',
            component:  permissionConfigPage,
            meta: {
                requiresAuth: true,
                requiresAdmin: true // 需要管理员权限
            }
        },
        {
            path: '/audit-log',
            name: 'AuditLog',
            component:  auditLogPage,
            meta: {
                requiresAuth: true,
                requiresAdmin: true // 需要管理员权限
            }
        },
    ]
})



// 全局路由前置守卫
// router.beforeEach((to, from, next) => {
//     const token = localStorage.getItem('token'); // 获取 token

//     if (to.meta.requiresAuth && !token) {
//         // 如果目标路由需要登录权限，且没有 token，跳转到登录页
//         next({ path: '/login' });
//         return;
//     }
    
//     // 检查资质验证要求
//     if (to.meta.requiresQualification) {
//         // 从localStorage获取用户资质状态
//         const qualificationStatus = localStorage.getItem('qualificationStatus');
        
//         // 只有资质状态为 'approved' 的用户才能访问需要资质验证的页面
//         if (qualificationStatus !== 'approved') {
//             // 如果资质未通过，重定向到个人信息页面
//             next({ path: '/profile' });
//             return;
//         }
//     }
    
//     // 检查管理员权限要求
//     if (to.meta.requiresAdmin) {
//         const isAdmin = localStorage.getItem('isAdmin') === 'true';
//         if (!isAdmin) {
//             // 如果不是管理员，重定向到首页
//             next({ path: '/home' });
//             return;
//         }
//     }
    
//     // 如果没有特殊要求或已满足所有要求，继续导航
//     next();
// });

export default router