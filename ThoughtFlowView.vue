<script setup>
import { ref, computed, onMounted } from 'vue'
import { EditPen, Delete, Plus, Timer, Collection, Document, Histogram, Calendar, Star, Reading, Bell, ChatRound } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const thoughts = ref([])
const newThought = ref('')
const editingThought = ref(null)
const editContent = ref('')

// 学习统计数据
const studyStats = ref({
  totalTime: 0,
  completedGoals: 0,
  flashcardsCount: 0,
  pendingTasks: 0,
  weeklyHours: [2, 4, 3, 5, 4, 6, 3]
})

// 番茄钟
const pomodoroTime = ref(25 * 60)
const isTimerRunning = ref(false)
const timerInterval = ref(null)

// 知识点管理
const flashcards = ref([])
const newFlashcard = ref({
  question: '',
  answer: '',
  category: '',
  tags: []
})
const currentFlashcard = ref(null)
const showAnswer = ref(false)

// 学习日程
const schedule = ref([])
const newSchedule = ref({
  title: '',
  date: '',
  time: '',
  duration: 60,
  completed: false
})

// 知识点分类
const categories = ref([
  { label: '数学', value: 'math' },
  { label: '英语', value: 'english' },
  { label: '编程', value: 'programming' },
  { label: '其他', value: 'other' }
])

// 标签选项
const tagOptions = ref([
  '重要', '需复习', '已掌握', '困难', '简单'
])

// 番茄钟控制
const startTimer = () => {
  if (!isTimerRunning.value) {
    isTimerRunning.value = true
    timerInterval.value = setInterval(() => {
      if (pomodoroTime.value > 0) {
        pomodoroTime.value--
      } else {
        stopTimer()
        studyStats.value.totalTime += 25
        ElMessage.success('专注时间结束！休息一下吧')
      }
    }, 1000)
  }
}

const stopTimer = () => {
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
    isTimerRunning.value = false
  }
}

const formatTime = computed(() => {
  const minutes = Math.floor(pomodoroTime.value / 60)
  const seconds = pomodoroTime.value % 60
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
})

// 添加知识点
const addFlashcard = () => {
  if (newFlashcard.value.question && newFlashcard.value.answer) {
    flashcards.value.push({
      id: Date.now(),
      ...newFlashcard.value,
      createdAt: new Date().toLocaleString(),
      lastReview: null
    })
    newFlashcard.value = { question: '', answer: '', category: '', tags: [] }
    studyStats.value.flashcardsCount = flashcards.value.length
  }
}

// 添加日程
const addSchedule = () => {
  if (newSchedule.value.title && newSchedule.value.date) {
    schedule.value.push({
      id: Date.now(),
      ...newSchedule.value
    })
    newSchedule.value = {
      title: '',
      date: '',
      time: '',
      duration: 60,
      completed: false
    }
    studyStats.value.pendingTasks = schedule.value.filter(t => !t.completed).length
  }
}

// 统计图表初始化
let studyChart = null
onMounted(() => {
  const chartDom = document.getElementById('studyChart')
  if (chartDom) {
    studyChart = echarts.init(chartDom)
    updateChart()
  }
})

const updateChart = () => {
  const option = {
    title: {
      text: '每周学习时长统计'
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    },
    yAxis: {
      type: 'value',
      name: '小时'
    },
    series: [
      {
        name: '学习时长',
        type: 'bar',
        data: studyStats.value.weeklyHours,
        itemStyle: {
          color: '#409EFF'
        }
      }
    ]
  }
  studyChart?.setOption(option)
}

// 原有的思维导图相关方法
const addThought = () => {
  if (newThought.value.trim()) {
    thoughts.value.push({
      id: Date.now(),
      content: newThought.value,
      createdAt: new Date().toLocaleString(),
      tags: []
    })
    newThought.value = ''
  }
}

const deleteThought = (id) => {
  thoughts.value = thoughts.value.filter(t => t.id !== id)
}

const startEdit = (thought) => {
  editingThought.value = thought.id
  editContent.value = thought.content
}

const saveEdit = (thought) => {
  if (editContent.value.trim()) {
    const index = thoughts.value.findIndex(t => t.id === thought.id)
    if (index !== -1) {
      thoughts.value[index].content = editContent.value
    }
  }
  editingThought.value = null
}

import { useRouter } from 'vue-router'
const router = useRouter()

const goToChat = () => {
  router.push('/chat')
}
</script>

