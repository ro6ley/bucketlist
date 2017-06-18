#!./bl-env/bin/python

import os

# from app.views import create_app
from app.app import create_app

config_name = "development"
# config_name = os.getenv('APP_SETTINGS')
app = create_app("development")

if __name__ == "__main__":
    app.run()
