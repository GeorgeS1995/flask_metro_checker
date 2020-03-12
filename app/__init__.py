from .app import app, db
from .models import Station
from flask_migrate import Migrate
from . import api_v1_bp

migrate = Migrate(app, db)

app.register_blueprint(api_v1_bp.bp)

if __name__ == '__main__':
    app.run()

