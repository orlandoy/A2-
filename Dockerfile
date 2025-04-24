ENV PORT 8000
CMD ["gunicorn", "-b", "0.0.0.0:$PORT", "app:ProjectDashboard().app.server"]

