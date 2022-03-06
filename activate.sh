#pyenv activate search_with_ml_week${1}
export FLASK_ENV=development
export FLASK_APP=week${1}
export SYNS_MODEL_LOC="/workspace/datasets/fasttext/phone_model.bin"
# jupyter-notebook --NotebookApp.allow_origin='*'
flask run --port 3000 --reload