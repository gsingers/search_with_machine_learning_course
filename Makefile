.PHONY: week1

FLASK_ENV ?= development
FLASK_APP ?= week1

#pyenv activate search_with_ml_week1

week1:
	flask run --port 3000