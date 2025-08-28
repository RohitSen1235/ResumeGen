from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from app.latex.processor import StagingTemplateProcessor
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
import uuid

router = APIRouter()

@router.post("/staging-templates/", response_model=schemas.StagingLatexTemplate)
def create_staging_template(template: schemas.StagingLatexTemplateCreate, db: Session = Depends(get_db)):
    db_template = models.StagingLatexTemplate(**template.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

@router.get("/staging-templates/", response_model=list[schemas.StagingLatexTemplate])
def read_staging_templates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    templates = db.query(models.StagingLatexTemplate).offset(skip).limit(limit).all()
    return templates

@router.get("/staging-templates/{template_id}", response_model=schemas.StagingLatexTemplate)
def read_staging_template(template_id: uuid.UUID, db: Session = Depends(get_db)):
    db_template = db.query(models.StagingLatexTemplate).filter(models.StagingLatexTemplate.id == template_id).first()
    if db_template is None:
        raise HTTPException(status_code=404, detail="StagingLatexTemplate not found")
    return db_template

@router.put("/staging-templates/{template_id}", response_model=schemas.StagingLatexTemplate)
def update_staging_template(template_id: uuid.UUID, template: schemas.StagingLatexTemplateUpdate, db: Session = Depends(get_db)):
    db_template = db.query(models.StagingLatexTemplate).filter(models.StagingLatexTemplate.id == template_id).first()
    if db_template is None:
        raise HTTPException(status_code=404, detail="StagingLatexTemplate not found")
    for var, value in vars(template).items():
        if value is not None:
            setattr(db_template, var, value)
    db.commit()
    db.refresh(db_template)
    return db_template

@router.delete("/staging-templates/{template_id}", response_model=schemas.StagingLatexTemplate)
def delete_staging_template(template_id: uuid.UUID, db: Session = Depends(get_db)):
    db_template = db.query(models.StagingLatexTemplate).filter(models.StagingLatexTemplate.id == template_id).first()
    if db_template is None:
        raise HTTPException(status_code=404, detail="StagingLatexTemplate not found")
    db.delete(db_template)
    db.commit()
    return db_template

@router.post("/staging-templates/{template_id}/push-to-production", response_model=schemas.LatexTemplate)
def push_to_production(template_id: uuid.UUID, db: Session = Depends(get_db)):
    staging_template = db.query(models.StagingLatexTemplate).filter(models.StagingLatexTemplate.id == template_id).first()
    if staging_template is None:
        raise HTTPException(status_code=404, detail="StagingLatexTemplate not found")

    production_template = db.query(models.LatexTemplate).filter(models.LatexTemplate.id == staging_template.template_id).first()
    if production_template is None:
        # Create a new production template if it doesn't exist
        production_template = models.LatexTemplate(
            id=staging_template.template_id,
            name=staging_template.name,
            description=staging_template.description,
            file_path="",  # This will be updated with the S3 path
            image_path=staging_template.image_path,
            is_default=staging_template.is_default,
            single_page=staging_template.single_page,
            is_active=staging_template.is_active,
        )
        db.add(production_template)
    else:
        # Update existing production template
        production_template.name = staging_template.name
        production_template.description = staging_template.description
        production_template.image_path = staging_template.image_path
        production_template.is_default = staging_template.is_default
        production_template.single_page = staging_template.single_page
        production_template.is_active = staging_template.is_active

    # Here you would add the logic to upload the latex_code to S3 and get the file_path
    # For now, we'll just set it to a placeholder
    production_template.file_path = f"templates/{production_template.name}.tex.j2"

    db.commit()
    db.refresh(production_template)
    return production_template
@router.post("/staging-templates/{template_id}/generate-pdf")
def generate_staging_pdf(template_id: uuid.UUID, db: Session = Depends(get_db)):
    # Use a standard test data for generating the preview
    test_data = {
        "name": "Dr. Jane Smith",
        "email": "jane.smith@example.com",
        "phone": "555-123-4567",
        "location": "San Francisco, CA",
        "linkedin": "linkedin.com/in/janesmith",
        "summary": "A dedicated and innovative research scientist with over 15 years of experience in molecular biology, genetics, and bioinformatics. Proven ability to lead complex research projects from conception to publication, resulting in significant advancements in the field. Adept at securing funding, managing laboratory operations, and mentoring junior scientists. Seeking to leverage expertise in a challenging role at a leading research institution.",
        "experience": [
            {
                "title": "Senior Research Scientist",
                "company": "BioGen Innovations",
                "duration": "2018 - Present",
                "achievements": [
                    "Led a team of 5 researchers in a project that identified a novel gene associated with a rare genetic disorder, leading to a publication in a high-impact journal.",
                    "Secured a $1.5 million grant from the National Institutes of Health (NIH) to fund a new research initiative.",
                    "Developed and optimized a new CRISPR-Cas9 gene-editing technique, improving efficiency by 40%.",
                    "Presented research findings at 5 international conferences."
                ]
            },
            {
                "title": "Postdoctoral Research Fellow",
                "company": "University of California, Berkeley",
                "duration": "2015 - 2018",
                "achievements": [
                    "Published 3 first-author papers in peer-reviewed journals.",
                    "Developed a new method for analyzing large-scale genomic data, which is now widely used in the field.",
                    "Mentored and supervised 2 graduate students."
                ]
            },
            {
                "title": "Graduate Research Assistant",
                "company": "Stanford University",
                "duration": "2010 - 2015",
                "achievements": [
                    "Conducted research on the genetic basis of a common metabolic disorder.",
                    "Developed a new assay for detecting a specific biomarker.",
                    "Presented research findings at 3 national conferences."
                ]
            }
        ],
        "education": [
            {
                "degree": "Ph.D. in Molecular Biology",
                "institution": "Stanford University",
                "year": "2010 - 2015"
            },
            {
                "degree": "B.S. in Biology",
                "institution": "University of California, Los Angeles",
                "year": "2006 - 2010"
            }
        ],
        "skills": ["Molecular Biology", "Genetics", "CRISPR-Cas9", "Next-Generation Sequencing (NGS)", "Bioinformatics", "Data Analysis", "Grant Writing", "Project Management", "Scientific Writing", "Public Speaking", "Python", "R", "SQL"],
        "projects": [
            {
                "title": "Genetic Basis of Neurodegenerative Diseases",
                "highlights": [
                    "Identified 3 new genetic risk factors for a common neurodegenerative disease.",
                    "Developed a new mouse model to study the disease.",
                    "Collaborated with a team of clinicians to translate research findings into potential therapeutic targets."
                ]
            },
            {
                "title": "Development of a High-Throughput Screening Platform",
                "highlights": [
                    "Designed and built a robotic platform for high-throughput screening of small molecules.",
                    "Screened over 100,000 compounds to identify potential drug candidates.",
                    "Published a paper describing the platform and its application."
                ]
            },
            {
                "title": "Analysis of the Gut Microbiome in a Mouse Model of a Metabolic Disorder",
                "highlights": [
                    "Characterized the gut microbiome of a mouse model of a common metabolic disorder.",
                    "Identified several bacterial species that are associated with the disease.",
                    "Published a paper describing the findings."
                ]
            }
        ],
        "achievements": [
            {
                "title": "A novel gene associated with a rare genetic disorder",
                "journal": "Nature Genetics",
                "year": "2021"
            },
            {
                "title": "A new method for analyzing large-scale genomic data",
                "journal": "Bioinformatics",
                "year": "2017"
            },
            {
                "title": "The role of the gut microbiome in a mouse model of a common metabolic disorder",
                "journal": "Cell Host & Microbe",
                "year": "2015"
            }
        ],
        "job_title": "Senior Research Scientist"
    }

    try:
        staging_processor = StagingTemplateProcessor(db)
        pdf_path = staging_processor.generate_staging_pdf(str(template_id), test_data)
        
        import os
        filename = os.path.basename(pdf_path)
        
        return {"filename": filename}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

@router.get("/staging-templates/preview/{filename}", response_class=FileResponse)
def get_preview_pdf(filename: str):
    import os
    from pathlib import Path
    output_dir = Path("/app/app/output")
    pdf_path = output_dir / filename
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Preview PDF not found")
    return FileResponse(pdf_path, media_type="application/pdf")