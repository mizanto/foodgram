[![Foodgram workflow](https://github.com/mizanto/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/mizanto/foodgram-project-react/actions/workflows/main.yml)

# Foodgram - Ваш рецепт успеха
[Foodgram]() - это проект, в котором пользователи могут делиться своими кулинарными рецептами, а также подписываться на понравившихся авторов и сохранять лучшие рецепты в своих "Избранных".

## Доступ в админку
#### Почта: `admin@admin.co`
#### Пароль: `admin`

## Зависимости  
- Django==4.2 
- djangorestframework==3.14.0
- django-filter==23.2
- gunicorn==20.1.0
- Pillow==9.5.0 
- psycopg2-binary==2.9.6
- python_dotenv==1.0.0
- sqlparse==0.3.1 
- asgiref==3.6.0 
- pytz==2020.1 

## Структура проекта
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

## Локальное развертывание

### Клонирование репозитория на локальный компьютер:
```bash
git clone git@github.com:mizanto/foodgram-project-react.git
cd foodgram-project-react
``` 
### Создание виртуального и активация окружения
Перейдите в папку `backend` и создайте виртуальное окружение:
```bash
cd backend
python -m venv venv
source venv/bin/activate
```

### Установка зависимостей
Находясь в папке `backend` установите зависимости из файла `requirements.txt`:

```bash
pip install -r requirements.txt
```
### Создание и настройка `.env` файла
Создайте файл `.env` в папке `infra`. Этот файл должен содержать следующие переменные:

```makefile
DB_NAME=<your-db-name>
POSTGRES_USER=<your-postgres-user>
POSTGRES_PASSWORD=<your-postgres-password>
POSTGRES_DB=<your-postgres-db>
DB_HOST=db
DB_PORT=5432
```
### Установка Docker и Docker-compose
Установите Docker и Docker-compose, следуя официальным руководствам на страницах [Docker](https://docs.docker.com/engine/install/) и [Docker-compose](https://docs.docker.com/compose/install/).

### Сборка и запуск контейнеров
Из папки `infra` запустите команду
```bash
docker-compose -f docker-compose.dev.yml up -d 
```
### Предварительная настройка
Для того чтобы сайт работал корректно - необходимо выполнить миграции и наполнить его содержимым. Для этого необходимо выполнить следующие команды:
```bash
# применить миграции
docker-compose -f docker-compose.dev.yml exec backend python manage.py migrate

# сгенерировать статику 
docker-compose -f docker-compose.dev.yml exec backend python manage.py collectstatic --no-input

# наполнить базу данных содержимым
docker-compose -f docker-compose.dev.yml exec backend python manage.py import_basic_data ../data/

# создать суперпользователя
docker-compose -f docker-compose.dev.yml exec backend python manage.py createsuperuser
```

## Список эндпоинтов

### Эндпоинты API пользователей (`/api/users/`)
-   `GET /api/users/` - получить список пользователей
-   `POST /api/users/` - создать нового пользователя
-   `GET /api/users/{id}/` - получить информацию о конкретном пользователе
-   `PUT /api/users/{id}/` - обновить информацию о пользователе
-   `DELETE /api/users/{id}/` - удалить пользователя
-   `GET /api/users/me/` - получить информацию о текущем пользователе
-   `GET /api/users/set_password/` - изменить пароль текущего пользователя
-   `POST /api/auth/token/login/` - выполнить вход пользователя (получить токен)
-   `POST /api/auth/token/logout/` - выполнить выход пользователя (удалить токен)

### Эндпоинты API рецептов (`/api/recipes/`)
-   `GET /api/recipes/` - получить список рецептов
-   `POST /api/recipes/` - создать новый рецепт
-   `GET /api/recipes/{id}/` - получить информацию о конкретном рецепте
-   `PUT /api/recipes/{id}/` - обновить информацию о рецепте
-   `DELETE /api/recipes/{id}/` - удалить рецепт

### Эндпоинты API тегов (`/api/tags/`)
-   `GET /api/tags/` - получить список тегов
-   `POST /api/tags/` - создать новый тег
-   `GET /api/tags/{id}/` - получить информацию о конкретном теге
-   `PUT /api/tags/{id}/` - обновить информацию о теге
-   `DELETE /api/tags/{id}/` - удалить тег

### Эндпоинты API ингредиентов (`/api/ingredients/`)
-   `GET /api/ingredients/` - получить список ингредиентов
-   `POST /api/ingredients/` - создать новый ингредиент
-   `GET /api/ingredients/{id}/` - получить информацию о конкретном ингредиенте
-   `PUT /api/ingredients/{id}/` - обновить информацию об ингредиенте
-   `DELETE /api/ingredients/{id}/` - удалить ингредиент

## Автор
[Сергей Бендак](https://www.linkedin.com/in/sergey-bendak/)
