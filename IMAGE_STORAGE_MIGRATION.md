# Project Image Storage Migration

## Overview
The application has been updated to store project cover images directly in the database instead of as local files. This provides several benefits:

### ✅ **Benefits**
- **Persistence**: Images survive deployments and server restarts
- **Backup**: Images are included in database backups
- **Portability**: No need to manage separate file storage
- **Cloud-friendly**: Works seamlessly on platforms like Render, Heroku, etc.

## What Changed

### **Database Schema**
The `Project` model now has these new fields:
- `cover_image_data` (LargeBinary): Stores the actual image data
- `cover_image_filename` (String): Stores the original filename
- `cover_image_mimetype` (String): Stores the MIME type (image/jpeg, image/png, etc.)

### **Old field removed:**
- `cover_image` (String): No longer used

### **New Routes**
- `/project/<id>/image`: Serves project images from the database

### **Updated Templates**
- `templates/new_project.html`: Uses new image serving route
- `templates/view_project.html`: Uses new image serving route and updated JSON-LD

## Migration Process

### **Automatic Migration**
The database schema was updated using Flask-Migrate:
```bash
flask db migrate -m "Change project images to database storage"
flask db upgrade
```

### **Data Migration**
Any existing project images can be migrated using the provided script:
```bash
python migrate_images_to_db.py
```

## Technical Implementation

### **Upload Process**
```python
# Read file data and store in database
image_data = file.read()
project.cover_image_data = image_data
project.cover_image_filename = secure_filename(file.filename)
project.cover_image_mimetype = file.mimetype
```

### **Image Serving**
```python
@app.route('/project/<int:project_id>/image')
def serve_project_image(project_id):
    project = Project.query.get_or_404(project_id)
    return Response(
        project.cover_image_data,
        mimetype=project.cover_image_mimetype,
        headers={'Cache-Control': 'public, max-age=3600'}
    )
```

### **Template Usage**
```html
{% if project.cover_image_data %}
<img src="{{ url_for('serve_project_image', project_id=project.id) }}" 
     alt="{{ project.title }} cover image" class="img-fluid">
{% endif %}
```

## Performance Considerations

### **Caching**
- Images are served with cache headers (1 hour cache)
- Consider adding CDN for production use

### **Database Size**
- Monitor database size growth
- Consider image compression for very large images
- Typical image sizes should be manageable

### **Memory Usage**
- Images are loaded into memory when served
- Consider implementing streaming for very large images if needed

## Deployment Notes

1. **Apply migrations** on deployment:
   ```bash
   flask db upgrade
   ```

2. **Run migration script** if you have existing images:
   ```bash
   python migrate_images_to_db.py
   ```

3. **Clean up old uploads** (optional):
   ```bash
   rm -rf static/uploads/*
   ```

## Rollback Plan

If you need to rollback to file-based storage:

1. Create new migration to restore `cover_image` field
2. Update upload logic to save files
3. Update templates to use static file URLs
4. Export images from database to files

---

**✅ Migration completed successfully!** 

Project images are now stored in the database and will persist across deployments. 