.PHONY: week1

week1:
	pyenv activate search_with_ml_week1
	export FLASK_ENV=development
	export FLASK_APP=week1
	flash run --port 3000