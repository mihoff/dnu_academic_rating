# DNU Academic Rating

A Django-based web application for calculating academic ratings based on the official strategy. This system provides a comprehensive solution for managing and calculating academic performance metrics.

## Features

- Academic rating calculations based on official strategy
- Microsoft OAuth integration for authentication
- User profile management
- Feedback system
- Responsive web interface using django-tables2

## Technical Stack

- Python 3.10
- Django 3.2.16
- Microsoft Authentication
- Gunicorn for production deployment
- WhiteNoise for static file serving

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd dnu_academic_rating
```

2. Install dependencies:
```bash
python setup.py install
```

3. Configure your environment variables and settings

4. Run migrations:
```bash
python manage.py migrate
```

5. Start the development server:
```bash
python manage.py runserver
```

## Project Structure

- `academic_rating/` - Main Django project configuration
- `user_profile/` - User profile management
- `system_app/` - Core system functionality
- `service_api/` - API endpoints
- `proxy_microsoft_oauth/` - Microsoft OAuth integration
- `feedbacks/` - Feedback system
- `templates/` - HTML templates
- `locale/` - Internationalization files - OUT OF SUPPORT

## Development

The project uses pylint for code quality checks. Run pylint with:
```bash
pylint --rcfile=.pylintrc .
```
