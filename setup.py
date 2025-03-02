from setuptools import setup, find_packages

setup(
    name="multiagent-system",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.100.0",
        "uvicorn>=0.22.0",
        "langchain>=0.0.267",
        "openai>=1.0.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "aiohttp>=3.8.5",
        "beautifulsoup4>=4.12.2",
        "numpy>=1.24.0",
        "pillow>=10.0.0",
        "pytesseract>=0.3.10",
        "easyocr>=1.7.0",
        "weaviate-client>=3.23.0",
        "chromadb>=0.4.13",
        "huggingface_hub>=0.16.4",
        "sentence-transformers>=2.2.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A multi-agent system with specialized agents for different tasks",
    keywords="llm, agents, ai, multiagent",
    python_requires=">=3.9",
) 