<template>
  <div v-if="article" class="article-detail-page">
    <el-button text @click="router.push('/articles')">返回文章列表</el-button>
    <div class="article-head">
      <div class="eyebrow">{{ article.category || '心理科普' }}</div>
      <h1>{{ article.title }}</h1>
      <div class="meta">
        <span>{{ article.authorName || '平台发布' }}</span>
        <span>{{ formatDate(article.createdAt) }}</span>
      </div>
      <p class="lead">{{ article.summary || '暂无摘要。' }}</p>
    </div>

    <el-alert
      title="以下内容用于健康教育与自助参考，不能替代专业诊断和治疗。"
      type="warning"
      :closable="false"
      show-icon
    />

    <el-alert
      v-if="errorMessage"
      :title="errorMessage"
      type="info"
      :closable="false"
      show-icon
    />

    <div class="content-card">
      <template v-if="blocks.length">
        <template v-for="(block, index) in blocks" :key="`${block.type}-${index}`">
          <h2 v-if="block.type === 'heading'" class="section-title">{{ block.text }}</h2>
          <p v-else>{{ block.text }}</p>
        </template>
      </template>
      <el-empty v-else description="文章正文暂时为空" />
    </div>
  </div>
  <el-skeleton v-else-if="loading" animated :rows="10" />
  <el-empty v-else description="文章不存在或已移除" />
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import http, { ApiError } from '@/api/http'
import type { Article } from '@/types'
import { getArticleById } from '@/data/articles'

const route = useRoute()
const router = useRouter()
const article = ref<Article | null>(null)
const loading = ref(false)
const errorMessage = ref('')

type ContentBlock = {
  type: 'heading' | 'paragraph'
  text: string
}

const shouldUseLocalFallback = (error: unknown) =>
  error instanceof ApiError && (error.status === undefined || error.status >= 500)

const blocks = computed<ContentBlock[]>(() => {
  const rawContent = article.value?.content?.replace(/\r\n/g, '\n').trim() || ''
  if (!rawContent) return []

  return rawContent
    .split(/\n{2,}/)
    .map((item) => item.trim())
    .filter(Boolean)
    .map((item) => ({
      type: item.length <= 18 && !/[。；：，,]/.test(item) ? 'heading' : 'paragraph',
      text: item
    }))
})

const formatDate = (value?: string) => value ? value.replace('T', ' ').slice(0, 16) : ''

onMounted(async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    article.value = await http.get<Article>(`/articles/${route.params.id}`)
    if (!article.value?.content?.trim()) {
      throw new Error('文章正文为空')
    }
  } catch (error) {
    const fallback = getArticleById(Number(route.params.id))
    if (fallback && shouldUseLocalFallback(error)) {
      article.value = {
        id: fallback.id,
        title: fallback.title,
        category: fallback.category,
        summary: fallback.summary,
        content: fallback.sections
          .flatMap((section) => [section.heading, ...section.paragraphs])
          .join('\n\n'),
        authorName: fallback.author,
        status: 'PUBLISHED',
        createdAt: `${fallback.publishedAt}T00:00:00`
      }
      errorMessage.value = error instanceof Error
        ? `文章服务暂时不可用，当前展示本地文章内容：${error.message}`
        : '文章服务暂时不可用，当前展示本地文章内容。'
    } else {
      article.value = null
      errorMessage.value = error instanceof Error ? error.message : '文章加载失败。'
    }
  } finally {
    loading.value = false
  }
})
</script>

<style scoped lang="scss">
.article-detail-page { display: grid; gap: 18px; }
.article-head { padding: 8px 0; }
.eyebrow { color: #2563eb; font-size: 13px; font-weight: 700; }
.article-head h1 { margin: 10px 0 12px; color: #0f172a; }
.meta { display: flex; flex-wrap: wrap; gap: 12px; color: #64748b; font-size: 13px; }
.lead { margin: 14px 0 0; line-height: 1.8; color: #475569; }
.content-card { padding: 22px; border-radius: 22px; background: #fff; border: 1px solid #e2e8f0; }
.section-title { margin: 0 0 14px; color: #0f172a; font-size: 22px; line-height: 1.4; }
.content-card p { margin: 0 0 14px; line-height: 1.9; color: #334155; white-space: pre-wrap; }
</style>
