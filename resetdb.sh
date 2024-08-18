#!/bin/bash

source .env

# Delete the database and create it again to make sure it is empty. Change the relevant ownership to the current user, because by default the database cannot be modified by anyone else than 'postgres' user. (All these commands are run as 'postgres' user using sudo.)
sudo -u postgres -- sh -c "cd; dropdb $TSOHA_DATABASE_NAME; createdb $TSOHA_DATABASE_NAME; psql -d $TSOHA_DATABASE_NAME -c 'ALTER SCHEMA public OWNER TO $USER;'"

psql -d $TSOHA_DATABASE_NAME < schema.sql

psql -d $TSOHA_DATABASE_NAME < testdata.sql
