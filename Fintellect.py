# Import all necessary packages
import os
import pandas as pd
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_bootstrap import Bootstrap
import plotly.express as px
from werkzeug.utils import secure_filename
from flask import jsonify

# Initialize Flask app
app = Flask(__name__, template_folder='templates')
bootstrap = Bootstrap(app)

# Configuration
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-key-change-me-later'),
    UPLOAD_FOLDER=os.path.abspath('uploads'),
    BOOTSTRAP_SERVE_LOCAL=True,
    ALLOWED_EXTENSIONS={'csv'} 
)

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
    
    # Field mapping specific to Chase Bank export format
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
    df['amount'] = df['amount'].replace(r'[\$,]', '', regex=True).astype(float)
    df['date'] = pd.to_datetime(df['date'])
    
    # Enhanced categorization (work in progress)
    food_keywords = ['restaurant', 'cafe', 'coffee', 'bar', 'grill', 'eat', 'food', 'dining',
                   'pizza', 'burger', 'starbucks', 'peets', 'egg', 'thai', 'grill', 'panda']
    
    grocery_keywords = ['wholefds', 'trader joe', 'king soopers']
    
    # Initialize auto_category
    if 'bank_category' in df.columns:
        df['auto_category'] = df['bank_category']
    else:
        df['auto_category'] = 'Uncategorized'
    
    # Apply categorization rules
    food_mask = df['description'].str.contains('|'.join(food_keywords), case=False, na=False)
    grocery_mask = df['description'].str.contains('|'.join(grocery_keywords), case=False, na=False)
    amazon_mask = df['description'].str.contains('amazon', case=False, na=False)
    
    df.loc[food_mask, 'auto_category'] = 'Eating Out'
    df.loc[grocery_mask, 'auto_category'] = 'Groceries'
    df.loc[amazon_mask, 'auto_category'] = 'Amazon'
    df['needs_review'] = amazon_mask
    
    # Remove payments before type normalization
    if 'transaction_type' in df.columns:
        df = df[~df['transaction_type'].str.lower().eq('payment')]
    
    # Then proceed with type normalization for remaining transactions
    type_mapping = {'sale': 'Expense', 'return': 'Income'}
    if 'transaction_type' in df.columns:
        df['transaction_type'] = df['transaction_type'].str.lower().map(type_mapping).fillna('Unknown')
    
    # Select final columns
    keep_cols = ['date', 'description', 'amount', 'auto_category', 
                'bank_category', 'transaction_type', 'needs_review']
    return df[[col for col in keep_cols if col in df.columns]]

# ======================
# Routes
# ======================

