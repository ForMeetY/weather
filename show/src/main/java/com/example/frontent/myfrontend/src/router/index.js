import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // home 页面 懒加载
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/home/home.vue'),
    },
    // 未匹配到的路由跳转home
    {
      path: '/:pathMatch(.*)*',
      redirect: '/',
    },
    // statistic 页面 懒加载
    {
      path: '/statistic',
      name: 'statistic',
      component: () => import('@/views/statistic/index.vue'), 
      children: [
        {
          path: '/statistic/diurnal',
          name: 'diurnal',
          component: () => import('@/views/statistic/diurnal.vue'),
        },
        {
          path: '/statistic/extreme',
          name: 'extreme',
          component: () => import('@/views/statistic/extreme.vue'),
        },
        {
          path: '/statistic/forecast',
          name: 'forecast',
          component: () => import('@/views/statistic/forecast.vue'),
        },
        {
          path: '/statistic/trend',
          name: 'trend',
          component: () => import('@/views/statistic/tender.vue'),
        },
      ]
    },
   
  ],
})

export default router
