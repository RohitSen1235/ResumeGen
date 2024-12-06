<template>
  <v-app>
    <v-main>
      <v-container fluid class="fill-height pa-0">
        <v-row no-gutters>
          <v-col cols="12">
            <ResumeBuilder />
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import ResumeBuilder from '@/components/ResumeBuilder.vue'
</script>

<style>
.v-application {
  background-color: rgb(var(--v-theme-background)) !important;
}
</style>
