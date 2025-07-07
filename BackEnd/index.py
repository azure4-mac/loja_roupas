from flask import Flask, render_template, jsonify, redirect, url_for

app = Flask(__name__, static_folder='../FrontEnd/static', template_folder='../FrontEnd/templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/produtos')
def produtos():
    return render_template('produtos.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

if __name__ == '__main__':
    app.run(debug=True)
