<template>
  <div v-if="isAdmin" class="monitor-page">
    <el-card shadow="never">
      <template #header>
        <div class="monitor-head">
          <div>
            <strong>风险监控</strong>
            <p>按列表查看用户参与测评的数据记录。</p>
          </div>
          <el-button text @click="loadAdminRecords">刷新</el-button>
        </div>
      </template>

      <el-table :data="adminRecords">
        <el-table-column prop="username" label="用户名" min-width="140" />
        <el-table-column prop="nickname" label="昵称" min-width="120" />
        <el-table-column prop="scaleName" label="量表" min-width="160" />
        <el-table-column prop="score" label="分数" width="90" />
        <el-table-column prop="riskProbability" label="风险概率" width="110">
          <template #default="{ row }">{{ row.riskProbability ?? 0 }}%</template>
        </el-table-column>
        <el-table-column prop="resultLevel" label="风险等级" width="110" />
        <el-table-column prop="status" label="状态" width="120" />
        <el-table-column prop="createdAt" label="参与时间" min-width="170" />
        <el-table-column prop="analysis" label="结果分析" min-width="280" show-overflow-tooltip />
      </el-table>
    </el-card>
  </div>

  <div v-else class="assessment-page">
    <el-card shadow="never">
      <template #header>专业量表</template>
      <div v-if="scalesLoading" class="table-status">量表加载中...</div>
      <el-table :data="scales" @row-click="selectScale">
        <el-table-column prop="name" label="量表名称" />
        <el-table-column prop="code" label="编码" />
        <el-table-column prop="description" label="说明" />
      </el-table>
    </el-card>
    <el-card shadow="never">
      <template #header>填写与提交</template>
      <el-alert v-if="currentScale" :title="`当前量表：${currentScale.name}`" type="success" :closable="false" />
      <el-alert
        v-if="submitError"
        class="submit-feedback"
        :title="submitError"
        type="error"
        :closable="false"
        show-icon
      />
      <div v-if="questions.length" class="question-list">
        <div v-for="item in questions" :key="item.id" class="question-item">
          <div class="question-header">
            <strong>{{ item.title }}</strong>
            <span v-if="item.type !== 'select'">{{ answerMap[item.id] ?? 0 }} / {{ item.max ?? 4 }}</span>
          </div>
          <p v-if="item.description" class="question-description">{{ item.description }}</p>
          <el-select
            v-if="item.type === 'select'"
            v-model="answerMap[item.id]"
            class="question-select"
            placeholder="请选择"
            filterable
          >
            <el-option
              v-for="option in item.options || []"
              :key="`${item.id}-${option.value}`"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
          <el-slider
            v-else
            :model-value="Number(answerMap[item.id] ?? item.min ?? 0)"
            @update:model-value="(value) => setAnswer(item.id, value)"
            :min="item.min ?? 0"
            :max="item.max ?? 4"
            :step="item.step ?? 1"
            show-stops
            show-input
          />
        </div>
      </div>
      <el-empty v-else description="当前量表未配置变量" />
      <div class="actions">
        <el-button :disabled="submitLoading || !questions.length" @click="saveDraft">保存进度</el-button>
        <el-button type="primary" :loading="submitLoading" :disabled="!questions.length" @click="submit">提交测评</el-button>
      </div>
      <div v-if="submitLoading" class="submit-status">正在生成测评结果，请稍候...</div>
      <div v-if="latestResult" ref="resultPanelRef" class="result-panel">
        <div class="section-title">本次测评结果</div>
        <div class="result-summary">
          <div class="result-metric">
            <span class="metric-label">风险等级</span>
            <strong>{{ latestResult.resultLevel }}</strong>
          </div>
          <div class="result-metric">
            <span class="metric-label">风险概率</span>
            <strong>{{ latestResult.riskProbability }}%</strong>
          </div>
          <div class="result-metric">
            <span class="metric-label">模型</span>
            <strong>{{ latestResult.modelName || '默认模型' }}</strong>
          </div>
        </div>
        <p class="analysis-text">{{ latestResult.analysis }}</p>
        <div v-if="latestResult.leadingFactors?.length" class="factor-grid">
          <div v-for="factor in latestResult.leadingFactors" :key="factor.key" class="factor-card">
            <div class="factor-card-head">
              <strong>{{ factor.name }}</strong>
              <el-tag :type="factor.direction === 'RISK' ? 'danger' : 'success'" effect="plain">
                {{ factor.direction === 'RISK' ? '风险项' : '保护项' }}
              </el-tag>
            </div>
            <div class="factor-card-meta">
              <span>得分 {{ factor.value }}</span>
              <span>影响度 {{ factor.contributionScore }}</span>
            </div>
            <p>{{ factor.description }}</p>
          </div>
        </div>
      </div>
      <div class="history">
        <h3>历史记录</h3>
        <el-timeline>
          <el-timeline-item v-for="item in history" :key="item.id" :timestamp="item.createdAt">
            <div class="history-item">
              <div class="history-head">
                <strong>{{ item.resultLevel }}</strong>
                <span>{{ item.score }} 分</span>
                <span v-if="item.riskProbability !== undefined">风险概率 {{ item.riskProbability }}%</span>
              </div>
              <p>{{ item.analysis }}</p>
              <div v-if="item.leadingFactors?.length" class="factor-detail-list">
                <div v-for="factor in item.leadingFactors" :key="`${item.id}-${factor.key}`" class="factor-detail-item">
                  <div class="factor-detail-head">
                    <strong>{{ factor.name }}</strong>
                    <el-tag :type="factor.direction === 'RISK' ? 'danger' : 'success'" effect="plain">
                      {{ factor.direction === 'RISK' ? '风险项' : '保护项' }}
                    </el-tag>
                  </div>
                  <div class="factor-detail-meta">
                    <span>得分 {{ factor.value }}</span>
                    <span>影响度 {{ factor.contributionScore }}</span>
                  </div>
                  <p>{{ factor.description }}</p>
                </div>
              </div>
            </div>
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '@/api/http'
import type { AssessmentMonitorRecord, AssessmentQuestion, AssessmentRecord, AssessmentScale } from '@/types'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const isAdmin = computed(() => userStore.user?.role === 'ADMIN')

