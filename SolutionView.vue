<template>
  <div class="solution-container">
    <div class="layout-wrapper">
      <!-- 侧边栏 -->
      <div class="sidebar" :class="{ collapsed: isSidebarCollapsed }">
        <h3 class="sidebar-title">智能解决方案</h3>
        <div class="langchain-tag">
          <el-tag type="success" effect="dark">
            <i class="el-icon-connection"></i>
            Powered by LangChain
          </el-tag>
        </div>
        <div class="mb-3">
          <el-button type="primary" class="new-chat-btn" @click="newChat">
            <i class="el-icon-plus"></i> 新对话
          </el-button>
        </div>
        <div class="chat-history">
          <div v-for="(chat, index) in chatHistory" 
               :key="index"
               class="history-item"
               :class="{ active: currentChatIndex === index }"
               @click="switchChat(index)">
            <i class="el-icon-chat-dot-round"></i>
            {{ chat.title || '新对话' }}
            <i class="el-icon-delete delete-btn" 
               @click.stop="deleteChat(index)" 
               v-if="chatHistory.length > 1">
            </i>
          </div>
        </div>
        <div class="help-section">
          <el-button link type="info" class="help-btn" @click="showHelpDialog = true">
            <el-icon><QuestionFilled /></el-icon>
            什么是智解？
          </el-button>
        </div>
        <div class="sidebar-toggle" @click="toggleSidebar" :class="{ collapsed: isSidebarCollapsed }">
          <i class="el-icon-arrow-left"></i>
        </div>
      </div>

      <!-- 主聊天区域 -->
      <div class="main-content">
        <!-- 聊天消息区域 -->
        <div class="chat-container" ref="chatContainer">
          <div v-for="(message, index) in messages" 
               :key="index"
               :class="['message', message.role === 'user' ? 'user-message' : 'assistant-message']"
               :data-time="message.timestamp || formatTime(new Date())">
            <div class="message-avatar">
              <el-avatar 
                :size="40"
                :class="[
                  'custom-avatar',
                  message.role === 'user' ? 'user-avatar' : 'assistant-avatar'
                ]"
              >
                <template v-if="message.role === 'user'">
                  <i class="el-icon-user-solid"></i>
                </template>
                <template v-else>
                  <i class="el-icon-monitor"></i>
                </template>
              </el-avatar>
            </div>
            <div class="message-content">{{ message.content }}</div>
          </div>
        </div>

        <!-- 小动物装饰 -->
        <div class="animals-container">
          <ChatAnimals @update:mode="handleModeChange" />
        </div>

        <!-- 输入区域 -->
        <div class="input-area">
          <div class="input-toolbar">
            <el-tooltip content="上传图片" placement="top">
              <el-button class="toolbar-btn" circle>
                <i class="el-icon-picture-outline"></i>
              </el-button>
            </el-tooltip>
            <el-tooltip content="表情符号" placement="top">
              <el-button class="toolbar-btn" circle>
                <i class="el-icon-magic-stick"></i>
              </el-button>
            </el-tooltip>
          </div>
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="3"
            class="custom-input"
            placeholder="请描述您的问题..."
            @keydown.enter.prevent="sendMessage"
          />
          <el-button type="primary" class="send-btn" @click="sendMessage" :loading="loading">
            <i class="el-icon-s-promotion"></i>
            <span class="send-text">发送</span>
          </el-button>
        </div>
      </div>
    </div>

    <!-- 加载提示 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <div class="loading-text">正在思考...</div>
    </div>

    <!-- 添加帮助对话框 -->
    <el-dialog
      v-model="showHelpDialog"
      title="智能解决方案说明"
      width="50%"
      :close-on-click-modal="true"
      destroy-on-close
    >
      <div class="help-content">
        <h4>什么是(智解)智能解决方案？</h4>
        <p>智能解决方案是一个基于人工智能的智能助手系统，它能够：</p>
        <ul>
          <li>使用langchain建构框架理解您的问题并提供专业解答的agent</li>
          <li>支持多种对话模式，满足不同场景需求</li>
          <li>提供持续对话能力，深入理解上下文</li>
          <li>整合多种知识源，对答案进行优化，给出全面的解决方案</li>
        </ul>
        
        <h4>主要特点</h4>
        <div class="feature-grid">
          <div class="feature-item">
            <el-icon class="feature-icon"><ChatDotRound /></el-icon>
            <h5>智能对话</h5>
            <p>自然语言交互，精准理解需求</p>
          </div>
          <div class="feature-item">
            <el-icon class="feature-icon"><Connection /></el-icon>
            <h5>多模式支持</h5>
            <p>支持轻松、标准、专业、专家四种模式</p>
          </div>
          <div class="feature-item">
            <el-icon class="feature-icon"><DataAnalysis /></el-icon>
            <h5>知识整合</h5>
            <p>多源数据支持，答案更全面</p>
          </div>
          <div class="feature-item">
            <el-icon class="feature-icon"><Lightning /></el-icon>
            <h5>实时响应</h5>
            <p>快速准确的问题解答</p>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ChatAnimals from '../components/ChatAnimals.vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { QuestionFilled, ChatDotRound, Connection, DataAnalysis, Lightning } from '@element-plus/icons-vue'

