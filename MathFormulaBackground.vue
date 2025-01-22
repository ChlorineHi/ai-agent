<template>
  <div class="math-background">
    <transition-group name="formula" tag="div">
      <div 
        v-for="formula in visibleFormulas" 
        :key="formula.id"
        class="formula"
        :style="formula.style"
      >
        {{ formula.currentText }}
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

// 数学公式库
const formulas = [
  'E = mc²',
  '∮ E⋅da = Q/ε₀',
  '∇ × B = μ₀J + μ₀ε₀∂E/∂t',
  'eiπ + 1 = 0',
  '∫(1/x) dx = ln|x| + C',
  'F = G(m₁m₂)/r²',
  '∇ × E = -∂B/∂t',
  'ψ(r,t) = ψ(r)e^(-iEt/ℏ)',
  'd/dx[e^x] = e^x',
  'P(A|B) = P(B|A)P(A)/P(B)',
  'Δx·Δp ≥ ℏ/2',
  '∇²ψ + (2m/ℏ²)(E-V)ψ = 0',
  'ds² = -(c·dt)² + dx² + dy² + dz²',
  'R_μν - (R/2)g_μν = 8πGT_μν',
  '∂ψ/∂t = -(ℏ/2m)∇²ψ + Vψ'
]

const visibleFormulas = ref([])
let nextId = 0
let animationInterval

// 生成随机位置和样式
const generateRandomFormula = () => {
  const x = Math.random() * window.innerWidth
  const y = Math.random() * window.innerHeight
  const opacity = 0.05 + Math.random() * 0.25
  const scale = 0.3 + Math.random() * 2.7
  const rotation = Math.random() * 40 - 20
  const text = formulas[Math.floor(Math.random() * formulas.length)]
  const baseSize = 8 + Math.floor(Math.random() * 16)

  return {
    id: nextId++,
    text: text,
    currentText: '',
    currentIndex: 0,
    style: {
      position: 'absolute',
      left: `${x}px`,
      top: `${y}px`,
      opacity: opacity,
      transform: `scale(${scale}) rotate(${rotation}deg)`,
      color: '#000',
      fontSize: `${baseSize}px`,
      fontFamily: 'MathJax_Math, serif',
      pointerEvents: 'none'
    }
  }
}

// 打字机效果
const typeFormula = (formula) => {
  const typeInterval = setInterval(() => {
    if (formula.currentIndex < formula.text.length) {
      formula.currentText = formula.text.substring(0, formula.currentIndex + 1)
      formula.currentIndex++
    } else {
      clearInterval(typeInterval)
      
      // 完成打字后等待一段时间再消失
      setTimeout(() => {
        const index = visibleFormulas.value.findIndex(f => f.id === formula.id)
        if (index !== -1) {
          visibleFormulas.value.splice(index, 1)
        }
      }, 1500 + Math.random() * 1500)
    }
  }, 30 + Math.random() * 50)
}

// 添加新公式
const addFormula = () => {
  const formula = generateRandomFormula()
  visibleFormulas.value.push(formula)
  typeFormula(formula)
}

onMounted(() => {
  animationInterval = setInterval(() => {
    if (visibleFormulas.value.length < 25) { 
      addFormula()
    }
  }, 400 + Math.random() * 800)
})

onUnmounted(() => {
  clearInterval(animationInterval)
})
</script>

<style scoped>
.math-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.formula {
  position: absolute;
  transition: opacity 0.5s ease;
}

.formula-enter-active {
  transition: opacity 0.5s ease;
}

.formula-leave-active {
  transition: opacity 0.8s ease;
}

.formula-enter-from,
.formula-leave-to {
  opacity: 0 !important;
}
</style>
