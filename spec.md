# Personal Finance Visualizer & Analyzer

### Project Description
A web app that allows users to upload their bank statements (CSV format) and get
categorized insights into their spending habits. It provides visual breakdowns (e.g.,
monthly expenses, categories like groceries/rent/entertainment) and alerts for budget
anomalies.

------------
### Biggest Problem
Automatic and accurate transaction categorization can be tough without access to highquality
training data. Will need to allow user to manually update / clarify ingested CSV
data.

### Personal Work & Support Needed
I can build the data upload and categorization logic using Python, and visualize data
using matplotlib or Plotly. GUI could be done with Flask and deployed to python
anywhere.com. I would want some assistance / may need help with matplotlib/Plotly
stuff, and would be curious if a mobile app would be feasible for this project (if not, that’s
ok).

------------

### Users
Individuals looking to budget or track spending (i.e. me)
Task/Problems Solved
- Helps users gain financial awareness and control over spending
- Helps users visualize categories they spend more money in, and identify where they
can save more
- Allows users to set a budget and track their adherence to it

-------------

### Workflow
User uploads CSV → App categorizes data → User sees dashboard with trends and
recommendations.
Primary Interaction
File upload → View dashboard → Adjust categories → Download report (loop possible
monthly).

### Data
- Input: CSV from banks (common export format).
- Processing: Categorize by keyword matching (e.g., “Netflix” = subscription), monthly
summaries, visualizations.

### Results
- Pie chart of spending categories.
- Line chart of monthly spending.
- Budget alerts or savings suggestions.