# Upload file function, allow user search PC for CSV files
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No files selected', 'error')
            return redirect(request.url)
            
        files = request.files.getlist('file')
        if not files or all(f.filename == '' for f in files):
            flash('No files selected', 'error')
            return redirect(request.url)
            
        try:
            all_dfs = []
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(temp_path)
                    df = process_statement(temp_path)
                    all_dfs.append(df)
            
            if all_dfs:
                combined_df = pd.concat(all_dfs)
                processed_path = os.path.join(app.config['UPLOAD_FOLDER'], 'processed.csv')
                combined_df.to_csv(processed_path, index=False)
                flash(f'{len(all_dfs)} files processed successfully!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('No valid CSV files were uploaded', 'error')
                
        except Exception as e:
            flash(f'Error processing files: {str(e)}', 'error')
    
    return render_template('upload.html')

# Dashboard view of uploaded CSV data plotted by amount and dates
@app.route('/dashboard')
def dashboard():
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'processed.csv')
        if not os.path.exists(filepath):
            flash('No processed data found. Please upload a file first.', 'error')
            return redirect(url_for('upload_file'))
        
        df = pd.read_csv(filepath)
        
        # Ensure required columns exist
        required_cols = ['date', 'amount', 'auto_category']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise ValueError(f"Missing columns: {', '.join(missing)}")
        
        # Budget categories with colors assigned for pie chart
        category_colors = {
            'Eating Out': '#8a3ffc',
            'Groceries': '#007d79',
            'Shopping': '#33b1ff',
            'Entertainment': '#d4bbff',
            'Travel': '#6fdc8c',
            'Utilities': '#08bdba',
            'Health': '#ff7eb6',
            'Cat': '#4589ff',
            'Dance': '#bae6ff',
            'Uncategorized': '#FF9800'
        }
        
        # Fill missing categories
        df['auto_category'] = df['auto_category'].fillna('Uncategorized')
        
        # Create visualizations
        charts = {}
        
        # 1. Pie Chart with custom colors
        df_pie = df.copy()
        df_pie['amount'] = df_pie['amount'].abs()
        pie_data = df_pie.groupby('auto_category', as_index=False)['amount'].sum()
        
        charts['pie'] = px.pie(
            pie_data,
            values='amount',
            names='auto_category',
            title='Spending by Category',
            color='auto_category',
            color_discrete_map=category_colors
        ).update_traces(
            textinfo='percent+label',
            textposition='inside',
            marker=dict(line=dict(color='#ffffff', width=1))
        ).update_layout(
            showlegend=True,
            uniformtext_minsize=12,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        ).to_html(full_html=False)
        
        # 2. Time Series Charts 
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            
            # Daily Expenses
            df_expense = df[df['transaction_type'] == 'Expense'].copy()
            df_expense['amount'] = df_expense['amount'].abs()
            df_daily = df_expense.groupby('date', as_index=False)['amount'].sum().sort_values('date')
            
            charts['timeline'] = px.line(
                df_daily, 
                x='date', 
                y='amount',
                title='Daily Spending',
                color_discrete_sequence=['#007d79']
            ).update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',

                # Grid lines on timeline charts
                xaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(200, 200, 200, 0.3)',
                    gridwidth=1
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(200, 200, 200, 0.3)',
                    gridwidth=1
                )
            ).to_html(full_html=False)
            
            # Cumulative Expenses
            df_daily['cumulative'] = df_daily['amount'].cumsum()
            charts['timeline_accumulated'] = px.line(
                df_daily, 
                x='date', 
                y='cumulative',
                title='Daily Spending (Accumulated)',
                color_discrete_sequence=['#007d79']
            ).update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                # ADDED GRID LINES CONFIGURATION:
                xaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(200, 200, 200, 0.3)',
                    gridwidth=1
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(200, 200, 200, 0.3)',
                    gridwidth=1
                )
            ).to_html(full_html=False)
            
            # Combined Chart
            df_long = df_daily.melt(
                id_vars='date',
                value_vars=['amount', 'cumulative'],
                var_name='Type',
                value_name='Value'
            )
            
            charts['timeline_combined'] = px.line(
                df_long,
                x='date',
                y='Value',
                color='Type',
                title='Daily and Cumulative Spending',
                color_discrete_sequence=['#007d79', '#d12771']
            ).update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                # ADDED GRID LINES CONFIGURATION:
                xaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(200, 200, 200, 0.3)',
                    gridwidth=1
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(200, 200, 200, 0.3)',
                    gridwidth=1
                )
            ).to_html(full_html=False)
            
        return render_template('dashboard.html', charts=charts)
        
    except Exception as e:
        flash(f'Dashboard error: {str(e)}', 'error')
        return redirect(url_for('upload_file'))
    
# Edit page where user can revise budget categories
@app.route('/results')
def show_results():
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'processed.csv')
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        return render_template('results.html', tables=[df.to_html(classes='data')])
    else:
        flash('No processed data found', 'error')
        return redirect(url_for('upload_file'))
    
@app.route('/edit', methods=['GET', 'POST'])
def edit_transactions():
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'processed.csv')
        if not os.path.exists(filepath):
            flash('No transactions found. Please upload a file first.', 'error')
            return redirect(url_for('upload_file'))
        
        # Define standard categories
        categories = [
            'Eating Out', 'Groceries', 'Shopping', 
            'Entertainment', 'Travel', 
            'Utilities', 'Health',
            'Cat', 'Dance'
        ]
        
        if request.method == 'POST':
            # Load existing data
            df = pd.read_csv(filepath)
            
            # Process form updates
            for i in range(len(df)):
                amount_key = f'amount_{i}'
                category_key = f'category_{i}'
                
                if amount_key in request.form:
                    df.at[i, 'amount'] = float(request.form[amount_key])
                if category_key in request.form:
                    df.at[i, 'auto_category'] = request.form[category_key]
            
            # Save back to CSV
            df.to_csv(filepath, index=False)
            flash('All changes saved successfully!', 'success')
            return redirect(url_for('edit_transactions'))
        
        # For GET requests
        df = pd.read_csv(filepath)
        transactions = df.to_dict('records')
        
        return render_template(
            'edit.html',
            transactions=transactions,
            categories=categories
        )
    
    except Exception as e:
        flash(f'Error editing transactions: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True,port=8000
)