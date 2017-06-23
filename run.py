#!./bl-env/bin/python

from app.app import create_app

config_name = "development"
app = create_app("development")

if __name__ == "__main__":
    app.run()
