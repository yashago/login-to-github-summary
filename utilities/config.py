import os
from dotenv import load_dotenv

load_dotenv()  # loads .env if it exists; real environment variables take priority

DEFAULT_TIMEOUT_MS = int(os.getenv("DEFAULT_TIMEOUT_MS", "15000"))

GITHUB_URL = "https://www.github.com"
TEST_EMAIL = os.getenv("TEST_JACOB_EMAIL")
TEST_PASSWORD = os.getenv("TEST_JACOB_PASSWORD")
