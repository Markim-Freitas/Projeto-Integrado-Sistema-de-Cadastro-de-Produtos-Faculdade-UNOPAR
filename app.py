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

def exibir_produto_console(produto):
    """ Função para exibir as informações do produto no console. """
    print("\n--- Produto Cadastrado ---")
    print(f"Código de Barras: {produto.codigo_barras}")
    print(f"Nome: {produto.nome}")
    print(f"Categoria: {produto.categoria}")
    print(f"Quantidade: {produto.quantidade}")
    print(f"Preço: {produto.preco}")
    print(f"Localização: Setor {produto.localizacao['setor']}, Corredor {produto.localizacao['corredor']}, Prateleira {produto.localizacao['prateleira']}")
    print("----------------------------\n")

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
    
    # Cria uma instância de Produto com localização e adiciona à lista de produtos
    localizacao = {
        "setor": setor,
        "corredor": corredor,
        "prateleira": prateleira
    }

    # Cria uma instância de Produto e adiciona à lista de produtos
    novo_produto = Produto(codigo_barras, nome, categoria, quantidade, preco, localizacao)
    produtos.append(novo_produto)
    
    # Exibe o produto cadastrado no console
    exibir_produto_console(novo_produto)

    return redirect('/')

@app.route('/atualizar_preco', methods=['POST'])
def atualizar_preco():
    # Recebe o código de barras e o novo preço do formulário
    codigo_barras = request.form['codigo_barras']
    novo_preco = float(request.form['novo_preco'])

    # Busca o produto pelo código de barras
    produto = buscar_produto_por_codigo(codigo_barras)

    if produto:
        # Atualiza o preço do produto
        produto.preco = novo_preco
        print(f"Preço atualizado: Produto {produto.nome}, novo preço: {produto.preco}")
        return redirect('/')
    else:
        return "Produto não encontrado", 404

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
        produto.atualizar_estoque(quantidade_recebida, 'entrada')
        exibir_produto_console(produto)  # Exibe o produto atualizado no console
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
            # Atualiza o estoque do produto
            produto.quantidade -= quantidade_venda
            
            # Exibe a venda no console (opcional)
            print(f"Venda realizada: {quantidade_venda} unidades do produto {produto.nome}.")
            print(f"Estoque restante: {produto.quantidade} unidades.")
            
            return redirect('/')
        else:
            # Retorna mensagem de erro em caso de estoque insuficiente
            return f"Quantidade insuficiente no estoque. Disponível: {produto.quantidade}", 400
    else:
        # Retorna erro caso o produto não seja encontrado
        return "Produto não encontrado", 404
    
@app.route('/gerar_relatorio', methods=['GET'])
def gerar_relatorio():
    limite_baixo_estoque = 10  # Limite de quantidade para definir estoque baixo
    limite_excesso_estoque = 100  # Limite para definir excesso de estoque
    produtos_baixo_estoque = []
    produtos_excesso_estoque = []

    # Processar relatórios
    for produto in produtos:
        if produto.quantidade < limite_baixo_estoque:
            produtos_baixo_estoque.append(produto)
        if produto.quantidade > limite_excesso_estoque:
            produtos_excesso_estoque.append(produto)

    # Garantir que os dados estão sendo passados para o template corretamente
    return render_template('relatorio.html', 
                           produtos_baixo_estoque=produtos_baixo_estoque, 
                           produtos_excesso_estoque=produtos_excesso_estoque)


if __name__ == '__main__':
    app.run(debug=True)
