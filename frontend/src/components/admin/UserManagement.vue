<template>
  <div class="user-management">
    <!-- Users Table -->
    <div class="users-table">
      <div class="table-container">
        <table class="modern-table">
          <thead>
            <tr>
              <th>Email</th>
              <th>Role</th>
              <th>Credits</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in filteredUsers" :key="user.id" class="table-row">
              <td class="user-email">
                <div class="user-info">
                  <div class="user-avatar">{{ user.email.charAt(0).toUpperCase() }}</div>
                  <span>{{ user.email }}</span>
                </div>
              </td>
              <td>
                <span :class="['role-badge', user.is_admin ? 'admin' : 'user']">
                  {{ user.is_admin ? 'Admin' : 'User' }}
                </span>
              </td>
              <td>
                <span class="credits-badge">{{ user.credits || 0 }}</span>
              </td>
              <td class="created-date">
                {{ formatDate(user.created_at) }}
              </td>
              <td class="actions">
                <div class="action-buttons">
                  <button @click="openCreditDialog(user)" class="action-btn credits" title="Manage Credits">
                    💳
                  </button>
                  <button @click="toggleAdminStatus(user)" class="action-btn admin" :title="user.is_admin ? 'Remove Admin' : 'Make Admin'">
                    {{ user.is_admin ? '👤' : '👑' }}
                  </button>
                  <button @click="confirmDeleteUser(user)" class="action-btn delete" title="Delete User" :disabled="user.is_admin && adminCount <= 1">
                    🗑️
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="loading" class="loading-overlay">
          <div class="loading-spinner">Loading...</div>
        </div>
        
        <div v-if="filteredUsers.length === 0 && !loading" class="no-users">
          <div class="no-users-icon">👥</div>
          <p>No users found</p>
        </div>
      </div>
    </div>

    <!-- Credit Management Dialog -->
    <div v-if="creditDialog" class="modal-overlay" @click="creditDialog = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Manage Credits</h3>
          <button @click="creditDialog = false" class="close-btn">✕</button>
        </div>
        <div class="modal-body">
          <div class="user-info-card">
            <div class="user-avatar large">{{ creditUser.email?.charAt(0).toUpperCase() }}</div>
            <div>
              <div class="user-email">{{ creditUser.email }}</div>
              <div class="current-credits">Current Credits: <strong>{{ creditUser.currentCredits }}</strong></div>
            </div>
          </div>
          
          <div class="credit-form">
            <div class="form-group">
              <label>Operation</label>
              <div class="radio-group">
                <label class="radio-option">
                  <input type="radio" v-model="creditUser.operation" value="add" />
                  <span>Add Credits</span>
                </label>
                <label class="radio-option">
                  <input type="radio" v-model="creditUser.operation" value="set" />
                  <span>Set Credits</span>
                </label>
              </div>
            </div>
            
            <div class="form-group">
              <label>Credits Amount</label>
              <input 
                type="number" 
                v-model.number="creditUser.newCredits" 
                min="0" 
                class="credit-input"
                placeholder="Enter amount"
              />
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="creditDialog = false" class="btn secondary">Cancel</button>
          <button @click="updateUserCredits" class="btn primary" :disabled="!creditUser.newCredits">
            Update Credits
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Dialog -->
    <div v-if="deleteDialog" class="modal-overlay" @click="deleteDialog = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Confirm Delete</h3>
          <button @click="deleteDialog = false" class="close-btn">✕</button>
        </div>
        <div class="modal-body">
          <div class="warning-icon">⚠️</div>
          <p>Are you sure you want to delete user <strong>{{ userToDelete?.email }}</strong>?</p>
          <p class="warning-text">This action cannot be undone and will also delete all associated profiles and resumes.</p>
        </div>
        <div class="modal-footer">
          <button @click="deleteDialog = false" class="btn secondary">Cancel</button>
          <button @click="deleteUser" class="btn danger" :disabled="deleting">
            {{ deleting ? 'Deleting...' : 'Delete User' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Success/Error Messages -->
    <div v-if="message.show" :class="['message', message.type]">
      {{ message.text }}
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/store/auth'
import axios from 'axios'

// Create axios instance with proper configuration
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL || 'http://localhost/api'
})

