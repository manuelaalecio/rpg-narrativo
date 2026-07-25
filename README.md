# RPG Narrativo

Jogo de texto (Text Adventure / RPG Narrativo) em Python com interface gráfica PySide6.

## Pré-requisitos

- Python 3.11+

## Configuração do ambiente

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
```

## Instalação

```bash
pip install -e ".[dev]"
```

## Executar o projeto

```bash
python main.py
```

## Testes

```bash
pytest
```

Com cobertura:

```bash
pytest --cov=. --cov-report=term-missing
```
