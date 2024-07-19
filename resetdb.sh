#!/bin/bash
source .env
sudo -u postgres -- sh -c "dropdb $TSOHA_DATABASE_NAME; createdb $TSOHA_DATABASE_NAME; psql -d $TSOHA_DATABASE_NAME -c 'ALTER SCHEMA public OWNER TO $USER;'"