<template>
  <div class="thought-flow-container">
    <!-- 添加返回聊天的悬浮按钮 -->
    <div class="back-to-chat" @click="goToChat">
      <el-tooltip
        content="返回聊天"
        placement="right"
        :show-after="300"
      >
        <el-button class="float-btn" type="primary" circle>
          <el-icon><ChatRound /></el-icon>
        </el-button>
      </el-tooltip>
    </div>
    <!-- 顶部统计卡片 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6" v-for="(stat, index) in [
        { icon: Timer, value: studyStats.totalTime, label: '总学习时长(分钟)' },
        { icon: Star, value: studyStats.completedGoals, label: '完成目标数' },
        { icon: Reading, value: studyStats.flashcardsCount, label: '知识点数量' },
        { icon: Bell, value: studyStats.pendingTasks, label: '待完成任务' }
      ]" :key="index">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <el-icon><component :is="stat.icon" /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="main-content">
      <!-- 左侧：番茄钟和统计图表 -->
      <el-col :span="8">
        <el-card class="timer-card">
          <template #header>
            <div class="card-header">
              <span>专注计时器</span>
              <el-icon><Timer /></el-icon>
            </div>
          </template>
          <div class="timer-display">
            <div class="time">{{ formatTime }}</div>
            <div class="timer-controls">
              <el-button 
                type="primary" 
                @click="startTimer" 
                :disabled="isTimerRunning"
              >
                开始
              </el-button>
              <el-button 
                type="warning" 
                @click="stopTimer" 
                :disabled="!isTimerRunning"
              >
                暂停
              </el-button>
            </div>
          </div>
        </el-card>

        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>学习统计</span>
              <el-icon><Histogram /></el-icon>
            </div>
          </template>
          <div id="studyChart" style="height: 300px;"></div>
        </el-card>
      </el-col>

      <!-- 中间：知识点管理 -->
      <el-col :span="8">
        <el-card class="flashcard-card">
          <template #header>
            <div class="card-header">
              <span>知识点管理</span>
              <el-icon><Reading /></el-icon>
            </div>
          </template>

          <el-form :model="newFlashcard" class="flashcard-form">
            <el-form-item>
              <el-input
                v-model="newFlashcard.question"
                type="textarea"
                :rows="2"
                placeholder="问题/概念"
              />
            </el-form-item>
            <el-form-item>
              <el-input
                v-model="newFlashcard.answer"
                type="textarea"
                :rows="2"
                placeholder="答案/解释"
              />
            </el-form-item>
            <el-form-item>
              <el-select
                v-model="newFlashcard.category"
                placeholder="选择分类"
                style="width: 100%"
              >
                <el-option
                  v-for="category in categories"
                  :key="category.value"
                  :label="category.label"
                  :value="category.value"
                />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-select
                v-model="newFlashcard.tags"
                multiple
                placeholder="选择标签"
                style="width: 100%"
              >
                <el-option
                  v-for="tag in tagOptions"
                  :key="tag"
                  :label="tag"
                  :value="tag"
                />
              </el-select>
            </el-form-item>
            <el-button type="primary" @click="addFlashcard" block>
              添加知识点
            </el-button>
          </el-form>

          <div class="flashcards-list">
            <el-collapse accordion>
              <el-collapse-item
                v-for="card in flashcards"
                :key="card.id"
                :title="card.question"
              >
                <div class="flashcard-content">
                  <p class="answer">{{ card.answer }}</p>
                  <div class="flashcard-footer">
                    <el-tag size="small" :type="card.category === 'important' ? 'danger' : ''">
                      {{ categories.find(c => c.value === card.category)?.label || '未分类' }}
                    </el-tag>
                    <el-tag
                      v-for="tag in card.tags"
                      :key="tag"
                      size="small"
                      class="ml-2"
                    >
                      {{ tag }}
                    </el-tag>
                  </div>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：学习日程 -->
      <el-col :span="8">
        <el-card class="schedule-card">
          <template #header>
            <div class="card-header">
              <span>学习日程</span>
              <el-icon><Calendar /></el-icon>
            </div>
          </template>

          <el-form :model="newSchedule" class="schedule-form">
            <el-form-item>
              <el-input
                v-model="newSchedule.title"
                placeholder="学习内容"
              />
            </el-form-item>
            <el-form-item>
              <el-date-picker
                v-model="newSchedule.date"
                type="date"
                placeholder="选择日期"
                style="width: 100%"
              />
            </el-form-item>
            <el-form-item>
              <el-time-picker
                v-model="newSchedule.time"
                placeholder="选择时间"
                style="width: 100%"
              />
            </el-form-item>
            <el-form-item>
              <el-input-number
                v-model="newSchedule.duration"
                :min="15"
                :max="240"
                :step="15"
                placeholder="时长(分钟)"
                style="width: 100%"
              />
            </el-form-item>
            <el-button type="primary" @click="addSchedule" block>
              添加日程
            </el-button>
          </el-form>

          <div class="schedule-list">
            <el-timeline>
              <el-timeline-item
                v-for="item in schedule"
                :key="item.id"
                :timestamp="new Date(item.date).toLocaleDateString()"
                :type="item.completed ? 'success' : 'primary'"
              >
                <el-card class="schedule-item">
                  <template #header>
                    <div class="schedule-header">
                      <span>{{ item.title }}</span>
                      <el-tag :type="item.completed ? 'success' : 'warning'" size="small">
                        {{ item.completed ? '已完成' : '未完成' }}
                      </el-tag>
                    </div>
                  </template>
                  <div class="schedule-info">
                    <p>
                      <el-icon><Timer /></el-icon>
                      {{ new Date(item.time).toLocaleTimeString() }}
                    </p>
                    <p>
                      <el-icon><Timer /></el-icon>
                      时长：{{ item.duration }}分钟
                    </p>
                  </div>
                </el-card>
              </el-timeline-item>
            </el-timeline>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 原有的思维导图部分 -->
    <div class="thoughts-section">
      <h3 class="section-title">思维导图</h3>
      <el-input
        v-model="newThought"
        placeholder="写下你的新想法..."
        class="thought-input"
        @keyup.enter="addThought"
      >
        <template #append>
          <el-button @click="addThought" :icon="Plus">添加</el-button>
        </template>
      </el-input>
      <el-empty v-if="thoughts.length === 0" description="还没有任何想法" />
      <el-card v-for="thought in thoughts" :key="thought.id" class="thought-card">
        <template #header>
          <div class="thought-header">
            <span class="time">{{ thought.createdAt }}</span>
            <div class="operations">
              <el-button
                type="primary"
                :icon="EditPen"
                circle
                @click="startEdit(thought)"
              />
              <el-button
                type="danger"
                :icon="Delete"
                circle
                @click="deleteThought(thought.id)"
              />
            </div>
          </div>
        </template>
        <div v-if="editingThought === thought.id" class="edit-mode">
          <el-input
            v-model="editContent"
            type="textarea"
            :rows="3"
            @keyup.enter="saveEdit(thought)"
          />
          <div class="edit-actions">
            <el-button type="primary" @click="saveEdit(thought)">保存</el-button>
            <el-button @click="editingThought = null">取消</el-button>
          </div>
        </div>
        <div v-else class="thought-content">
          {{ thought.content }}
        </div>
        <div class="tags" v-if="thought.tags.length > 0">
          <el-tag
            v-for="tag in thought.tags"
            :key="tag"
            size="small"
            class="tag"
          >
            {{ tag }}
          </el-tag>
        </div>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.thought-flow-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.stat-cards {
  margin-bottom: 20px;
}

