from flask import Flask, render_template, redirect, url_for, flash, request
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
from forms import ProdutoForm, LoginForm, RegisterForm
from models import db, Produto, Users

app = Flask(
    __name__,
    static_folder="../FrontEnd/static",
    template_folder="../FrontEnd/templates",
)

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
        # Verificar se já existe usuário com o email
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
    return redirect(url_for("login"))


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


# Cria o banco na primeira execução
with app.app_context():
    db.create_all()

# handler para Vercel
def handler(environ, start_response):
    return app(environ, start_response)
