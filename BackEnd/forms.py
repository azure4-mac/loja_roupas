from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email

class ProdutoForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    descricao = StringField('Descrição', validators=[DataRequired()])
    tipo = SelectField('Tipo', choices=[('roupa', 'Roupa'), ('comida', 'Comida'), ('dinheiro', 'Dinheiro')], validators=[DataRequired()])
    contato = StringField('Contato', validators=[DataRequired(), Length(max=120)])
    submit = SubmitField('Salvar Produto')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6, max=128)])
    submit = SubmitField('Entrar')
