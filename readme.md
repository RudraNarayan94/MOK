# Master Of Keys

Welcome to our Typing Website! This platform is designed to help users improve their typing speed and accuracy through engaging and interactive exercises.

## Features

- **Typing Practice**: Improve your typing skills with real-time feedback.
- **Progress Tracking**: Monitor your typing speed and accuracy over time.
- **User Authentication**: Secure login and registration system.
- **Responsive Design**: Seamless experience across devices.

## Tech Stack

- **Backend**: Django
- **Frontend**: React
- **Database**: SQLite (development) / PostgreSQL (production)
- **API**: RESTful API using Django REST Framework

## Installation



### Backend Setup

1. Clone the repository:

```bash
git clone https://github.com/your-repo/typing-website.git
cd typing-website/backend
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run migrations:

```bash
python manage.py migrate
```

5. Start the development server:

```bash
python manage.py runserver
```

### Frontend Setup

1. Navigate to the frontend directory:

```bash
cd ../frontend
```

2. Install dependencies:

```bash
npm install
```

3. Start the development server:

```bash
npm start
```

## Usage

1. Open your browser and navigate to `http://localhost:3000` for the frontend.
2. The backend API runs at `http://localhost:8000`.

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes and push the branch.
4. Submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

For any questions or feedback, please contact us at `support@example.com`.

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
