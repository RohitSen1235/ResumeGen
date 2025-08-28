# Template Definition Schema

This document defines the JSON schema for template definitions that enable WYSIWYG editing in the frontend.

## Schema Structure

```json
{
  "template_id": "string",
  "name": "string", 
  "description": "string",
  "layout": {
    "type": "single-column" | "two-column",
    "columns": [
      {
        "width": "percentage or fixed width",
        "background": "color",
        "padding": "css padding value",
        "sections": ["array of section names in order"]
      }
    ]
  },
  "colors": {
    "primary": "hex color",
    "secondary": "hex color", 
    "accent": "hex color",
    "background": "hex color",
    "text": "hex color"
  },
  "typography": {
    "font_family": "font name",
    "name_size": "font size for name",
    "section_header_size": "font size for section headers",
    "body_size": "font size for body text",
    "line_height": "line height multiplier"
  },
  "sections": {
    "header": {
      "type": "header",
      "fields": ["name", "title", "contact"],
      "layout": "centered" | "left" | "right",
      "styling": {
        "name_style": "css properties",
        "title_style": "css properties", 
        "contact_style": "css properties"
      }
    },
    "summary": {
      "type": "text",
      "title": "Summary" | "Professional Summary",
      "styling": {
        "section_title": "css properties",
        "content": "css properties"
      }
    },
    "experience": {
      "type": "list",
      "title": "Experience" | "Professional Experience",
      "item_layout": "timeline" | "standard",
      "fields": ["title", "company", "duration", "achievements"],
      "styling": {
        "section_title": "css properties",
        "item_title": "css properties",
        "item_company": "css properties", 
        "item_duration": "css properties",
        "achievements": "css properties"
      }
    },
    "education": {
      "type": "list", 
      "title": "Education",
      "fields": ["degree", "institution", "year", "details"],
      "styling": {
        "section_title": "css properties",
        "item_degree": "css properties",
        "item_institution": "css properties",
        "item_year": "css properties"
      }
    },
    "skills": {
      "type": "tags" | "list",
      "title": "Skills" | "Key Skills",
      "layout": "inline" | "columns" | "grid",
      "styling": {
        "section_title": "css properties",
        "skill_item": "css properties"
      }
    },
    "projects": {
      "type": "list",
      "title": "Projects", 
      "fields": ["title", "highlights"],
      "styling": {
        "section_title": "css properties",
        "project_title": "css properties",
        "highlights": "css properties"
      }
    },
    "achievements": {
      "type": "list",
      "title": "Key Achievements",
      "layout": "single" | "columns",
      "styling": {
        "section_title": "css properties",
        "achievement_item": "css properties"
      }
    },
    "certifications": {
      "type": "list",
      "title": "Certifications",
      "layout": "single" | "columns", 
      "styling": {
        "section_title": "css properties",
        "cert_item": "css properties"
      }
    }
  },
  "spacing": {
    "section_margin": "css margin",
    "item_margin": "css margin",
    "paragraph_spacing": "css margin"
  }
}
```

## Field Types

- **text**: Simple text content (summary, descriptions)
- **list**: Array of items (experience, education, skills)
- **tags**: Comma-separated or array of short items (skills)
- **header**: Special section for name and contact info

## Layout Types

- **single-column**: Traditional single column layout
- **two-column**: Left and right column layout
- **timeline**: Special layout for experience with dates on left