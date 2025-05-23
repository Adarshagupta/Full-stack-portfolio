#!/usr/bin/env python3
"""
Script to compress existing images in the database to improve performance.
Run this after implementing image compression to optimize existing images.
"""

import os
from app import app, db, Project, compress_image

def compress_existing_images():
    """Compress existing images in the database to reduce size and improve performance."""
    
    with app.app_context():
        projects = Project.query.filter(Project.cover_image_data.isnot(None)).all()
        compressed_count = 0
        total_savings = 0
        
        print(f"Found {len(projects)} projects with images to compress")
        
        for project in projects:
            if project.cover_image_data:
                original_size = len(project.cover_image_data)
                
                # Skip if already JPEG and reasonably sized (likely already compressed)
                if project.cover_image_mimetype == 'image/jpeg' and original_size < 200000:  # 200KB
                    print(f"Skipping '{project.title}' - already optimized ({original_size} bytes)")
                    continue
                
                try:
                    # Compress the image
                    compressed_data, compressed_mimetype = compress_image(project.cover_image_data)
                    
                    # Only update if compression actually made it smaller
                    compressed_size = len(compressed_data)
                    if compressed_size < original_size:
                        project.cover_image_data = compressed_data
                        if compressed_mimetype:
                            project.cover_image_mimetype = compressed_mimetype
                        
                        savings = original_size - compressed_size
                        total_savings += savings
                        compressed_count += 1
                        
                        print(f"✅ Compressed '{project.title}': {original_size} -> {compressed_size} bytes (saved {savings} bytes)")
                    else:
                        print(f"⏭️  Skipped '{project.title}' - compression didn't improve size")
                        
                except Exception as e:
                    print(f"❌ Error compressing image for '{project.title}': {str(e)}")
        
        # Commit all changes
        try:
            db.session.commit()
            print(f"\n🎉 Compression completed successfully!")
            print(f"- Compressed: {compressed_count} images")
            print(f"- Total space saved: {total_savings:,} bytes ({total_savings/1024/1024:.2f} MB)")
            
            if compressed_count > 0:
                average_savings = total_savings / compressed_count
                print(f"- Average savings per image: {average_savings:,.0f} bytes")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error committing changes: {str(e)}")

if __name__ == "__main__":
    compress_existing_images() 