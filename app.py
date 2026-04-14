from flask import Flask, render_template

app = Flask(__name__)

# Rota para a página inicial
@app.route('/')
def home():
    return render_template('index.html')

# Rota para a página de serviços
@app.route('/servicos')
def servicos():
    return render_template('servicos.html')

# Rota para a página de contato
@app.route('/contato')
def contato:
    return render_template('contato.html')

if __name__ == '__main__':
    app.run(debug=True)
