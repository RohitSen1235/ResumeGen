<template>
  <div class="admin-dashboard">
    <AdminNav />
    
    <div class="admin-content">
      <div class="dashboard-header">
        <h1>Admin Dashboard</h1>
        <div class="refresh-controls">
          <button @click="refreshData" :disabled="loading" class="refresh-btn">
            <span class="refresh-icon" :class="{ spinning: loading }">🔄</span>
            Refresh Data
          </button>
        </div>
      </div>
      
      <!-- Analytics Cards -->
      <div class="analytics-cards">
        <div class="stat-card primary">
          <div class="stat-icon">👥</div>
          <div class="stat-content">
            <div class="stat-number">{{ analytics.total_users || 0 }}</div>
            <div class="stat-label">Total Users</div>
          </div>
        </div>
        
        <div class="stat-card success">
          <div class="stat-icon">⚡</div>
          <div class="stat-content">
            <div class="stat-number">{{ analytics.active_users || 0 }}</div>
            <div class="stat-label">Active Users (30d)</div>
          </div>
        </div>
        
        <div class="stat-card info">
          <div class="stat-icon">📝</div>
          <div class="stat-content">
            <div class="stat-number">{{ analytics.total_resumes || 0 }}</div>
            <div class="stat-label">Total Resumes</div>
          </div>
        </div>
        
        <div class="stat-card warning">
          <div class="stat-icon">📈</div>
          <div class="stat-content">
            <div class="stat-number">{{ analytics.resumes_last_30_days || 0 }}</div>
            <div class="stat-label">Recent Resumes (30d)</div>
          </div>
        </div>
      </div>

      <!-- Main Content Tabs -->
      <div class="content-tabs">
        <div class="tab-buttons">
          <button 
            v-for="tab in tabs" 
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="['tab-btn', { active: activeTab === tab.id }]"
          >
            <span class="tab-icon">{{ tab.icon }}</span>
            {{ tab.label }}
          </button>
        </div>

        <div class="tab-content">
          <!-- User Management Tab -->
          <div v-if="activeTab === 'users'" class="tab-panel">
            <div class="panel-header">
              <h2>User Management</h2>
              <div class="panel-actions">
                <div class="search-box">
                  <input 
                    v-model="userSearch" 
                    type="text" 
                    placeholder="Search users..."
                    class="search-input"
                  >
                </div>
              </div>
            </div>
            <UserManagement :search="userSearch" @refresh="refreshData" />
          </div>

          <!-- Template Management Tab -->
          <div v-if="activeTab === 'templates'" class="tab-panel">
            <div class="panel-header">
              <h2>Template Management</h2>
              <div class="panel-actions">
                <button class="action-btn primary">
                  <span class="btn-icon">➕</span>
                  Add Template
                </button>
              </div>
            </div>
            <TemplateManagement />
          </div>

          <!-- Analytics Tab -->
          <div v-if="activeTab === 'analytics'" class="tab-panel">
            <div class="panel-header">
              <h2>System Analytics</h2>
              <div class="panel-actions">
                <select class="time-filter">
                  <option value="7d">Last 7 days</option>
                  <option value="30d" selected>Last 30 days</option>
                  <option value="90d">Last 90 days</option>
                </select>
              </div>
            </div>
            
            <div class="analytics-grid">
              <div class="analytics-card">
                <h3>User Growth</h3>
                <div class="metric-row">
                  <span class="metric-label">Total Users:</span>
                  <span class="metric-value">{{ analytics.total_users || 0 }}</span>
                </div>
                <div class="metric-row">
                  <span class="metric-label">Active Users (30d):</span>
                  <span class="metric-value">{{ analytics.active_users || 0 }}</span>
                </div>
                <div class="metric-row">
                  <span class="metric-label">Activity Rate:</span>
                  <span class="metric-value">{{ getActivityRate() }}%</span>
                </div>
              </div>

              <div class="analytics-card">
                <h3>Resume Generation</h3>
                <div class="metric-row">
                  <span class="metric-label">Total Resumes:</span>
                  <span class="metric-value">{{ analytics.total_resumes || 0 }}</span>
                </div>
                <div class="metric-row">
                  <span class="metric-label">Recent (30d):</span>
                  <span class="metric-value">{{ analytics.resumes_last_30_days || 0 }}</span>
                </div>
                <div class="metric-row">
                  <span class="metric-label">Avg per User:</span>
                  <span class="metric-value">{{ getAvgResumesPerUser() }}</span>
                </div>
              </div>

              <div class="analytics-card full-width">
                <h3>System Health</h3>
                <div class="health-indicators">
                  <div class="health-item">
                    <div class="health-status good"></div>
                    <span>Database Connection</span>
                  </div>
                  <div class="health-item">
                    <div class="health-status good"></div>
                    <span>API Response Time</span>
                  </div>
                  <div class="health-item">
                    <div class="health-status good"></div>
                    <span>Resume Generation Service</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- System Tab -->
          <div v-if="activeTab === 'system'" class="tab-panel">
            <div class="panel-header">
              <h2>System Information</h2>
            </div>
            
            <div class="system-info">
              <div class="info-card">
                <h3>Server Status</h3>
                <div class="status-item">
                  <span class="status-dot online"></span>
                  <span>API Server: Online</span>
                </div>
                <div class="status-item">
                  <span class="status-dot online"></span>
                  <span>Database: Connected</span>
                </div>
                <div class="status-item">
                  <span class="status-dot online"></span>
                  <span>File Storage: Available</span>
                </div>
              </div>

              <div class="info-card">
                <h3>Recent Activity</h3>
                <div class="activity-list">
                  <div class="activity-item">
                    <span class="activity-time">{{ getCurrentTime() }}</span>
                    <span class="activity-desc">Dashboard refreshed</span>
                  </div>
                  <div class="activity-item">
                    <span class="activity-time">{{ getRecentTime(5) }}</span>
                    <span class="activity-desc">Analytics data updated</span>
                  </div>
                  <div class="activity-item">
                    <span class="activity-time">{{ getRecentTime(15) }}</span>
                    <span class="activity-desc">User management accessed</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'
