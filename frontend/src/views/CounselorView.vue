<template>
  <div class="view-grid">
    <el-card shadow="never">
      <div class="hero">
        <div>
          <div class="eyebrow">咨询服务</div>
          <h2>咨询师列表已完成统一展示优化</h2>
          <p>保留当前项目的后端数据来源，同时补充更清晰的介绍结构、详情入口和预约动线。</p>
        </div>
      </div>
      <div class="toolbar">
        <el-input v-model="keyword" placeholder="搜索擅长领域" />
        <el-select v-model="onlineStatus" clearable placeholder="在线状态">
          <el-option label="在线" :value="1" />
          <el-option label="离线" :value="0" />
        </el-select>
        <el-button type="primary" @click="loadData">筛选</el-button>
      </div>
      <div class="summary-bar">
        <div class="summary-item">
          <span>当前可选咨询师</span>
          <strong>{{ counselors.length }}</strong>
        </div>
        <div class="summary-item">
          <span>在线接诊</span>
          <strong>{{ counselors.filter((item) => item.onlineStatus === 1).length }}</strong>
        </div>
      </div>
      <div class="card-grid">
        <el-card v-for="row in counselors" :key="row.id" shadow="hover" class="doctor-card">
          <div class="card-banner">
            <el-tag :type="row.onlineStatus ? 'success' : 'info'" effect="dark" class="status-tag">
              {{ row.onlineStatus ? '在线可约' : '暂时离线' }}
            </el-tag>
            <div class="doctor-head">
              <div class="avatar">{{ (row.nickname || '咨').slice(0, 1) }}</div>
              <div class="doctor-name">
                <h3>{{ row.nickname || '未命名咨询师' }}</h3>
                <p>{{ row.title || '咨询师' }}</p>
              </div>
            </div>
          </div>

          <div class="stat-grid">
            <div class="stat-item">
              <span>从业经验</span>
              <strong>{{ row.yearsOfExperience || 0 }} 年</strong>
            </div>
            <div class="stat-item">
              <span>咨询价格</span>
              <strong>{{ row.pricePerHour ? `¥${row.pricePerHour}` : '面议' }}</strong>
            </div>
            <div class="stat-item">
              <span>综合评分</span>
              <strong>{{ row.rating || 0 }}</strong>
            </div>
            <div class="stat-item">
              <span>评价数量</span>
              <strong>{{ row.reviewCount || 0 }}</strong>
            </div>
          </div>

          <div class="section-title">
            <span>擅长方向</span>
          </div>
          <div class="tags">
            <el-tag
              v-for="tag in splitSpecialties(row.specialties)"
              :key="tag"
              size="small"
              effect="plain"
              class="skill-tag"
            >
              {{ tag.trim() }}
            </el-tag>
            <span v-if="!splitSpecialties(row.specialties).length" class="empty-text">暂未填写擅长方向</span>
          </div>

          <div class="section-title">
            <span>专业简介</span>
          </div>
          <p class="intro">{{ row.introduction || '该咨询师暂未补充简介，建议查看详情了解更多服务信息。' }}</p>

          <div class="actions">
            <el-button plain @click="openDetail(row.id)">查看详情</el-button>
            <el-button type="primary" @click="goAppointment(row.id)">发起预约</el-button>
          </div>
        </el-card>
      </div>
      <el-empty v-if="!counselors.length" description="当前还没有可展示的咨询师，请先完善咨询师档案" />
    </el-card>

    <el-drawer v-model="detailVisible" :title="detail?.nickname || '咨询师详情'" size="42%">
      <div v-if="detail" class="detail-panel">
        <div class="detail-top">
          <div class="detail-avatar">{{ (detail.nickname || '咨').slice(0, 1) }}</div>
          <div>
            <h3>{{ detail.nickname }}</h3>
            <p>{{ detail.title }}</p>
          </div>
        </div>
        <div class="detail-info">
          <div class="detail-item">
            <span>擅长方向</span>
            <strong>{{ detail.specialties || '暂无' }}</strong>
          </div>
          <div class="detail-item">
            <span>从业年限</span>
            <strong>{{ detail.yearsOfExperience || 0 }} 年</strong>
          </div>
          <div class="detail-item">
            <span>收费标准</span>
            <strong>{{ detail.pricePerHour ? `¥${detail.pricePerHour}/小时` : '暂无' }}</strong>
          </div>
          <div class="detail-item">
            <span>服务评分</span>
            <strong>{{ detail.rating || 0 }}</strong>
          </div>
        </div>
        <div class="detail-block">
          <h4>个人介绍</h4>
          <p>{{ detail.introduction || '暂无介绍' }}</p>
        </div>
        <div class="detail-actions">
          <el-button @click="detailVisible = false">关闭</el-button>
          <el-button type="primary" @click="goAppointment(detail.id)">去预约</el-button>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/api/http'
