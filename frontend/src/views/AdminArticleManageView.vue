<template>
  <div class="manage-page">
    <div class="header-row">
      <div>
        <div class="eyebrow">文章管理</div>
        <h2>文章列表</h2>
        <p>支持分页、搜索、状态筛选，以及文章新增、编辑和删除。</p>
      </div>
      <el-button type="primary" @click="router.push('/admin/articles/new')">新建文章</el-button>
    </div>

    <el-card shadow="never" class="table-card">
      <div class="toolbar">
        <el-input v-model="keyword" clearable placeholder="按标题搜索" @keyup.enter="handleSearch" />
        <el-select v-model="status" clearable placeholder="文章状态">
          <el-option label="已发布" value="PUBLISHED" />
          <el-option label="草稿" value="DRAFT" />
        </el-select>
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
      </div>

      <el-table :data="articles" class="article-table">
        <el-table-column prop="title" label="标题" min-width="240" show-overflow-tooltip />
        <el-table-column prop="category" label="分类" width="140" />
        <el-table-column prop="authorName" label="作者" width="140" />
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === 'PUBLISHED' ? 'success' : 'info'">
              {{ row.status === 'PUBLISHED' ? '已发布' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updatedAt" label="更新时间" min-width="170" />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="router.push(`/admin/articles/${row.id}/edit`)">编辑</el-button>
            <el-button link @click="router.push(`/articles/${row.id}`)">预览</el-button>
            <el-button link type="danger" @click="openDeleteDialog(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="current"
          v-model:page-size="size"
          background
          layout="total, sizes, prev, pager, next, jumper"
          :page-sizes="[10, 20, 50]"
          :total="total"
          @current-change="loadData"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>

    <el-dialog
      v-model="deleteDialogVisible"
      width="460px"
      :show-close="false"
      class="delete-dialog"
      align-center
      
    >
      <div class="delete-card">
        <div class="delete-heading">
          <span class="delete-kicker">此操作不可撤销</span>
          <h3>确定删除这篇文章吗？</h3>
        </div>
        <div class="delete-title">
          <span class="delete-title-label">文章标题</span>
          <strong>{{ deletingArticle?.title }}</strong>
        </div>
        <p>删除后，这篇文章将不会出现在后台列表与前台文章页中，请谨慎确认。</p>
      </div>
      <template #footer>
        <div class="delete-actions">
          <el-button class="delete-cancel" @click="closeDeleteDialog">取消</el-button>
          <el-button class="delete-confirm" type="danger" :loading="deleting" @click="submitDelete">
            确认删除
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import http from '@/api/http'
import type { Article } from '@/types'

interface ArticlePageResult {
  records: Article[]
  total: number
}

const router = useRouter()
const articles = ref<Article[]>([])
const total = ref(0)
const current = ref(1)
const size = ref(10)
const keyword = ref('')
const status = ref('')
const deleteDialogVisible = ref(false)
const deleting = ref(false)
const deletingArticle = ref<Article | null>(null)

const loadData = async () => {
  const res = await http.get<ArticlePageResult>('/articles', {
    params: {
      keyword: keyword.value || undefined,
      status: status.value || undefined,
      current: current.value,
      size: size.value
    }
  })
  articles.value = res.records
  total.value = res.total
}

const handleSearch = async () => {
  current.value = 1
  await loadData()
}

const resetFilters = async () => {
  keyword.value = ''
  status.value = ''
  current.value = 1
  size.value = 10
  await loadData()
}

const handleSizeChange = async () => {
  current.value = 1
  await loadData()
}

const openDeleteDialog = (article: Article) => {
  deletingArticle.value = article
  deleteDialogVisible.value = true
}

const closeDeleteDialog = () => {
  deleteDialogVisible.value = false
  deletingArticle.value = null
}

const submitDelete = async () => {
  if (!deletingArticle.value) return
  try {
    deleting.value = true
    await http.delete(`/articles/${deletingArticle.value.id}`)
    ElMessage.success('文章已删除')
    closeDeleteDialog()
    if (articles.value.length === 1 && current.value > 1) {
      current.value -= 1
    }
    await loadData()
  } finally {
    deleting.value = false
  }
}

onMounted(loadData)
</script>

<style scoped lang="scss">
.manage-page { display: grid; gap: 18px; }
.header-row { display: flex; justify-content: space-between; align-items: center; gap: 18px; }
.eyebrow { color: #b45309; font-size: 13px; font-weight: 700; }
.header-row h2 { margin: 8px 0 10px; color: #0f172a; }
.header-row p { margin: 0; color: #64748b; line-height: 1.7; }
.table-card { border-radius: 22px; }
.toolbar { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 18px; }
.toolbar :deep(.el-input),
.toolbar :deep(.el-select) { width: 220px; }
.article-table { width: 100%; }
.pagination-wrap { display: flex; justify-content: flex-end; margin-top: 18px; }
.delete-card {
  display: grid;
  gap: 16px;
  padding: 24px 22px 18px;
  border: 1px solid rgba(255, 255, 255, 0.9);
  border-radius: 26px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(250, 247, 242, 0.96)),
    radial-gradient(circle at top right, rgba(217, 139, 79, 0.08), transparent 34%);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.7),
    0 20px 40px rgba(15, 23, 42, 0.08);
}

.delete-heading {
  display: grid;
  gap: 8px;
}

.delete-kicker {
  color: #b45309;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.delete-card h3,
.delete-card p {
  margin: 0;
}

.delete-card h3 {
  color: #172033;
  font-size: 22px;
  line-height: 1.35;
  font-weight: 650;
}

.delete-title {
  display: grid;
  gap: 6px;
  padding: 14px 16px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 22px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 250, 252, 0.98)),
    linear-gradient(135deg, rgba(217, 139, 79, 0.04), rgba(32, 92, 79, 0.05));
}

.delete-title-label {
  color: #94a3b8;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.04em;
}

.delete-title strong {
  color: #0f172a;
  font-size: 15px;
  line-height: 1.6;
  font-weight: 700;
  word-break: break-word;
}

.delete-card p {
  color: #64748b;
  line-height: 1.8;
}

.delete-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.delete-actions :deep(.el-button) {
  min-width: 108px;
  height: 42px;
  border-radius: 14px;
  font-weight: 600;
}

.delete-cancel {
  border-color: rgba(148, 163, 184, 0.26);
  background: rgba(255, 255, 255, 0.9);
  color: #475569;
}

.delete-confirm {
  border-color: #c2410c;
  background: linear-gradient(135deg, #dc2626, #c2410c);
  box-shadow: 0 14px 28px rgba(194, 65, 12, 0.22);
}

:deep(.delete-dialog.el-dialog) {
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.85);
  border-radius: 10px !important;
  background:
    radial-gradient(circle at top right, rgba(217, 139, 79, 0.1), transparent 28%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 250, 252, 0.98));
  box-shadow:
    0 34px 80px rgba(15, 23, 42, 0.16),
    0 8px 24px rgba(15, 23, 42, 0.08);
}

:deep(.delete-dialog .el-dialog__body) {
  padding: 18px 18px 10px;
}

:deep(.delete-dialog .el-dialog__footer) {
  padding: 0 28px 28px;
}
</style>
