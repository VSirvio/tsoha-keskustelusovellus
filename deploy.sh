#!/bin/bash
source .env
ssh -i $PRIVATE_KEY_FILE $LOGIN_INFO '
  cd ~/'$REPOSITORY_NAME';
  git fetch --all;
  git reset --hard origin/main;
  source venv/bin/activate;
  pip install -r ./requirements.txt;
  killall -9 gunicorn;
  ./resetdb.sh;
  gunicorn --bind 0.0.0.0:5000 app:app &> ../gunicorn.log &
'
