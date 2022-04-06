from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell
from edubackend.main import app
from common.models import db
from common.models.models import *

manage = Manager(app)
migrate = Migrate(app, db)
manage.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manage.run()