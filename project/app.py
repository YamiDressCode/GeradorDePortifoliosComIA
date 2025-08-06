from flask import Flask, render_template, request, redirect, url_for, session, flash
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Necessário para sessions

# Configuração do Gemini (mantido igual)
genai.configure(api_key="AIzaSyCivW8gc-xXxLsM5R_yN0tgTmpjPi5138w")
model = genai.GenerativeModel('models/gemini-2.0-flash')

# Dados temporários (substituir por banco de dados depois)
users = {
    "admin@email.com": {"senha": "123456"}
}

#######################################################################
# Rotas Públicas (acessíveis sem login)
#######################################################################

@app.route('/')
def index2():
    """Página inicial NÃO LOGADA (antiga landing page)"""
    return render_template('index2.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        # Verifica no dicionário de usuários
        if email in users and users[email]['senha'] == senha:
            session['logado'] = True
            session['email'] = email
            return redirect(url_for('index'))  # Redireciona para a página principal
        
        flash('Credenciais inválidas!', 'danger')
    
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        if email in users:
            flash('E-mail já cadastrado!', 'error')
        else:
            users[email] = {"senha": senha}
            flash('Cadastro realizado! Faça login.', 'success')
            return redirect(url_for('login'))
    
    return render_template('cadastro.html')

#######################################################################
# Rotas Protegidas (requerem login)
#######################################################################

@app.route('/index')
def index():
    """Página principal LOGADA (gerador de conteúdo)"""
    if 'logado' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/gerar-conteudo', methods=['POST'])
def gerar_conteudo():
    """Gera conteúdo HTML (funcionalidade existente)"""
    if 'logado' not in session:
        return redirect(url_for('login'))
    
    descricao = request.form.get('descricao', '').strip()
    
    if not descricao:
        flash('Digite uma descrição!', 'error')
        return redirect(url_for('index'))
    
    # Seu código original de geração (mantido intacto)
    prompt = f"""
    Você é um assistente que gera conteúdo HTML acessível.
    Descrição: {descricao}
    """
    
    try:
        response = model.generate_content(prompt)
        html_gerado = response.text
        
        # Salva o HTML na sessão para possível download
        session['ultimo_html'] = html_gerado
        
        return render_template(
            'resultado.html',
            filename="Conteúdo Gerado",
            text=html_gerado
        )
    except Exception as e:
        print(f"Erro: {str(e)}")
        flash('Erro ao gerar conteúdo', 'error')
        return redirect(url_for('index'))

@app.route('/baixar-html')
def baixar_html():
    """Baixa o último HTML gerado (nova funcionalidade)"""
    if 'logado' not in session or 'ultimo_html' not in session:
        return redirect(url_for('login'))
    
    from flask import make_response
    response = make_response(session['ultimo_html'])
    response.headers['Content-Type'] = 'text/html'
    response.headers['Content-Disposition'] = 'attachment; filename=conteudo_gerado.html'
    return response

@app.route('/logout')
def logout():
    """Desloga o usuário"""
    session.clear()
    return redirect(url_for('index2'))
@app.route('/sobre')
def sobre():
    """Rota para a página Sobre Nós"""
    return render_template('sobre.html')
if __name__ == '__main__':
    app.run(debug=True)