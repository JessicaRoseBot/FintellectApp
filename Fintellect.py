import os
import pandas as pd
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_bootstrap import Bootstrap4
import plotly.express as px
from werkzeug.utils import secure_filename
import numpy as np  

# Initialize Flask app
app = Flask(__name__, template_folder='templates')

# Configuration
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-key-change-me-later'),
    UPLOAD_FOLDER=os.path.abspath('uploads'),
    BOOTSTRAP_SERVE_LOCAL=True,
    ALLOWED_EXTENSIONS={'csv'} 
)

# Initialize extensions
bootstrap = Bootstrap4(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ======================
# Helper Functions
# ======================

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def process_statement(file_stream):
    """Process Chase bank CSV with custom field handling"""
    df = pd.read_csv(file_stream)
    
    # Standardize column names
    df.columns = [col.lower().strip() for col in df.columns]
    
    # Field mapping specific to Chase format
    column_mapping = {
        'transaction date': 'date',
        'description': 'description',
        'amount': 'amount',
        'category': 'bank_category',
        'type': 'transaction_type'
    }
    # Only rename columns that exist in the dataframe
    df = df.rename(columns={k:v for k,v in column_mapping.items() if k in df.columns})
    
    # Required fields check
    required = ['date', 'description', 'amount']
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    
    # Data cleaning
    df['amount'] = df['amount'].replace('[\$,]', '', regex=True).astype(float)
    df['date'] = pd.to_datetime(df['date'])
    
    # Enhanced categorization - with fallback to bank categories
    food_keywords = ['restaurant', 'cafe', 'coffee', 'bar', 'grill', 'eat', 'food', 'dining',
                   'pizza', 'burger', 'starbucks', 'peets', 'egg', 'thai', 'grill', 'panda']
    
    # Initialize auto_category with bank_category if it exists, otherwise 'Uncategorized'
    if 'bank_category' in df.columns:
        df['auto_category'] = df['bank_category']
    else:
        df['auto_category'] = 'Uncategorized'
    
    # Apply food categorization
    food_mask = df['description'].str.contains('|'.join(food_keywords), case=False, na=False)
    df.loc[food_mask, 'auto_category'] = 'Eating Out'
    
    # Special handling for grocery stores
    grocery_keywords = ['wholefds', 'trader joe', 'king soopers']
    grocery_mask = df['description'].str.contains('|'.join(grocery_keywords), case=False, na=False)
    df.loc[grocery_mask, 'auto_category'] = 'Groceries'
    
    # Special handling for Amazon
    amazon_mask = df['description'].str.contains('amazon', case=False, na=False)
    df.loc[amazon_mask, 'auto_category'] = 'Amazon'
    df['needs_review'] = amazon_mask  # Flag Amazon purchases for review
    
    # Type normalization
    type_mapping = {'sale': 'Expense', 'payment': 'Income', 'return': 'Income'}
    if 'transaction_type' in df.columns:
        df['transaction_type'] = df['transaction_type'].str.lower().map(type_mapping).fillna('Unknown')
    
    # Select final columns
    keep_cols = ['date', 'description', 'amount', 'auto_category', 
                'bank_category', 'transaction_type', 'needs_review']
    return df[[col for col in keep_cols if col in df.columns]]


# ======================
# Routes
# ======================

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
            
        if file and allowed_file(file.filename):
            try:
                # Secure the filename before saving
                filename = secure_filename(file.filename)
                temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(temp_path)
                
                # Process and save
                df = process_statement(temp_path)
                processed_path = os.path.join(app.config['UPLOAD_FOLDER'], 'processed.csv')
                df.to_csv(processed_path, index=False)
                
                flash('File processed successfully!', 'success')
                return redirect(url_for('dashboard'))  # <-- Fixed redirect
                
            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'error')
        else:
            flash('Only CSV files allowed', 'error')
    
    return render_template('upload.html')

@app.route('/dashboard')
def dashboard():
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'processed.csv')
        df = pd.read_csv(filepath)
        
        # Ensure required columns exist
        required_cols = ['date', 'amount', 'auto_category']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise ValueError(f"Missing columns: {', '.join(missing)}")
        
        # Create visualizations
        charts = {}
        charts['pie'] = px.pie(df, values='amount', names='auto_category',
                             title='Spending by Category').to_html(full_html=False)
        
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])  # Ensure datetime
            charts['timeline'] = px.line(df, x='date', y='amount',
                                       title='Daily Spending').to_html(full_html=False)
        
        return render_template('dashboard.html', **charts)
        
    except Exception as e:
        flash(f'Dashboard error: {str(e)}', 'error')
        return redirect(url_for('upload_file'))

@app.route('/results')
def show_results():
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'processed.csv')
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        return render_template('results.html', tables=[df.to_html(classes='data')])
    else:
        flash('No processed data found', 'error')
        return redirect(url_for('upload_file'))

if __name__ == '__main__':
    app.run(debug=False)