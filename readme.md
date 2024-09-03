# Personal Portfolio Website

This project is a personal portfolio website built with Flask, featuring a blog and project showcase.

## Features

- Blog post management
- Project showcase
- Admin dashboard
- Markdown support with Mermaid diagrams
- Image upload for project cover images

## Technologies Used

- Python
- Flask
- SQLAlchemy
- Flask-Login
- Markdown
- Bootstrap
- Docker

## Setup and Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the project root and add the following:
   ```bash
   SECRET_KEY=your_secret_key
   DATABASE_URL=sqlite:///site.db
   ADMIN_USERNAME=your_admin_username
   ADMIN_PASSWORD=your_admin_password
   ```

5. Initialize the database:
   ```bash
   flask db upgrade
   ```

6. Run the application:
   ```bash
   python app.py
   ```

## Docker Support

To run the application using Docker:

1. Build the Docker image:
   ```bash
   docker build -t portfolio-website .
   ```

2. Run the container:
   ```bash
   docker run -p 5000:5000 portfolio-website
   ```

## Usage

- Access the website at `http://localhost:5000`
- Log in to the admin dashboard at `http://localhost:5000/login`
- Use the admin dashboard to create, edit, and manage blog posts and projects

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
#   f u l l s t a c k - b l o g - p r o j e c t 
 
 #   f u l l s t a c k - b l o g - p r o j e c t 
 
 