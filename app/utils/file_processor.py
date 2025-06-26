import pandas as pd

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