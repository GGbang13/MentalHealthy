import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import Layout from '@/views/Layout.vue'

const resolveHome = (role?: string) => {
  if (role === 'ADMIN') return '/admin'
  if (role === 'COUNSELOR') return '/counselor'
  return '/user'
}

const hasRoleAccess = (role: string | undefined, allowedRoles?: string[]) => {
  if (!allowedRoles?.length) return true
  if (!role) return false
  return allowedRoles.includes(role)
}

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      component: () => import('@/views/LoginView.vue')
    },
    {
      path: '/',
      component: Layout,
      children: [
        { path: '', redirect: '/user' },
        { path: 'dashboard', component: () => import('@/views/DashboardView.vue'), meta: { allowedRoles: ['ADMIN'] } },
        { path: 'user', component: () => import('@/views/UserPortalView.vue'), meta: { allowedRoles: ['USER'] } },
        { path: 'counselor', component: () => import('@/views/CounselorPortalView.vue'), meta: { allowedRoles: ['COUNSELOR'] } },
        { path: 'admin', component: () => import('@/views/AdminPortalView.vue'), meta: { allowedRoles: ['ADMIN'] } },
        { path: 'admin/notifications', component: () => import('@/views/AdminNotificationManageView.vue'), meta: { allowedRoles: ['ADMIN'] } },
        { path: 'admin/users', component: () => import('@/views/AdminUserManageView.vue'), meta: { allowedRoles: ['ADMIN'] } },
        { path: 'admin/counselors', component: () => import('@/views/AdminCounselorManageView.vue'), meta: { allowedRoles: ['ADMIN'] } },
        { path: 'admin/articles', component: () => import('@/views/AdminArticleManageView.vue'), meta: { allowedRoles: ['ADMIN'] } },
        { path: 'admin/articles/new', component: () => import('@/views/AdminArticleCreateView.vue'), meta: { allowedRoles: ['ADMIN'] } },
        { path: 'admin/articles/:id/edit', component: () => import('@/views/AdminArticleEditView.vue'), meta: { allowedRoles: ['ADMIN'] } },
        { path: 'counselors', component: () => import('@/views/CounselorView.vue'), meta: { allowedRoles: ['USER', 'ADMIN'] } },
        { path: 'appointments', component: () => import('@/views/AppointmentView.vue'), meta: { allowedRoles: ['USER'] } },
        { path: 'assessments', component: () => import('@/views/AssessmentView.vue'), meta: { allowedRoles: ['USER', 'ADMIN'] } },
        { path: 'articles', component: () => import('@/views/ArticleListView.vue'), meta: { allowedRoles: ['USER', 'COUNSELOR', 'ADMIN'] } },
        { path: 'articles/:id', component: () => import('@/views/ArticleDetailView.vue'), meta: { allowedRoles: ['USER', 'COUNSELOR', 'ADMIN'] } },
        { path: 'chat', component: () => import('@/views/ChatView.vue'), meta: { allowedRoles: ['USER', 'COUNSELOR'] } },
        { path: 'profile', component: () => import('@/views/ProfileView.vue'), meta: { allowedRoles: ['USER', 'COUNSELOR', 'ADMIN'] } }
      ]
    }
  ]
})

router.beforeEach((to) => {
  const userStore = useUserStore()
  if (to.path !== '/login' && !userStore.token) {
    return '/login'
  }
  if (to.path === '/login' && userStore.token) {
    return resolveHome(userStore.user?.role)
  }
  if (to.path === '/') {
    return resolveHome(userStore.user?.role)
  }
  if (!hasRoleAccess(userStore.user?.role, to.meta.allowedRoles as string[] | undefined)) {
    return resolveHome(userStore.user?.role)
  }
})

export default router
