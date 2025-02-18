from setuptools import setup, find_packages

setup(
    name='attention_bci',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        # API Dependencies
        'fastapi>=0.75.0',
        'uvicorn>=0.17.0',
        'websockets>=10.0',
        'aiofiles>=0.8.0',
        'python-multipart>=0.0.5',
        'pydantic-settings>=2.0.0',

        # Scientific Computing
        'numpy>=1.19.0',
        'pandas>=1.2.0',
        'scipy>=1.6.0',
        'scikit-learn>=0.24.0',
        'mne>=0.23.0',
        'PyWavelets>=1.1.0',
    ],
    extras_require={
        'dev': [
            # Testing
            'pytest>=7.0.0',
            'pytest-asyncio>=0.18.0',
            'pytest-cov>=4.1.0',
            'httpx>=0.24.1',
            'requests>=2.31.0',
            
            # Development Tools
            'black>=23.0.0',
            'isort>=5.12.0',
            'flake8>=6.0.0',
            'mypy>=1.5.0',
            'pytest-watch>=4.2.0'
        ]
    },
    python_requires='>=3.8',
)