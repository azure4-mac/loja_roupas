from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    UserMixin,
    current_user,
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from forms import ProdutoForm, LoginForm, RegisterForm, PedidoAjudaForm
from models import db, Produto, Users
from flask_mail import Mail, Message

app = Flask(__name__)

app.config["SECRET_KEY"] = "sua_chave_secreta_aqui"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# --- Configuração do Flask-Mail ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'amnipora@gmail.com'
app.config['MAIL_PASSWORD'] = 'scxz fmbn lnnx uact'

db.init_app(app)
mail = Mail(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route("/")
def index():
    # Passamos os formulários para a página principal para serem usados nos modais
    login_form = LoginForm()
    register_form = RegisterForm()
    return render_template("index.html", login_form=login_form, register_form=register_form)


@app.route("/register", methods=["POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = Users.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("Este email já está cadastrado. Por favor, faça login.", "warning")
            return redirect(url_for("index"))

        hashed_password = generate_password_hash(form.password.data)
        novo_usuario = Users(email=form.email.data, password=hashed_password)
        db.session.add(novo_usuario)
        db.session.commit()
        flash("Cadastro realizado com sucesso! Agora você pode fazer login.", "success")
        return redirect(url_for("index"))

    # Se a validação falhar, exibe os erros e redireciona
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"Erro no campo {getattr(form, field).label.text}: {error}", "danger")
    return redirect(url_for("index"))


@app.route("/login", methods=["POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("produtos"))
        else:
            flash("Email ou senha incorretos. Tente novamente.", "danger")
    else:
        # Se a validação falhar (ex: campo vazio)
        flash("Por favor, preencha todos os campos para entrar.", "danger")
        
    return redirect(url_for("index"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout realizado com sucesso.", "info")
    return redirect(url_for("index"))


@app.route("/produtos", methods=["GET", "POST"])
@login_required
def produtos():
    form = ProdutoForm()
    produtos = Produto.query.all()

    if form.validate_on_submit():
        novo_produto = Produto(
            nome=form.nome.data,
            descricao=form.descricao.data,
            tipo=form.tipo.data,
            contato=form.contato.data,
        )
        db.session.add(novo_produto)
        db.session.commit()
        flash("Produto cadastrado com sucesso!", "success")
        return redirect(url_for("produtos"))

    return render_template("produtos.html", form=form, produtos=produtos)


@app.route('/pedir-ajuda', methods=['GET', 'POST'])
def pedir_ajuda():
    form = PedidoAjudaForm()
    produtos = Produto.query.all()

    if form.validate_on_submit():
        nome = form.nome.data
        email = form.email.data
        mensagem = form.mensagem.data

        msg = Message(
            subject="Novo Pedido de Ajuda",
            sender='amnipora@gmail.com',
            recipients=['amnipora@gmail.com'],
            body=f"""
Novo pedido de ajuda recebido:

Nome: {nome}
E-mail: {email}

Mensagem:
{mensagem}
            """
        )
        mail.send(msg)
        flash("Pedido enviado com sucesso! Em breve entraremos em contato.", "success")
        return redirect(url_for('pedir_ajuda'))

    return render_template('pedir_ajuda.html', form=form, produtos=produtos)


@app.route('/requisitar-produto/<int:produto_id>', methods=['POST'])
def requisitar_produto(produto_id):
    produto = Produto.query.get_or_404(produto_id)

    if current_user.is_authenticated:
        solicitante = current_user.email
    else:
        solicitante = "Usuário não autenticado"

    msg = Message(
        subject="Produto requisitado",
        sender='amnipora@gmail.com',
        recipients=['amnipora@gmail.com'],
        body=f"""
Um produto foi requisitado.

Produto: {produto.nome}
Tipo: {produto.tipo}
Descrição: {produto.descricao}
Contato do Produto: {produto.contato}

Solicitado por: {solicitante}
        """
    )
    mail.send(msg)
    flash(f'Produto "{produto.nome}" requisitado com sucesso!', 'success')
    return redirect(url_for('pedir_ajuda'))


@app.route("/delete_produto/<int:id>", methods=["POST"])
@login_required
def delete_produto(id):
    produto = Produto.query.get_or_404(id)
    db.session.delete(produto)
    db.session.commit()
    flash("Produto deletado com sucesso.", "info")
    return redirect(url_for("produtos"))


@app.route("/admin")
@login_required
def admin():
    return render_template("admin.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

app.wsgi_app = ProxyFix(app.wsgi_app)
