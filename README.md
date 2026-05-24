# Banking_Dashboard_SUPData

The project provides an example of a supervisory dashboard using SUP Data, in a comparison between Italy and Spain in an aggregate sample for SII Institutions. The dashboard provides a visualization of key risk metrics: CET1 Ratio, Liquidity Coverage Ratio and Non Performing Loans Ratio.

Data are directly downloaded from 'ECB Supervisory data'

Requirements
Python 3.10+
pip
Installation
1. Clone repository
git clone https://github.com/YOUR_USERNAME/ecb-banking-dashboard.git
cd ecb-banking-dashboard
2. Create virtual environment
macOS / Linux
python3 -m venv venv
source venv/bin/activate
Windows
python -m venv venv
venv\Scripts\activate
3. Install dependencies
pip install -r requirements.txt
Run the project
python main.py

After execution, the dashboard will be generated:

output/ecb_banking_dashboard.html
View the dashboard

Open the file directly in your browser:

Double click the file, OR
Run:
open output/ecb_banking_dashboard.html   # macOS
start output\ecb_banking_dashboard.html   # Windows
📊 Features
Automatic data retrieval from ECB SDMX API
Clean transformation with Pandas
Interactive Plotly charts
Multi-country comparison (Italy vs Spain)
Responsive HTML report
Hover + zoom functionality
🏦 Data Source

European Central Bank (ECB)
Supervisory Banking Statistics (SUP)

https://data.ecb.europa.eu/data/datasets/SUP

Metrics Explained
CET1 Ratio

Measures bank capital strength under regulatory standards.

Liquidity Coverage Ratio (LCR)

Indicates short-term liquidity resilience.

Non-Performing Loans (NPL)

Measures asset quality and credit risk.

Technical Stack
Python
Pandas
Requests
Plotly
Jinja2

ECB SDMX API
🔧 Possible Improvements
Add more countries (Germany, France, EU average)
Streamlit interactive web app
Docker containerization
GitHub Actions automation
Database storage (PostgreSQL)
Forecasting (ARIMA / ML models)
PDF export of dashboard

⚠️ Notes
Data is fetched live from ECB API
Requires internet connection
Some series may not update in real-time depending on ECB publication schedule

Author

Developed as a financial data engineering project using ECB Supervisory Banking Statistics.
