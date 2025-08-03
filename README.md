# Fintellect User Guide
Fintellect is a data-driven personal finance dashboard that transforms raw bank statements into visualized 

## 📌 Prerequisites

Before using this application, ensure you have:
- Python 3.8+ installed
- pip package manager
- (Optional) Virtual environment (recommended)

## 🛠️ Setup Instructions

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt

## Prepare your data:

The app expects CSV files with these required columns:

- `date` (format: YYYY-MM-DD)

- `amount` (numeric values)

- `transaction_type` (should include "Expense" entries)

- `auto_category` (spending categories)

## Example CSV structure:

```text
date,amount,description,transaction_type,auto_category
2023-01-01,15.50,Coffee shop,Expense,Eating Out
2023-01-02,120.00,Supermarket,Expense,Groceries
```

## 🚀 How to Use the Application
### 1. Launch the Application
```bash
python app.py
```
The application will start at http://localhost:8000

### 2. Upload Your Data

- Click "Choose File" and select your CSV

- Click "Upload"

- Wait for processing to complete (you'll see a success message)

### 3. View Your Dashboard
After successful upload, you'll be automatically redirected to the dashboard with three visualizations:

#### Spending by Category (Pie Chart)

- Shows percentage breakdown of expenses

- Hover over slices for exact amounts

#### Daily Spending (Line Chart)

- Shows expenses over time

- Grid lines help visualize amounts

#### Accumulated Spending (Line Chart)

- Shows running total of expenses

- Helps track spending trends

## 🔍 Example Walkthrough
1. Prepare a CSV file with your financial data

2. Upload the file through the web interface

3. Review your uploaded expenses and edit the categories as necessary

4. Explore your dashboard:

- Identify largest spending categories

- Track daily spending patterns

- Monitor accumulated expenses over time

## ⚠️ Known Limitations
- Currently only supports CSV files (no Excel or JSON)

- Maximum file size: 10MB

- Date range limited to 2 years for optimal performance

- Categories are case-sensitive ("Groceries" ≠ "groceries")

## 🆘 Getting Help
### For additional support:

- Check the docs/ directory for detailed documentation

- Open an issue on GitHub for bug reports

- You can host these images in your repo's `/docs/images` folder or use an image hosting service.


   
