#!/bin/bash

if [[ -e venv/bin/activate ]]; then
	source venv/bin/activate
else
	echo "ERROR: No se encontró el entorno virtual de Python"
	exit 1
fi

python3 -m pip install -r requirements.txt

python3 src/main.py