const inputMessage = ref('')
const loading = ref(false)
const messages = ref([])
const chatHistory = ref([
  { title: '默认对话', messages: [] }
])
const currentChatIndex = ref(0)
const chatContainer = ref(null)
const currentMode = ref('normal')
const isSidebarCollapsed = ref(false)
const showHelpDialog = ref(false)

const formatTime = (date) => {
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  return `${hours}:${minutes}`
}

const sendMessage = async () => {
  if (!inputMessage.value.trim()) return
  
  const timestamp = formatTime(new Date())
  
  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: inputMessage.value,
    timestamp
  })
  
  loading.value = true
  try {
    // 这里添加实际的API调用逻辑，传入当前模式
    const response = `这是一个${getModeLabel(currentMode.value)}的模拟回复`
    
    // 添加助手回复
    messages.value.push({
      role: 'assistant',
      content: response,
      timestamp: formatTime(new Date())
    })
  } catch (error) {
    console.error('Error:', error)
  } finally {
    loading.value = false
    inputMessage.value = ''
    scrollToBottom()
  }
}

const scrollToBottom = () => {
  setTimeout(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  }, 100)
}

const newChat = () => {
  chatHistory.value.push({
    title: '新对话',
    messages: []
  })
  currentChatIndex.value = chatHistory.value.length - 1
  messages.value = []
}

const switchChat = (index) => {
  currentChatIndex.value = index
  messages.value = chatHistory.value[index].messages
}

const handleModeChange = (mode) => {
  currentMode.value = mode
  // 可以在这里添加提示
  ElMessage({
    message: `已切换至${getModeLabel(mode)}`,
    type: 'success'
  })
}

const getModeLabel = (mode) => {
  const modeMap = {
    casual: '轻松模式',
    normal: '标准模式',
    professional: '专业模式',
    expert: '专家模式'
  }
  return modeMap[mode] || '标准模式'
}

const deleteChat = (index) => {
  ElMessageBox.confirm(
    '确定要删除这个对话吗？',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(() => {
      chatHistory.value.splice(index, 1)
      if (currentChatIndex.value === index) {
        currentChatIndex.value = Math.max(0, index - 1)
        messages.value = chatHistory.value[currentChatIndex.value].messages
      } else if (currentChatIndex.value > index) {
        currentChatIndex.value--
      }
      ElMessage({
        type: 'success',
        message: '删除成功'
      })
    })
    .catch(() => {
      // 用户取消删除
    })
}

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

onMounted(() => {
  scrollToBottom()
})
</script>

<style scoped>
.solution-container {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.layout-wrapper {
  display: flex;
  height: 100vh;
}

/* 侧边栏样式 */
.sidebar {
  width: 260px;
  background-color: #fff;
  border-right: 1px solid #e6e6e6;
  padding: 20px;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  position: relative;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
}

.sidebar-title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 20px;
  text-align: center;
  color: var(--el-color-primary);
  position: relative;
  padding-bottom: 10px;
}

.sidebar-title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 40px;
  height: 3px;
  background: linear-gradient(90deg, var(--el-color-primary), var(--el-color-primary-light-3));
  border-radius: 2px;
}

