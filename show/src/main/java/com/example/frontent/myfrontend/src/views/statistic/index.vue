<template>
  <div class="stat-container">
    <nav class="stat-sidebar">
      <div class="nav-brand">
        <div class="brand-logo"></div>
        <span>分析工作台</span>
      </div>
      
      <div class="nav-list">
        <router-link to="/statistic/trend" class="nav-item">
          <el-icon><TrendCharts /></el-icon> 气温趋势分析
        </router-link>
        <router-link to="/statistic/extreme" class="nav-item">
          <el-icon><Warning /></el-icon> 极端气温研判
        </router-link>
        <router-link to="/statistic/diurnal" class="nav-item">
          <el-icon><Histogram /></el-icon> 日较差分布
        </router-link>
        <router-link to="/statistic/forecast" class="nav-item">
          <el-icon><Cpu /></el-icon> 预测建模
        </router-link>
      </div>

      <div class="sidebar-footer">
        <router-link to="/" class="nav-item back">
          <el-icon><ArrowLeft /></el-icon> 返回总控台
        </router-link>
      </div>
    </nav>

    <main class="stat-content">
      <router-view v-slot="{ Component, route }">
  <transition name="fade-slide" mode="out-in">
    <component :is="Component" :key="route.fullPath" />
  </transition>
</router-view>
    </main>
  </div>
</template>

<script setup>
import { TrendCharts, Warning, Histogram, Cpu, ArrowLeft } from '@element-plus/icons-vue'
</script>

<style scoped>
.stat-container { 
  display: flex; height: 100vh; 
  background: radial-gradient(circle at top right, #0c1a3d, #060d1a);
}

/* 左侧栏样式 */
.stat-sidebar { 
  width: 240px; 
  background: rgba(8, 15, 30, 0.6);
  border-right: 1px solid rgba(26, 58, 106, 0.5); 
  padding: 24px; 
  display: flex; flex-direction: column;
}
.nav-brand { font-size: 16px; font-weight: bold; color: #e2eaf6; margin-bottom: 40px; display: flex; align-items: center; gap: 10px; }
.brand-logo { width: 8px; height: 8px; background: #3a8fff; border-radius: 50%; box-shadow: 0 0 10px #3a8fff; }

.nav-item { 
  display: flex; align-items: center; gap: 12px;
  color: #4a7abf; text-decoration: none; padding: 12px 16px; 
  margin-bottom: 8px; border-radius: 6px;
  transition: all 0.3s; font-size: 14px;
}
.nav-item:hover { background: rgba(58, 143, 255, 0.1); color: #e2eaf6; }
.nav-item.router-link-active { 
  background: #3a8fff; color: white; 
  box-shadow: 0 4px 15px rgba(58, 143, 255, 0.3);
}

.sidebar-footer { margin-top: auto; border-top: 1px solid #1a3a6a; padding-top: 20px; }

/* 内容区样式 */
.stat-content { 
  flex: 1; padding: 24px; overflow-y: auto;
  position: relative;
}

/* 切换动效 */
.fade-slide-enter-active, .fade-slide-leave-active { transition: all 0.3s ease; }
.fade-slide-enter-from { opacity: 0; transform: translateX(20px); }
.fade-slide-leave-to { opacity: 0; transform: translateX(-20px); }
</style>