.stat-card {
  height: 100%;
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-content .el-icon {
  font-size: 24px;
  color: #409EFF;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.main-content {
  margin-top: 20px;
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.timer-card {
  margin-bottom: 20px;
}

.timer-display {
  text-align: center;
  padding: 20px 0;
}

.time {
  font-size: 48px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 20px;
  font-family: monospace;
}

.timer-controls {
  display: flex;
  justify-content: center;
  gap: 10px;
}

.chart-card {
  margin-top: 20px;
}

.flashcard-form,
.schedule-form {
  margin-bottom: 20px;
}

.flashcards-list {
  margin-top: 20px;
}

.flashcard-content {
  padding: 10px 0;
}

.answer {
  margin-bottom: 10px;
  white-space: pre-wrap;
}

.flashcard-footer {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 10px;
}

.schedule-list {
  margin-top: 20px;
}

.schedule-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.schedule-info {
  color: #606266;
}

.schedule-info p {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 5px 0;
}

.thoughts-section {
  margin-top: 40px;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 20px;
  padding-left: 15px;
  border-left: 4px solid #409EFF;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .el-col {
    width: 100% !important;
    margin-bottom: 20px;
  }
}

/* 返回聊天按钮样式 */
.back-to-chat {
  position: fixed;
  top: 20px;
  left: 20px;
  z-index: 1000;
}

.float-btn {
  width: 40px;
  height: 40px;
  padding: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.float-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.float-btn .el-icon {
  font-size: 20px;
  margin: 0;
}
</style>
