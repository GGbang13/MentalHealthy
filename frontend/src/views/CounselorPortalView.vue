<template>
  <div class="portal-page">
    <div class="hero">
      <div>
        <div class="eyebrow">咨询师端</div>
        <h2>咨询师工作台</h2>
        <p>处理预约申请、维护咨询关系，并在预约确认后直接进入沟通窗口。</p>
      </div>
    </div>

    <el-card shadow="never">
      <template #header>待处理与已确认预约</template>
      <div class="appointment-list">
        <div v-for="item in appointments" :key="item.id" class="appointment-item">
          <div class="appointment-main">
            <div class="appointment-top">
              <strong>{{ item.userNickname || `用户#${item.userId}` }}</strong>
              <el-tag :type="statusType(item.status)" effect="plain">{{ statusLabel(item.status) }}</el-tag>
            </div>
            <div class="appointment-meta">
              <span>{{ formatDate(item.appointmentTime) }}</span>
              <span>{{ typeLabel(item.type) }}</span>
              <span>{{ item.durationMinutes }} 分钟</span>
            </div>
            <p class="appointment-desc">{{ item.issueDescription || '对方暂未填写问题描述。' }}</p>
          </div>
          <div class="appointment-actions">
            <el-button
              v-if="item.status === 'PENDING'"
              type="success"
              plain
              @click="confirmAppointment(item.id)"
            >
              同意
            </el-button>
            <el-button
              v-if="item.status === 'PENDING'"
              type="danger"
              plain
              @click="rejectAppointment(item.id)"
            >
              拒绝
            </el-button>
            <el-button
              v-if="item.canChat"
              type="primary"
              @click="openChat(item.userId)"
            >
              开始沟通
            </el-button>
          </div>
        </div>
        <el-empty v-if="!appointments.length" description="暂无预约记录" />
      </div>
    </el-card>

    <div class="panel-grid">
      <el-card shadow="never" class="portal-card portal-link-card" @click="openChatPage">
        <h3>可沟通来访者</h3>
        <p>已确认预约或已有历史会话的来访者共 {{ contacts.length }} 位，点击这里直接进入聊天页。</p>
        <div class="link-row">
          <el-button type="primary" @click.stop="openChatPage">进入聊天页</el-button>
        </div>
      </el-card>

      <el-card shadow="never" class="portal-card">
        <h3>资料维护</h3>
        <p>更新擅长方向、价格和在线状态，用户列表会同步展示这些信息。</p>
        <el-button type="primary" @click="router.push('/profile')">编辑资料</el-button>
      </el-card>
    </div>
    <NotificationPanel />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import http from '@/api/http'
import NotificationPanel from '@/components/NotificationPanel.vue'
import type { Appointment, ChatContact } from '@/types'

const router = useRouter()
const appointments = ref<Appointment[]>([])
const contacts = ref<ChatContact[]>([])

const loadData = async () => {
  const [appointmentData, contactData] = await Promise.all([
    http.get<Appointment[]>('/appointments/counselor'),
    http.get<ChatContact[]>('/chat/contacts')
  ])
  appointments.value = appointmentData
  contacts.value = contactData
}

const confirmAppointment = async (id: number) => {
  await http.post(`/appointments/${id}/confirm`)
  ElMessage.success('已同意该预约')
  await loadData()
}

const rejectAppointment = async (id: number) => {
  await http.post(`/appointments/${id}/reject`)
  ElMessage.success('已拒绝该预约')
  await loadData()
}

const openChat = (peerId: number) => {
  router.push({ path: '/chat', query: { peerId: String(peerId) } })
}

const openChatPage = () => {
  if (contacts.value.length === 1) {
    openChat(contacts.value[0].userId)
    return
  }
  router.push('/chat')
}

const formatDate = (value: string) => value?.replace('T', ' ') ?? ''

const typeLabel = (value?: string) => {
  if (value === 'VIDEO') return '视频咨询'
  if (value === 'TEXT') return '文字咨询'
  return value || '未设置'
}

const statusLabel = (value?: string) => {
  if (value === 'PENDING') return '待处理'
  if (value === 'CONFIRMED') return '已确认'
  if (value === 'REJECTED') return '已拒绝'
  if (value === 'CANCELLED') return '已取消'
  return value || '未知状态'
}

const statusType = (value?: string) => {
  if (value === 'CONFIRMED') return 'success'
  if (value === 'PENDING') return 'warning'
  if (value === 'REJECTED' || value === 'CANCELLED') return 'info'
  return ''
}

onMounted(loadData)
</script>

<style scoped lang="scss">
.portal-page {
  display: grid;
  gap: 18px;
}

.hero {
  padding: 22px;
  border-radius: 22px;
  background: linear-gradient(135deg, #f0fdf4, #eff6ff);
}

.eyebrow {
  color: #15803d;
  font-size: 13px;
  font-weight: 700;
}

.hero h2 {
  margin: 10px 0;
}

.hero p {
  margin: 0;
  color: #475569;
  line-height: 1.7;
}

.appointment-list {
  display: grid;
  gap: 14px;
}

.appointment-item {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 16px;
  padding: 16px 18px;
  border-radius: 18px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}

.appointment-main {
  display: grid;
  gap: 10px;
}

.appointment-top,
.appointment-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.appointment-meta {
  color: #64748b;
  font-size: 13px;
}

.appointment-desc {
  margin: 0;
  line-height: 1.7;
  color: #334155;
}

.appointment-actions {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 10px;
}

.panel-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.portal-card {
  display: grid;
  gap: 12px;
}

.portal-link-card {
  cursor: pointer;
  transition: 0.2s ease;
}

.portal-link-card:hover {
  border-color: #93c5fd;
  background: linear-gradient(135deg, #eff6ff, #f8fafc);
}

.portal-card h3,
.portal-card p {
  margin: 0;
}

.portal-card p {
  color: #475569;
  line-height: 1.7;
}

.link-row {
  display: flex;
  align-items: center;
}

@media (max-width: 960px) {
  .panel-grid {
    grid-template-columns: 1fr;
  }

  .appointment-item {
    grid-template-columns: 1fr;
  }

  .appointment-actions {
    flex-direction: row;
    justify-content: flex-start;
  }
}
</style>
