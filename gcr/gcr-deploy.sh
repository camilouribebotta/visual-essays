#!/bin/bash

gcloud builds submit --tag gcr.io/visual-essay/visual-essay
gcloud beta run deploy visual-essay --image gcr.io/visual-essay/visual-essay --allow-unauthenticated --platform managed --memory 1Gi