const adminRecords = ref<AssessmentMonitorRecord[]>([])
const scales = ref<AssessmentScale[]>([])
const history = ref<AssessmentRecord[]>([])
const currentScale = ref<AssessmentScale | null>(null)
const answerMap = ref<Record<string, number | string>>({})
const latestResult = ref<AssessmentRecord | null>(null)
const resultPanelRef = ref<HTMLDivElement>()
const scalesLoading = ref(false)
const submitLoading = ref(false)
const submitError = ref('')

const questions = computed<AssessmentQuestion[]>(() => {
  if (!currentScale.value?.questionJson) return []
  try {
    return JSON.parse(currentScale.value.questionJson)
  } catch (error) {
    return []
  }
})

const loadAdminRecords = async () => {
  adminRecords.value = await http.get<AssessmentMonitorRecord[]>('/assessments/admin/records')
}

const loadScales = async () => {
  try {
    scalesLoading.value = true
    scales.value = await http.get<AssessmentScale[]>('/assessments/scales')
    currentScale.value = scales.value[0] || null
    hydrateAnswerMap()
  } finally {
    scalesLoading.value = false
  }
}

const loadHistory = async () => {
  history.value = await http.get<AssessmentRecord[]>('/assessments/history')
}

const selectScale = (row: AssessmentScale) => {
  currentScale.value = row
  latestResult.value = null
  submitError.value = ''
  hydrateAnswerMap()
}

const draftKey = () => `assessmentDraft:${currentScale.value?.code || 'default'}`

