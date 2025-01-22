<template>
  <div class="dog-container" :class="{ 'is-typing': isTyping }">
    <div class="interaction-hint" v-if="!showCloud">
      <el-tooltip
        content="点击小狗来选择回答模式"
        placement="top"
        :show-after="200"
        effect="light"
      >
        <div class="hint-icon">
          <el-icon><Pointer /></el-icon>
        </div>
      </el-tooltip>
    </div>
    <div class="model-selector" v-if="showCloud" @mouseleave="handleMouseLeave">
      <div class="selector-header">
        <div class="selector-title">选择回答模式</div>
        <div class="selector-subtitle">选择最适合你的回答方式</div>
      </div>
      <div class="selector-options">
        <div class="option" @click="selectMode('simple')" :class="{ 'option-hover': hoverIndex === 0 }" @mouseenter="hoverIndex = 0" @mouseleave="hoverIndex = -1">
          <div class="option-icon">
            <el-icon><ChatRound /></el-icon>
          </div>
          <div class="option-content">
            <div class="option-title">简单模式</div>
            <div class="option-desc">通俗易懂的解释</div>
          </div>
          <div class="option-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
        <div class="option" @click="selectMode('complex')" :class="{ 'option-hover': hoverIndex === 1 }" @mouseenter="hoverIndex = 1" @mouseleave="hoverIndex = -1">
          <div class="option-icon">
            <el-icon><ChatLineRound /></el-icon>
          </div>
          <div class="option-content">
            <div class="option-title">复杂模式</div>
            <div class="option-desc">详细的分析和示例</div>
          </div>
          <div class="option-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
        <div class="option" @click="selectMode('professional')" :class="{ 'option-hover': hoverIndex === 2 }" @mouseenter="hoverIndex = 2" @mouseleave="hoverIndex = -1">
          <div class="option-icon">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <div class="option-content">
            <div class="option-title">专业模式</div>
            <div class="option-desc">技术性的专业解答</div>
          </div>
          <div class="option-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
      </div>
    </div>
    <div class="dog" @click="handleDogClick">
      <div class="dog-ears">
        <div class="dog-ear-left"></div>
        <div class="dog-ear-right"></div>
      </div>
      <div class="dog-face">
        <div class="dog-eyes">
          <div class="dog-eye-left"></div>
          <div class="dog-eye-right"></div>
        </div>
        <div class="dog-nose"></div>
        <div class="dog-mouth"></div>
      </div>
      <div class="dog-body">
        <div class="dog-chest"></div>
        <div class="dog-paws">
          <div class="paw-left"></div>
          <div class="paw-right"></div>
        </div>
      </div>
      <div class="dog-tail"></div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, ref, defineEmits } from 'vue'
import { Pointer, ChatRound, ChatLineRound, ChatDotRound, ArrowRight } from '@element-plus/icons-vue'
import { ElTooltip, ElIcon } from 'element-plus'

const emit = defineEmits(['modeSelect'])
const showCloud = ref(false)
const hoverIndex = ref(-1)
let hideTimeout = null

const handleDogClick = () => {
  if (hideTimeout) {
    clearTimeout(hideTimeout)
  }
  showCloud.value = true
}

const handleMouseLeave = () => {
  hideTimeout = setTimeout(() => {
    showCloud.value = false
  }, 500)
}

const selectMode = (mode) => {
  emit('modeSelect', mode)
  showCloud.value = false
}

