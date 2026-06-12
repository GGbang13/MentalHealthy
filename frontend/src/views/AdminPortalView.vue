<template>
  <div class="portal-page">
    <div class="hero">
      <div>
        <div class="eyebrow">管理员端</div>
        <h2>平台管理与风险监控</h2>
        <p>聚合运营数据、风险记录和咨询师管理入口，形成清晰的管理员视角。</p>
      </div>
    </div>
    <div class="stats-grid">
      <el-card shadow="never" class="stat-card">
        <span>平台用户</span>
        <strong>{{ summary.userCount }}</strong>
      </el-card>
      <el-card shadow="never" class="stat-card">
        <span>咨询师总数</span>
        <strong>{{ summary.counselorCount }}</strong>
      </el-card>
      <el-card shadow="never" class="stat-card">
        <span>总预约数</span>
        <strong>{{ summary.appointmentCount }}</strong>
      </el-card>
      <el-card shadow="never" class="stat-card risk">
        <span>高风险记录</span>
        <strong>{{ summary.highRiskCount }}</strong>
      </el-card>
    </div>
    <div class="panel-grid">
      <el-card shadow="never">
        <template #header>风险分布</template>
        <div class="risk-list">
          <div v-for="item in summary.riskDistribution" :key="item.level" class="risk-row">
            <span>{{ item.level }}</span>
            <strong>{{ item.count }}</strong>
          </div>
        </div>
      </el-card>
      <el-card shadow="never">
        <template #header>管理入口</template>
        <div class="admin-actions">
          <el-button type="primary" @click="router.push('/dashboard')">运营总览</el-button>
          <el-button @click="router.push('/admin/notifications')">通知管理</el-button>
          <el-button @click="router.push('/admin/users')">用户管理</el-button>
          <el-button @click="router.push('/admin/counselors')">咨询师管理</el-button>
          <el-button @click="router.push('/admin/articles')">文章管理</el-button>
        </div>
      </el-card>
    </div>
    <NotificationPanel />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/api/http'
import NotificationPanel from '@/components/NotificationPanel.vue'
import type { DashboardSummary } from '@/types'

const router = useRouter()
const summary = ref<DashboardSummary>({
  userCount: 0,
  counselorCount: 0,
  onlineCounselorCount: 0,
  appointmentCount: 0,
  pendingAppointmentCount: 0,
  assessmentCount: 0,
  highRiskCount: 0,
  riskDistribution: [],
  recentActivities: []
})

onMounted(async () => {
  summary.value = await http.get<DashboardSummary>('/dashboard/summary')
})
</script>

<style scoped lang="scss">
.portal-page { display: grid; gap: 18px; }
.hero { padding: 22px; border-radius: 22px; background: linear-gradient(135deg, #fef2f2, #fff7ed); }
.eyebrow { color: #b91c1c; font-size: 13px; font-weight: 700; }
.hero h2 { margin: 10px 0; }
.hero p { margin: 0; color: #475569; line-height: 1.7; }
.stats-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; }
.stat-card { display: grid; gap: 8px; }
.stat-card span { color: #64748b; }
.stat-card strong { color: #0f172a; font-size: 28px; }
.stat-card.risk strong { color: #dc2626; }
.panel-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.risk-list { display: grid; gap: 10px; }
.risk-row { display: flex; justify-content: space-between; padding: 12px; border-radius: 12px; background: #f8fafc; }
.admin-actions { display: flex; flex-wrap: wrap; gap: 10px; }
@media (max-width: 960px) { .stats-grid, .panel-grid { grid-template-columns: 1fr; } }
</style>
