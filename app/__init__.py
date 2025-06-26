from flask import Flask
from flask_bootstrap import Bootstrap4  # Changed from Bootstrap

def create_app():
    app = Flask(__name__)
    
    app.config.update(
        SECRET_KEY='dev-key-change-me-later',
        UPLOAD_FOLDER='uploads',
        BOOTSTRAP_SERVE_LOCAL=True
    )
    
    # Initialize Bootstrap4 instead of Bootstrap
    bootstrap = Bootstrap4(app)  # Updated here
    
    from app.routes.upload import bp as upload_bp
    app.register_blueprint(upload_bp)
    
    import os
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app