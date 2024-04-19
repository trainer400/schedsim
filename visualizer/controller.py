from flask import Flask, render_template, request

app = Flask(__name__)

# Route per la homepage
@app.route('/')
def home():
    return render_template('index.html')

# Route per ricevere i dati dal form
@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        return render_template('submitted.html', name=name, email=email)

if __name__ == '__main__':
    app.run(debug=True)