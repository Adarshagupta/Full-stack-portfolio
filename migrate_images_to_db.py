#!/usr/bin/env python3
"""
Migration script to convert existing project images from local files to database storage.
Run this once after deploying the new image storage system.
"""

import os
from app import app, db, Project

def migrate_images_to_database():
    """Migrate existing project images from local files to database storage."""
    
    with app.app_context():
        projects = Project.query.all()
        migrated_count = 0
        skipped_count = 0
        
        print(f"Found {len(projects)} projects to check for image migration")
        
        for project in projects:
            # Skip if already has database image
            if project.cover_image_data:
                print(f"Project '{project.title}' already has database image, skipping")
                skipped_count += 1
                continue
            
            # Check if project has old-style filename but no data
            if hasattr(project, 'cover_image') and project.cover_image:
                old_filename = project.cover_image
                file_path = os.path.join('static', 'uploads', old_filename)
                
                if os.path.exists(file_path):
                    try:
                        # Read the file and store in database
                        with open(file_path, 'rb') as f:
                            image_data = f.read()
                        
                        # Determine MIME type based on extension
                        ext = os.path.splitext(old_filename)[1].lower()
                        mime_types = {
                            '.jpg': 'image/jpeg',
                            '.jpeg': 'image/jpeg',
                            '.png': 'image/png',
                            '.gif': 'image/gif',
                            '.webp': 'image/webp'
                        }
                        mimetype = mime_types.get(ext, 'image/jpeg')
                        
                        # Update project with database image
                        project.cover_image_data = image_data
                        project.cover_image_filename = old_filename
                        project.cover_image_mimetype = mimetype
                        
                        print(f"Migrated image for project '{project.title}': {old_filename} ({len(image_data)} bytes)")
                        migrated_count += 1
                        
                    except Exception as e:
                        print(f"Error migrating image for project '{project.title}': {str(e)}")
                
                else:
                    print(f"Image file not found for project '{project.title}': {file_path}")
            
            else:
                print(f"Project '{project.title}' has no image to migrate")
                skipped_count += 1
        
        # Commit all changes
        try:
            db.session.commit()
            print(f"\nMigration completed successfully!")
            print(f"- Migrated: {migrated_count} projects")
            print(f"- Skipped: {skipped_count} projects")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error committing changes: {str(e)}")

if __name__ == "__main__":
    migrate_images_to_database() 