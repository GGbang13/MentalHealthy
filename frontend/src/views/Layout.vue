<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="brand">
        <h2>MindBridge</h2>
        <p>心理健康服务平台</p>
        <div class="brand-tip">按角色拆分为用户端、咨询师端、管理员端，支持可展开的分组导航。</div>
      </div>

      <div class="menu-sections">
        <div v-for="section in visibleSections" :key="section.title" class="menu-section">
          <div class="section-label">{{ section.title }}</div>

          <div v-for="group in section.groups" :key="group.key" class="nav-group">
            <router-link
              v-if="group.children.length === 1"
              :to="group.children[0].path"
              class="nav-direct"
              :class="{ active: isRouteMatch(group.children[0].path, route.path) }"
            >
              <div class="nav-icon">
                <component :is="group.icon" />
              </div>
              <div class="nav-copy">
                <strong>{{ group.children[0].label }}</strong>
                <span>{{ group.children[0].description }}</span>
              </div>
            </router-link>

            <template v-else>
              <button
                type="button"
                class="nav-group-trigger"
                :class="{ active: isGroupActive(group) }"
                @click="toggleGroup(group.key)"
              >
                <div class="nav-icon">
                  <component :is="group.icon" />
                </div>
                <div class="nav-copy">
                  <strong>{{ group.label }}</strong>
                  <span>{{ group.description }}</span>
                </div>
                <span class="nav-arrow" :class="{ open: expandedGroups[group.key] }">⌄</span>
              </button>

              <transition name="nav-expand">
                <div v-show="expandedGroups[group.key]" class="nav-children">
                  <router-link
                    v-for="child in group.children"
                    :key="child.path"
                    :to="child.path"
                    class="nav-child"
                    :class="{ active: isRouteMatch(child.path, route.path) }"
                  >
                    <strong>{{ child.label }}</strong>
                    <span>{{ child.description }}</span>
                  </router-link>
                </div>
              </transition>
            </template>
          </div>
        </div>
      </div>
    </aside>

    <main class="content">
      <header class="topbar">
        <div>
          <h1>{{ pageTitle }}</h1>
          <span>按角色组织的心理服务与管理入口</span>
        </div>
        <div class="topbar-user">
          <span>{{ userStore.user?.nickname || userStore.user?.username }}</span>
          <el-tag>{{ roleLabel }}</el-tag>
          <el-button text @click="logout">退出</el-button>
        </div>
      </header>
      <section class="page-card">
        <router-view />
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Calendar,
  ChatLineRound,
  Collection,
  DataAnalysis,
  Monitor,
  Service,
  User
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

type NavChild = {
  path: string
  label: string
  description: string
}

type NavGroup = {
  key: string
  label: string
  description: string
  icon: unknown
  children: NavChild[]
}

type NavSection = {
  title: string
  roles: string[]
  groups: NavGroup[]
}

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const currentRole = computed(() => userStore.user?.role || 'USER')
const expandedGroups = ref<Record<string, boolean>>({})

