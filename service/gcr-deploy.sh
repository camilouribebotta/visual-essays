#!/bin/bash

rm -rf build
mkdir build
rsync -va --exclude=venv --exclude=__pycache__ src Dockerfile ../index.html viewer.html ../images/favicon.ico build
cd build
gcloud builds submit --tag gcr.io/visual-essay/visual-essay
gcloud beta run deploy visual-essay --image gcr.io/visual-essay/visual-essay --allow-unauthenticated --platform managed --memory 1Gi