interface User {
  id: string
  email: string
  is_admin: boolean
  credits?: number
  created_at?: string
  updated_at?: string
}

export default defineComponent({
  name: 'UserManagement',
  props: {
    search: {
      type: String,
      default: ''
    }
  },
  emits: ['refresh'],
  setup(props, { emit }) {
    const auth = useAuthStore()
    const users = ref<User[]>([])
    const loading = ref(false)
    const deleting = ref(false)
    const deleteDialog = ref(false)
    const userToDelete = ref<User | null>(null)

    const creditDialog = ref(false)
    const creditUser = ref({
      id: '',
      email: '',
      currentCredits: 0,
      newCredits: 0,
      operation: 'add'
    })

    const message = ref({
      show: false,
      text: '',
      type: 'success'
    })

    // Computed properties
    const filteredUsers = computed(() => {
      if (!props.search) return users.value
      return users.value.filter(user => 
        user.email.toLowerCase().includes(props.search.toLowerCase())
      )
    })

    const adminCount = computed(() => {
      return users.value.filter(user => user.is_admin).length
    })

    // Methods
    const showMessage = (text: string, type: 'success' | 'error' = 'success') => {
      message.value = { show: true, text, type }
      setTimeout(() => {
        message.value.show = false
      }, 3000)
    }

    const formatDate = (dateString?: string) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString()
    }

    const fetchUsers = async () => {
      try {
        loading.value = true
        const response = await apiClient.get('/admin/users', {
          headers: {
            Authorization: `Bearer ${auth.token}`
          }
        })
        users.value = response.data
        emit('refresh')
      } catch (error) {
        console.error('Error fetching users:', error)
        showMessage('Error fetching users', 'error')
      } finally {
        loading.value = false
      }
    }

    const openCreditDialog = (user: User) => {
      creditUser.value = {
        id: user.id,
        email: user.email,
        currentCredits: user.credits || 0,
        newCredits: 0,
        operation: 'add'
      }
      creditDialog.value = true
    }

    const updateUserCredits = async () => {
      try {
        await apiClient.post('/admin/users/credits', {
          user_id: creditUser.value.id,
          credits: creditUser.value.newCredits,
          operation: creditUser.value.operation
        }, {
          headers: {
            Authorization: `Bearer ${auth.token}`
          }
        })
        
        creditDialog.value = false
        await fetchUsers()
        showMessage('Credits updated successfully')
      } catch (error) {
        console.error('Error updating credits:', error)
        showMessage('Error updating credits', 'error')
      }
    }

    const toggleAdminStatus = async (user: User) => {
      if (user.is_admin && adminCount.value <= 1) {
        showMessage('Cannot remove admin status from the last admin user', 'error')
        return
      }

      try {
        await apiClient.put(`/admin/users/${user.id}`, {
          ...user,
          is_admin: !user.is_admin
        }, {
          headers: {
            Authorization: `Bearer ${auth.token}`
          }
        })
        
        await fetchUsers()
        showMessage(`User ${user.is_admin ? 'admin status removed' : 'made admin'}`)
      } catch (error) {
        console.error('Error toggling admin status:', error)
        showMessage('Error updating user status', 'error')
      }
    }

    const confirmDeleteUser = (user: User) => {
      if (user.is_admin && adminCount.value <= 1) {
        showMessage('Cannot delete the last admin user', 'error')
        return
      }
      
      userToDelete.value = user
      deleteDialog.value = true
    }

    const deleteUser = async () => {
      if (!userToDelete.value) return
      
      try {
        deleting.value = true
        await apiClient.delete(`/admin/users/${userToDelete.value.id}`, {
          headers: {
            Authorization: `Bearer ${auth.token}`
          }
        })
        
        deleteDialog.value = false
        userToDelete.value = null
        await fetchUsers()
        showMessage('User deleted successfully')
      } catch (error) {
        console.error('Error deleting user:', error)
        showMessage('Error deleting user', 'error')
      } finally {
        deleting.value = false
      }
    }

    onMounted(fetchUsers)

    return {
      auth,
      users,
      loading,
      deleting,
      deleteDialog,
      userToDelete,
      creditDialog,
      creditUser,
      message,
      filteredUsers,
      adminCount,
      formatDate,
      fetchUsers,
      openCreditDialog,
      updateUserCredits,
      toggleAdminStatus,
      confirmDeleteUser,
      deleteUser
    }
  }
})
</script>

