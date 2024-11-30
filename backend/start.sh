#!/bin/bash

# install requirements
pip install -r requirements.txt

# load German spaCy-model
python -m spacy download de_core_news_sm

# start flask-app with Gunicorn
gunicorn app:app