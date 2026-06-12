<template>
  <div class="articles-page">
    <div class="hero-card">
      <div>
        <div class="eyebrow">心理文章</div>
        <h2>把心理科普内容整合进服务平台</h2>
        <p>支持持续发布心理健康教育内容，便于在测评和咨询之外提供长期帮助。</p>
      </div>
      <el-input v-model="keyword" class="search" clearable placeholder="搜索文章标题" @change="loadData" />
    </div>

    <el-skeleton v-if="loading" animated :rows="6" />

    <el-alert
      v-if="errorMessage"
      :title="errorMessage"
      type="warning"
      :closable="false"
      show-icon
    />

    <div v-if="!loading" class="article-grid">
      <el-card
        v-for="item in articles"
        :key="item.id"
        shadow="hover"
        class="article-card"
        @click="router.push(`/articles/${item.id}`)"
      >
        <div class="article-cover" :class="`tone-${(item.id % 4) + 1}`">
          <span>{{ item.category || '心理科普' }}</span>
        </div>
        <h3>{{ item.title }}</h3>
        <p class="summary">{{ item.summary || '暂无摘要，点击查看全文。' }}</p>
        <div class="meta">
          <span>{{ item.authorName || '平台发布' }}</span>
          <span>{{ formatDate(item.createdAt) }}</span>
        </div>
      </el-card>
    </div>

    <el-empty v-if="!loading && !articles.length" description="当前还没有已发布文章" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import http, { ApiError } from '@/api/http'
import type { Article } from '@/types'
import { ARTICLES } from '@/data/articles'

interface ArticlePageResult {
  records: Article[]
  total: number
}

const router = useRouter()
const keyword = ref('')
const articles = ref<Article[]>([])
const loading = ref(false)
const errorMessage = ref('')

const localArticles: Article[] = ARTICLES.map((item) => ({
  id: item.id,
  title: item.title,
  category: item.category,
  summary: item.summary,
  content: item.sections
    .flatMap((section) => [section.heading, ...section.paragraphs])
    .join('\n\n'),
  authorName: item.author,
  status: 'PUBLISHED',
  createdAt: `${item.publishedAt}T00:00:00`
}))

const shouldUseLocalFallback = (error: unknown) =>
  error instanceof ApiError && (error.status === undefined || error.status >= 500)

const loadData = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await http.get<ArticlePageResult>('/articles', {
      params: {
        keyword: keyword.value,
        current: 1,
        size: 50
      }
    })
    articles.value = res.records
  } catch (error) {
    if (shouldUseLocalFallback(error)) {
      const normalizedKeyword = keyword.value.trim().toLowerCase()
      articles.value = localArticles.filter((item) =>
        !normalizedKeyword || item.title.toLowerCase().includes(normalizedKeyword)
      )
      errorMessage.value = error instanceof Error
        ? `文章服务暂时不可用，当前展示本地文章内容：${error.message}`
        : '文章服务暂时不可用，当前展示本地文章内容。'
    } else {
      articles.value = []
      errorMessage.value = error instanceof Error ? error.message : '文章加载失败。'
    }
  } finally {
    loading.value = false
  }
}

const formatDate = (value?: string) => value ? value.replace('T', ' ').slice(0, 16) : '刚刚'

onMounted(loadData)
</script>

<style scoped lang="scss">
.articles-page { display: grid; gap: 18px; }
.hero-card { display: grid; grid-template-columns: 1.2fr 320px; gap: 16px; align-items: end; padding: 22px; border-radius: 22px; background: linear-gradient(135deg, #fff7ed, #eff6ff); border: 1px solid #fde68a; }
.eyebrow { color: #c2410c; font-size: 13px; font-weight: 700; }
.hero-card h2 { margin: 10px 0; }
.hero-card p { margin: 0; color: #475569; line-height: 1.7; }
.search { width: 100%; }
.article-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 18px; }
.article-card { cursor: pointer; }
.article-card h3 { margin: 12px 0 10px; color: #0f172a; }
.article-cover { height: 92px; padding: 14px; border-radius: 14px; color: #fff; display: flex; align-items: end; font-weight: 700; }
.tone-1 { background: linear-gradient(135deg, #5b8ff9, #7eb6ff); }
.tone-2 { background: linear-gradient(135deg, #61d9a8, #8ce0c5); }
.tone-3 { background: linear-gradient(135deg, #0f766e, #34d399); }
.tone-4 { background: linear-gradient(135deg, #f6a645, #f8c471); }
.summary { margin: 0 0 12px; line-height: 1.7; color: #475569; }
.meta { display: flex; justify-content: space-between; gap: 12px; color: #64748b; font-size: 12px; margin-bottom: 10px; }
@media (max-width: 960px) { .hero-card { grid-template-columns: 1fr; } }
</style>
