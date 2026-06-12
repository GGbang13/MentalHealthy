<template>
  <div class="dashboard">
    <div class="hero">
      <div>
        <span class="badge">数据驱动的心理健康支持中台</span>
        <h2>统一管理测评、咨询、预约与随访流程</h2>
        <p>首页总览实时聚合用户、咨询师、预约和测评数据，便于演示和运营分析。</p>
      </div>
      <div class="metrics">
        <div class="metric">
          <strong>{{ summary.userCount }}</strong>
          <span>平台用户总量</span>
        </div>
        <div class="metric">
          <strong>{{ summary.onlineCounselorCount }} / {{ summary.counselorCount }}</strong>
          <span>在线咨询师 / 咨询师总数</span>
        </div>
        <div class="metric">
          <strong>{{ summary.pendingAppointmentCount }}</strong>
          <span>待处理预约</span>
        </div>
      </div>
    </div>
    <div class="panel-grid">
      <el-card shadow="never">
        <template #header>服务概览</template>
        <ul class="summary-list">
          <li>总预约数：{{ summary.appointmentCount }}</li>
          <li>总测评数：{{ summary.assessmentCount }}</li>
          <li>高风险记录：{{ summary.highRiskCount }}</li>
          <li>在线咨询师：{{ summary.onlineCounselorCount }}</li>
        </ul>
      </el-card>
      <el-card shadow="never">
        <template #header>平台能力</template>
        <ul class="summary-list">
          <li>心理测评接入真实 CatBoost 模型与解释变量</li>
          <li>预约、聊天、用户资料均接入统一鉴权</li>
          <li>支持风险分层与近期动态追踪</li>
          <li>前后端分离，适合课程答辩与功能演示</li>
        </ul>
      </el-card>
      <el-card shadow="never">
        <template #header>近期动态</template>
        <div class="activity-list">
          <div v-for="item in summary.recentActivities" :key="`${item.title}-${item.timestamp}`" class="activity-item">
            <strong>{{ item.title }}</strong>
            <p>{{ item.description }}</p>
            <span>{{ item.timestamp }}</span>
          </div>
        </div>
      </el-card>
    </div>
    <el-card shadow="never">
      <template #header>测评风险分布</template>
      <div ref="chartRef" style="height: 320px"></div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { PieChart } from 'echarts/charts'
import { TooltipComponent, type TooltipComponentOption } from 'echarts/components'
import { init, use, type ComposeOption, type ECharts } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import http from '@/api/http'
import type { DashboardSummary } from '@/types'

use([PieChart, TooltipComponent, CanvasRenderer])

type PieOption = ComposeOption<TooltipComponentOption>

const chartRef = ref<HTMLDivElement>()
let chart: ECharts | undefined
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

const levelLabelMap: Record<string, string> = {
  LOW: '低风险',
  MEDIUM: '中风险',
  HIGH: '高风险'
}

const levelColorMap: Record<string, string> = {
  LOW: '#22c55e',
  MEDIUM: '#f59e0b',
  HIGH: '#ef4444'
}

const renderChart = () => {
  if (!chartRef.value) return
  chart ??= init(chartRef.value)
  const option: PieOption = {
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['42%', '72%'],
      label: {
        formatter: (params: { name: string; value: number }) => `${params.name}\n${params.value}`
      },
      data: summary.value.riskDistribution.map((item) => ({
        name: levelLabelMap[item.level] || item.level,
        value: item.count,
        itemStyle: {
          color: levelColorMap[item.level] || '#205c4f'
        }
      }))
    }]
  }
  chart.setOption(option)
}

const loadSummary = async () => {
  summary.value = await http.get<DashboardSummary>('/dashboard/summary')
  await nextTick()
  renderChart()
}

const handleResize = () => chart?.resize()

onMounted(() => {
  loadSummary()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
  chart = undefined
})
</script>

<style scoped lang="scss">
.dashboard {
  display: grid;
  gap: 22px;
}

.hero {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 20px;
  padding: 24px;
  border-radius: 24px;
  background: linear-gradient(135deg, rgba(32, 92, 79, 0.95), rgba(24, 59, 51, 0.92));
  color: #fff;
}

.hero h2 {
  margin: 12px 0;
  font-size: 36px;
}

.badge {
  display: inline-block;
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.14);
}

.metrics {
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
}

.metric {
  padding: 16px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.1);
}

.metric strong {
  display: block;
  font-size: 28px;
}

.panel-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}

.summary-list {
  display: grid;
  gap: 10px;
  margin: 0;
  padding-left: 18px;
  color: #334155;
}

.activity-list {
  display: grid;
  gap: 12px;
}

.activity-item {
  padding: 14px;
  border-radius: 16px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}

.activity-item strong {
  display: block;
  color: #0f172a;
}

.activity-item p {
  margin: 8px 0 6px;
  color: #475569;
}

.activity-item span {
  color: #64748b;
  font-size: 12px;
}

@media (max-width: 960px) {
  .hero,
  .panel-grid {
    grid-template-columns: 1fr;
  }
}
</style>
