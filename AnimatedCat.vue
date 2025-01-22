<template>
  <div class="cat-container" :class="{ 'is-typing': isTyping }">
    <div class="cat">
      <div class="cat-ears">
        <div class="cat-ear-left"></div>
        <div class="cat-ear-right"></div>
      </div>
      <div class="cat-face">
        <div class="cat-eyes">
          <div class="cat-eye-left"></div>
          <div class="cat-eye-right"></div>
        </div>
        <div class="cat-nose"></div>
        <div class="cat-whiskers">
          <div class="whiskers-left">
            <div class="whisker"></div>
            <div class="whisker"></div>
            <div class="whisker"></div>
          </div>
          <div class="whiskers-right">
            <div class="whisker"></div>
            <div class="whisker"></div>
            <div class="whisker"></div>
          </div>
        </div>
      </div>
      <div class="cat-body">
        <div class="cat-chest"></div>
        <div class="cat-paws">
          <div class="paw-left"></div>
          <div class="paw-right"></div>
        </div>
      </div>
      <div class="cat-tail"></div>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'

defineProps({
  isTyping: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
/* 猫咪动画样式 */
.cat-container {
  position: absolute;
  top: -85px;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 85px;
  pointer-events: none;
  z-index: 1;
}

.cat {
  position: relative;
  width: 100%;
  height: 100%;
}

/* 尾巴样式 */
.cat-tail {
  position: absolute;
  bottom: 15px;
  right: -8px;
  width: 30px;
  height: 6px;
  background: #4a4a4a;
  border-radius: 3px;
  transform-origin: left center;
  transform: rotate(-20deg);
  animation: tail-wave 3s infinite ease-in-out;
}

.is-typing .cat-tail {
  animation: tail-wave-fast 1s infinite ease-in-out;
}

@keyframes tail-wave {
  0%, 100% { transform: rotate(-20deg); }
  50% { transform: rotate(-10deg); }
}

@keyframes tail-wave-fast {
  0%, 100% { transform: rotate(-25deg); }
  50% { transform: rotate(-5deg); }
}

/* 耳朵样式 */
.cat-ears {
  position: absolute;
  top: 15px;
  left: 50%;
  transform: translateX(-50%);
  width: 36px;
  height: 15px;
  display: flex;
  justify-content: space-between;
}

.cat-ear-left,
.cat-ear-right {
  width: 0;
  height: 0;
  border-left: 8px solid transparent;
  border-right: 8px solid transparent;
  border-bottom: 15px solid #4a4a4a;
  transition: transform 0.3s ease;
}

/* 脸部样式 */
.cat-face {
  position: absolute;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  width: 38px;
  height: 28px;
  background: #4a4a4a;
  border-radius: 19px 19px 15px 15px;
}

/* 眼睛样式 */
.cat-eyes {
  position: absolute;
  top: 8px;
  left: 50%;
  transform: translateX(-50%);
  width: 28px;
  height: 8px;
  display: flex;
  justify-content: space-between;
}

.cat-eye-left,
.cat-eye-right {
  width: 8px;
  height: 8px;
  background: #ffffff;
  border-radius: 50%;
  position: relative;
  transition: height 0.2s ease;
}

.cat-eye-left::after,
.cat-eye-right::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 4px;
  height: 4px;
  background: #000000;
  border-radius: 50%;
  transition: all 0.2s ease;
}

/* 鼻子样式 */
.cat-nose {
  position: absolute;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%);
  width: 6px;
  height: 4px;
  background: #ff9999;
  border-radius: 3px;
  animation: nose-wiggle 3s infinite;
}

@keyframes nose-wiggle {
  0%, 100% { transform: translateX(-50%) scale(1); }
  50% { transform: translateX(-50%) scale(1.1); }
}

/* 胡须样式 */
.cat-whiskers {
  position: absolute;
  bottom: 8px;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  display: flex;
  justify-content: space-between;
  padding: 0 2px;
}

.whiskers-left,
.whiskers-right {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.whisker {
  width: 15px;
  height: 1px;
  background: rgba(255, 255, 255, 0.6);
  position: relative;
}

.whiskers-left .whisker {
  transform-origin: right center;
  transform: rotate(5deg);
}

.whiskers-right .whisker {
  transform-origin: left center;
  transform: rotate(-5deg);
}

/* 身体样式 */
.cat-body {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 45px;
  height: 35px;
  background: #4a4a4a;
  border-radius: 20px 20px 15px 15px;
  z-index: -1;
}

.cat-chest {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 30px;
  height: 25px;
  background: #666666;
  border-radius: 15px 15px 10px 10px;
}

.cat-paws {
  position: absolute;
  bottom: -5px;
  left: 50%;
  transform: translateX(-50%);
  width: 35px;
  display: flex;
  justify-content: space-between;
}

.paw-left,
.paw-right {
  width: 12px;
  height: 8px;
  background: #4a4a4a;
  border-radius: 6px;
  animation: paw-wiggle 3s infinite ease-in-out;
}

@keyframes paw-wiggle {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-2px); }
}

.is-typing .paw-left,
.is-typing .paw-right {
  animation: paw-typing 1s infinite ease-in-out;
}

@keyframes paw-typing {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

/* 输入时的动画效果 */
.is-typing .cat-ear-left {
  transform: rotate(-15deg) translateY(-2px);
}

.is-typing .cat-ear-right {
  transform: rotate(15deg) translateY(-2px);
}

.is-typing .cat-eye-left,
.is-typing .cat-eye-right {
  height: 7px;
  animation: eye-squeeze 0.5s infinite;
}

.is-typing .whiskers-left .whisker {
  animation: whisker-left-wave 1s infinite;
}

.is-typing .whiskers-right .whisker {
  animation: whisker-right-wave 1s infinite;
}

@keyframes eye-squeeze {
  0%, 100% { height: 7px; }
  50% { height: 6px; }
}

@keyframes whisker-left-wave {
  0%, 100% { transform: rotate(5deg); }
  50% { transform: rotate(10deg); }
}

@keyframes whisker-right-wave {
  0%, 100% { transform: rotate(-5deg); }
  50% { transform: rotate(-10deg); }
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .cat-ear-left,
  .cat-ear-right {
    border-bottom-color: #666666;
  }

  .cat-face,
  .cat-tail,
  .cat-body {
    background: #666666;
  }

  .whisker {
    background: rgba(255, 255, 255, 0.4);
  }
}
</style>
