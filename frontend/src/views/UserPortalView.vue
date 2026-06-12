<template>
  <div class="portal-page">
    <div class="hero">
      <div>
        <div class="eyebrow">用户端</div>
        <h2>面向来访用户的心理支持入口</h2>
        <p>整合心理测评、预约咨询、心理文章、在线聊天和个人资料，适合完整演示用户使用流程。</p>
      </div>
    </div>
    <div class="panel-grid">
      <el-card shadow="never" class="portal-card">
        <h3>心理测评</h3>
        <p>提交量表，查看 CatBoost 风险概率与高影响变量。</p>
        <el-button type="primary" @click="router.push('/assessments')">去测评</el-button>
      </el-card>
      <el-card shadow="never" class="portal-card">
        <h3>预约咨询</h3>
        <p>浏览咨询师并提交预约，追踪预约状态与时间安排。</p>
        <el-button type="primary" @click="router.push('/appointments')">去预约</el-button>
      </el-card>
      <el-card shadow="never" class="portal-card">
        <h3>心理文章</h3>
        <p>阅读已整合到平台内的心理健康科普内容。</p>
        <el-button type="primary" @click="router.push('/articles')">去阅读</el-button>
      </el-card>
      <el-card shadow="never" class="portal-card">
        <h3>在线沟通</h3>
        <p>与咨询师或平台角色保持消息沟通，支持会话历史查看。</p>
        <el-button type="primary" @click="router.push('/chat')">去聊天</el-button>
      </el-card>
    </div>
    <NotificationPanel />
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import NotificationPanel from '@/components/NotificationPanel.vue'
const router = useRouter()
</script>

<style scoped lang="scss">
.portal-page { display: grid; gap: 18px; }
.hero { padding: 22px; border-radius: 22px; background: linear-gradient(135deg, #eff6ff, #ecfeff); }
.eyebrow { color: #2563eb; font-size: 13px; font-weight: 700; }
.hero h2 { margin: 10px 0; }
.hero p { margin: 0; color: #475569; line-height: 1.7; }
.panel-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.portal-card { display: grid; gap: 12px; }
.portal-card h3 { margin: 0; }
.portal-card p { margin: 0; color: #475569; line-height: 1.7; }
@media (max-width: 960px) { .panel-grid { grid-template-columns: 1fr; } }
</style>
