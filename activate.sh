#pyenv activate search_with_ml_week${1}
export FLASK_ENV=development
export FLASK_APP=week${1}
export SYNS_MODEL_LOC="/workspace/search_with_machine_learning_course/model_titles.bin"
flask run --port 3000 --reload