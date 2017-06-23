from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from app.app import db, create_app


app = create_app(config_name="development")
migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command("db", MigrateCommand)

if __name__ == "__main__":
    manager.run()
    db.create_all()