const navSections: NavSection[] = [
  {
    title: '用户端',
    roles: ['USER'],
    groups: [
      {
        key: 'user-home',
        label: '用户首页',
        description: '查看用户端核心服务入口',
        icon: Monitor,
        children: [
          { path: '/user', label: '服务首页', description: '查看用户常用服务和概览' }
        ]
      },
      {
        key: 'user-mental',
        label: '心理服务',
        description: '测评与心理健康内容',
        icon: DataAnalysis,
        children: [
          { path: '/assessments', label: '心理测评', description: '提交量表并查看高影响变量' },
          { path: '/articles', label: '心理文章', description: '查看心理科普与健康教育资料' }
        ]
      },
      {
        key: 'user-consult',
        label: '咨询服务',
        description: '咨询师、预约与在线沟通',
        icon: Service,
        children: [
          { path: '/counselors', label: '咨询师列表', description: '浏览咨询师和专业方向' },
          { path: '/appointments', label: '预约咨询', description: '发起预约并跟踪状态' },
          { path: '/chat', label: '在线聊天', description: '与咨询师保持沟通' }
        ]
      },
      {
        key: 'user-profile',
        label: '我的资料',
        description: '维护个人资料信息',
        icon: User,
        children: [
          { path: '/profile', label: '个人中心', description: '维护账号资料与个人信息' }
        ]
      }
    ]
  },
  {
    title: '咨询师端',
    roles: ['COUNSELOR'],
    groups: [
      {
        key: 'counselor-workbench',
        label: '工作台',
        description: '查看预约与工作入口',
        icon: Monitor,
        children: [
          { path: '/counselor', label: '咨询师工作台', description: '查看我的预约和来访沟通入口' }
        ]
      },
      {
        key: 'counselor-service',
        label: '沟通与内容',
        description: '沟通来访者与阅读内容',
        icon: ChatLineRound,
        children: [
          { path: '/chat', label: '来访沟通', description: '查看联系人并继续会话' },
          { path: '/articles', label: '心理文章', description: '阅读文章并用于沟通辅导' }
        ]
      },
      {
        key: 'counselor-profile',
        label: '资料维护',
        description: '维护个人资料与简介',
        icon: User,
        children: [
          { path: '/profile', label: '个人资料', description: '更新个人资料与专业简介' }
        ]
      }
    ]
  },
  {
    title: '管理员端',
    roles: ['ADMIN'],
    groups: [
      {
        key: 'admin-overview',
        label: '平台总览',
        description: '查看运营与风险概况',
        icon: Monitor,
        children: [
          { path: '/admin', label: '管理首页', description: '按管理员视角查看平台数据' },
          { path: '/dashboard', label: '运营总览', description: '查看平台核心数据与风险分布' }
        ]
      },
      {
        key: 'admin-manage',
        label: '账号与服务管理',
        description: '分开管理用户、咨询师和风险记录',
        icon: Service,
        children: [
          { path: '/admin/notifications', label: '通知管理', description: '向用户和咨询师发布平台通知' },
          { path: '/admin/users', label: '用户管理', description: '查看普通用户与管理员列表' },
          { path: '/admin/counselors', label: '咨询师管理', description: '查看咨询师资料与账号列表' },
          { path: '/assessments', label: '风险监控', description: '按列表查看用户参与测评的数据记录' }
        ]
      },
      {
        key: 'admin-content',
        label: '内容与设置',
        description: '管理内容和管理员资料',
        icon: Collection,
        children: [
          { path: '/admin/articles', label: '文章管理', description: '增删改查心理文章内容' },
          { path: '/articles', label: '文章预览', description: '按普通访客视角查看文章列表' },
          { path: '/profile', label: '管理员资料', description: '维护管理员账户信息' }
        ]
      }
    ]
  }
]

const visibleSections = computed(() =>
  navSections.filter((section) => section.roles.includes(currentRole.value))
)

const isRouteMatch = (targetPath: string, currentPath: string) => {
  if (currentPath === targetPath) return true
  if (targetPath === '/admin/articles' && currentPath.startsWith('/admin/articles/')) return true
  if (targetPath === '/articles' && /^\/articles\/\d+$/.test(currentPath)) return true
  return false
}

const titleMap: Record<string, string> = {
  '/user': '用户首页',
  '/counselor': '咨询师工作台',
  '/admin': '管理首页',
  '/admin/notifications': '通知管理',
  '/admin/users': '用户管理',
  '/admin/counselors': '咨询师管理',
  '/admin/articles': '文章管理',
  '/dashboard': '平台总览',
  '/counselors': '咨询师管理',
  '/appointments': '预约咨询',
  '/assessments': '心理测评',
  '/articles': '心理文章',
  '/chat': '在线聊天',
  '/profile': '个人中心'
}

const pageTitle = computed(() => {
  if (route.path === '/assessments' && currentRole.value === 'ADMIN') {
    return '风险监控'
  }
  if (route.path === '/admin/articles/new') {
    return '新建文章'
  }
  if (/^\/admin\/articles\/[^/]+\/edit$/.test(route.path)) {
    return '编辑文章'
  }
  if (/^\/articles\/[^/]+$/.test(route.path)) {
    return '文章详情'
  }
  return titleMap[route.path] || '心理健康服务平台'
})
const roleLabel = computed(() => currentRole.value === 'ADMIN' ? '管理员' : currentRole.value === 'COUNSELOR' ? '咨询师' : '用户')

const ensureActiveGroupOpen = () => {
  const nextState: Record<string, boolean> = { ...expandedGroups.value }
  for (const section of visibleSections.value) {
    for (const group of section.groups) {
      if (group.children.some((child) => child.path === route.path)) {
        nextState[group.key] = true
      } else if (group.children.some((child) => isRouteMatch(child.path, route.path))) {
        nextState[group.key] = true
      } else if (!(group.key in nextState)) {
        nextState[group.key] = false
      }
    }
  }
  expandedGroups.value = nextState
}

watch([visibleSections, () => route.path], ensureActiveGroupOpen, { immediate: true })

const toggleGroup = (key: string) => {
  expandedGroups.value[key] = !expandedGroups.value[key]
}

const isGroupActive = (group: NavGroup) => group.children.some((child) => isRouteMatch(child.path, route.path))

const logout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped lang="scss">
.layout {
  display: grid;
  grid-template-columns: 300px 1fr;
  min-height: 100vh;
  background: var(--bg);
}