<style scoped>
.user-management {
  width: 100%;
}

.users-table {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.table-container {
  position: relative;
  overflow-x: auto;
}

.modern-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.modern-table th {
  background: #f8f9fa;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #2c3e50;
  border-bottom: 2px solid #e9ecef;
}

.modern-table td {
  padding: 1rem;
  border-bottom: 1px solid #e9ecef;
  vertical-align: middle;
}

.table-row:hover {
  background: #f8f9fa;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #3498db;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.9rem;
}

.user-avatar.large {
  width: 48px;
  height: 48px;
  font-size: 1.2rem;
}

.role-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.role-badge.admin {
  background: #e74c3c;
  color: white;
}

.role-badge.user {
  background: #95a5a6;
  color: white;
}

.credits-badge {
  background: #f39c12;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.8rem;
}

.created-date {
  color: #7f8c8d;
  font-size: 0.85rem;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.action-btn:hover:not(:disabled) {
  transform: translateY(-2px);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-btn.credits {
  background: #f39c12;
}

.action-btn.credits:hover:not(:disabled) {
  background: #e67e22;
}

.action-btn.admin {
  background: #9b59b6;
}

.action-btn.admin:hover:not(:disabled) {
  background: #8e44ad;
}

.action-btn.delete {
  background: #e74c3c;
}

.action-btn.delete:hover:not(:disabled) {
  background: #c0392b;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-spinner {
  padding: 2rem;
  font-size: 1.1rem;
  color: #3498db;
}

.no-users {
  text-align: center;
  padding: 3rem;
  color: #7f8c8d;
}

.no-users-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e9ecef;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: #2c3e50;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #7f8c8d;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: #f8f9fa;
  color: #2c3e50;
}

.modal-body {
  padding: 1.5rem;
}

.user-info-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.user-email {
  font-weight: 600;
  color: #2c3e50;
}

.current-credits {
  color: #7f8c8d;
  font-size: 0.9rem;
  margin-top: 0.25rem;
}

.credit-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.9rem;
}

.radio-group {
  display: flex;
  gap: 1rem;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.9rem;
}

.radio-option input[type="radio"] {
  margin: 0;
}

.credit-input {
  padding: 0.75rem;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 0.9rem;
  transition: border-color 0.3s ease;
}

.credit-input:focus {
  outline: none;
  border-color: #3498db;
}

.warning-icon {
  text-align: center;
  font-size: 3rem;
  margin-bottom: 1rem;
}

.warning-text {
  color: #e74c3c;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid #e9ecef;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn.primary {
  background: #3498db;
  color: white;
}

.btn.primary:hover:not(:disabled) {
  background: #2980b9;
}

.btn.secondary {
  background: #95a5a6;
  color: white;
}

.btn.secondary:hover:not(:disabled) {
  background: #7f8c8d;
}

.btn.danger {
  background: #e74c3c;
  color: white;
}

.btn.danger:hover:not(:disabled) {
  background: #c0392b;
}

.message {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  color: white;
  font-weight: 500;
  z-index: 1001;
  animation: slideIn 0.3s ease;
}

.message.success {
  background: #27ae60;
}

.message.error {
  background: #e74c3c;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .modern-table {
    font-size: 0.8rem;
  }
  
  .modern-table th,
  .modern-table td {
    padding: 0.75rem 0.5rem;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .action-btn {
    width: 28px;
    height: 28px;
    font-size: 0.8rem;
  }
  
  .modal-content {
    width: 95%;
    margin: 1rem;
  }
  
  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 1rem;
  }
}
</style>
