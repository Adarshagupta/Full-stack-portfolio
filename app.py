from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
import os
import markdown
from datetime import datetime
import pytz
from markdown.preprocessors import Preprocessor
from markdown.extensions import Extension
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
from xml.dom import minidom
from urllib.parse import quote

# Load environment variables
load_dotenv()


# Set up the upload folder
basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['SERVER_NAME'] = 'full-stack-portfolio-hl3j.onrender.com'  # Replace with your actual domain
app.config['PREFERRED_URL_SCHEME'] = 'https'  # Or 'http' if you're not using HTTPS
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class MermaidPreprocessor(Preprocessor):
    def run(self, lines):
        new_lines = []
        is_mermaid_block = False
        for line in lines:
            if line.strip() == '```mermaid':
                is_mermaid_block = True
                new_lines.append('<pre class="mermaid">')
            elif line.strip() == '```' and is_mermaid_block:
                is_mermaid_block = False
                new_lines.append('</pre>')
            elif is_mermaid_block:
                new_lines.append(line)
            else:
                new_lines.append(line)
        return new_lines

class MermaidExtension(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.register(MermaidPreprocessor(md), 'mermaid', 175)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_archived = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def render_content(self):
        return markdown.markdown(self.content, extensions=['fenced_code', MermaidExtension()])

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_archived = db.Column(db.Boolean, default=False)
    github_link = db.Column(db.String(255))
    twitter_link = db.Column(db.String(255))
    project_files_link = db.Column(db.String(255))
    research_link = db.Column(db.String(255))
    cover_image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tech_used = db.Column(db.Text)

    def render_description(self):
        return markdown.markdown(self.description, extensions=['fenced_code', MermaidExtension()])

    def get_tech_used_list(self):
        return [tech.strip() for tech in self.tech_used.split(',')] if self.tech_used else []

class Research(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_archived = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def render_content(self):
        return markdown.markdown(self.content, extensions=['fenced_code', MermaidExtension()])

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    blogs = Blog.query.filter_by(is_archived=False).all()
    projects = Project.query.filter_by(is_archived=False).all()
    return render_template('home.html', blogs=blogs, projects=projects)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/admin')
@login_required
def admin_dashboard():
    blogs = Blog.query.all()
    projects = Project.query.all()
    research_items = Research.query.all()
    return render_template('admin_dashboard.html', blogs=blogs, projects=projects, research_items=research_items)

@app.route('/admin/blog/new', methods=['GET', 'POST'])
@login_required
def new_blog():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        new_blog = Blog(title=title, content=content, author_id=current_user.id)
        db.session.add(new_blog)
        db.session.commit()
        update_robots_txt()
        update_sitemap()
        flash('Blog post created successfully', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('new_blog.html')

@app.route('/admin/project/new', methods=['GET', 'POST'])
@login_required
def new_project():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        github_link = request.form.get('github_link')
        twitter_link = request.form.get('twitter_link')
        project_files_link = request.form.get('project_files_link')
        research_link = request.form.get('research_link')
        tech_used = request.form.get('tech_used')
        
        new_project = Project(
            title=title,
            description=description,
            author_id=current_user.id,
            github_link=github_link,
            twitter_link=twitter_link,
            project_files_link=project_files_link,
            research_link=research_link,
            tech_used=tech_used
        )
        
        # Handle file upload
        if 'cover_image' in request.files:
            file = request.files['cover_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                try:
                    if not os.path.exists(app.config['UPLOAD_FOLDER']):
                        os.makedirs(app.config['UPLOAD_FOLDER'])
                    file.save(file_path)
                    new_project.cover_image = filename
                except Exception as e:
                    flash(f'Error saving file: {str(e)}', 'error')
                    print(f'Error saving file: {str(e)}')
            else:
                flash('Invalid file type', 'error')
        
        try:
            db.session.add(new_project)
            db.session.commit()
            update_robots_txt()
            update_sitemap()
            flash('Project created successfully', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating project: {str(e)}', 'error')
            print(f'Error creating project: {str(e)}')
    
    return render_template('new_project.html')

@app.route('/admin/project/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        project.title = request.form.get('title')
        project.description = request.form.get('description')
        project.github_link = request.form.get('github_link')
        project.twitter_link = request.form.get('twitter_link')
        project.project_files_link = request.form.get('project_files_link')
        project.research_link = request.form.get('research_link')
        project.tech_used = request.form.get('tech_used')
        
        if 'cover_image' in request.files:
            file = request.files['cover_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                try:
                    if not os.path.exists(app.config['UPLOAD_FOLDER']):
                        os.makedirs(app.config['UPLOAD_FOLDER'])
                    file.save(file_path)
                    project.cover_image = filename
                except Exception as e:
                    flash(f'Error saving file: {str(e)}', 'error')
                    print(f'Error saving file: {str(e)}')
        
        db.session.commit()
        update_sitemap()
        flash('Project updated successfully', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('new_project.html', project=project)

@app.route('/admin/blog/<int:blog_id>/delete', methods=['POST'])
@login_required
def delete_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    db.session.delete(blog)
    db.session.commit()
    flash('Blog post deleted successfully', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/blog/<int:blog_id>/archive', methods=['POST'])
@login_required
def archive_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    blog.is_archived = not blog.is_archived
    db.session.commit()
    update_sitemap()
    action = 'archived' if blog.is_archived else 'unarchived'
    flash(f'Blog post {action} successfully', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/project/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted successfully', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/project/<int:project_id>/archive', methods=['POST'])
@login_required
def archive_project(project_id):
    project = Project.query.get_or_404(project_id)
    project.is_archived = not project.is_archived
    db.session.commit()
    update_sitemap()
    action = 'archived' if project.is_archived else 'unarchived'
    flash(f'Project {action} successfully', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/blog/<int:blog_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    if request.method == 'POST':
        blog.title = request.form.get('title')
        blog.content = request.form.get('content')
        db.session.commit()
        update_sitemap()
        flash('Blog post updated successfully', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('new_blog.html', blog=blog)

@app.route('/blog/<int:blog_id>')
def view_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    share_url = quote(url_for('view_blog', blog_id=blog.id, _external=True))
    share_text = quote(f"Check out this blog post: {blog.title}")
    return render_template('view_blog.html', blog=blog, share_url=share_url, share_text=share_text)

@app.route('/project/<int:project_id>')
def view_project(project_id):
    project = Project.query.get_or_404(project_id)
    share_url = quote(url_for('view_project', project_id=project.id, _external=True))
    share_text = quote(f"Check out this project: {project.title}")
    return render_template('view_project.html', project=project, share_url=share_url, share_text=share_text)

@app.route('/research')
def research():
    research_items = Research.query.filter_by(is_archived=False).order_by(Research.created_at.desc()).all()
    return render_template('research.html', research_items=research_items)

@app.route('/admin/research/new', methods=['GET', 'POST'])
@login_required
def new_research():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        new_research = Research(title=title, content=content, author_id=current_user.id)
        db.session.add(new_research)
        db.session.commit()
        update_robots_txt()
        update_sitemap()
        flash('Research item created successfully', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('new_research.html')

@app.route('/admin/research/<int:research_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_research(research_id):
    research = Research.query.get_or_404(research_id)
    if request.method == 'POST':
        research.title = request.form.get('title')
        research.content = request.form.get('content')
        db.session.commit()
        update_sitemap()
        flash('Research item updated successfully', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('new_research.html', research=research)

@app.route('/admin/research/<int:research_id>/delete', methods=['POST'])
@login_required
def delete_research(research_id):
    research = Research.query.get_or_404(research_id)
    db.session.delete(research)
    db.session.commit()
    flash('Research item deleted successfully', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/research/<int:research_id>/archive', methods=['POST'])
@login_required
def archive_research(research_id):
    research = Research.query.get_or_404(research_id)
    research.is_archived = not research.is_archived
    db.session.commit()
    update_sitemap()
    action = 'archived' if research.is_archived else 'unarchived'
    flash(f'Research item {action} successfully', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/research/<int:research_id>')
def view_research(research_id):
    research = Research.query.get_or_404(research_id)
    share_url = quote(url_for('view_research', research_id=research.id, _external=True))
    share_text = quote(f"Check out this research: {research.title}")
    return render_template('view_research.html', research=research, share_url=share_url, share_text=share_text)

def create_admin_user():
    admin_username = os.getenv('ADMIN_USERNAME')
    admin_password = os.getenv('ADMIN_PASSWORD')
    
    # Check if admin user already exists
    admin = User.query.filter_by(username=admin_username).first()
    if not admin:
        admin = User(username=admin_username, password_hash=generate_password_hash(admin_password))
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user created with username: {admin_username}")
    else:
        print("Admin user already exists")

def update_existing_blogs():
    with app.app_context():
        blogs_without_date = Blog.query.filter(Blog.created_at.is_(None)).all()
        for blog in blogs_without_date:
            blog.created_at = datetime.utcnow()
        db.session.commit()
        print(f"Updated {len(blogs_without_date)} blog posts with creation dates.")

def update_existing_projects():
    with app.app_context():
        projects_without_date = Project.query.filter(Project.created_at.is_(None)).all()
        for project in projects_without_date:
            project.created_at = datetime.utcnow()
        db.session.commit()
        print(f"Updated {len(projects_without_date)} projects with creation dates.")

def update_robots_txt():
    with open('robots.txt', 'w') as f:
        f.write("User-agent: *\n")
        f.write("Disallow:\n\n")
        f.write(f"Sitemap: {url_for('sitemap', _external=True)}\n")

def update_sitemap():
    root = ET.Element("urlset")
    root.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
    root.set("xmlns:xhtml", "http://www.w3.org/1999/xhtml")
    root.set("xmlns:image", "http://www.google.com/schemas/sitemap-image/1.1")

    # Add home page
    add_url(root, url_for('home', _external=True), changefreq="daily", priority="1.0")

    # Add blog posts
    blogs = Blog.query.filter_by(is_archived=False).order_by(Blog.created_at.desc()).all()
    for blog in blogs:
        url = add_url(root, url_for('view_blog', blog_id=blog.id, _external=True),
                      lastmod=blog.created_at,
                      changefreq="weekly",
                      priority="0.8")
        
        # Add blog post translations if available
        # add_translations(url, 'view_blog', {'blog_id': blog.id})

    # Add projects
    projects = Project.query.filter_by(is_archived=False).order_by(Project.created_at.desc()).all()
    for project in projects:
        url = add_url(root, url_for('view_project', project_id=project.id, _external=True),
                      lastmod=project.created_at,
                      changefreq="monthly",
                      priority="0.7")
        
        # Add project image
        if project.cover_image:
            image = ET.SubElement(url, "image:image")
            ET.SubElement(image, "image:loc").text = url_for('static', filename=f'uploads/{project.cover_image}', _external=True)
            ET.SubElement(image, "image:caption").text = project.title
        
        # Add project translations if available
        # add_translations(url, 'view_project', {'project_id': project.id})

    # Add research items
    research_items = Research.query.filter_by(is_archived=False).order_by(Research.created_at.desc()).all()
    for research in research_items:
        url = add_url(root, url_for('view_research', research_id=research.id, _external=True),
                      lastmod=research.created_at,
                      changefreq="monthly",
                      priority="0.7")

    # Save the sitemap
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(xml_str)

def add_url(root, loc, lastmod=None, changefreq=None, priority=None):
    url = ET.SubElement(root, "url")
    ET.SubElement(url, "loc").text = loc
    if lastmod:
        ET.SubElement(url, "lastmod").text = lastmod.replace(tzinfo=pytz.UTC).isoformat()
    if changefreq:
        ET.SubElement(url, "changefreq").text = changefreq
    if priority:
        ET.SubElement(url, "priority").text = priority
    return url

# Uncomment and implement this function if you have multi-language support
# def add_translations(url, endpoint, params):
#     for lang in ['en', 'es', 'fr']:  # Add your supported languages
#         alternate = ET.SubElement(url, "xhtml:link")
#         alternate.set("rel", "alternate")
#         alternate.set("hreflang", lang)
#         alternate.set("href", url_for(endpoint, lang_code=lang, _external=True, **params))

@app.route('/sitemap.xml')
def sitemap():
    return send_file('sitemap.xml')

@app.route('/api/posts')
def api_posts():
    blogs = Blog.query.filter_by(is_archived=False).all()
    projects = Project.query.filter_by(is_archived=False).all()
    research_items = Research.query.filter_by(is_archived=False).all()
    
    posts = []
    for blog in blogs:
        posts.append({
            'type': 'blog',
            'id': blog.id,
            'title': blog.title,
            'created_at': blog.created_at.isoformat(),
            'url': url_for('view_blog', blog_id=blog.id, _external=True)
        })
    
    for project in projects:
        posts.append({
            'type': 'project',
            'id': project.id,
            'title': project.title,
            'created_at': project.created_at.isoformat(),
            'url': url_for('view_project', project_id=project.id, _external=True)
        })
    
    for research in research_items:
        posts.append({
            'type': 'research',
            'id': research.id,
            'title': research.title,
            'created_at': research.created_at.isoformat(),
            'url': url_for('view_research', research_id=research.id, _external=True)
        })
    
    return jsonify(posts)

if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        db.create_all()
        create_admin_user()
        update_existing_blogs()
        update_existing_projects()
        update_robots_txt()
        update_sitemap()
    app.run(host='127.0.0.1', port=5000, debug=True)