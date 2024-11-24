import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  { path: '/', component: () => import('@/views/TheHome.vue') },
  { path: '/login', component: () => import('@/views/TheLogin.vue') },
  { path: '/register', component: () => import('@/views/TheRegister.vue') },
  { path: '/sponsor/dashboard', component: () => import('@/views/sponsor/TheDashboard.vue') },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
