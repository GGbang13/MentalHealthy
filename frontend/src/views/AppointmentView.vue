<template>
  <div class="appointment-page">
    <el-card shadow="never" class="booking-card">
      <template #header>
        <div class="card-header">
          <div>
            <h3>预约咨询</h3>
            <p>选择咨询师并提交预约申请，待对方确认后即可进入在线沟通。</p>
          </div>
        </div>
      </template>

      <div v-if="selectedCounselor" class="selected-counselor">
        <div class="avatar">{{ (selectedCounselor.nickname || '咨').slice(0, 1) }}</div>
        <div class="selected-meta">
          <strong>{{ selectedCounselor.nickname }}</strong>
          <span>{{ selectedCounselor.title || '咨询师' }}</span>
          <small>{{ selectedCounselor.specialties || '暂无擅长方向说明' }}</small>
        </div>
      </div>

      <el-form :model="form" label-width="96px" class="booking-form">
        <el-form-item label="咨询师">
          <el-select v-model="form.counselorId" filterable placeholder="请选择咨询师" @change="syncSelectedCounselor">
            <el-option
              v-for="item in counselors"
              :key="item.id"
              :label="`${item.nickname || '未命名咨询师'} ${item.title ? `· ${item.title}` : ''}`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="预约时间">
          <el-date-picker
            v-model="form.appointmentTime"
            type="datetime"
            value-format="YYYY-MM-DDTHH:mm:ss"
            placeholder="选择咨询时间"
          />
        </el-form-item>
        <el-form-item label="咨询形式">
          <el-segmented v-model="form.type" :options="typeOptions" />
        </el-form-item>
        <el-form-item label="时长">
          <el-input-number v-model="form.durationMinutes" :min="30" :max="180" :step="10" />
        </el-form-item>
        <el-form-item label="问题描述">
          <el-input
            v-model="form.issueDescription"
            type="textarea"
            :rows="5"
            placeholder="简单描述当前困扰、希望获得的帮助，以及想重点沟通的内容"
          />
        </el-form-item>
        <div class="form-actions">
          <el-button type="primary" @click="submit">提交预约</el-button>
        </div>
      </el-form>
    </el-card>

    <el-card shadow="never" class="records-card">
      <template #header>
        <div class="card-header">
          <div>
            <h3>我的预约</h3>
            <p>确认后可直接进入聊天窗口与咨询师沟通。</p>
          </div>
        </div>
      </template>

      <div class="record-list">
        <div v-for="record in records" :key="record.id" class="record-item">
          <div class="record-main">
            <div class="record-top">
              <strong>{{ record.counselorName || `咨询师#${record.counselorId}` }}</strong>
              <el-tag :type="statusType(record.status)" effect="plain">{{ statusLabel(record.status) }}</el-tag>
            </div>
            <div class="record-meta">
              <span>{{ formatDate(record.appointmentTime) }}</span>
              <span>{{ typeLabel(record.type) }}</span>
              <span>{{ record.durationMinutes }} 分钟</span>
            </div>
            <div class="record-extra">
              <span>{{ record.counselorTitle || '咨询师' }}</span>
              <span>{{ record.counselorSpecialties || '暂无擅长方向说明' }}</span>
            </div>
            <p class="record-desc">{{ record.issueDescription || '未填写问题描述' }}</p>
          </div>
          <div class="record-actions">
            <el-button
              v-if="record.canChat && record.counselorUserId"
              type="primary"
              plain
              @click="openChat(record.counselorUserId)"
            >
              开始沟通
            </el-button>
            <el-button
              v-if="['PENDING', 'CONFIRMED'].includes(record.status)"
              @click="cancelAppointment(record.id)"
            >
              取消预约
            </el-button>
          </div>
        </div>
        <el-empty v-if="!records.length" description="还没有预约记录" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import http from '@/api/http'
import type { Appointment, Counselor } from '@/types'

interface CounselorPageResult {
  records: Counselor[]
}

const route = useRoute()
const router = useRouter()
const counselors = ref<Counselor[]>([])
const records = ref<Appointment[]>([])
const form = reactive({
  counselorId: undefined as number | undefined,
  appointmentTime: '',
  durationMinutes: 50,
  type: 'TEXT',
  issueDescription: ''
})

