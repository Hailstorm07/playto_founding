web: cd backend && python3 -m pip install -r requirements.txt --quiet && python3 -m gunicorn playto_pay.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120
