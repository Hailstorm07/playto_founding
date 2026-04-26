web: cd backend && python3 -m pip install gunicorn 2>/dev/null; python3 -m gunicorn playto_pay.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120