import type { Counselor } from '@/types'

interface CounselorPageResult {
  records: Counselor[]
}

const keyword = ref('')
const onlineStatus = ref<number | undefined>()
const counselors = ref<Counselor[]>([])
const detail = ref<Counselor | null>(null)
const detailVisible = ref(false)
const router = useRouter()

const splitSpecialties = (value?: string) => (value || '').split(/[、,，/]/).map((item) => item.trim()).filter(Boolean)

const loadData = async () => {
  const res = await http.get<CounselorPageResult>('/counselors', {
    params: {
      keyword: keyword.value,
      onlineStatus: onlineStatus.value
    }
  })
  counselors.value = res.records
}

const openDetail = async (id: number) => {
  detail.value = await http.get<Counselor>(`/counselors/${id}`)
  detailVisible.value = true
}

const goAppointment = (counselorId?: number) => {
  router.push({
    path: '/appointments',
    query: counselorId ? { counselorId: String(counselorId) } : undefined
  })
}

onMounted(loadData)
</script>

<style scoped lang="scss">
.view-grid {
  display: grid;
}

.hero {
  margin-bottom: 16px;
  padding: 18px 20px;
  border-radius: 18px;
  background: linear-gradient(135deg, #eff6ff, #f8fafc);
}

.eyebrow {
  color: #2563eb;
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

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}

.summary-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 18px;
}

.summary-item {
  min-width: 150px;
  padding: 12px 16px;
  border-radius: 16px;
  background: linear-gradient(135deg, #eff6ff, #ffffff);
  border: 1px solid #dbeafe;
  display: grid;
  gap: 6px;
}

.summary-item span {
  font-size: 13px;
  color: #64748b;
}

.summary-item strong {
  font-size: 24px;
  color: #0f172a;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 18px;
}

.doctor-card {
  display: grid;
  gap: 14px;
  overflow: hidden;
  border-radius: 24px;
  border: 1px solid #dbeafe;
  background:
    radial-gradient(circle at top right, rgba(56, 189, 248, 0.16), transparent 34%),
    linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
}

.card-banner {
  margin: -20px -20px 0;
  padding: 18px 18px 20px;
  background: linear-gradient(135deg, #0f766e, #2563eb 72%, #60a5fa);
  color: #fff;
}

.status-tag {
  margin-bottom: 14px;
  border: none;
}

.doctor-head {
  display: grid;
  grid-template-columns: 64px 1fr;
  gap: 12px;
  align-items: center;
}

.doctor-name {
  min-width: 0;
}

.avatar,
.detail-avatar {
  width: 64px;
  height: 64px;
  border-radius: 22px;
  background: linear-gradient(135deg, #1d4ed8, #60a5fa);
  color: #fff;
  display: grid;
  place-items: center;
  font-size: 24px;
  font-weight: 700;
}

.doctor-head h3,
.detail-top h3 {
  margin: 0 0 6px;
  color: inherit;
}

.doctor-head p,
.detail-top p {
  margin: 0;
  color: rgba(255, 255, 255, 0.84);
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.stat-item {
  display: grid;
  gap: 4px;
  padding: 12px 14px;
  border-radius: 16px;
  background: #fff;
  border: 1px solid #e2e8f0;
}

.stat-item span {
  font-size: 12px;
  color: #64748b;
}

.stat-item strong {
  color: #0f172a;
}

.section-title span {
  font-size: 13px;
  font-weight: 700;
  color: #334155;
}

.intro {
  margin: 0;
  color: #475569;
  line-height: 1.7;
  min-height: 74px;
}

.tags,
.actions,
.detail-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.skill-tag {
  border-radius: 999px;
}

.empty-text {
  font-size: 13px;
  color: #94a3b8;
}

.detail-panel {
  display: grid;
  gap: 18px;
}

.detail-top {
  display: grid;
  grid-template-columns: 56px 1fr;
  gap: 12px;
  align-items: center;
}

.detail-info {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.detail-item {
  display: grid;
  gap: 6px;
  padding: 12px;
  border-radius: 12px;
  background: #f8fafc;
}

.detail-item span {
  color: #64748b;
  font-size: 13px;
}

.detail-item strong {
  color: #0f172a;
}

.detail-block h4 {
  margin: 0 0 10px;
}

.detail-block p {
  margin: 0;
  line-height: 1.8;
  color: #475569;
}

@media (max-width: 960px) {
  .card-grid,
  .detail-info {
    grid-template-columns: 1fr;
  }
}
</style>
