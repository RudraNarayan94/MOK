## Running the Background Tasks

1. Start Redis Server:

```bash
# Windows (WSL or Redis Windows)
redis-server

# Linux/Mac
sudo service redis-server start
```

2. Start Celery Worker:

```bash
# From Backend/project directory
celery -A core worker -l info
```

3. Start Django Server:

```bash
python manage.py runserver
```
