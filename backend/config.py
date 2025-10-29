import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Support both legacy DB_PATH and new data directory structure
# In Docker, data will be mounted to /app/data
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "salarium.db")

JWT_SECRET = os.environ.get("JWT_SECRET", "super-secret-change-me")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24))

CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")