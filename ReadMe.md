# Multimedia Game Asset API – FastAPI + MongoDB

This project is a RESTful web API developed for the Database Essentials home assignment. It uses FastAPI to manage multimedia game assets such as sprites (images), audio files, and player scores. The database is hosted on MongoDB Atlas.

---

## Development Environment Setup

- Python version: 3.13.2 (64-bit)
- Code Editor: Visual Studio Code
- Virtual Environment: Created using `venv`

### Creating the virtual environment

```
py -m venv env
env\Scripts\activate
```

### Installed Dependencies

```
pip install fastapi uvicorn motor pydantic python-dotenv requests python-multipart
```

To freeze the installed packages:

```
pip freeze > requirements.txt
```

---

## Running the API Locally

1. Activate the virtual environment:

```
env\Scripts\activate
```

2. Runinng the server:

```
uvicorn main:app --reload
```

3. Accessiing the Swagger UI:
Opened browser and navigated to:
```
http://127.0.0.1:8000/docs
```

This opens an interactive API documentation page with the following endpoints:
- `POST /upload_sprite`
- `POST /upload_audio`
- `POST /player_score`

Screenshot in Task 3A
