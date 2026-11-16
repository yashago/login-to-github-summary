import os

import pytest
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # pick up OPENAI_API_KEY from .env if present

if not os.getenv("OPENAI_API_KEY"):
    pytest.skip("OPENAI_API_KEY not set", allow_module_level=True)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TEST_STRING = "Suggest test cases for a login page."

def test_open_ai_temp_02():
    response = creteOpenAiResponse(0.2, TEST_STRING)
    assert response.output_text

def test_open_ai_temp_06():
    response = creteOpenAiResponse(0.6, TEST_STRING)
    assert response.output_text


def creteOpenAiResponse(temp, inputString):
    return client.responses.create(
        model="gpt-4.1",
        input=inputString,
        temperature=temp
    )