import { useAuthStore } from '@/store/auth'
import AdminNav from '@/components/admin/AdminNav.vue'
import UserManagement from '@/components/admin/UserManagement.vue'
import TemplateManagement from '@/components/admin/TemplateManagement.vue'
import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL || 'http://localhost/api'
})

export default defineComponent({
  name: 'AdminDashboard',
  components: {
    AdminNav,
    UserManagement,
    TemplateManagement
  },
  setup() {
    const auth = useAuthStore()
    const analytics = ref<any>({})
    const loading = ref(false)
    const activeTab = ref('users')
    const userSearch = ref('')

    const tabs = [
      { id: 'users', label: 'Users', icon: '👥' },
      { id: 'templates', label: 'Templates', icon: '📄' },
      { id: 'analytics', label: 'Analytics', icon: '📊' },
      { id: 'system', label: 'System', icon: '⚙️' }
    ]

    const refreshData = async () => {
      loading.value = true
      try {
        const response = await apiClient.get('/admin/analytics', {
          headers: {
            Authorization: `Bearer ${auth.token}`
          }
        })
        analytics.value = response.data
      } catch (error) {
        console.error('Error fetching analytics:', error)
      } finally {
        loading.value = false
      }
    }

    const getActivityRate = () => {
      const total = analytics.value.total_users || 0
      const active = analytics.value.active_users || 0
      return total > 0 ? Math.round((active / total) * 100) : 0
    }

    const getAvgResumesPerUser = () => {
      const total = analytics.value.total_users || 0
      const resumes = analytics.value.total_resumes || 0
      return total > 0 ? (resumes / total).toFixed(1) : '0.0'
    }

    const getCurrentTime = () => {
      return new Date().toLocaleTimeString()
    }

    const getRecentTime = (minutesAgo: number) => {
      const time = new Date()
      time.setMinutes(time.getMinutes() - minutesAgo)
      return time.toLocaleTimeString()
    }

    onMounted(() => {
      refreshData()
      // Auto-refresh every 5 minutes
      setInterval(refreshData, 5 * 60 * 1000)
    })

    return {
      auth,
      analytics,
      loading,
      activeTab,
      userSearch,
      tabs,
      refreshData,
      getActivityRate,
      getAvgResumesPerUser,
      getCurrentTime,
      getRecentTime
    }
  }
})
</script>

<style scoped>
.admin-dashboard {
  display: flex;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.admin-content {
  flex: 1;
  padding: 2rem;
  margin-left: 256px;
  max-width: calc(100vw - 256px);
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.dashboard-header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0;
}

.refresh-controls {
  display: flex;
  gap: 1rem;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.refresh-btn:hover:not(:disabled) {
  background: #2980b9;
  transform: translateY(-2px);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.refresh-icon.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.analytics-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-card.primary { border-left: 4px solid #3498db; }
.stat-card.success { border-left: 4px solid #27ae60; }
.stat-card.info { border-left: 4px solid #8e44ad; }
.stat-card.warning { border-left: 4px solid #f39c12; }

.stat-icon {
  font-size: 2.5rem;
  opacity: 0.8;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
  line-height: 1;
}

.stat-label {
  font-size: 0.9rem;
  color: #7f8c8d;
  margin-top: 0.25rem;
}

.content-tabs {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.tab-buttons {
  display: flex;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  background: none;
  border: none;
  cursor: pointer;
  font-weight: 500;
  color: #6c757d;
  transition: all 0.3s ease;
  border-bottom: 3px solid transparent;
}

.tab-btn:hover {
  background: #e9ecef;
  color: #495057;
}

.tab-btn.active {
  background: white;
  color: #3498db;
  border-bottom-color: #3498db;
}

.tab-icon {
  font-size: 1.1rem;
}

.tab-content {
  padding: 2rem;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.panel-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.panel-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.search-box {
  position: relative;
}

.search-input {
  padding: 0.5rem 1rem;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 0.9rem;
  width: 250px;
  transition: border-color 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #3498db;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.action-btn.primary {
  background: #3498db;
  color: white;
}

.action-btn.primary:hover {
  background: #2980b9;
}

.time-filter {
  padding: 0.5rem 1rem;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  background: white;
  cursor: pointer;
}

.analytics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.analytics-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  border: 1px solid #e9ecef;
}

.analytics-card.full-width {
  grid-column: 1 / -1;
}

.analytics-card h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 1rem 0;
}

.metric-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid #e9ecef;
}

.metric-row:last-child {
  border-bottom: none;
}

.metric-label {
  color: #6c757d;
  font-size: 0.9rem;
}

.metric-value {
  font-weight: 600;
  color: #2c3e50;
}

.health-indicators {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.health-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: white;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.health-status {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.health-status.good {
  background: #27ae60;
}

.system-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.info-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  border: 1px solid #e9ecef;
}

.info-card h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 1rem 0;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-dot.online {
  background: #27ae60;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.activity-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid #e9ecef;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-time {
  font-size: 0.8rem;
  color: #6c757d;
}

.activity-desc {
  font-size: 0.9rem;
  color: #2c3e50;
}

@media (max-width: 768px) {
  .admin-content {
    margin-left: 0;
    max-width: 100vw;
    padding: 1rem;
  }
  
  .analytics-cards {
    grid-template-columns: 1fr;
  }
  
  .tab-buttons {
    flex-wrap: wrap;
  }
  
  .panel-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
}
</style>