.langchain-tag {
  margin-bottom: 20px;
  text-align: center;
}

.new-chat-btn {
  width: 100%;
  margin-bottom: 20px;
  height: 44px;
  border-radius: 22px;
  font-size: 15px;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, var(--el-color-primary), var(--el-color-primary-light-3));
  border: none;
  box-shadow: 0 2px 6px rgba(var(--el-color-primary-rgb), 0.2);
}

.new-chat-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(var(--el-color-primary-rgb), 0.3);
}

.chat-history {
  flex: 1;
  overflow-y: auto;
  padding-right: 10px;
  margin-right: -10px;
}

.history-item {
  padding: 12px 15px;
  margin: 8px 0;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
  border: 1px solid transparent;
  position: relative;
}

.history-item:hover {
  background-color: var(--el-color-primary-light-9);
  transform: translateX(5px);
}

.history-item.active {
  background-color: var(--el-color-primary-light-9);
  border: 1px solid var(--el-color-primary-light-5);
  box-shadow: 0 2px 8px rgba(var(--el-color-primary-rgb), 0.1);
}

.history-item i {
  font-size: 18px;
  color: var(--el-color-primary);
  transition: transform 0.3s ease;
}

.history-item:hover i {
  transform: scale(1.2);
}

.history-item::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: -4px;
  width: 100%;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--el-color-primary-light-7), transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.history-item:hover::after {
  opacity: 1;
}

/* 添加删除按钮 */
.history-item .delete-btn {
  position: absolute;
  right: 10px;
  opacity: 0;
  transition: opacity 0.3s ease;
  color: var(--el-color-danger);
  font-size: 16px;
}

.history-item:hover .delete-btn {
  opacity: 1;
}

/* 添加收起侧边栏的按钮 */
.sidebar-toggle {
  position: absolute;
  right: -12px;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  background: #fff;
  border: 1px solid #e6e6e6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 10;
  transition: all 0.3s ease;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
}

.sidebar-toggle:hover {
  background: var(--el-color-primary-light-9);
  transform: translateY(-50%) scale(1.1);
}

.sidebar-toggle i {
  font-size: 12px;
  color: var(--el-color-primary);
  transition: transform 0.3s ease;
}

.sidebar.collapsed {
  width: 0;
  padding: 0;
  overflow: hidden;
}

.sidebar-toggle.collapsed i {
  transform: rotate(180deg);
}

