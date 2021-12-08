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
Just execute the command line as follow to see how to use:

```bash
python src/sgbikecrawler/cli.py --help
```

For example, to search for a specific bike model:

```bash
 python3 src/sgbikecrawler/cli.py --model="KTM Duke 200"
```

To output results to csv:
```bash
 python3 src/sgbikecrawler/cli.py --model="KTM Duke 200" --csv
```