import os
from dotenv import load_dotenv

load_dotenv()

# pg8000 is a pure Python PostgreSQL driver (no compilation needed on Windows)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+pg8000://postgres:12.34.qw.er.@45.88.137.131:5432/gps")