.sidebar {
  display: grid;
  align-content: start;
  gap: 20px;
  padding: 28px 20px;
  background: rgba(23, 49, 43, 0.97);
  color: #f8f4eb;
  height: 100vh;
  position: sticky;
  top: 0;
  overflow-y: auto;
  scrollbar-gutter: stable;
  box-sizing: border-box;
}

.brand {
  margin-bottom: 8px;
}

.brand h2 {
  margin: 0;
  font-size: 28px;
}

.brand p {
  margin: 8px 0 0;
  color: rgba(248, 244, 235, 0.72);
}

.brand-tip {
  margin-top: 14px;
  padding: 10px 12px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.08);
  color: rgba(248, 244, 235, 0.82);
  font-size: 13px;
  line-height: 1.6;
}

.menu-sections {
  display: grid;
  gap: 18px;
}

.menu-section {
  display: grid;
  gap: 12px;
}

.section-label {
  padding: 0 10px;
  color: rgba(248, 244, 235, 0.5);
  font-size: 12px;
  letter-spacing: 0.08em;
}

.nav-group {
  display: grid;
  gap: 8px;
}

.nav-group-trigger {
  display: grid;
  grid-template-columns: 42px 1fr 20px;
  gap: 12px;
  align-items: center;
  width: 100%;
  padding: 12px;
  border: 0;
  border-radius: 16px;
  color: #f8f4eb;
  background: transparent;
  text-align: left;
  cursor: pointer;
  transition: background-color 0.2s ease, box-shadow 0.2s ease;
}

.nav-group-trigger:hover {
  background: rgba(255, 255, 255, 0.08);
}

.nav-group-trigger.active {
  background: linear-gradient(135deg, rgba(78, 180, 132, 0.2), rgba(117, 211, 158, 0.12));
  box-shadow: inset 0 0 0 1px rgba(167, 243, 208, 0.18);
}

.nav-direct {
  display: grid;
  grid-template-columns: 42px 1fr;
  gap: 12px;
  align-items: center;
  width: 100%;
  padding: 12px;
  border-radius: 16px;
  color: #f8f4eb;
  text-decoration: none;
  transition: background-color 0.2s ease, box-shadow 0.2s ease;
}

.nav-direct:hover {
  background: rgba(255, 255, 255, 0.08);
}

.nav-direct.active {
  background: linear-gradient(135deg, rgba(78, 180, 132, 0.2), rgba(117, 211, 158, 0.12));
  box-shadow: inset 0 0 0 1px rgba(167, 243, 208, 0.18);
}

.nav-icon {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.1);
  font-size: 18px;
}

.nav-copy {
  display: grid;
  gap: 4px;
}

.nav-copy strong {
  font-size: 15px;
}

.nav-copy span {
  color: rgba(248, 244, 235, 0.68);
  font-size: 12px;
  line-height: 1.4;
}

.nav-arrow {
  color: rgba(248, 244, 235, 0.72);
  transition: transform 0.2s ease;
}

.nav-arrow.open {
  transform: rotate(180deg);
}

.nav-children {
  display: grid;
  gap: 8px;
  margin-left: 18px;
  padding-left: 18px;
  border-left: 1px solid rgba(248, 244, 235, 0.12);
}

.nav-child {
  display: grid;
  gap: 3px;
  padding: 10px 12px;
  border-radius: 12px;
  color: rgba(248, 244, 235, 0.86);
  text-decoration: none;
  transition: background-color 0.2s ease;
}

.nav-child:hover {
  background: rgba(255, 255, 255, 0.06);
}

.nav-child.active {
  background: rgba(167, 243, 208, 0.14);
  color: #fff;
}

.nav-child strong {
  font-size: 14px;
}

.nav-child span {
  font-size: 12px;
  color: rgba(248, 244, 235, 0.62);
  line-height: 1.4;
}

.nav-expand-enter-active,
.nav-expand-leave-active {
  transform-origin: top;
  transition: opacity 0.22s ease, transform 0.22s ease;
}

.nav-expand-enter-from,
.nav-expand-leave-to {
  opacity: 0;
  transform: translateY(-6px) scaleY(0.98);
}

.content {
  padding: 26px;
  min-width: 0;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.topbar h1 {
  margin: 0;
}

.topbar span {
  color: var(--muted);
}

.topbar-user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-card {
  min-height: calc(100vh - 120px);
  padding: 24px;
  border-radius: 24px;
  background: var(--panel);
  backdrop-filter: blur(18px);
  box-shadow: 0 24px 60px rgba(33, 58, 50, 0.1);
}

@media (max-width: 960px) {
  .layout {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: static;
    height: auto;
    padding-bottom: 10px;
  }
}
</style>
