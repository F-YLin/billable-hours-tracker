
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

**Data Import & Migration**
Allow existing users to import billable hours from a CSV file, enabling lawyers switching from other tools like Clio or Excel to bring their historical data over. The main challenge would be data cleaning — handling inconsistent column names, date formats, and hour values.

**Password Recovery**
Implement email-based password reset using a service like SendGrid — generate a secure one-time token, store it temporarily in the database, and email the user a reset link with a 15-minute expiration.

**PDF Invoice Generation**
Allow users to generate a professional invoice PDF per client, pulling from logged hours and the client's hourly rate. This would make the tool immediately usable in a real billing workflow.

**Multi-user Firm Support**
Currently each account is independent. A future version could support a law firm as an organization with multiple attorney accounts, shared client rosters, and an admin dashboard for managing billing across the team.

**Persistent Cloud Deployment**
SQLite resets on Streamlit Cloud's free tier. A production version would use PostgreSQL hosted on a service like Supabase or Railway for persistent, reliable data storage.

## Future Improvements
- Email-based password recovery
- PDF invoice generation
- Multi-user law firm support
- Cloud database for persistent deployment
