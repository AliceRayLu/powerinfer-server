from setuptools import setup

setup(
    name='powerinfer-server',
    version='1.0.4',
    author='ARL',
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "paramiko>=2.11.0",
        "requests>=2.25.0",
        "tqdm>=4.61.0",
        "tabulate>=0.8.9",
        "huggingface_hub>=0.10.1",
        "cryptography>=39.0.0",
        "keyboard>=0.13.5",
    ],
    extras_require={
        ':sys_platform == "win32"': [
            "windows-curses>=2.2.1",
        ],
    },
)