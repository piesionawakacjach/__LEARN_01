from flask import Flask, render_template, request

app = Flask(__name__)

app = Flask(__name__)

@app.route('/')
def index():
    return '<h1> Hello World!!!</h1>'

@app.route('/first')
def first():
    moja_zmienna = 'Ala ma kota'
    return render_template('first.html', moja_zmienna=moja_zmienna)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        return "ALAAA"
    else:
        return render_template('login.html')


@app.route('/register')
def register():
    return "Not implemented yet"

if __name__ == '__main__':
    app.run()
