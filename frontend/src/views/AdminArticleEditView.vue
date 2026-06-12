<template>
  <div class="page-wrap">
    <AdminArticleForm
      v-if="loaded"
      :model="form"
      mode="edit"
      :submitting="submitting"
      @submit="submit"
      @cancel="router.push('/admin/articles')"
    />
    <el-card v-else shadow="never" class="loading-card">文章加载中...</el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import http from '@/api/http'
import type { Article } from '@/types'
import AdminArticleForm, { type ArticleFormModel } from '@/components/admin/AdminArticleForm.vue'

const route = useRoute()
const router = useRouter()
const loaded = ref(false)
const submitting = ref(false)
const form = reactive<ArticleFormModel>({
  title: '',
  category: '心理科普',
  summary: '',
  content: '',
  status: 'PUBLISHED'
})

const loadArticle = async () => {
  const article = await http.get<Article>(`/articles/${route.params.id}`)
  form.title = article.title
  form.category = article.category || '心理科普'
  form.summary = article.summary || ''
  form.content = article.content
  form.status = (article.status as 'PUBLISHED' | 'DRAFT') || 'PUBLISHED'
  loaded.value = true
}

const submit = async () => {
  try {
    submitting.value = true
    await http.put(`/articles/${route.params.id}`, form)
    ElMessage.success('文章已更新')
    router.push('/admin/articles')
  } finally {
    submitting.value = false
  }
}

onMounted(loadArticle)
</script>

<style scoped lang="scss">
.page-wrap { display: grid; gap: 18px; }
.loading-card { padding: 26px; border-radius: 22px; color: #64748b; }
</style>
