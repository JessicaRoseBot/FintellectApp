# Import required modules
import os  # For operating system interactions (file paths, environment variables)
from flask import Flask  # Flask core framework
from flask_bootstrap import Bootstrap4  # Bootstrap integration (version 4)

def create_app():
    """Factory function that creates and configures the Flask application"""
    
    # 1. FLASK APP INITIALIZATION
    app = Flask(
        __name__,  # Use the current module as the application name
        # Set absolute path to templates folder to avoid path resolution issues
        template_folder=os.path.abspath('app/templates')  
    )
    
    # 2. APPLICATION CONFIGURATION
    app.config.update(
        # Secret key for session security - loaded from environment variables
        SECRET_KEY=os.environ['SECRET_KEY'],
        # Absolute path for file uploads directory
        UPLOAD_FOLDER=os.path.abspath('uploads'),
        # Serve Bootstrap files locally rather than from CDN
        BOOTSTRAP_SERVE_LOCAL=True  
    )
    
    # 3. EXTENSIONS INITIALIZATION
    bootstrap = Bootstrap4(app)  # Initialize Flask-Bootstrap extension
    
    # 4. BLUEPRINT REGISTRATION
    # Import upload blueprint from routes
    from app.routes.upload import bp as upload_bp
    # Register the blueprint with the application
    app.register_blueprint(upload_bp)
    
    # 5. FILE SYSTEM PREPARATION
    # Create uploads directory if it doesn't exist
    # exist_ok=True prevents errors if directory already exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Return the fully configured application instance
    return app