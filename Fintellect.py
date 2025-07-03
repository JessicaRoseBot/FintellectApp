import os
import pandas as pd
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_bootstrap import Bootstrap4

# Initialize Flask app
app = Flask(__name__, template_folder='templates')

# Configuration
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-key-change-me-later'),
    UPLOAD_FOLDER=os.path.abspath('uploads'),
    BOOTSTRAP_SERVE_LOCAL=True
)

# Initialize extensions
bootstrap = Bootstrap4(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --------------------------
# Routes
# --------------------------

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
            
        if file and file.filename.endswith('.csv'):
            try:
                df = process_statement(file)
                # Save processed data temporarily (example)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'processed.csv')
                df.to_csv(filepath)
                flash('File processed successfully!', 'success')
                return redirect(url_for('show_results'))
            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'error')
    
    return render_template('upload.html')

@app.route('/results')
def show_results():
    # Example: Display processed data
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'processed.csv')
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        return render_template('results.html', tables=[df.to_html(classes='data')])
    else:
        flash('No processed data found', 'error')
        return redirect(url_for('upload_file'))

# --------------------------
# Helper Functions
# --------------------------

def process_statement(file_stream):
    """Convert bank CSV to cleaned DataFrame"""
    df = pd.read_csv(file_stream)
    
    # Standardize columns
    df.columns = df.columns.str.lower()
    required_cols = ['date', 'description', 'amount']
    if not all(col in df.columns for col in required_cols):
        raise ValueError("CSV missing required columns")
    
    # Clean data
    df['date'] = pd.to_datetime(df['date'])
    df['amount'] = df['amount'].astype(float)
    
    return df

# --------------------------
# Run the App
# --------------------------

if __name__ == '__main__':
    app.run(debug=True)