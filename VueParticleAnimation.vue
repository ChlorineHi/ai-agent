<template>
  <canvas ref="canvas"></canvas>
</template>

<script>
export default {
  mounted() {
    const canvas = this.$refs.canvas;
    const ctx = canvas.getContext('2d');
    canvas.width = this.$el.clientWidth;
    canvas.height = this.$el.clientHeight;

    // 粒子类
    class Particle {
      constructor(x, y) {
        this.x = x;
        this.y = y;
        this.size = Math.random() * 5 + 2;
        this.color = `hsl(${Math.random() * 360}, 100%, 50%)`;
        this.speedX = (Math.random() - 0.5) * 2;
        this.speedY = (Math.random() - 0.5) * 2;
      }
      update() {
        this.x += this.speedX;
        this.y += this.speedY;
        // 边界检测
        if (this.x < 0 || this.x > canvas.width) this.speedX *= -1;
        if (this.y < 0 || this.y > canvas.height) this.speedY *= -1;
      }
      draw() {
        ctx.fillStyle = this.color;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    // 初始化粒子数组
    let particles = [];
    for (let i = 0; i < 100; i++) {
      const x = Math.random() * canvas.width;
      const y = Math.random() * canvas.height;
      particles.push(new Particle(x, y));
    }

    // 动画循环
    function animate() {
      requestAnimationFrame(animate);
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      particles.forEach(particle => {
        particle.update();
        particle.draw();
      });
    }
    animate();

    // 鼠标交互
    window.addEventListener('mousemove', (e) => {
      particles.forEach(particle => {
        const dx = particle.x - e.x;
        const dy = particle.y - e.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        if (distance < 100) {
          particle.speedX += dx * 0.01;
          particle.speedY += dy * 0.01;
          particle.size = Math.max(2, particle.size - 0.1);
        }
      });
    });

    // 点击效果
    window.addEventListener('click', (e) => {
      particles.forEach(particle => {
        const dx = particle.x - e.x;
        const dy = particle.y - e.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        if (distance < 50) {
          particle.speedX += (Math.random() - 0.5) * 5;
          particle.speedY += (Math.random() - 0.5) * 5;
          particle.size += 5;
        }
      });
    });
  }
};
</script>

<style scoped>
canvas {
  display: block;
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  overflow: hidden;
}
</style>
