from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    UserMixin,
)
from werkzeug.security import check_password_hash
from forms import ProdutoForm, LoginForm
from models import db, Produto, Users  # Certifique-se que Users está em models.py

app = Flask(
    __name__,
    static_folder="../FrontEnd/static",
    template_folder="../FrontEnd/templates",
)

# Configurações do app e banco de dados
app.config["SECRET_KEY"] = "sua_chave_secreta_aqui"  # Use variável ambiente em produção
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Configuração do login
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# ROTAS

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
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


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