/* 主内容区域 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #fff;
}

/* 聊天区域 */
.chat-container {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.message {
  display: flex;
  align-items: flex-start;
  margin: 20px 0;
  position: relative;
  animation: messageSlideIn 0.3s ease;
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-avatar {
  margin: 0 12px;
  position: relative;
}

.message-avatar .el-avatar {
  border: 2px solid #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.message-avatar .el-avatar:hover {
  transform: scale(1.1);
}

.message-content {
  padding: 12px 16px;
  border-radius: 15px;
  max-width: 70%;
  line-height: 1.6;
  position: relative;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease;
}

.message-content:hover {
  transform: translateY(-2px);
}

/* 用户消息样式 */
.user-message {
  flex-direction: row-reverse;
}

.user-message .message-content {
  background: linear-gradient(135deg, var(--el-color-primary) 0%, var(--el-color-primary-light-3) 100%);
  color: #fff;
  margin-right: 8px;
  border-top-right-radius: 4px;
}

.user-message .message-content::after {
  content: '';
  position: absolute;
  right: -8px;
  top: 14px;
  border-style: solid;
  border-width: 8px 0 8px 8px;
  border-color: transparent transparent transparent var(--el-color-primary);
}

/* 助手消息样式 */
.assistant-message .message-content {
  background: #fff;
  margin-left: 8px;
  border-top-left-radius: 4px;
  border: 1px solid #ebeef5;
}

.assistant-message .message-content::before {
  content: '';
  position: absolute;
  left: -8px;
  top: 14px;
  border-style: solid;
  border-width: 8px 8px 8px 0;
  border-color: transparent #fff transparent transparent;
}

/* 在线状态指示器 */
.message-avatar::after {
  content: '';
  position: absolute;
  bottom: 0;
  right: 0;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 1;
}

.user-message .message-avatar::after {
  background: linear-gradient(135deg, var(--el-color-success) 0%, var(--el-color-success-light-3) 100%);
}

.assistant-message .message-avatar::after {
  background: linear-gradient(135deg, var(--el-color-primary) 0%, var(--el-color-primary-light-3) 100%);
}

/* 时间戳样式 */
.message::after {
  content: attr(data-time);
  position: absolute;
  bottom: -18px;
  font-size: 12px;
  color: #909399;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.message:hover::after {
  opacity: 1;
}

.user-message::after {
  right: 50px;
}

.assistant-message::after {
  left: 50px;
}

/* 输入区域 */
.input-area {
  padding: 20px;
  border-top: 1px solid #e6e6e6;
  background-color: #fff;
}

.input-toolbar {
  margin-bottom: 10px;
  display: flex;
  gap: 8px;
}

.custom-input {
  margin-bottom: 10px;
}

.send-btn {
  width: 100px;
  height: 40px;
  border-radius: 20px;
}

/* 加载提示 */
.loading-overlay {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: #fff;
  padding: 20px 40px;
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.loading-spinner {
  width: 30px;
  height: 30px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid var(--el-color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 滚动条样式 */
.chat-container::-webkit-scrollbar,
.chat-history::-webkit-scrollbar {
  width: 6px;
}

.chat-container::-webkit-scrollbar-thumb,
.chat-history::-webkit-scrollbar-thumb {
  background-color: #ddd;
  border-radius: 3px;
}

.chat-container::-webkit-scrollbar-track,
.chat-history::-webkit-scrollbar-track {
  background-color: transparent;
}

/* 头像样式优化 */
.custom-avatar {
  background: #fff !important;
  position: relative;
  overflow: visible !important;
}

.custom-avatar i {
  font-size: 20px;
  line-height: 40px;
}

.user-avatar {
  background: linear-gradient(135deg, var(--el-color-primary-light-5) 0%, var(--el-color-primary) 100%) !important;
  box-shadow: 0 2px 12px rgba(var(--el-color-primary-rgb), 0.2);
}

.user-avatar i {
  color: #fff;
}

.assistant-avatar {
  background: linear-gradient(135deg, #f0f9ff 0%, #e6f4ff 100%) !important;
  border: 2px solid var(--el-color-primary-light-5);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.assistant-avatar i {
  color: var(--el-color-primary);
  font-size: 22px;
}

/* 小动物容器样式 */
.animals-container {
  position: relative;
  height: 0;
  pointer-events: auto;
  z-index: 10;
}

/* 帮助按钮样式 */
.help-section {
  margin-top: auto;
  padding-top: 20px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.help-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  justify-content: center;
  padding: 12px;
  color: var(--el-text-color-secondary);
  transition: all 0.3s ease;
}

.help-btn:hover {
  color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
}

.help-btn .el-icon {
  font-size: 16px;
}

/* 帮助内容样式 */
.help-content {
  padding: 20px;
}

.help-content h4 {
  color: var(--el-color-primary);
  margin-bottom: 16px;
  font-size: 18px;
}

.help-content p {
  color: var(--el-text-color-regular);
  line-height: 1.6;
  margin-bottom: 16px;
}

.help-content ul {
  margin-bottom: 24px;
  padding-left: 20px;
}

.help-content li {
  color: var(--el-text-color-regular);
  line-height: 1.8;
  margin-bottom: 8px;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-top: 20px;
}

.feature-item {
  padding: 20px;
  border-radius: 8px;
  background-color: var(--el-color-primary-light-9);
  text-align: center;
  transition: all 0.3s ease;
}

.feature-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  font-size: 24px;
  color: var(--el-color-primary);
  margin-bottom: 12px;
}

.feature-item h5 {
  color: var(--el-color-primary);
  margin-bottom: 8px;
  font-size: 16px;
}

.feature-item p {
  color: var(--el-text-color-regular);
  font-size: 14px;
  margin: 0;
}

:deep(.el-dialog) {
  border-radius: 8px;
}

:deep(.el-dialog__header) {
  margin-right: 0;
  padding: 20px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

:deep(.el-dialog__body) {
  padding: 0;
}
</style>