const typeOptions = [
  { label: '文字咨询', value: 'TEXT' },
  { label: '视频咨询', value: 'VIDEO' }
]

const selectedCounselor = computed(() => counselors.value.find((item) => item.id === form.counselorId) ?? null)

const loadCounselors = async () => {
  const res = await http.get<CounselorPageResult>('/counselors', { params: { size: 100 } })
  counselors.value = res.records
  syncSelectedCounselor()
}

const loadRecords = async () => {
  records.value = await http.get<Appointment[]>('/appointments')
}

const syncSelectedCounselor = () => {
  const queryId = Number(route.query.counselorId)
  if (!form.counselorId && queryId) {
    form.counselorId = queryId
  }
  if (!form.counselorId && counselors.value.length) {
    form.counselorId = counselors.value[0].id
  }
}

const submit = async () => {
  if (!form.counselorId || !form.appointmentTime) {
    ElMessage.warning('请选择咨询师和预约时间')
    return
  }
  await http.post('/appointments', form)
  ElMessage.success('预约申请已提交，等待咨询师确认')
  form.issueDescription = ''
  await loadRecords()
}

const cancelAppointment = async (id: number) => {
  await http.post(`/appointments/${id}/cancel`)
  ElMessage.success('预约已取消')
  await loadRecords()
}

const openChat = (peerId: number) => {
  router.push({ path: '/chat', query: { peerId: String(peerId) } })
}

const formatDate = (value: string) => value?.replace('T', ' ') ?? ''

const typeLabel = (value?: string) => {
  if (value === 'VIDEO') return '视频咨询'
  if (value === 'TEXT') return '文字咨询'
  return value || '未设置'
}

const statusLabel = (value?: string) => {
  if (value === 'PENDING') return '待确认'
  if (value === 'CONFIRMED') return '已确认'
  if (value === 'REJECTED') return '已拒绝'
  if (value === 'CANCELLED') return '已取消'
  if (value === 'RESCHEDULED') return '已改期'
  return value || '未知状态'
}

const statusType = (value?: string) => {
  if (value === 'CONFIRMED') return 'success'
  if (value === 'PENDING') return 'warning'
  if (value === 'REJECTED' || value === 'CANCELLED') return 'info'
  return ''
}

onMounted(async () => {
  await Promise.all([loadCounselors(), loadRecords()])
})
</script>

<style scoped lang="scss">
.appointment-page {
  display: grid;
  grid-template-columns: 420px 1fr;
  gap: 18px;
}

.booking-card,
.records-card {
  min-height: 100%;
}

.card-header h3,
.card-header p {
  margin: 0;
}

.card-header p {
  margin-top: 6px;
  color: #64748b;
  line-height: 1.6;
}

.selected-counselor {
  display: grid;
  grid-template-columns: 56px 1fr;
  gap: 12px;
  align-items: center;
  padding: 14px;
  margin-bottom: 18px;
  border-radius: 16px;
  background: linear-gradient(135deg, #eff6ff, #f8fafc);
}

.avatar {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  color: #fff;
  font-size: 22px;
  font-weight: 700;
  background: linear-gradient(135deg, #0f766e, #38bdf8);
}

.selected-meta {
  display: grid;
  gap: 4px;
}

.selected-meta span,
.selected-meta small {
  color: #64748b;
}

.booking-form {
  display: grid;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
}

.record-list {
  display: grid;
  gap: 14px;
}

.record-item {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 16px;
  padding: 16px 18px;
  border-radius: 18px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}

.record-main {
  display: grid;
  gap: 10px;
}

.record-top,
.record-meta,
.record-extra {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.record-meta,
.record-extra {
  color: #64748b;
  font-size: 13px;
}

.record-desc {
  margin: 0;
  color: #334155;
  line-height: 1.7;
}

.record-actions {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 10px;
}

@media (max-width: 960px) {
  .appointment-page {
    grid-template-columns: 1fr;
  }

  .record-item {
    grid-template-columns: 1fr;
  }

  .record-actions {
    flex-direction: row;
    justify-content: flex-start;
  }
}
</style>
