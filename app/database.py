from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from . import config

settings = config.Settings()

# SQLALCHEMY_DATABASE_URL = "postgresql://<username>:<password>@<ip-address/hostname>/<database_name>"
SQLALCHEMY_DATABASE_URL = (
    "postgresql://{username}:{password}@{hostname}:{port}/{database_name}".format(
        username=settings.database_username,
        password=settings.database_password,
        hostname=settings.database_hostname,
        port=settings.database_port,
        database_name=settings.database_name,
    )
)

# Establishes connection with DB
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Handles session w/ DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models to have methods to interact with session

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# while True:
#     try:
#         conn = psycopg2.connect(
#             host="localhost",
#             database="fastapi",
#             user="postgres",
#             password="w1l4a7d8k9b10c11r12",
#             cursor_factory=RealDictCursor,
#         )
#         cursor = conn.cursor()
#         print("Database connection was successfull")
#         break
#     except Exception as e:
#         print("Connecting to database failed with error: {}".format(e))
#         time.sleep(2)
