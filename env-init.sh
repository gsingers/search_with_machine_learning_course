export FLASK_ENV=development
export FLASK_APP=week3
flask run

pip install -r requirements_week3.txt
pip install jupyterlab
jupyter lab --NotebookApp.allow_origin='*'

gunzip /workspace/search_with_machine_learning_course/data/*/*.xml.gz

python week3/createContentTrainingData.py --output /workspace/datasets/categories/output.fasttext --min_products=5
