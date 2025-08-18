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

app = Flask(__name__)

app.config["SECRET_KEY"] = "sua_chave_secreta_aqui"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = Users.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("Email já cadastrado. Faça login.", "warning")
            return redirect(url_for("login"))

        hashed_password = generate_password_hash(form.password.data)
        novo_usuario = Users(email=form.email.data, password=hashed_password)
        db.session.add(novo_usuario)
        db.session.commit()
        flash("Cadastro realizado com sucesso! Faça login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("produtos"))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("produtos"))
        else:
            flash("Email ou senha incorretos.", "danger")
    return render_template("login.html", form=form)


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

from flask_mail import Mail, Message

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'amnipora@gmail.com'
app.config['MAIL_PASSWORD'] = 'scxz fmbn lnnx uact'

mail = Mail(app)

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
