<template>
  <footer class="footer-container">
    <div class="footer-inner">
      <div class="top-row">
        <h2 class="logo">FUTURE<span class="highlight">SHOW</span></h2>
        <nav class="nav-links">
          <nav class="nav-links">
            <a href="#" class="link-item">实验室</a>
            <a href="https://github.com/dashboard" class="link-item">案例展示</a>
            <a href="#" class="link-item">技术文档</a>
            <a href="https://github.com/ForMeetY/weatherShow" class="link-item"
              >联系我们</a
            >
          </nav>
        </nav>
      </div>

      <div class="bottom-meta">
        <span>© 2026 FutureShow. All Rights Reserved.</span>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.footer-container {
  background: #0a0b10;
  border-top: 1px solid #1e293b;
  padding: 20px 24px;
  margin-top: 60px;
  color: #94a3b8;
}

.footer-inner {
  max-width: 1024px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 12px; /* 间距大幅压缩 */
}

.top-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 18px; /* 缩小 Logo */
  margin: 0;
  letter-spacing: 0.05em;
  color: #fff;
}

.highlight {
  color: #3b82f6;
}

.nav-links {
  display: flex;
  gap: 20px;
}

.link-item {
  font-size: 13px;
  text-decoration: none;
  color: #94a3b8;
}
.link-item:hover {
  color: #3b82f6;
}

.bottom-meta {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  opacity: 0.8;
}

.tech-tag {
  color: #3b82f6;
  text-transform: uppercase;
}
</style>
