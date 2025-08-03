# Fintellect Developer Documentation

## Overview
Fintellect is a Flask-based web application that processes financial transaction data and presents it through interactive visualizations. The system consists of:
- Data processing pipeline (Pandas)
- Visualization engine (Plotly)
- Web interface (Flask/Bootstrap)

## Implemented Features
| Spec | Implemented | Location |
|------|-------------|----------|
| CSV Upload | ✅ | `app.py` (upload route) |
| Transaction Categorization | ✅ | `process_data.py` |
| Pie Chart Visualization | ✅ | `app.py` (dashboard route) |
| Time Series Charts | ✅ | `app.py` (dashboard route) |
| Responsive Design | ✅ | `templates/dashboard.html` |

## User Flow
### 

## Installation & Deployment
### Additional Developer Setup
1. Install dev dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Environment configuration:
```bash
cp .env.example .env
# Edit with your local settings
```

3. Deployment to Dev / testing environment

The application currently uses Flask's built-in server for development:
```python
if __name__ == '__main__':
    app.run(debug=True, port=8000)
```

## Code Walkthrough

<img src="https://github.com/JessicaRoseBot/FintellectApp/blob/main/Fintellect_codeflow.png" width="33%" alt="Code Diagram">

```graph TD
    A[Upload CSV] --> B[Validate Data]
    B --> C[Process Transactions]
    C --> D[Generate Visualizations]
    D --> E[Render Dashboard]
```

## Key Components
#### 1. Data Processing (`process_data.py`)

- `clean_transactions()`: Handles missing data

- `categorize_spending()`: Applies category rules

- `accumulate_spending()`: Calculates running totals

#### Visualization (`app.py`)

- `generate_pie_chart()`: Creates category breakdown

- `generate_timeline()`: Daily spending chart

- `generate_accumulated()`: Running total chart

#### Routes (`app.py`)

- `/upload`: File processing endpoint

- `/dashboard`: Main visualization endpoint

## Known Issues / Future Work

### 1. Bank (CSV Structure) Compatibility
**Status**: 
- Limited to Chase Bank CSV format

**Solution Needed**:  
- Need to create flexible mapping to allow other bank formats to be ingested easily
- Would be good to expand auto-category recognition or flagging features for certain purchases (like Amazon, impossible to determine correct category)
- It has been suggested to incorporate OpenAI as a smart-agent to determine the best category as files are ingested, could be worth exploring

### 2. Upload Behavior
**Status**:

- Uploads create separate files instead of appending to processed.csv

- No duplicate detection logic

**Solution Needed**:
- Investigate where this is going wrong
- Potential code fix:
```python 
# Planned solution in app.py
if not is_duplicate(uploaded_file):
    append_to_processed(uploaded_file)
```

### 3. Visualization Features
**Status**:
Missing filtering abilities for `Date range` and `Expense type`

**Solution Needed**: 
- Allow for user to get more granular views of their visualized data through additional filters
- Important for scalalbility and value of the tool to track budget over months or years

### 4. UI Consistency Bug
**Status**: `upload.html` not inheriting base template styles

```text
templates/
├── base.html
└── upload.html  
```

**Solution Needed**: 
- Investigate where the root cause is and ensure the code is simplfied and the CSS is not duplicated / unique to any .html page
