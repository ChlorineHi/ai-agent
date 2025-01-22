<script setup>
import { ref, onMounted, nextTick, computed, watch } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import AnimatedCat from '../components/AnimatedCat.vue'
import AnimatedDog from '../components/AnimatedDog.vue'
import { useRouter, useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import FileUploader from '../components/FileUploader.vue'
import { useChatStore } from '../stores/chat'
import MessageBanner from '../components/MessageBanner.vue'
import { 
  ChatLineRound, InfoFilled, Plus, Position, UserFilled, Monitor, Lightning, 
  PictureRounded, Document, Picture, FolderOpened, Setting, Collection, Share,
  Upload
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const chatStore = useChatStore()
const { messages, loading } = storeToRefs(chatStore)
const userInput = ref('')
const chatHistory = ref(null)
const drawerVisible = ref(true)
const isCollapse = ref(false)
const messagesContainer = ref(null)
const showRightDrawer = ref(false)
const rightDrawerTimer = ref(null)

// 添加模型选择相关的数据
const selectedModel = ref('zhipu')

const handleModelChange = (model) => {
  selectedModel.value = model
  console.log('Selected model:', model)
}

const modelOptions = [
  { value: 'zhipu', label: 'Zhipu' },
  { value: 'zhipu-3.5', label: 'Zhipu-3.5' },
  { value: 'glm-4', label: 'GLM-4' },
]

const chatId = computed(() => route.params.id || null)

// 监听路由参数变化
watch(() => route.params.id, (newId) => {
  if (newId) {
    chatStore.loadChat(newId)
  }
}, { immediate: true })

const startNewChat = () => {
  const chatId = chatStore.createNewChat()
  router.push(`/chat/${chatId}`)
}

const handleSend = async () => {
  // 确保 userInput.value 是字符串类型
  if (!userInput.value || typeof userInput.value !== 'string' || !userInput.value.trim() || loading.value) return
  
  const message = userInput.value
  userInput.value = ''

  // 如果有图片，发送图片问题
  if (imageFile.value) {
    const formData = new FormData()
    formData.append('image', imageFile.value)
    formData.append('question', message)
    formData.append('model', selectedModel.value)

    try {
      const response = await fetch('http://localhost:5000/chat_with_image', {
        method: 'POST',
        body: formData,
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
        }
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || '上传失败')
      }

      // 添加用户消息（包含图片）
      messages.value.push({
        role: 'user',
        content: message,
        image: imagePreview.value
      })

      // 添加AI回复
      messages.value.push({
        role: 'assistant',
        content: data.response
      })

      // 清理图片
      imageFile.value = null
      imagePreview.value = ''
    } catch (error) {
      ElMessage.error(error.message || '处理失败')
    }
    return
  }

  try {
    // 添加用户消息到消息列表
    messages.value.push({
      role: 'user',
      content: message
    })

    // 发送消息到后端，包含模型选择
    const response = await fetch('http://localhost:5000/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages: messages.value,
        model: selectedModel.value
      }),
      credentials: 'include'
    })

    if (!response.ok) {
      throw new Error('Failed to send message')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let content = ''

    // 添加AI消息占位符
    messages.value.push({
      role: 'assistant',
      content: ''
    })

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value)
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const text = line.slice(6) // Remove 'data: ' prefix
          if (text === '[DONE]') {
            break
          }
          content += text
          // 更新最后一条消息的内容
          messages.value[messages.value.length - 1].content = content
        }
      }
    }
  } catch (error) {
    console.error('Error:', error)
    ElMessage.error('发送消息失败')
  }
}

// 图片上传相关
const imageFile = ref(null)
const imagePreview = ref('')
const fileInput = ref(null)  // 添加文件输入引用

const handleImageSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    imageFile.value = file
    // 创建预览URL
    imagePreview.value = URL.createObjectURL(file)
  }
}

const handleMouseEnter = () => {
  if (rightDrawerTimer.value) {
    clearTimeout(rightDrawerTimer.value)
  }
  showRightDrawer.value = true
}

const handleMouseLeave = () => {
  rightDrawerTimer.value = setTimeout(() => {
    showRightDrawer.value = false
  }, 200) // 减少延迟时间
}

// 添加响应式变量
const searchResults = ref([])
const isSearching = ref(false)

// 搜索函数
const performSearch = async (query) => {
  try {
    isSearching.value = true
    const response = await fetch('http://localhost:5000/api/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    })
    const data = await response.json()
    searchResults.value = data.results
  } catch (error) {
    console.error('Search error:', error)
  } finally {
    isSearching.value = false
  }
}

// 监听用户输入
watch(() => userInput.value, async (newInput) => {
  if (newInput && newInput.trim()) {
    await performSearch(newInput)
  } else {
    searchResults.value = []
  }
}, { debounce: 500 }) // 防抖，避免频繁请求

// 添加复制功能
const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('复制成功')
  } catch (err) {
    ElMessage.error('复制失败')
  }
}

// 添加相关问题的响应式变量
const relatedQuestions = ref({})  // 用于存储每条消息的相关问题

