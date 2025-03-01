# FoodZone - Full Stack Food Ordering System

## Overview
FoodZone is a full-stack food ordering system built using Django. It provides a seamless experience for users to browse, order, and manage food items while supporting real-time updates and secure authentication. The system integrates Google authorization, CRUD operations, PostgreSQL as the database, and load balancing for efficient performance.

## Features
- **User Authentication:** Secure user authentication with email and Google OAuth.
- **CRUD Operations:** Users can create, read, update, and delete food items.
- **PostgreSQL Database:** Scalable and reliable database for storing user and order details.
- **Load Balancing:** Optimized performance with load balancing strategies.
- **Order Management:** Real-time order tracking and status updates.
- **Admin Panel:** Manage users, food items, and orders efficiently.
- **Responsive UI:** Fully responsive frontend for smooth user experience.

## Technologies Used
- **Backend:** Django, Django REST Framework
- **Frontend:** HTML, CSS, JavaScript (Optional React integration)
- **Database:** PostgreSQL
- **Authentication:** Django authentication, Google OAuth
- **Deployment:** Load balancing with Nginx/Gunicorn

## Installation
### Prerequisites
- Python (>=3.8)
- PostgreSQL
- Virtual environment (optional but recommended)

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/foodzone.git
   cd foodzone
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Mac/Linux
   venv\Scripts\activate  # For Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up PostgreSQL database and update `settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'your_db_name',
           'USER': 'your_db_user',
           'PASSWORD': 'your_db_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. Create a superuser (for admin access):
   ```bash
   python manage.py createsuperuser
   ```
7. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Google OAuth Setup
1. Go to [Google Developer Console](https://console.cloud.google.com/).
2. Create a new project and enable Google OAuth.
3. Obtain client ID and secret.
4. Add credentials to `settings.py`:
   ```python
   SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'your-client-id'
   SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'your-client-secret'
   ```
5. Configure OAuth callback URL in Google Developer Console:
   ```
   http://localhost:8000/accounts/google/login/callback/
   ```

## Load Balancing Setup
- Use **Nginx** as a reverse proxy to distribute traffic across multiple instances of Gunicorn workers.
- Example Nginx configuration:
  ```nginx
  upstream app_servers {
      server 127.0.0.1:8001;
      server 127.0.0.1:8002;
  }
  server {
      listen 80;
      server_name yourdomain.com;
      location / {
          proxy_pass http://app_servers;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      }
  }
  ```

## API Endpoints (Sample)
| Method | Endpoint              | Description                 |
|--------|----------------------|-----------------------------|
| POST   | /auth/login/         | User login                  |
| GET    | /auth/logout/        | User logout                 |
| GET    | /food/               | Get all food items          |
| POST   | /food/add/           | Add a new food item         |
| PUT    | /food/update/<id>/   | Update food item            |
| DELETE | /food/delete/<id>/   | Delete food item            |

## Deployment
To deploy the application:
1. Set up a production server with Nginx and Gunicorn.
2. Configure PostgreSQL database.
3. Use `supervisor` to manage the Django application.
4. Enable HTTPS with Let's Encrypt.

## Contributors
- **Sayandeb Sarkar** (Lead Developer)

## License
This project is licensed under the MIT License.

