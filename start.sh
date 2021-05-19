source venv/bin/activate

sudo python3 collection.py

export FLASK_APP=server
flask run --host=0.0.0.0
