from flask import Flask, render_template, request, redirect
from datetime import datetime

app = Flask(__name__)

produtos = []

class Produto:
    def __init__(self, codigo_barras, nome, categoria, quantidade, preco, localizacao):
        self.codigo_barras = codigo_barras
        self.nome = nome
        self.categoria = categoria
        self.quantidade = quantidade
        self.preco = preco
        self.localizacao = localizacao  # Dicionário de localização
        self.movimentacoes = []  # Lista para rastrear movimentações
        self.validade = validade  # Adiciona a data de validade do produto (Coloquei Como opcional)
        
    def atualizar_estoque(self, quantidade, tipo_movimentacao):
        """Atualiza o estoque do produto e registra a movimentação."""
        if tipo_movimentacao == 'entrada':
            self.quantidade += quantidade
        elif tipo_movimentacao == 'saida' and self.quantidade >= quantidade:
            self.quantidade -= quantidade
        else:
            return "Quantidade insuficiente no estoque"

        # Registrar a movimentação
        movimentacao = {
            'tipo': tipo_movimentacao,
            'quantidade': quantidade,
            'data': datetime.now()
        }
        self.movimentacoes.append(movimentacao)

    def atualizar_localizacao(self, setor, corredor, prateleira):
        """Atualiza a localização do produto."""
        self.localizacao = {
            "setor": setor,
            "corredor": corredor,
            "prateleira": prateleira
        }
        
# Lista para armazenar os produtos cadastrados
produtos = []

def buscar_produto_por_codigo(codigo_barras):
    """ Função para buscar um produto pelo código de barras. """
    for produto in produtos:
        if produto.codigo_barras == codigo_barras:
            return produto
    return None

@app.route('/')
def index():
    # Renderiza o formulário e a lista de produtos
    return render_template('cadastro.html', produtos=produtos)

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    # Recebe os dados do formulário e cria um novo produto
    codigo_barras = request.form['codigo_barras']
    nome = request.form['nome']
    categoria = request.form['categoria']
    quantidade = int(request.form['quantidade'])
    preco = float(request.form['preco'])
    setor = request.form['setor']
    corredor = request.form['corredor']
    prateleira = request.form['prateleira']
    validade = request.form['validade']
    
    # Cria uma instância de Produto com localização e adiciona à lista de produtos
    localizacao = {
        "setor": setor,
        "corredor": corredor,
        "prateleira": prateleira
    }

    # Cria uma instância de Produto e adiciona à lista de produtos
    novo_produto = Produto(codigo_barras, nome, categoria, quantidade, preco, localizacao, validade if validade else None)
    produtos.append(novo_produto)

    return redirect('/')

@app.route('/atualizar_localizacao', methods=['POST'])
def atualizar_localizacao():
    # Atualiza a localização de um produto no depósito
    codigo_barras = request.form['codigo_barras']
    setor = request.form['setor']
    corredor = request.form['corredor']
    prateleira = request.form['prateleira']

    produto = buscar_produto_por_codigo(codigo_barras)

    if produto:
        produto.atualizar_localizacao(setor, corredor, prateleira)
        return redirect('/')
    else:
        return "Produto não encontrado", 404


@app.route('/atualizar_estoque', methods=['POST'])
def atualizar_estoque():
    # Atualiza a quantidade de produtos no estoque
    codigo_barras = request.form['codigo_barras']
    quantidade_recebida = int(request.form['quantidade'])

    produto = buscar_produto_por_codigo(codigo_barras)
    
    if produto:
        produto.quantidade += quantidade_recebida
        return redirect('/')
    else:
        return "Produto não encontrado", 404

@app.route('/vender_produto', methods=['POST'])
def vender_produto():
    # Reduz a quantidade de produtos no estoque após uma venda
    codigo_barras = request.form['codigo_barras']
    quantidade_venda = int(request.form['quantidade'])

    produto = buscar_produto_por_codigo(codigo_barras)

    if produto:
        if produto.quantidade >= quantidade_venda:
            produto.quantidade -= quantidade_venda
            return redirect('/')
        else:
            return "Quantidade insuficiente no estoque", 400
    else:
        return "Produto não encontrado", 404
    
@app.route('/gerar_relatorio', methods=['GET'])
def gerar_relatorio():
    limite_baixo_estoque = 10  # Limite de quantidade para definir estoque baixo
    limite_excesso_estoque = 100  # Limite para definir excesso de estoque
    produtos_baixo_estoque = []
    produtos_excesso_estoque = []
    produtos_validade_proxima = []
    
    # Processar relatórios
    for produto in produtos:
        if produto.quantidade < limite_baixo_estoque:
            produtos_baixo_estoque.append(produto)
        if produto.quantidade > limite_excesso_estoque:
            produtos_excesso_estoque.append(produto)
        if produto.validade and datetime.strptime(produto.validade, '%Y-%m-%d') < datetime.now():
            produtos_validade_proxima.append(produto)

    # Renderizar os relatórios em uma nova página
    return render_template('relatorio.html', produtos_baixo_estoque=produtos_baixo_estoque,
                           produtos_excesso_estoque=produtos_excesso_estoque,
                           produtos_validade_proxima=produtos_validade_proxima)


if __name__ == '__main__':
    app.run(debug=True)
