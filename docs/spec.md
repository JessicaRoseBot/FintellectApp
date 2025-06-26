# Fintellect 
A data-driven personal finance app that transforms raw bank statements into actionable spending insights using smart categorization, trend forecasting, and anomaly detection.

-------------

### General Description
The Personal Finance Visualizer is a web application that helps users gain insights into their spending habits by analyzing bank statement data. Users upload CSV files (standard bank statement format) which are automatically categorized and visualized through interactive dashboards. The system provides monthly spending breakdowns, category trends, and budget alerts.

The core technology stack will use Python with Flask for the web interface, pandas for data processing, and Plotly for interactive visualizations. For categorization, we'll implement rule-based matching (e.g., "Netflix" → "Entertainment") with manual override capabilities. The minimal viable product will be a web app deployable to PythonAnywhere, with potential for future mobile adaptation using Bootstrap.

Key external packages: Flask, pandas, Plotly, matplotlib, csv, Bootstrap. No external APIs required for v1. The GUI will be browser-based with file upload capabilities. A CLI version could be implemented for batch processing, but wouldn't serve the visualization needs. Future versions could expose an API for programmatic access to the analysis engine.

--------------

### Task Vignettes
#### 1. Data Upload and Initial Categorization
Sarah wants to understand her monthly spending patterns. She logs into the web app and uploads her bank's CSV statement. The system processes the file, automatically categorizing transactions based on merchant names (e.g., "Whole Foods" → Groceries, "AMC Theaters" → Entertainment). Sarah sees a loading screen with progress indicators as the system processes her data.
Technical Details:
CSV parsing with pandas
Initial categorization using keyword matching rules
Progress feedback during processing
Error handling for malformed CSV files
Temporary storage of processed data in session

[Wireframe description: File upload button → Processing spinner → Basic categorization table] 

#### 2. Category Review and Adjustment
After initial processing, Sarah reviews the automatic categorizations. She notices "Amazon" transactions were all categorized as "Shopping" but wants to split them between "Books" and "Electronics". She selects transactions and uses a dropdown to recategorize them. The system learns from her adjustments for future imports.
Technical Details:
Interactive data table display
Category override interface
Session persistence of user changes
Simple "learning" by saving user overrides to a profile
Undo/redo capability for corrections

[Wireframe description: Table view with category dropdowns + "Apply Changes" button] 

#### 3. Dashboard Visualization
With her data categorized, Sarah views her monthly spending dashboard. Interactive pie charts show category breakdowns, while line graphs display spending trends over time. She hovers over chart elements to see exact amounts and can click to drill down into specific categories or time periods.
Technical Details:
Plotly interactive charts
Responsive dashboard layout
Tooltip hover information
Time period selectors
Export options (PNG, PDF)

[Wireframe description: Main dashboard with 3 chart areas + time filters]



[Screenshot of excel basis for web app.]

------------


### Technical Flow
#### Input Handling
- Web: File upload → Flask endpoint → pandas DataFrame
- (Future) CLI: File path argument → same DataFrame processing 

#### Processing Pipeline
- CSV sanitization (handle bank-specific formats)
- Transaction categorization engine
    - Rule-based matcher (predefined patterns)
    - User override storage
- Monthly aggregation
- Budget comparison 

#### Visualization Layer
- Plotly figure generation
- Dashboard layout assembly
- Interactive element handlers 

#### Output
- HTML dashboard rendering
- Export file generation

#### Data Types:
- Raw transactions: List[Dict] (from CSV)
- Processed data: pandas DataFrame
- Visualization: Plotly Figure objects
- User config: JSON (categories, rules, budgets)

-------------

### Implementation Plan & Assessment
#### Version 1: Flask web interface with file upload
Basic categorization rules
Static visualizations (matplotlib)
Manual category adjustment

#### Version 2: Enhancements with interactivity and responsive design
Interactive Plotly dashboards
User profiles for saving preferences
Budget tracking/alerts
Improved categorization learning
Bootstrap for responsive design

#### Self Assessment
I found this exercise extremely helpful to identify the types of packages I’ll need to incorporate to make this app work. It feels like I am de-mystifying things I’ve long observed by taking them off the shelf and using them myself (like Bootstrap!).

The two biggest challenges I foresee with this will be aligning bank statement formatting while allowing the ability for the user to add ad-hoc expenses OR to update vague categories like “Amazon” which could fall into Shopping, Groceries, etc. The hardest part for me is think will be getting Plotly to display the data in the ways I want, as I anticipate a learning curve with that.
