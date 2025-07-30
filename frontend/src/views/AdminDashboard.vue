<template>
  <div class="admin-dashboard">
    <AdminNav />
    
    <div class="admin-content">
      <h1>Admin Dashboard</h1>
      
      <div class="admin-sections">
        <section class="users-section">
        <h2>User Management</h2>
        <div class="user-list">
          <!-- User list will be populated here -->
        </div>
      </section>

      <section class="templates-section">
        <h2>Template Management</h2>
        <!-- Template management UI will go here -->
      </section>

      <section class="analytics-section">
        <h2>Analytics</h2>
        <!-- Analytics charts will go here -->
      </section>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { useAuthStore } from '@/store/auth'
import AdminNav from '@/components/admin/AdminNav.vue'

export default defineComponent({
  name: 'AdminDashboard',
  components: {
    AdminNav
  },
  setup() {
    const auth = useAuthStore()
    return { auth }
  }
})
</script>

<style scoped>
.admin-dashboard {
  display: flex;
  min-height: 100vh;
}

.admin-content {
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  margin-left: 256px; /* Match nav width */
}

.admin-sections {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 2rem;
}

section {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

h1 {
  font-size: 2rem;
  margin-bottom: 1rem;
}

h2 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: #333;
}
</style>
