[![Foodgram workflow](https://github.com/mizanto/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/mizanto/foodgram-project-react/actions/workflows/main.yml)

# Foodgram - Your Recipe for Success

**Foodgram** is a diploma project from the Python Backend Developer course offered by Yandex.Practicum. It is a platform where users can share their culinary recipes, follow their favorite authors, and save the best recipes in their "Favorites".

## Dependencies  
- Django 4.2 
- djangorestframework 3.14.0
- django-filter 23.2
- gunicorn 20.1.0
- Pillow 9.5.0 
- psycopg2-binary 2.9.6
- python_dotenv 1.0.0
- sqlparse 0.3.1 
- asgiref 3.6.0 
- pytz 2020.1 

## Project Structure
```
├── README.md
├── backend
│   └── src
│       ├── Dockerfile.dev
│       ├── Dockerfile.prod
│       ├── manage.py
|	├── requirements.txt
│       ├── api
│       │   └── ...
│       ├── foodgram
│       │   └── ...
│       ├── recipes
│       │   └── ...
│       └── users
│           └── ...
├── data
│   └── ...
├── docs
│   └── ...
├── infra
│   ├── docker-compose.dev.yml
│   ├── docker-compose.prod.yml
│   └── nginx.conf
└── frontend
	└── ...
```

## Local Deployment

### Cloning the repository to your local machine:
```bash
git clone git@github.com:mizanto/foodgram-project-react.git
cd foodgram-project-react
```

### Creating and activating a virtual environment
Navigate to the backend folder and create a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate
```

### Installing dependencies
While in the backend folder, install the dependencies from the requirements.txt file:
```bash
pip install -r requirements.txt
```

### Creating and configuring the .env file
Create a .env file in the infra directory. This file should contain the following variables:
```makefile
DB_NAME=<your-db-name>
POSTGRES_USER=<your-postgres-user>
POSTGRES_PASSWORD=<your-postgres-password>
POSTGRES_DB=<your-postgres-db>
DB_HOST=db
DB_PORT=5432
```

### Установка Docker и Docker-compose
Installing Docker and Docker-compose
Install Docker and Docker-compose by following the official guides on [Docker](https://docs.docker.com/engine/install/) and [Docker-compose](https://docs.docker.com/compose/install/) pages.

### Building and running containers
From the `infra` directory, run the command:
```bash
docker-compose -f docker-compose.dev.yml up -d 
```

### Preliminary setup
For the site to work correctly, migrations must be applied, and the database should be populated with initial data. Execute the following commands for setup:
```bash
# apply migrations
docker-compose -f docker-compose.dev.yml exec backend python manage.py migrate

# generate static files
docker-compose -f docker-compose.dev.yml exec backend python manage.py collectstatic --no-input

# populate the database with initial data
docker-compose -f docker-compose.dev.yml exec backend python manage.py import_basic_data ../data/

# create a superuser
docker-compose -f docker-compose.dev.yml exec backend python manage.py createsuperuser
```

## List of Endpoints

### Users
- `GET /api/users/` - retrieve a list of users
- `POST /api/users/` - create a new user
- `GET /api/users/{id}/` - retrieve information about a specific user
- `PUT /api/users/{id}/` - update information about a user
- `DELETE /api/users/{id}/` - delete a user
- `GET /api/users/me/` - retrieve information about the current user
- `GET /api/users/set_password/` - change the password of the current user
- `POST /api/auth/token/login/` - perform user login (obtain a token)
- `POST /api/auth/token/logout/` - perform user logout (delete token)

### Recipes
- `GET /api/recipes/` - retrieve a list of recipes
- `POST /api/recipes/` - create a new recipe
- `GET /api/recipes/{id}/` - retrieve information about a specific recipe
- `PUT /api/recipes/{id}/` - update information about a recipe
- `DELETE /api/recipes/{id}/` - delete a recipe

### Tag
- `GET /api/tags/` - Get a list of all tags
- `POST /api/tags/` - Create a new tag
- `GET /api/tags/{id}/` - Retrieve details of a specific tag
- `PUT /api/tags/{id}/` - Update a specific tag
- `DELETE /api/tags/{id}/` - Delete a specific tag

### Ingredients
- `GET /api/ingredients/` - Get a list of all ingredients
- `POST /api/ingredients/` - Create a new ingredient
- `GET /api/ingredients/{id}/` - Retrieve details of a specific ingredient
- `PUT /api/ingredients/{id}/` - Update a specific ingredient
- `DELETE /api/ingredients/{id}/` - Delete a specific ingredient

### Shopping Cart
- `GET /api/shopping_cart/` - Retrieve the current user's shopping cart
- `POST /api/shopping_cart/` - Add items to the shopping cart
- `DELETE /api/shopping_cart/{id}/` - Remove an item from the shopping cart

### Favorites
- `GET /api/favorites/` - Get a list of the current user's favorite recipes
- `POST /api/favorites/` - Add a recipe to favorites
- `DELETE /api/favorites/{id}/` - Remove a recipe from favorites

## Author
[Sergei Bendak](https://www.linkedin.com/in/sergey-bendak/)
