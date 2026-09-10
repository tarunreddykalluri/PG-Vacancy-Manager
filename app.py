from flask import Flask
from config import Config
from extensions import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Import models so SQLAlchemy knows about all tables
    from models.building import Building
    from models.room import Room
    from models.bed import Bed
    from models.tenant import Tenant

    # Import and register routes
    from routes.main import main_bp
    from routes.buildings import buildings_bp
    from routes.rooms import rooms_bp
    from routes.tenants import tenants_bp
    from routes.vacancies import vacancies_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(buildings_bp)
    app.register_blueprint(rooms_bp)
    app.register_blueprint(tenants_bp)
    app.register_blueprint(vacancies_bp)

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)