// 添加表情符号列表
const EMOJIS = [
  "🤔", "💡", "✨", "🎯", "🌟", "🚀", "💪", "👍", "🎨", "📚",
  "🔍", "💭", "🎊", "🌈", "🎵", "🎮", "🎲", "🎯", "🎪", "🎭",
  "🌺", "🌸", "🍀", "🌿", "🎋", "🎍", "🎪", "🎢", "🎡", "🎠",
  "🎮", "🎲", "🎯", "🎱", "🎳", "🎾", "🏀", "⚽", "🏈", "🏉"
]

// 获取随机表情的函数
const getRandomEmoji = () => {
  const randomIndex = Math.floor(Math.random() * EMOJIS.length)
  return EMOJIS[randomIndex]
}

// 生成相关问题的方法
const generateRelatedQuestions = async (messageContent) => {
  try {
    const response = await fetch('http://localhost:5000/generate_questions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      credentials: 'include',
      mode: 'cors',
      body: JSON.stringify({
        content: messageContent
      })
    })
    
    if (!response.ok) {
      throw new Error('Failed to generate questions')
    }
    
    const questions = await response.json()
    // 为每个问题添加随机表情
    return Array.isArray(questions) ? questions.map(q => ({
      text: q,
      emoji: getRandomEmoji()
    })) : []
  } catch (error) {
    console.error('生成相关问题失败:', error)
    return []
  }
}

// 处理相关问题点击
const handleRelatedQuestionClick = (question) => {
  // 检查 question 是否为对象并且具有 text 属性
  userInput.value = typeof question === 'object' && question.text ? question.text : question
  handleSend()
}

// 文件上传相关
const uploadFile = ref(null)
const isUploading = ref(false)

// 处理文件上传
const handleFileUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  isUploading.value = true
  const formData = new FormData()
  formData.append('file', file)
  
  try {
    const response = await fetch('http://127.0.0.1:5000/upload_knowledge', {
      method: 'POST',
      headers: {
        'Accept': 'application/json'
      },
      credentials: 'include',
      mode: 'cors',
      body: formData
    })
    
    if (response.ok) {
      ElMessage.success('知识库文件上传成功')
    } else {
      ElMessage.error('文件上传失败')
    }
  } catch (error) {
    console.error('上传出错:', error)
    ElMessage.error('上传过程中发生错误')
  } finally {
    isUploading.value = false
    // 清空文件输入以允许重复上传相同文件
    uploadFile.value = null
  }
}

// 添加拖拽相关的状态和方法
const isResizing = ref(false)
const startHeight = ref(0)
const startY = ref(0)
const containerHeight = ref(120) // 默认高度

const handleMouseDown = (e) => {
  isResizing.value = true
  startY.value = e.clientY
  startHeight.value = containerHeight.value
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
  // 添加禁止选择文本的类
  document.body.classList.add('resizing')
}

const handleMouseMove = (e) => {
  if (!isResizing.value) return
  const delta = e.clientY - startY.value
  containerHeight.value = Math.max(120, startHeight.value - delta)
}

const handleMouseUp = () => {
  isResizing.value = false
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
  // 移除禁止选择文本的类
  document.body.classList.remove('resizing')
}

const triggerFileUpload = () => {
  if (fileInput.value) {
    fileInput.value.click()
  }
}

// 添加输入状态
const isTyping = ref(false)
let typingTimeout = null

// 监听输入事件
const handleInput = () => {
  isTyping.value = true
  clearTimeout(typingTimeout)
  typingTimeout = setTimeout(() => {
    isTyping.value = false
  }, 1000)
}

// 清理定时器
onMounted(() => {
  return () => {
    if (typingTimeout) {
      clearTimeout(typingTimeout)
    }
  }
})

// 添加回答模式
const responseMode = ref('simple')

// 模式说明配置
const modeDescriptions = {
  simple: {
    title: '简单模式说明',
    message: `
      <div class="mode-description">
        <h4>🌟 简单模式特点</h4>
        <ul>
          <li>使用通俗易懂的语言</li>
          <li>提供简洁明了的解释</li>
          <li>适合快速理解概念</li>
          <li>避免专业术语</li>
        </ul>
        <div class="mode-tip">💡 适合：日常交流和基础学习</div>
      </div>
    `,
    type: 'success'
  },
  complex: {
    title: '复杂模式说明',
    message: `
      <div class="mode-description">
        <h4>📚 复杂模式特点</h4>
        <ul>
          <li>提供详细的解释和分析</li>
          <li>包含具体的示例</li>
          <li>展示多个解决方案</li>
          <li>涵盖相关知识点</li>
        </ul>
        <div class="mode-tip">💡 适合：深入学习和问题分析</div>
      </div>
    `,
    type: 'warning'
  },
  professional: {
    title: '专业模式说明',
    message: `
      <div class="mode-description">
        <h4>🎯 专业模式特点</h4>
        <ul>
          <li>使用专业术语和标准</li>
          <li>提供技术性解答</li>
          <li>包含专业引用和依据</li>
          <li>深入技术细节</li>
        </ul>
        <div class="mode-tip">💡 适合：专业技术讨论和研究</div>
      </div>
    `,
    type: 'info'
  }
}

