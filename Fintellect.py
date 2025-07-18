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
    df['amount'] = df['amount'].replace(r'[\$,]', '', regex=True).astype(float)
    df['date'] = pd.to_datetime(df['date'])
    
    # Enhanced categorization
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
                filename = secure_filename(file.filename)
                temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(temp_path)
                
                df = process_statement(temp_path)
                processed_path = os.path.join(app.config['UPLOAD_FOLDER'], 'processed.csv')
                hdr = False  if os.path.isfile(processed_path) else True
                df.to_csv(processed_path, index=False, mode="a", header=hdr)
                
                flash('File processed successfully!', 'success')
                return redirect(url_for('dashboard'))
                
            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'error')
        else:
            flash('Only CSV files allowed', 'error')
    
    return render_template('upload_CH.html')

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
        else:
            print("All required columns are present.")
        
        # Fill missing categories
        df['auto_category'] = df['auto_category'].fillna('Uncategorized')
        
        # Create visualizations
        charts = {}
        
        # 1. Overall Pie Chart
        df_pie = df.copy()
        df_pie['amount'] = df_pie['amount'].abs()
        pie_data = df_pie.groupby('auto_category', as_index=False)['amount'].sum()
        
        charts['pie'] = px.pie(
            pie_data,
            values='amount',
            names='auto_category',
            title='Spending by Category (Percentage of Total)'
        ).update_traces(textinfo='percent+label').to_html(full_html=False)
        
        # 2. Expense Pie Chart
        # if 'transaction_type' in df.columns:
            # df_expense = df[df['transaction_type'] == 'Expense'].copy()
            # df_expense['amount'] = df_expense['amount'].abs()
            # pie_data_expense = df_expense.groupby('auto_category', as_index=False)['amount'].sum()
            
            # charts['pie_exp'] = px.pie(
               # pie_data_expense,
               # values='amount',
               # names='auto_category',
               # title='Expenses by Category (Percentage of Total)'
            # ).update_traces(textinfo='percent+label').to_html(full_html=False)
            
            # 3. Income Pie Chart - TBD
            # df_income = df[df['transaction_type'] == 'Income'].copy()
            # df_income['amount'] = df_income['amount'].abs()
            # pie_data_income = df_income.groupby('auto_category', as_index=False)['amount'].sum()
            
            #charts['pie_inc'] = px.pie(
               # pie_data_income,
               # values='amount',
               # names='auto_category',
               # title='Income by Category (Percentage of Total)'
            # ).update_traces(textinfo='percent+label').to_html(full_html=False)
        
        # 4. Time Series Charts
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
                title='Daily Spending'
            ).to_html(full_html=False)
            
            # Cumulative Expenses
            df_daily['cumulative'] = df_daily['amount'].cumsum()
            charts['timeline_accumulated'] = px.line(
                df_daily, 
                x='date', 
                y='cumulative',
                color_discrete_sequence=['red'],
                title='Daily Spending (Accumulated)'
            ).to_html(full_html=False)
            
            # Combined Daily and Cumulative
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
                title='Daily and Cumulative Spending'
            ).to_html(full_html=False)
        
        return render_template('dashboard_CH.html', charts=charts)
        
    except Exception as e:
        flash(f'Dashboard error: {str(e)}', 'error')
        return redirect(url_for('upload_file'))

@app.route('/results')
def show_results():
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'processed.csv')
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        return render_template('results_CH.html', tables=[df.to_html(classes='data')])
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
        
        # Define standard categories (you can expand this)
        categories = [
            'Eating Out', 'Groceries', 'Amazon', 
            'Entertainment', 'Transportation', 
            'Utilities', 'Uncategorized'
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
    app.run(debug=True,port=5000
)