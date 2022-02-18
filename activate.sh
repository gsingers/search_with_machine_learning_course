#pyenv activate search_with_ml_week${1}
export FLASK_ENV=development
export FLASK_APP=week${1}
flask run --port 3000 --reload