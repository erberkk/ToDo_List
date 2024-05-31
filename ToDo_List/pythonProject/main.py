from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import io
from flask import send_file

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/todoDB"
mongo = PyMongo(app)


@app.route('/')
def index():
    todos = mongo.db.todos.find()
    return render_template('index.html', todos=todos)


@app.route('/add', methods=['POST'])
def add_todo():
    todo = request.form.get('todo')
    mongo.db.todos.insert_one({'text': todo, 'completed': False})
    return redirect(url_for('index'))


@app.route('/complete/<todo_id>')
def complete(todo_id):
    mongo.db.todos.update_one({'_id': ObjectId(todo_id)}, {'$set': {'completed': True}})
    return redirect(url_for('index'))


@app.route('/delete/<todo_id>')
def delete_todo(todo_id):
    mongo.db.todos.delete_one({'_id': ObjectId(todo_id)})
    return redirect(url_for('index'))


@app.route('/edit/<todo_id>', methods=['GET', 'POST'])
def edit_todo(todo_id):
    todo = mongo.db.todos.find_one({'_id': ObjectId(todo_id)})
    if request.method == 'POST':
        new_text = request.form.get('new_text')
        mongo.db.todos.update_one({'_id': ObjectId(todo_id)}, {'$set': {'text': new_text}})
        return redirect(url_for('index'))
    return render_template('index', todo=todo)


@app.route('/add_photo/<todo_id>', methods=['POST'])
def add_photo(todo_id):
    photo = request.files['photo']
    photo_data = photo.read()
    mongo.db.todos.update_one({'_id': ObjectId(todo_id)}, {'$set': {'photo': photo_data}})
    return redirect(url_for('index'))


@app.route('/view_photo/<todo_id>')
def view_photo(todo_id):
    todo = mongo.db.todos.find_one({'_id': ObjectId(todo_id)})
    photo_data = todo.get('photo')
    return send_file(io.BytesIO(photo_data), mimetype='image/jpeg')


if __name__ == '__main__':
    app.run(debug=True)
