from flask import Flask, render_template, request, redirect, session
import sqlite3 as sql
import uuid

app = Flask(__name__)
app.secret_key = "quitandazezinho"

usuario = "zezinho"
senha = "4321"
login = False

#FUNÇÃO PARA VERIFICAR SESSÃO
def verifica_sessao():
    if "login" in session and session["login"]:
        return True
    else:
        return False

#CONEXÃO COM O BANCO DE DADOS
def conecta_database():
    conexao = sql.connect("db_quitanda.db")
    conexao.row_factory = sql.Row
    return conexao

#INICIAR O BANCO DE DADOS
def iniciar_db():
    conexao = conecta_database()
    with app.open_resource('esquema.sql', mode='r') as comandos:
        conexao.cursor().executescript(comandos.read())
    conexao.commit()
    conexao.close()
    
# ROTA DA PÁGINA INICIAL
@app.route("/")
def index():
    iniciar_db()
    conexao = conecta_database()
    produtos = conexao.execute('SELECT * FROM produtos ORDER BY id_prod DESC').fetchall()
    conexao.close()
    return render_template("home.html", produtos=produtos)

#ROTA DA PÁGINA LOGIN
@app.route("/login")
def login():
    return render_template("login.html")

#código do LOGOUT
@app.route("/logout")
def logout():
    global login
    login = False
    session.clear()
    return redirect('/')

# ROTA DA PÁGINA DE CADASTRO
@app.route("/cadprodutos")
def cadprodutos():
    return render_template("cadprodutos.html")

# ROTA DA PÁGINA DE CADASTRO NO BANCO
@app.route("/cadastro",methods=["post"])
def cadastro():
    nomeproduto=request.form['nome_prod']
    descproduto=request.form['desc_prod']
    preco=request.form['preco']
    imagem=request.files['imagem']
    id_foto=str(uuid.uuid4().hex)
    filename=id_foto+nomeproduto+'.png'
    imagem.save("static/img/produtos/"+filename)
    conexao = conecta_database()
    conexao.execute('INSERT INTO produtos (nome_prod, desc_prod, preco, img) VALUES (?, ?, ?, ?)',(nomeproduto, descproduto, preco, filename))
    conexao.commit()
    conexao.close()
    return redirect("/")

# ROTA DA PÁGINA DE BUSCA
@app.route("/busca",methods=["post"])
def busca():
    busca=request.form['buscar']
    conexao = conecta_database()
    produtos = conexao.execute('SELECT * FROM produtos WHERE nome_prod LIKE  "%" || ? || "%"',(busca,)).fetchall()
    return render_template("home.html", produtos=produtos)

# ROTA DA PÁGINA ADM
@app.route("/adm")
def adm():
    if verifica_sessao():
        iniciar_db()
        conexao = conecta_database()
        produtos = conexao.execute('SELECT * FROM produtos ORDER BY id_prod DESC').fetchall()
        conexao.close()
        return render_template("adm.html", produtos=produtos)
    else:
        return render_template("login.html") 

# ROTA DA PÁGINA ACESSO
@app.route("/acesso", methods=['post'])
def acesso():
    global usuario, senha
    usuario_informado = request.form["usuario"]
    senha_informada = request.form["senha"]
    if usuario == usuario_informado and senha == senha_informada:
        session["login"] = True
        return redirect('/adm') #homepage
    else:
        return render_template("login.html",msg="Usuário/Senha estão incorretos!")

#CRIAR A ROTA DO EDITAR
@app.route("/editprodutos/<id_prod>")
def editar(id_prod):
    if verifica_sessao():
        iniciar_db()
        conexao = conecta_database()
        produtos = conexao.execute('SELECT * FROM produtos WHERE id_prod = ?',(id_prod,)).fetchall()
        conexao.close()
        return render_template("editprodutos.html",produtos=produtos)

#CRIAR A ROTA PARA TRATAR A EDIÇÃO
@app.route("/editarprodutos", methods=['POST'])
def editprod():
    id_prod = request.form['id_prod']
    nomeproduto=request.form['nome_prod']
    descproduto=request.form['desc_prod']
    preco=request.form['preco']
    conexao = conecta_database()
    conexao.execute('UPDATE produtos SET nome_prod = ?, desc_prod = ?, preco = ? WHERE id_prod = ?',(nomeproduto,descproduto,preco,id_prod))
    conexao.commit() #Confirma a alteração no BD
    conexao.close()
    return redirect('/adm') # Vai para a ÁREA ADM

#ROTA DE EXCLUSÃO
@app.route("/excluir/<id>")
def excluir(id):
    #id = int(id)
    conexao = conecta_database()
    conexao.execute('DELETE FROM produtos WHERE id_prod = ?',(id,))
    conexao.commit()
    conexao.close()
    return redirect('/adm')

# FINAL DO CODIGO - EXECUTANDO O SERVIDOR
app.run(debug=True)
