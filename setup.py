from setuptools import setup, find_packages

setup(
    name="llm_sqler",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "torch",
        "transformers",
        "peft",
        "openai",
    ],
)
