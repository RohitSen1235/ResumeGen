<template>
  <v-container>
    <v-row>
      <v-col>
        <h1>Staging Template Management</h1>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-btn color="primary" @click="dialog = true">New Staging Template</v-btn>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-data-table
          :headers="headers"
          :items="templates"
          :loading="loading"
          class="elevation-1"
        >
          <template v-slot:item.actions="{ item }">
            <v-icon small class="mr-2" @click="editTemplate(item)">mdi-pencil</v-icon>
            <v-icon small class="mr-2" @click="deleteTemplate(item)">mdi-delete</v-icon>
            <v-btn small color="primary" class="mr-2" @click="generatePreview(item)">Generate Preview</v-btn>
            <v-btn small color="success" @click="pushToProduction(item)">Push to Production</v-btn>
          </template>
        </v-data-table>
      </v-col>
    </v-row>

    <v-dialog v-model="dialog" max-width="800px">
      <v-card>
        <v-card-title>
          <span class="headline">{{ formTitle }}</span>
        </v-card-title>
        <v-card-text>
          <v-container>
            <v-row>
              <v-col cols="12" sm="6">
                <v-text-field v-model="editedTemplate.name" label="Name"></v-text-field>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="editedTemplate.description" label="Description"></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-textarea v-model="editedTemplate.latex_code" label="LaTeX Code" rows="15"></v-textarea>
              </v-col>
              <v-col cols="12" sm="6">
                <v-checkbox v-model="editedTemplate.is_default" label="Default"></v-checkbox>
              </v-col>
              <v-col cols="12" sm="6">
                <v-checkbox v-model="editedTemplate.single_page" label="Single Page"></v-checkbox>
              </v-col>
              <v-col cols="12" sm="6">
                <v-checkbox v-model="editedTemplate.is_active" label="Active"></v-checkbox>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="close">Cancel</v-btn>
          <v-btn color="blue darken-1" text @click="save">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import axios from 'axios';

export default {
  data: () => ({
    dialog: false,
    loading: false,
    headers: [
      { text: 'Name', value: 'name' },
      { text: 'Description', value: 'description' },
      { text: 'Default', value: 'is_default' },
      { text: 'Single Page', value: 'single_page' },
      { text: 'Active', value: 'is_active' },
      { text: 'Actions', value: 'actions', sortable: false },
    ],
    templates: [],
    editedIndex: -1,
    editedTemplate: {
      name: '',
      description: '',
      latex_code: '',
      is_default: false,
      single_page: true,
      is_active: true,
    },
    defaultTemplate: {
      name: '',
      description: '',
      latex_code: '',
      is_default: false,
      single_page: true,
      is_active: true,
    },
  }),

  computed: {
    formTitle() {
      return this.editedIndex === -1 ? 'New Staging Template' : 'Edit Staging Template';
    },
  },

  watch: {
    dialog(val) {
      val || this.close();
    },
  },

  created() {
    this.fetchStagingTemplates();
  },

  methods: {
    async fetchStagingTemplates() {
      this.loading = true;
      try {
        const response = await axios.get('/admin/staging-templates/');
        this.templates = response.data;
      } catch (error) {
        console.error('Error fetching staging templates:', error);
      } finally {
        this.loading = false;
      }
    },

    editTemplate(item) {
      this.editedIndex = this.templates.indexOf(item);
      this.editedTemplate = Object.assign({}, item);
      this.dialog = true;
    },

    deleteTemplate(item) {
      const index = this.templates.indexOf(item);
      confirm('Are you sure you want to delete this template?') &&
        axios.delete(`/admin/staging-templates/${item.id}`).then(() => {
          this.templates.splice(index, 1);
        });
    },

    close() {
      this.dialog = false;
      this.$nextTick(() => {
        this.editedTemplate = Object.assign({}, this.defaultTemplate);
        this.editedIndex = -1;
      });
    },

    async save() {
      if (this.editedIndex > -1) {
        // Update
        try {
          const response = await axios.put(`/admin/staging-templates/${this.editedTemplate.id}`, this.editedTemplate);
          Object.assign(this.templates[this.editedIndex], response.data);
        } catch (error) {
          console.error('Error updating template:', error);
        }
      } else {
        // Create
        try {
          const response = await axios.post('/admin/staging-templates/', this.editedTemplate);
          this.templates.push(response.data);
        } catch (error) {
          console.error('Error creating template:', error);
        }
      }
      this.close();
    },

    async generatePreview(item) {
      try {
        const response = await axios.post(`/admin/staging-templates/${item.id}/generate-pdf`);
        const filename = response.data.filename;
        
        // Open the PDF in a new tab
        window.open(`/api/admin/staging-templates/preview/${filename}`, '_blank');
      } catch (error) {
        console.error('Error generating preview:', error);
        alert('Failed to generate preview PDF.');
      }
    },

    async pushToProduction(item) {
      try {
        await axios.post(`/admin/staging-templates/${item.id}/push-to-production`);
        alert('Template pushed to production successfully!');
      } catch (error) {
        console.error('Error pushing template to production:', error);
        alert('Failed to push template to production.');
      }
    },
  },
};
</script>