from flask import Flask, request, jsonify
from flask_cors import CORS
from calculadora_v2 import (
    calcular_simples_comparativo,
    calculadora_lucro_presumido,
    calculadora_lucro_real,
    get_preco_liquido_lucro_presumido,
    get_preco_liquido_lucro_real,
    get_difal_pa
)

app = Flask(__name__)
CORS(app)  # Libera CORS para tudo

#CORS(app, resources={r"/*": {"origins": "https://sua-app.vercel.app"}})  # domínio da Vercel


@app.route('/calcular_simples_comparativo', methods=['POST'])
def calcular_simples():
    data = request.get_json()

    print(data)
    resultado = calcular_simples_comparativo(
        anexo=data['anexo'],
        rbt12=data['rbt12'],
        faturamento=data['faturamento'],
        ano=data['ano'],
        credito_pis_cofins=data['credito_pis_cofins']
    )
    print(resultado)
    return jsonify(resultado)


@app.route('/calculadora_presumido', methods=['POST'])
def calcular_presumido():
    data = request.get_json()

    preco_liquido = get_preco_liquido_lucro_presumido(
        valor_total=data['valor_total'],
        aliquota_tributo=float(data['aliquota_tributo']),
        aliquota_pis_cofins=0.0365,
        tipo=data['tipo']
    )

    difal = 0
    if data['tipo'] == 'venda':
        difal = get_difal_pa(preco_liquido, data['ano'], data['uf_saida'], data['uf_entrada'])

    resultado = calculadora_lucro_presumido(
        preco_liquido=preco_liquido,
        ano=data['ano'],
        aliquota=float(data['aliquota_tributo']),
        difal=difal,
        credito_pis_cofins=data.get('credito_pis_cofins', False)
    )
    custo = resultado['custo']
    tributo_efetivo =resultado['tributo_efetivo']
    bc_tributo = resultado['bc_tributo']
    irpj_efetivo = resultado['irpj_efetivo']
    csll_efetivo = resultado['csll_efetivo']
    pis_cofins_efetivo = resultado['pis_cofins_efetivo']
    ibs = resultado['ibs']
    cbs = resultado['cbs']

    return jsonify({
        'preco_liquido':preco_liquido,
        'custo':custo,
        'tributo_efetivo':tributo_efetivo,
        'bc_tributo':bc_tributo,
        'irpj_efetivo':irpj_efetivo,
        'csll_efetivo':csll_efetivo,
        'pis_cofins_efetivo':pis_cofins_efetivo,
        'ibs':ibs,
        'cbs':cbs
    })


@app.route('/calculadora_real', methods=['POST'])
def calcular_real():
    data = request.get_json()

    preco_liquido = get_preco_liquido_lucro_real(
        valor_total=data['valor_total'],
        aliquota_tributo=float(data['aliquota_tributo']),
        aliquota_pis_cofins=0.0925
    )

    difal = 0
    if data['tipo'] == 'venda':
        difal = get_difal_pa(preco_liquido, data['ano'], data['uf_saida'], data['uf_entrada'])

    resultado = calculadora_lucro_real(
        preco_liquido=preco_liquido,
        ano=data['ano'],
        aliquota=float(data['aliquota_tributo']),
        difal=difal,
        credito_pis_cofins=data.get('credito_pis_cofins', False)
    )


    custo = resultado['custo']
    tributo_efetivo =resultado['tributo_efetivo']
    bc_tributo = resultado['bc_tributo']
    pis_cofins_efetivo = resultado['pis_cofins_efetivo']
    ibs = resultado['ibs']
    cbs = resultado['cbs']

    return jsonify({
        'preco_liquido':preco_liquido,
        'custo':custo,
        'tributo_efetivo':tributo_efetivo,
        'bc_tributo':bc_tributo,
        'pis_cofins_efetivo':pis_cofins_efetivo,
        'ibs':ibs,
        'cbs':cbs
    })


if __name__ == '__main__':
    app.run(debug=True)
