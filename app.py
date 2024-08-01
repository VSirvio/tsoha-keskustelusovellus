import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']

import routes  # pylint: disable=wrong-import-position,unused-import
