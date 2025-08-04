<template>
  <div class="user-management">
    <h2>User Management</h2>
    
    <v-data-table
      :headers="headers"
      :items="users"
      :loading="loading"
      class="elevation-1"
    >
      <template v-slot:item.is_admin="{ item }">
        <v-icon :color="item.is_admin ? 'green' : 'red'">
          {{ item.is_admin ? 'mdi-check-circle' : 'mdi-close-circle' }}
        </v-icon>
      </template>

      <template v-slot:item.actions="{ item }">
        <v-btn
          small
          color="orange-lighten-2"
          @click="editUser(item)"
        >
          Edit
        </v-btn>
        <v-btn
          small
          color="error"
          @click="deleteUser(item)"
          class="ml-2"
        >
          Delete
        </v-btn>
      </template>
    </v-data-table>

    <v-dialog v-model="editDialog" max-width="500">
      <v-card>
        <v-card-title>Edit User</v-card-title>
        <v-card-text>
          <v-text-field v-model="editedUser.email" label="Email"></v-text-field>
          <v-checkbox v-model="editedUser.is_admin" label="Admin"></v-checkbox>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="editDialog = false">Cancel</v-btn>
          <v-btn color="orange-lighten-2" @click="saveUser">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'
import { useAuthStore } from '@/store/auth'
import axios from 'axios'
interface User {
  id: string
  email: string
  is_admin: boolean
  created_at?: string
  updated_at?: string
}

interface UserData {
  id: string
  email: string
  is_admin: boolean
}

export default defineComponent({
  name: 'UserManagement',
  setup() {
    const auth = useAuthStore()
    const users = ref<User[]>([])
    const loading = ref(false)
    const editDialog = ref(false)
    const editedUser = ref({
      id: '',
      email: '',
      is_admin: false
    })

    const headers = [
      { text: 'Email', value: 'email' },
      { text: 'Admin', value: 'is_admin' },
      { text: 'Actions', value: 'actions', sortable: false }
    ]

    const fetchUsers = async () => {
      try {
        loading.value = true
        const response = await axios.get('/api/admin/users', {
          headers: {
            Authorization: `Bearer ${auth.token}`
          }
        })
        users.value = response.data
      } catch (error) {
        console.error('Error fetching users:', error)
      } finally {
        loading.value = false
      }
    }

    const editUser = (user: UserData) => {
      editedUser.value = { ...user }
      editDialog.value = true
    }

    const saveUser = async () => {
      try {
        await axios.put(`/api/admin/users/${editedUser.value.id}`, editedUser.value, {
          headers: {
            Authorization: `Bearer ${auth.token}`
          }
        })
        await fetchUsers()
        editDialog.value = false
      } catch (error) {
        console.error('Error updating user:', error)
      }
    }

    const deleteUser = async (user: UserData) => {
      if (!confirm(`Are you sure you want to delete ${user.email}?`)) return
      
      try {
        await axios.delete(`/api/admin/users/${user.id}`, {
          headers: {
            Authorization: `Bearer ${auth.token}`
          }
        })
        await fetchUsers()
      } catch (error) {
        console.error('Error deleting user:', error)
      }
    }

    onMounted(fetchUsers)

    return {
      auth,
      users,
      loading,
      headers,
      editDialog,
      editedUser,
      editUser,
      saveUser,
      deleteUser
    }
  }
})
</script>

<style scoped>
.user-management {
  padding: 2rem;
}
</style>
