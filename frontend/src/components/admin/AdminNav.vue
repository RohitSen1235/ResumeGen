<template>
  <v-navigation-drawer permanent>
    <v-list density="compact" nav>
      <v-list-item
        prepend-icon="mdi-view-dashboard"
        title="Dashboard"
        value="dashboard"
        to="/admin"
        exact
      ></v-list-item>
      
      <v-list-item
        prepend-icon="mdi-account-group"
        title="User Management"
        value="users"
        to="/admin/users"
      ></v-list-item>
      
      <v-list-item
        prepend-icon="mdi-file-document-multiple"
        title="Template Management"
        value="templates"
        to="/admin/templates"
      ></v-list-item>
    </v-list>
  </v-navigation-drawer>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'AdminNav'
})
</script>

<style scoped>
.v-navigation-drawer {
  height: 100vh;
  position: fixed;
}
</style>
