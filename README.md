# ⚖️ Billable Hours Tracker

# ⚖️ Billable Hours Tracker

A web-based billable hours management tool built for legal professionals. 
This project was developed as a vibe coding portfolio piece — built by 
directing and collaborating with AI tools to design, scaffold, and iterate 
on a full-stack Python application. The focus was on product thinking, 
feature scoping, and understanding how the pieces fit together, rather than 
writing every line of code from scratch. This reflects how modern software 
is increasingly built in professional environments.

## Features
- User registration and login with password hashing
- Client management with per-client hourly rates
- Time entry logging with automatic 6-minute billing increment calculator
- Edit and delete existing time entries
- Analytics dashboard with bar chart, line chart, and billing summary table
- Filter analytics by client and time frame

## Tech Stack
- **Frontend/UI:** Streamlit
- **Backend:** Python
- **Database:** SQLite
- **Data Analysis:** Pandas

## How to Run Locally
1. Clone the repository
2. Install dependencies: `pip install streamlit pandas`
3. Run the app: `streamlit run app.py`
4. Open your browser at `http://localhost:8501`

## Future Improvements
- Email-based password recovery
- PDF invoice generation
- Multi-user law firm support
- Cloud database for persistent deployment
