from flask import Flask, render_template
from flask_login import LoginManager
from config import Config
from models import db
from models.user import User

# Blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.shopping_lists import shopping_lists_bp
from routes.shopping_items import shopping_items_bp
from routes.reports import reports_bp
from routes.history import history_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access your Smart Shopping List.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(shopping_lists_bp)
    app.register_blueprint(shopping_items_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(history_bp)

    @app.route('/')
    def landing_page():
        return render_template('landing.html')

    # Context processors
    @app.context_processor
    def inject_globals():
        return {
            'app_name': 'Smart Shopping List'
        }

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    print("Starting Smart Shopping List on http://127.0.0.1:5000 ...")
    app.run(host='0.0.0.0', port=5000, debug=True)
