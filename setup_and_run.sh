#!/bin/bash
# Make a trip - one-command setup & run (Mac/Linux)
set -e
cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

source venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip > /dev/null
pip install -r requirements.txt

echo "Applying database migrations..."
python manage.py migrate

if [ ! -f ".seeded" ]; then
  read -p "Load demo data (a sample hotel, bus, car, package, admin & customer login)? [Y/n] " yn
  if [[ "$yn" != "n" && "$yn" != "N" ]]; then
    python manage.py shell < scripts/seed_data.py
    touch .seeded
  fi
fi

echo ""
echo "Starting the dev server at http://127.0.0.1:8000/"
echo "Press CTRL+C to stop."
python manage.py runserver