const handleModeSelect = (mode) => {
  responseMode.value = mode
  // 显示模式说明通知
  ElNotification({
    title: modeDescriptions[mode].title,
    message: modeDescriptions[mode].message,
    type: modeDescriptions[mode].type,
    duration: 6000,
    dangerouslyUseHTMLString: true,
    position: 'top-right'
  })
}
</script>

<template>
  <div class="chat-container">
    <el-container>
      <el-aside width="200px">
        <el-menu
          default-active="/"
          class="el-menu-vertical"
          :collapse="isCollapse"
          router
        >
          <el-menu-item index="/" @click="startNewChat">
            <el-icon><Plus /></el-icon>
            <span>新对话</span>
          </el-menu-item>

          <el-sub-menu index="history">
            <template #title>
              <el-icon><ChatLineRound /></el-icon>
              <span>历史对话</span>
            </template>
            <el-menu-item 
              v-for="chat in chatStore.chatHistory" 
              :key="chat.id"
              :index="`/chat/${chat.id}`"
              @click="() => {
                chatStore.loadChat(chat.id);
                router.push(`/chat/${chat.id}`);
              }"
            >
              <div class="chat-title">
                <div class="title-text" :title="chat.title">
                  {{ chat.messages.length > 0 ? chat.messages[0].content.slice(0, 20) + (chat.messages[0].content.length > 20 ? '...' : '') : '新对话' }}
                </div>
                <div class="chat-date">{{ chat.createdAt }}</div>
              </div>
            </el-menu-item>
          </el-sub-menu>

          <el-menu-item index="/solution" @click="router.push('/solution')">
            <el-icon><Lightning /></el-icon>
            <span>智解</span>
          </el-menu-item>

          <el-menu-item index="/thought-flow">
            <el-icon><EditPen /></el-icon>
            <span>思流</span>
          </el-menu-item>

          <el-menu-item index="/about">
            <el-icon><InfoFilled /></el-icon>
            <span>关于</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-main>
        <div class="chat-content">
          <div class="messages-container" ref="messagesContainer">
            <MessageBanner @model-change="handleModelChange">
            </MessageBanner>
            <div class="messages-wrapper">
              <div v-for="(msg, index) in chatStore.messages" 
                   :key="index" 
                   class="message-wrapper">
                <div :class="['message', msg.role]">
                  <el-avatar 
                    :size="36"
                    :icon="msg.role === 'user' ? UserFilled : Monitor"
                    :class="['message-avatar', msg.role]"
                  />
                  <div class="message-content" 
                       :class="{ 
                         'streaming': msg.role === 'assistant' && 
                                    index === chatStore.messages.length - 1 && 
                                    chatStore.loading 
                       }">
                    <div v-if="msg.role === 'user'" class="user-text">
                      {{ msg.content }}
                      <div class="copy-button-wrapper">
                        <el-tooltip
                          content="复制内容"
                          placement="left"
                          :show-after="300"
                        >
                          <el-button
                            class="copy-button"
                            type="text"
                            @click="copyToClipboard(msg.content)"
                          >
                            <el-icon><CopyDocument /></el-icon>
                          </el-button>
                        </el-tooltip>
                      </div>
                    </div>
                    <div v-else-if="msg.role === 'assistant'" 
                         class="assistant-text"
                         :class="{ 'typing': index === chatStore.messages.length - 1 && chatStore.loading }">
                      <span>{{ msg.content }}</span>
                      <div class="copy-button-wrapper">
                        <el-tooltip
                          content="复制内容"
                          placement="right"
                          :show-after="300"
                        >
                          <el-button
                            class="copy-button"
                            type="text"
                            @click="copyToClipboard(msg.content)"
                          >
                            <el-icon><CopyDocument /></el-icon>
                          </el-button>
                        </el-tooltip>
                      </div>
                      <span v-if="msg.role === 'assistant' && 
                                 index === chatStore.messages.length - 1 && 
                                 chatStore.loading" 
                             class="cursor"></span>
                    </div>
                    <div v-else-if="msg.role === 'user' && msg.image" 
                         class="user-image">
                      <img :src="msg.image" alt="用户上传的图片" />
                    </div>
                  </div>
                </div>
                <!-- 将相关问题按钮移到消息外面 -->
                <div v-if="msg.role === 'assistant' && relatedQuestions[index]" 
                     class="related-questions">
                  <div class="related-questions-label">
                    <el-icon class="label-icon"><ChatLineRound /></el-icon>
                    <span>相关问题</span>
                  </div>
                  <div class="related-questions-buttons">
                    <el-button
                      v-for="(question, qIndex) in relatedQuestions[index]"
                      :key="qIndex"
                      link
                      size="small"
                      class="related-question-btn"
                      @click="handleRelatedQuestionClick(question)"
                    >
                      <el-icon class="question-icon"><Plus /></el-icon>
                      <span>{{ question.text }}</span>
                      <span class="question-emoji">{{ question.emoji }}</span>
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
            <div class="input-container">
              <!-- 添加拖拽手柄 -->
              <div class="resize-handle" @mousedown="handleMouseDown"></div>
              <div class="input-area">
                <AnimatedCat :is-typing="isTyping" />
                <AnimatedDog :is-typing="isTyping" @mode-select="handleModeSelect" />
                <div class="input-left">
                  <!-- 文件上传按钮 -->
                  <div class="upload-button" :class="{ 'is-uploading': isUploading }">
                    <el-tooltip
                      content="上传文件 (PDF, TXT, DOC)"
                      placement="top"
                      :show-after="300"
                    >
                      <el-button
                        circle
                        class="custom-upload-btn"
                        @click="triggerFileUpload"
                        :loading="isUploading"
                      >
                        <el-icon><Upload /></el-icon>
                      </el-button>
                    </el-tooltip>
                    <input
                      type="file"
                      ref="fileInput"
                      @change="handleFileUpload"
                      accept=".txt,.pdf,.doc,.docx"
                      style="display: none"
                    />
                  </div>
                </div>

                <!-- 输入框 -->
                <div class="custom-input">
                  <el-input
                    v-model="userInput"
                    type="textarea"
                    :autosize="{ minRows: 1, maxRows: 4 }"
                    placeholder="输入问题..."
                    @keydown.enter.exact.prevent="handleSend"
                    @input="handleInput"
                    ref="inputRef"
                  />
                </div>

                <!-- 发送按钮 -->
                <div class="input-right">
                  <el-button
                    class="send-button"
                    type="primary"
                    @click="handleSend"
                    :disabled="!userInput.trim() && !imageFile"
                  >
                    发送
                    <el-icon><Position /></el-icon>
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
        <!-- 添加右侧触发区域 -->
        <div 
          class="right-drawer-trigger"
          @mouseenter="handleMouseEnter"
        ></div>
      </el-main>
    </el-container>

    <!-- 添加右侧悬浮按钮 -->
        <!-- 添加右侧悬浮按钮 -->
    <div class="float-button" @click="showRightDrawer = true">
      <el-button
        type="primary"
        circle
        class="drawer-trigger-button"
        :icon="Share"
      />
    </div>

    <!-- 添加右侧抽屉 -->
    <el-drawer
      v-model="showRightDrawer"
      direction="rtl"
      size="300px"
      :show-close="false"
      :modal="false"
      custom-class="right-side-drawer"
      @mouseenter="handleMouseEnter"
      @mouseleave="handleMouseLeave"
    >
      <template #header>
        <div class="drawer-header">
          <h3 class="drawer-title">搜索结果</h3>
          <el-icon class="drawer-icon" :class="{ 'is-loading': isSearching }"><Collection /></el-icon>
        </div>
      </template>
      <div class="drawer-content">
        <div v-if="isSearching" class="search-loading">
          <el-icon class="loading-icon"><Loading /></el-icon>
          <span>正在搜索...</span>
        </div>
        <div v-else-if="searchResults.length === 0" class="no-results">
          <el-empty description="暂无搜索结果" />
        </div>
        <div v-else class="search-results">
          <div v-for="(result, index) in searchResults" 
               :key="index" 
               class="search-result-item">
            <h4 class="result-title">
              <a :href="result.link" target="_blank">{{ result.title }}</a>
            </h4>
            <p class="result-snippet">{{ result.snippet }}</p>
            <a :href="result.link" 
               target="_blank" 
               class="result-link">{{ result.link }}</a>
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<style scoped>
/* 导航栏容器样式 */
.el-aside {
  background: white;
  border-right: 1px solid #e6e6e6;
  transition: all 0.3s ease;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
  height: 100vh;
  position: relative;
  z-index: 1000;
}

