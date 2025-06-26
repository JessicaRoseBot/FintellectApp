# AI-Assisted
from flask import Blueprint, render_template, request, flash, redirect, url_for
import pandas as pd
from app.utils.file_processor import process_statement

bp = Blueprint('upload', __name__)

@bp.route('/', methods=['GET', 'POST']) 
def upload():
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
                # Process the file
                df = process_statement(file)
                # Store in session (temporarily)
                return redirect(url_for('preview.show'))
            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'error')
    
    return render_template('upload.html')