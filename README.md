# sgbikecrawler

A crawler to compare bike prices across different Singapore websites

## Setup your environment

(prerequisites: install pyenv and virtualenv)

1. Create your virtual environment (choose your 3.x python version)

```bash
pyenv virtualenv 3.8.3 venv-sgbikecrawler
```

1. Activate your virtual environment

```bash
pyenv activate venv-sgbikecrawler
```

1. Install dependencies

```bash
pip install -r requirements.txt
```

## Running the script
Just execute the command line as follow:

```bash
python src/sgbikecrawler/sgbike_crawler.py
```