/* 菜单样式优化 */
.el-menu {
  border-right: none;
  background: transparent;
  width: 100%;
}

.el-menu-vertical {
  height: 100%;
}

.el-menu-item {
  height: 50px;
  line-height: 50px;
  padding: 0 16px !important;
  margin: 4px 8px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.el-menu-item:hover {
  background: #f0f7ff !important;
  transform: translateX(4px);
}

.el-menu-item.is-active {
  background: #409EFF !important;
  color: white !important;
  font-weight: 500;
}

.el-menu-item.is-active .el-icon {
  color: white !important;
}

/* 子菜单样式 */
.el-sub-menu {
  margin: 4px 8px;
}

.el-sub-menu__title {
  height: 50px;
  line-height: 50px;
  padding: 0 16px !important;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.el-sub-menu__title:hover {
  background: #f0f7ff !important;
}

/* 历史对话项样式 */
.chat-title {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 100%;
  overflow: hidden;
}

.title-text {
  font-size: 14px;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color 0.3s ease;
}

.chat-date {
  font-size: 12px;
  color: #909399;
}

/* 图标样式 */
.el-icon {
  font-size: 18px;
  margin-right: 8px;
  transition: all 0.3s ease;
}

/* 添加滚动条样式 */
.el-menu::-webkit-scrollbar {
  width: 4px;
}

.el-menu::-webkit-scrollbar-track {
  background: transparent;
}

.el-menu::-webkit-scrollbar-thumb {
  background: #e0e0e0;
  border-radius: 2px;
}

.el-menu::-webkit-scrollbar-thumb:hover {
  background: #c0c0c0;
}

/* 折叠按钮样式 */
.collapse-btn {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
}

.collapse-btn:hover {
  background: #f0f7ff;
  transform: translateX(-50%) scale(1.1);
}

/* 动画效果 */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.el-menu-item, .el-sub-menu {
  animation: slideIn 0.3s ease-out forwards;
}

/* 其他样式保持不变 */
.nav-container {
  position: relative;
  background: linear-gradient(to right, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.98));
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  padding: 0;
  z-index: 100;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.nav-container:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.nav-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  padding: 0 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.nav-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 20px;
  font-weight: 600;
  color: var(--el-color-primary);
  text-decoration: none;
  transition: all 0.3s ease;
}

.nav-logo:hover {
  transform: translateY(-1px);
}

.nav-logo-icon {
  font-size: 24px;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-menu-item {
  position: relative;
  padding: 8px 16px;
  border-radius: 8px;
  color: var(--el-text-color-regular);
  font-weight: 500;
  text-decoration: none;
  transition: all 0.3s ease;
}

.nav-menu-item:hover {
  color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

.nav-menu-item.active {
  color: var(--el-color-primary);
  background: var(--el-color-primary-light-8);
}

.nav-menu-item.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 50%;
  transform: translateX(-50%);
  width: 24px;
  height: 3px;
  border-radius: 2px;
  background: var(--el-color-primary);
}

.nav-menu-item.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 50%;
  transform: translateX(-50%);
  width: 24px;
  height: 3px;
  border-radius: 2px;
  background: var(--el-color-primary);
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.nav-button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.nav-button.primary {
  color: white;
  background: var(--el-color-primary);
  border: none;
}

.nav-button.primary:hover {
  background: var(--el-color-primary-dark-2);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.nav-button.secondary {
  color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
  border: 1px solid var(--el-color-primary-light-5);
}

.nav-button.secondary:hover {
  background: var(--el-color-primary-light-8);
  transform: translateY(-1px);
}

/* 暗色模式适配 */
@media (prefers-color-scheme: dark) {
  .nav-container {
    background: linear-gradient(to right, rgba(30, 30, 30, 0.95), rgba(30, 30, 30, 0.98));
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }

  .nav-menu-item {
    color: var(--el-text-color-secondary);
  }

  .nav-menu-item:hover {
    background: rgba(var(--el-color-primary-rgb), 0.1);
  }

  .nav-menu-item.active {
    background: rgba(var(--el-color-primary-rgb), 0.15);
  }

  .nav-button.secondary {
    background: rgba(var(--el-color-primary-rgb), 0.1);
    border-color: rgba(var(--el-color-primary-rgb), 0.2);
  }

  .nav-button.secondary:hover {
    background: rgba(var(--el-color-primary-rgb), 0.15);
  }
}

/* 响应式设计 */
@media screen and (max-width: 768px) {
  .nav-content {
    padding: 0 16px;
  }

  .nav-menu {
    display: none;
  }

  .nav-button {
    padding: 6px 12px;
    font-size: 14px;
  }
}

.chat-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

:deep(.el-container) {
  height: 100vh;
}

:deep(.el-main) {
  padding: 0 !important;
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.chat-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.messages-container {
  flex: 1;
  position: relative;
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.messages-wrapper {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  padding-bottom: 20px;
}

.input-container {
  padding: 16px 24px;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  margin-top: auto;
  transition: none;
  box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.03);
  position: relative;
  z-index: 2;
  height: v-bind(containerHeight + 'px');
  min-height: 120px;
}

/* 拖拽手柄样式 */
.resize-handle {
  position: absolute;
  top: -3px;
  left: 0;
  right: 0;
  height: 6px;
  cursor: row-resize;
  background: linear-gradient(to bottom,
    transparent,
    rgba(0, 0, 0, 0.05) 50%,
    transparent
  );
  opacity: 0;
  transition: opacity 0.2s ease;
  z-index: 10;
}

.resize-handle:hover,
.resize-handle:active {
  opacity: 1;
}

.resize-handle::before {
  content: '';
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 40px;
  height: 2px;
  border-radius: 1px;
  background: rgba(0, 0, 0, 0.2);
}

/* 禁止文本选择的全局样式 */
:global(.resizing) {
  user-select: none !important;
  cursor: row-resize !important;
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .resize-handle {
    background: linear-gradient(to bottom,
      transparent,
      rgba(255, 255, 255, 0.1) 50%,
      transparent
    );
  }

  .resize-handle::before {
    background: rgba(255, 255, 255, 0.3);
  }
}

.input-area {
  height: calc(100% - 6px);
  margin-top: 6px;
  display: flex;
  align-items: stretch;
  gap: 12px;
  width: 100%;
  position: relative;
  padding: 12px 16px;
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 16px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
}

.input-area:focus-within {
  border-color: var(--el-color-primary);
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.1),
              0 4px 12px rgba(0, 0, 0, 0.05);
}

.input-left {
  display: flex;
  gap: 8px;
  align-items: flex-start;
  padding-top: 4px;
}

.input-right {
  display: flex;
  align-items: flex-start;
  padding-top: 4px;
}

.custom-input {
  flex: 1;
  margin: 0 12px;
  min-height: 100%;
  display: flex;
}

:deep(.el-textarea) {
  width: 100%;
  height: 100%;
}

:deep(.el-textarea__inner) {
  height: 100% !important;
  min-height: 36px !important;
  max-height: none !important;
  resize: none;
  line-height: 1.6;
  font-size: 15px;
  padding: 8px 12px;
  border: none;
  background: transparent;
  box-shadow: none;
}

:deep(.el-textarea__inner:focus) {
  box-shadow: none;
}

.upload-button .el-button,
.image-button .el-button {
  font-size: 18px;
  transition: all 0.3s ease;
  height: 36px;
  width: 36px;
  padding: 8px;
}

.upload-button,
.image-button {
  position: relative;
}

.custom-upload-btn {
  font-size: 18px;
  width: 36px;
  height: 36px;
  padding: 8px;
  background: rgba(var(--el-color-primary-rgb), 0.05);
  border: 1px solid rgba(var(--el-color-primary-rgb), 0.1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  color: var(--el-text-color-secondary);
}

.custom-upload-btn:hover {
  transform: translateY(-1px);
  background: rgba(var(--el-color-primary-rgb), 0.1);
  border-color: var(--el-color-primary);
  color: var(--el-color-primary);
  box-shadow: 0 4px 12px rgba(var(--el-color-primary-rgb), 0.15);
}

.custom-upload-btn:active {
  transform: translateY(0);
  background: rgba(var(--el-color-primary-rgb), 0.15);
  box-shadow: 0 2px 6px rgba(var(--el-color-primary-rgb), 0.1);
}

.upload-button.is-uploading .custom-upload-btn {
  background: rgba(var(--el-color-primary-rgb), 0.1);
  border-color: var(--el-color-primary);
  color: var(--el-color-primary);
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(var(--el-color-primary-rgb), 0.3);
  }
  70% {
    box-shadow: 0 0 0 8px rgba(var(--el-color-primary-rgb), 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(var(--el-color-primary-rgb), 0);
  }
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .custom-upload-btn {
    background: rgba(255, 255, 255, 0.04);
    border-color: rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.7);
  }

  .custom-upload-btn:hover {
    background: rgba(var(--el-color-primary-rgb), 0.2);
    border-color: var(--el-color-primary-light-3);
    color: var(--el-color-primary-light-3);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  }

  .custom-upload-btn:active {
    background: rgba(var(--el-color-primary-rgb), 0.25);
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
  }

  .upload-button.is-uploading .custom-upload-btn {
    background: rgba(var(--el-color-primary-rgb), 0.2);
    border-color: var(--el-color-primary-light-3);
    color: var(--el-color-primary-light-3);
  }
}

/* 输入框提示文字样式 */
:deep(.el-textarea__inner::placeholder) {
  color: var(--el-text-color-placeholder);
  font-size: 14px;
}

/* 自定义滚动条 */
:deep(.el-textarea__inner::-webkit-scrollbar) {
  width: 4px;
}

:deep(.el-textarea__inner::-webkit-scrollbar-thumb) {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 2px;
}

:deep(.el-textarea__inner::-webkit-scrollbar-track) {
  background: transparent;
}

/* 适配深色模式 */
@media (prefers-color-scheme: dark) {
  .input-container {
    background: rgba(30, 30, 30, 0.98);
    border-top-color: rgba(255, 255, 255, 0.06);
  }

  :deep(.el-textarea__inner) {
    background-color: rgba(0, 0, 0, 0.2);
    border-color: rgba(255, 255, 255, 0.08);
    color: var(--el-text-color-primary);
  }

  :deep(.el-textarea__inner:focus) {
    background-color: rgba(0, 0, 0, 0.3);
    border-color: var(--el-color-primary);
    box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.15);
  }

  :deep(.el-textarea__inner:hover) {
    background-color: rgba(0, 0, 0, 0.25);
  }

  .upload-button {
    :deep(.el-upload-dragger) {
      background: linear-gradient(to right, 
        rgba(64, 158, 255, 0.1), 
        rgba(64, 158, 255, 0.15)
      );
      border-color: rgba(64, 158, 255, 0.2);

      &:hover {
        background: linear-gradient(to right, 
          rgba(64, 158, 255, 0.15), 
          rgba(64, 158, 255, 0.2)
        );
        border-color: rgba(64, 158, 255, 0.3);
      }
    }
  }
}

/* 输入区域动画 */
.input-container {
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* 响应式调整 */
@media (max-width: 768px) {
  .input-container {
    padding: 12px 16px;
  }

  :deep(.el-textarea__inner) {
    padding: 12px 16px;
    font-size: 14px;
  }

  .send-button {
    padding: 0 20px;
    height: 40px;
    font-size: 14px;
  }

  .button-group {
    gap: 8px;
  }
}

/* 消息内容样式 */
.message {
  display: flex;
  align-items: flex-start;
  margin-bottom: 20px;
  gap: 12px;
  padding: 0 20px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  transition: all 0.3s ease;
  border: 2px solid transparent;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.message-avatar.user {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-color: #818cf8;
}

.message-avatar.assistant {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border-color: #34d399;
}

.message-avatar:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.message-avatar::after {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  border-radius: 50%;
  background: inherit;
  filter: blur(8px);
  opacity: 0;
  z-index: -1;
  transition: opacity 0.3s ease;
}

.message-avatar:hover::after {
  opacity: 0.4;
}

.message-content {
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  position: relative;
  word-wrap: break-word;
  transition: all 0.3s ease;
  white-space: pre-wrap;
}

.user-text,
.assistant-text {
  display: inline-block;
  min-height: 1.6em;
}

.assistant-text.typing {
  color: var(--el-text-color-primary);
}

.cursor {
  display: inline-block;
  width: 2px;
  height: 1em;
  background-color: currentColor;
  margin-left: 1px;
  vertical-align: middle;
  animation: blink 0.8s infinite;
}

@keyframes blink {
  0%,
  100% {
    opacity: 0;
  }
  50% {
    opacity: 1;
  }
}

.message-content.streaming {
  border-right: none;
}

/* 打字机效果 */
.assistant-text {
  opacity: 1;
  transition: opacity 0.1s ease;
}

.assistant-text.typing {
  position: relative;
}

/* 添加打字机声音效果的动画 */
@keyframes typing {
  from {
    opacity: 0.7;
  }
  to {
    opacity: 1;
  }
}

.assistant-text.typing {
  animation: typing 0.15s ease-out;
}

.user .message-content {
  background: #ECF5FF;
  color: #2C3E50;
  border-top-right-radius: 4px;
  margin-right: 8px;
}

.assistant .message-content {
  background: #F0F9EB;
  color: #2C3E50;
  border-top-left-radius: 4px;
  margin-left: 8px;
}

/* 添加小三角 */
.user .message-content::before {
  content: '';
  position: absolute;
  right: -8px;
  top: 0;
  border-left: 8px solid #ECF5FF;
  border-top: 8px solid transparent;
  border-bottom: 8px solid transparent;
}

.assistant .message-content::before {
  content: '';
  position: absolute;
  left: -8px;
  top: 0;
  border-right: 8px solid #F0F9EB;
  border-top: 8px solid transparent;
  border-bottom: 8px solid transparent;
}

/* 消息内容悬停效果 */
.message:hover .message-content {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

/* 优化消息气泡样式 */
.user-text,
.assistant-text {
  position: relative;
  line-height: 1.6;
}

/* 确保复制按钮不会遮挡文字 */
.user-text,
.assistant-text {
  padding-right: 40px;
}

.related-questions {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.related-questions-label {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 8px;
  color: var(--el-color-primary);
  font-size: 13px;
}

.label-icon {
  font-size: 16px;
}

.related-questions-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.related-question-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  padding: 6px 12px;
  border-radius: 6px;
  color: var(--el-color-primary-dark-2);
  background: var(--el-color-primary-light-8);
  transition: all 0.3s ease;
  border: none;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.question-icon {
  font-size: 14px;
  opacity: 0.7;
}

.question-emoji {
  margin-left: 4px;
  font-size: 14px;
}

.related-question-btn:hover {
  color: var(--el-color-primary-dark-2);
  background: var(--el-color-primary-light-7);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.related-question-btn:active {
  transform: translateY(0);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

@media (prefers-color-scheme: dark) {
  .related-questions {
    background: rgba(64, 158, 255, 0.08);
    border-color: rgba(64, 158, 255, 0.2);
  }

  .related-questions-label {
    color: var(--el-color-primary-light-3);
  }

  .related-question-btn {
    color: var(--el-color-primary-light-3);
    background: rgba(64, 158, 255, 0.15);
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  }

  .related-question-btn:hover {
    color: var(--el-color-primary-light-5);
    background: rgba(64, 158, 255, 0.25);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  }

  .related-question-btn:active {
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  }
}

.message-wrapper {
  margin-bottom: 20px;
}

.message {
  display: flex;
  align-items: flex-start;
  margin-bottom: 8px;
}

.related-questions {
  margin-left: 44px;
  /* 36px avatar + 8px gap */
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.related-question-btn {
  font-size: 12px;
  padding: 4px 12px;
  border-radius: 16px;
  background-color: var(--el-color-primary-light-9);
  border-color: var(--el-color-primary-light-7);
  color: var(--el-color-primary);
}

.related-question-btn:hover {
  background-color: var(--el-color-primary-light-8);
  border-color: var(--el-color-primary-light-6);
}

@media (prefers-color-scheme: dark) {
  .related-question-btn {
    background-color: rgba(64, 158, 255, 0.1);
    border-color: rgba(64, 158, 255, 0.2);
    color: var(--el-color-primary-light-3);
  }

  .related-question-btn:hover {
    background-color: rgba(64, 158, 255, 0.2);
    border-color: rgba(64, 158, 255, 0.3);
  }
}

.image-upload-container {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.image-preview {
  position: relative;
  margin-right: 8px;
  height: 36px;
  width: 36px;
  border-radius: 4px;
  overflow: hidden;
  border: 2px solid var(--el-color-primary);
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-image {
  position: absolute;
  top: -6px;
  right: -6px;
  padding: 4px;
  background: var(--el-color-danger);
  color: white;
  border: none;
  transform: scale(0.8);
}

.remove-image:hover {
  transform: scale(0.9);
  background: var(--el-color-danger-dark-2);
}

.button-group {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.action-button {
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.action-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.action-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.float-button {
  position: fixed;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 99;
}

.drawer-trigger-button {
  width: 48px;
  height: 48px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.drawer-trigger-button:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.drawer-trigger-button:active {
  transform: scale(0.95);
}

.right-sidebar {
  position: fixed;
  right: 0;
  top: 0;
  height: 100vh;
  width: 300px;
  background: #fff;
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.15);
  transition: transform 0.3s ease-in-out, opacity 0.3s ease;
  transform: translateX(0);
  opacity: 1;
}

.right-sidebar.hidden {
  transform: translateX(100%);
  opacity: 0;
}

.sidebar-content {
  padding: 20px;
  animation: fadeIn 0.4s ease-in-out;
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: calc(100vh - 40px);
  overflow-y: auto;
}

.sidebar-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  transition: all 0.2s ease;
  transform-origin: left;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sidebar-item-title {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 4px;
}

.sidebar-item-content {
  font-size: 14px;
  color: #5c6c7c;
  line-height: 1.5;
}

.sidebar-divider {
  height: 1px;
  background: linear-gradient(to right, rgba(0,0,0,0.05), rgba(0,0,0,0.1), rgba(0,0,0,0.05));
  margin: 8px 0;
}

.sidebar-content::-webkit-scrollbar {
  width: 6px;
}

.sidebar-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.sidebar-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.sidebar-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.drawer-header {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  background: linear-gradient(to right, #ffffff, #f8f9fa);
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 10;
  backdrop-filter: blur(8px);
  
  h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    color: #2c3e50;
    letter-spacing: 0.3px;
    
    /* 添加微妙的文字阴影 */
    text-shadow: 1px 1px 1px rgba(255, 255, 255, 0.5);
  }
  
  /* 添加装饰性元素 */
  &::after {
    content: '';
    position: absolute;
    bottom: -1px;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(to right, 
      rgba(66, 153, 225, 0.6), 
      rgba(99, 179, 237, 0.4), 
      rgba(144, 205, 244, 0.2)
    );
  }
  
  /* 操作按钮样式 */
  .header-actions {
    display: flex;
    gap: 12px;
    align-items: center;
    
    button {
      padding: 6px 12px;
      border-radius: 6px;
      border: none;
      background: transparent;
      color: #666;
      transition: all 0.2s ease;
      
      &:hover {
        background: rgba(0, 0, 0, 0.05);
        color: #333;
      }
      
      &:active {
        transform: scale(0.98);
      }
    }
  }
}

.el-icon.drawer-icon {
  font-size: 20px;
  color: #409EFF;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  padding: 8px;
  border-radius: 50%;
  background: rgba(64, 158, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  
  /* 悬停效果 */
  &:hover {
    transform: rotate(90deg) scale(1.1);
    background: rgba(64, 158, 255, 0.15);
    box-shadow: 0 0 12px rgba(64, 158, 255, 0.2);
  }
  
  /* 点击效果 */
  &:active {
    transform: rotate(180deg) scale(0.95);
  }
  
  /* 呼吸光效 */
  &::after {
    content: '';
    position: absolute;
    width: 100%;
    height: 100%;
    border-radius: 50%;
    background: rgba(64, 158, 255, 0.2);
    z-index: -1;
    animation: pulse 2s infinite;
  }
}

/* 呼吸动画 */
@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 0.6;
  }
  50% {
    transform: scale(1.2);
    opacity: 0;
  }
  100% {
    transform: scale(1);
    opacity: 0;
  }
}

/* 添加进入/离开动画 */
.drawer-icon-enter-active,
.drawer-icon-leave-active {
  transition: all 0.3s ease;
}

.drawer-icon-enter-from,
.drawer-icon-leave-to {
  opacity: 0;
  transform: scale(0.5) rotate(-180deg);
}

/* 点击波纹效果 */
.drawer-icon-ripple {
  position: absolute;
  border-radius: 50%;
  background: rgba(64, 158, 255, 0.4);
  transform: scale(0);
  animation: ripple 0.6s linear;
}

@keyframes ripple {
  to {
    transform: scale(2.5);
    opacity: 0;
  }
}

.upload-button {
  margin-right: 8px;
  display: flex;
  align-items: center;
}

.input-area {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 模式说明样式 */
.mode-description {
  padding: 8px 0;
}

.mode-description h4 {
  margin: 0 0 8px 0;
  color: var(--el-text-color-primary);
}

.mode-description ul {
  margin: 0;
  padding-left: 20px;
  color: var(--el-text-color-regular);
}

.mode-description li {
  margin: 4px 0;
  font-size: 13px;
}

.mode-tip {
  margin-top: 8px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
  font-style: italic;
}

/* 通知样式定制 */
:deep(.el-notification) {
  width: 330px;
}

:deep(.el-notification__content) {
  margin: 0;
}
</style>