defineProps({
  isTyping: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
/* 模型选择器样式 */
.model-selector {
  position: absolute;
  top: -180px;
  right: -20px;
  width: 280px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  z-index: 10;
  overflow: hidden;
  animation: slide-in 0.3s ease-out;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.selector-header {
  padding: 16px;
  background: linear-gradient(135deg, #f0f2f5 0%, #e6e8eb 100%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.selector-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 4px;
}

.selector-subtitle {
  font-size: 12px;
  color: #666;
}

.selector-options {
  padding: 8px;
}

.option {
  display: flex;
  align-items: center;
  padding: 12px;
  margin: 4px 0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  background: #fff;
}

.option-hover {
  background: #f5f7fa;
  transform: translateX(4px);
}

.option-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, #e6f7ff 0%, #b3e0ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  color: #0089ff;
  transition: all 0.2s ease;
}

.option-hover .option-icon {
  background: linear-gradient(135deg, #1890ff 0%, #0089ff 100%);
  color: white;
}

.option-content {
  flex: 1;
}

.option-title {
  font-size: 14px;
  font-weight: 500;
  color: #1a1a1a;
  margin-bottom: 2px;
}

.option-desc {
  font-size: 12px;
  color: #666;
}

.option-arrow {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  opacity: 0;
  transform: translateX(-10px);
  transition: all 0.2s ease;
}

.option-hover .option-arrow {
  opacity: 1;
  transform: translateX(0);
}

@keyframes slide-in {
  0% {
    transform: translateY(10px) scale(0.95);
    opacity: 0;
  }
  100% {
    transform: translateY(0) scale(1);
    opacity: 1;
  }
}

/* 狗狗动画样式 */
.dog-container {
  position: absolute;
  top: -65px;
  right: 50px;
  width: 100px;
  height: 60px;
  z-index: 1;
  transform: rotate(0deg);
  pointer-events: auto;
  cursor: pointer;
}

.dog {
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 0.1s ease;
}

.dog:active {
  transform: scale(0.95);
}

/* 身体样式 - 躺着的姿势 */
.dog-body {
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 30px;
  background: #8B4513;
  border-radius: 30px;
  z-index: 1;
}

.dog-chest {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 50px;
  height: 20px;
  background: #D2691E;
  border-radius: 25px;
}

/* 头部样式 - 侧躺 */
.dog-face {
  position: absolute;
  bottom: 15px;
  left: 15px;
  width: 35px;
  height: 30px;
  background: #8B4513;
  border-radius: 18px;
  transform: rotate(0deg);
}

/* 耳朵样式 - 适应侧躺 */
.dog-ears {
  position: absolute;
  top: 5px;
  left: 50%;
  transform: translateX(-50%);
  width: 40px;
  height: 15px;
  display: flex;
  justify-content: space-between;
}

.dog-ear-left,
.dog-ear-right {
  width: 15px;
  height: 18px;
  background: #8B4513;
  border-radius: 50% 50% 0 0;
  transform-origin: bottom center;
}

.dog-ear-left {
  transform: rotate(-15deg) skewX(5deg);
}

.dog-ear-right {
  transform: rotate(15deg) skewX(-5deg);
}

/* 眼睛样式 - 闭着的样子 */
.dog-eyes {
  position: absolute;
  top: 12px;
  left: 50%;
  transform: translateX(-50%);
  width: 25px;
  height: 6px;
  display: flex;
  justify-content: space-between;
}

.dog-eye-left,
.dog-eye-right {
  width: 8px;
  height: 2px;
  background: #000000;
  border-radius: 2px;
  position: relative;
}

/* 鼻子样式 */
.dog-nose {
  position: absolute;
  bottom: 15px;
  left: 50%;
  transform: translateX(-50%);
  width: 8px;
  height: 6px;
  background: #000000;
  border-radius: 50%;
}

/* 嘴巴样式 - 微笑 */
.dog-mouth {
  position: absolute;
  bottom: 8px;
  left: 50%;
  transform: translateX(-50%);
  width: 12px;
  height: 4px;
  border: 2px solid #000000;
  border-radius: 0 0 50% 50%;
  border-top: none;
}

/* 爪子样式 - 躺着 */
.dog-paws {
  position: absolute;
  bottom: 5px;
  right: 10px;
  width: 30px;
  display: flex;
  justify-content: space-between;
  transform: rotate(-10deg);
}

.paw-left,
.paw-right {
  width: 10px;
  height: 15px;
  background: #8B4513;
  border-radius: 5px;
  transform-origin: top center;
}

.paw-left {
  transform: rotate(-5deg);
}

.paw-right {
  transform: rotate(5deg);
}

/* 尾巴样式 - 躺着摇 */
.dog-tail {
  position: absolute;
  bottom: 15px;
  right: 0;
  width: 25px;
  height: 8px;
  background: #8B4513;
  border-radius: 4px;
  transform-origin: right center;
  animation: tail-wag-lying 2s infinite ease-in-out;
}

@keyframes tail-wag-lying {
  0%, 100% { transform: rotate(0deg); }
  50% { transform: rotate(-15deg); }
}

/* 输入时的动画效果 */
.is-typing .dog-ear-left {
  animation: ear-twitch-lying 1s infinite alternate;
}

.is-typing .dog-ear-right {
  animation: ear-twitch-lying 1s infinite alternate-reverse;
}

@keyframes ear-twitch-lying {
  0% { transform: rotate(-15deg) skewX(5deg); }
  100% { transform: rotate(-5deg) skewX(5deg); }
}

.is-typing .dog-tail {
  animation: tail-wag-lying-fast 0.5s infinite ease-in-out;
}

@keyframes tail-wag-lying-fast {
  0%, 100% { transform: rotate(0deg); }
  50% { transform: rotate(-25deg); }
}

.is-typing .paw-left,
.is-typing .paw-right {
  animation: paw-twitch 0.5s infinite alternate;
}

@keyframes paw-twitch {
  0% { transform: rotate(-5deg); }
  100% { transform: rotate(5deg); }
}

/* 交互提示样式 */
.interaction-hint {
  position: absolute;
  top: -20px;
  right: -15px;
  z-index: 11;
  animation: bounce 2s infinite;
}

.hint-icon {
  width: 24px;
  height: 24px;
  background: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  color: #409EFF;
  cursor: pointer;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .model-selector {
    background: #1a1a1a;
    border-color: rgba(255, 255, 255, 0.1);
  }

  .selector-header {
    background: linear-gradient(135deg, #2a2a2a 0%, #222 100%);
    border-bottom-color: rgba(255, 255, 255, 0.1);
  }

  .selector-title {
    color: #fff;
  }

  .selector-subtitle {
    color: #999;
  }

  .option {
    background: #1a1a1a;
  }

  .option-hover {
    background: #2a2a2a;
  }

  .option-icon {
    background: linear-gradient(135deg, #003a66 0%, #001f33 100%);
    color: #40a9ff;
  }

  .option-hover .option-icon {
    background: linear-gradient(135deg, #40a9ff 0%, #1890ff 100%);
    color: white;
  }

  .option-title {
    color: #fff;
  }

  .option-desc {
    color: #999;
  }

  .option-arrow {
    color: #666;
  }

  .dog-face,
  .dog-tail,
  .dog-body,
  .dog-ear-left,
  .dog-ear-right,
  .paw-left,
  .paw-right {
    filter: brightness(0.8);
  }
  .hint-icon {
    background: #1a1a1a;
    color: #79bbff;
  }
}
</style>
