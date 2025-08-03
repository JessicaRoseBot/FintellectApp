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
```graph TD
    A[Upload CSV] --> B[Validate Data]
    B --> C[Process Transactions]
    C --> D[Generate Visualizations]
    D --> E[Render Dashboard]
```