const hydrateAnswerMap = () => {
  const saved = localStorage.getItem(draftKey())
  let draft: Record<string, number | string> = {}
  if (saved) {
    try {
      draft = JSON.parse(saved)
    } catch (error) {
      draft = {}
    }
  }
  const next: Record<string, number | string> = {}
  questions.value.forEach((item) => {
    next[item.id] = draft[item.id] ?? (item.type === 'select' ? item.options?.[0]?.value ?? '' : item.min ?? 0)
  })
  answerMap.value = next
}

const saveDraft = () => {
  localStorage.setItem(draftKey(), JSON.stringify(answerMap.value))
  ElMessage.success('进度已保存')
}

const setAnswer = (id: string, value: number | number[]) => {
  answerMap.value[id] = Array.isArray(value) ? value[0] ?? 0 : value
}

const submit = async () => {
  if (!currentScale.value) return
  submitError.value = ''
  latestResult.value = null

  try {
    submitLoading.value = true
    latestResult.value = await http.post<AssessmentRecord>('/assessments/submit', {
      scaleId: currentScale.value.id,
      answerJson: JSON.stringify(answerMap.value),
      status: 'COMPLETED'
    })
    ElMessage.success('测评提交成功')
    saveDraft()
    await loadHistory()
    await nextTick()
    resultPanelRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  } catch (error) {
    submitError.value = (error as Error).message || '测评提交失败，请稍后重试'
    ElMessage.error(submitError.value)
  } finally {
    submitLoading.value = false
  }
}

onMounted(() => {
  if (isAdmin.value) {
    void loadAdminRecords()
    return
  }
  void loadScales()
  void loadHistory()
})
</script>

<style scoped lang="scss">
.monitor-page { display: grid; gap: 18px; }
.monitor-head { display: flex; justify-content: space-between; gap: 12px; align-items: center; }
.monitor-head p { margin: 6px 0 0; color: #64748b; line-height: 1.6; }

.assessment-page {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}

.actions {
  margin: 16px 0;
}

.submit-feedback {
  margin-top: 12px;
}

.submit-status {
  margin-top: 12px;
  color: #475569;
  font-size: 14px;
}

.table-status {
  margin-bottom: 12px;
  color: #475569;
  font-size: 14px;
}

.result-panel {
  display: grid;
  gap: 16px;
  margin-top: 20px;
  padding: 18px;
  border-radius: 14px;
  background: linear-gradient(135deg, #f8fbff 0%, #f4fdf7 100%);
  border: 1px solid #dbeafe;
}

.section-title {
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
}

.result-summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.result-metric {
  display: grid;
  gap: 6px;
  padding: 12px;
  border-radius: 12px;
  background: #fff;
  border: 1px solid #e5e7eb;
}

.metric-label {
  color: #64748b;
  font-size: 13px;
}

.analysis-text {
  margin: 0;
  color: #334155;
  line-height: 1.7;
}

.question-list {
  margin-top: 16px;
}

.question-item {
  padding: 14px 0;
  border-bottom: 1px solid #eef2f7;
}

.question-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 8px;
}

.question-description {
  margin: 0 0 12px;
  color: #6b7280;
  font-size: 13px;
}

.question-select {
  width: 100%;
}

.history {
  margin-top: 24px;
}

.history-item {
  display: grid;
  gap: 8px;
}

.history-head {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  color: #1f2937;
}

.history-head span {
  color: #4b5563;
}

.factor-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.factor-card,
.factor-detail-item {
  display: grid;
  gap: 8px;
  padding: 12px 14px;
  border-radius: 12px;
  background: #fff;
  border: 1px solid #e5e7eb;
}

.factor-card p,
.factor-detail-item p {
  margin: 0;
  color: #475569;
  line-height: 1.6;
}

.factor-card-head,
.factor-detail-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.factor-card-meta,
.factor-detail-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  color: #64748b;
  font-size: 13px;
}

.factor-detail-list {
  display: grid;
  gap: 10px;
}

@media (max-width: 960px) {
  .assessment-page {
    grid-template-columns: 1fr;
  }

  .result-summary,
  .factor-grid {
    grid-template-columns: 1fr;
  }
}
</style>
