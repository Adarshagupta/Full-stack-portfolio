#### Overview
This Flask application is a comprehensive full-stack portfolio website that includes features for managing blogs, projects, and research items. The application is designed to be user-friendly, with an admin dashboard for managing content and a public-facing interface for viewing content. The application also includes SEO optimizations, such as updating the `robots.txt` and `sitemap.xml` files automatically.
![Screenshot](https://adarshgupta.onrender.com/static/uploads/Screenshot_2024-09-15_182844.png)
#### Key Features

1. **User Authentication and Authorization**
   - **Flask-Login**: Manages user sessions and provides decorators for protecting routes.
   - **User Model**: Stores user information, including username and hashed password.
   - **Login/Logout**: Routes for user login and logout.

2. **Content Management**
   - **Blogs**: CRUD operations for blog posts, including archiving and deletion.
   - **Projects**: CRUD operations for projects, including file uploads for cover images.
   - **Research**: CRUD operations for research items.

3. **SEO and Sitemap**
   - **Robots.txt**: Automatically updates to allow all bots and include the sitemap URL.
   - **Sitemap.xml**: Automatically generates a sitemap with URLs for blogs, projects, and research items.

4. **Advanced Search**
   - **Query Parameters**: Supports advanced search with filters for category, tags, date range, and query text.
   - **Search Results**: Displays search results across blogs, projects, and research items.

5. **Markdown Support**
   - **Mermaid Extension**: Allows for rendering Mermaid diagrams within Markdown content.
   - **Fenced Code Blocks**: Supports syntax highlighting for code blocks.

6. **API**
   - **API Endpoint**: Provides a JSON API for retrieving posts (blogs, projects, research items).

#### Code Structure

1. **Models**
   - **User**: Represents a user with a username and password hash.
   - **Blog**: Represents a blog post with title, content, author, and creation date.
   - **Project**: Represents a project with title, description, links, cover image, and creation date.
   - **Research**: Represents a research item with title, content, author, and creation date.

2. **Routes**
   - **Home**: Displays the home page with recent blogs and projects.
   - **Login/Logout**: Handles user authentication.
   - **Admin Dashboard**: Displays all content for management.
   - **CRUD Routes**: Routes for creating, reading, updating, and deleting blogs, projects, and research items.
   - **View Routes**: Routes for viewing individual blogs, projects, and research items.
   - **Search**: Route for advanced search functionality.
   - **API**: Route for retrieving posts via a JSON API.

3. **Utilities**
   - **Mermaid Preprocessor**: Custom Markdown preprocessor for handling Mermaid diagrams.
   - **Robots.txt and Sitemap.xml**: Functions to update these files based on content changes.
   - **File Upload**: Function to handle file uploads for project cover images.

#### Potential Improvements

1. **Multi-Language Support**
   - Implement multi-language support by adding language codes to URLs and updating the `add_translations` function.

2. **Pagination**
   - Implement pagination for the admin dashboard and search results to handle large amounts of content.

3. **User Roles**
   - Implement user roles (e.g., admin, editor) to restrict access to certain features.

4. **Testing**
   - Add unit tests and integration tests to ensure the application functions correctly.

5. **Deployment**
   - Configure the application for deployment on a production server (e.g., using Gunicorn, Nginx).

### Installation and Setup Guide

#### Prerequisites
Before setting up the Flask application, ensure you have the following installed:

- Python 3.7 or higher
- pip (Python package installer)
- Virtualenv (optional but recommended)
- Git (for version control)

#### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
   ```

2. **Set Up a Virtual Environment (Optional but Recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**
   Create a `.env` file in the root directory of your project and add the following variables:
   ```env
   SECRET_KEY=your_secret_key
   DATABASE_URL=sqlite:///site.db  # or your preferred database URL
   ADMIN_USERNAME=your_admin_username
   ADMIN_PASSWORD=your_admin_password
   ```

5. **Initialize the Database**
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

6. **Run the Application**
   ```bash
   flask run
   ```

#### Running the Application Locally vs. Hosting

##### Running Locally
- **Database**: Use a local SQLite database (`sqlite:///site.db`).
- **Environment Variables**: Set the `DATABASE_URL` to point to your local SQLite database.
- **File Uploads**: Ensure the `UPLOAD_FOLDER` is set to a local directory.
- **Debug Mode**: Run the application in debug mode for easier development (`flask run --debug`).

##### Hosting Your Own Website
- **Database**: Use a production-ready database (e.g., PostgreSQL, MySQL). Update the `DATABASE_URL` in your `.env` file accordingly.
- **Environment Variables**: Ensure all necessary environment variables are set in your hosting environment.
- **File Uploads**: Ensure the `UPLOAD_FOLDER` is set to a directory accessible by your web server.
- **Web Server**: Use a production-ready web server like Gunicorn.
- **HTTPS**: Ensure your application is served over HTTPS.

#### Example for Hosting with Gunicorn

1. **Install Gunicorn**
   ```bash
   pip install gunicorn
   ```

2. **Run the Application with Gunicorn**
   ```bash
   gunicorn -w 4 'your_repo:create_app()'
   ```

3. **Set Up Nginx (Optional)**
   Configure Nginx as a reverse proxy to serve your application over HTTPS.

   Example Nginx configuration:
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

#### Additional Configuration

1. **HTTPS Configuration**
   - Ensure your domain is configured to use HTTPS.
   - Update the `PREFERRED_URL_SCHEME` in your Flask configuration to `https`.

2. **Static Files**
   - Ensure your static files (CSS, JS, images) are served correctly.
   - Use a CDN for better performance if hosting static files on your server.

3. **Logging**
   - Configure logging for production to monitor your application's performance and errors.

4. **Security**
   - Use environment variables for sensitive information.
   - Regularly update dependencies to patch security vulnerabilities.

#### Conclusion
By following these steps, you can set up and run the Flask application locally or host it on your own server. Ensure you configure the environment variables and settings appropriately for your specific use case.
