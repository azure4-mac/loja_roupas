from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class ProdutoForm(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired()])
    descricao = StringField("Descrição", validators=[DataRequired()])
    tipo = SelectField(
        "Tipo",
        choices=[("roupa", "Roupa"), ("comida", "Comida"), ("dinheiro", "Dinheiro")],
        validators=[DataRequired()],
    )
    contato = StringField("Contato", validators=[DataRequired(), Length(max=120)])
    submit = SubmitField("Salvar Produto")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Senha", validators=[DataRequired(), Length(min=6, max=128)])
    submit = SubmitField("Entrar")


class RegisterForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[DataRequired(), Email(), Length(max=120)]
    )
    password = PasswordField(
        "Senha",
        validators=[DataRequired(), Length(min=6, max=128)]
    )
    confirm_password = PasswordField(
        "Confirme a senha",
        validators=[DataRequired(), EqualTo("password", message="Senhas devem ser iguais.")]
    )
    submit = SubmitField("Cadastrar")

from wtforms import TextAreaField

class PedidoAjudaForm(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    mensagem = TextAreaField("Mensagem", validators=[DataRequired()])
    submit = SubmitField("Enviar Pedido")


