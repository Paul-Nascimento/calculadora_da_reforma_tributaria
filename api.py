# api.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from calculadora_v2 import (
    calcular_simples_comparativo,
    calculadora_lucro_presumido,
    calculadora_lucro_real,
    get_preco_liquido_lucro_presumido,
    get_preco_liquido_lucro_real,
    get_difal_pa,
)

def create_app():
    app = Flask(__name__)

    # CORS configurado para o domínio do Vercel
    CORS(
        app,
        resources={r"/*": {"origins": ["https://calculadora-da-reforma-frontend.vercel.app",'http://localhost:5173']}},
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "OPTIONS"],
        max_age=86400,
    )

    @app.get("/")
    def root():
        return {"status": "ok"}

    @app.get("/health")
    def health():
        return {"ok": True}

    @app.post("/calcular_simples_comparativo")
    def calcular_simples():
        data = request.get_json(force=True)
        resultado = calcular_simples_comparativo(
            anexo=data["anexo"],
            rbt12=float(data["rbt12"]),
            faturamento=float(data["faturamento"]),
            ano=int(data["ano"]),
            credito_pis_cofins=bool(data.get("credito_pis_cofins", False)),
        )
        return jsonify(resultado)

    @app.post("/calculadora_presumido")
    def calcular_presumido():
        data = request.get_json(force=True)
        preco_liquido = get_preco_liquido_lucro_presumido(
            valor_total=float(data["valor_total"]),
            aliquota_tributo=float(data["aliquota_tributo"]),
            aliquota_pis_cofins=0.0365,
            tipo=data["tipo"]
        )


        resultado = calculadora_lucro_presumido(
            preco_liquido=preco_liquido,
            ano=int(data["ano"]),
            aliquota=float(data["aliquota_tributo"]),
            uf_entrada=data['uf_entrada'],
            uf_saida=data['uf_saida'],
            credito_pis_cofins=bool(data.get("credito_pis_cofins", False)),
            aliquota_ibs=data['aliquota_ibs'] * ( 1 - data['percentual_de_reducao_ibs_cbs']),
            aliquota_cbs=data['aliquota_cbs'] * ( 1 - data['percentual_de_reducao_ibs_cbs']),
            tipo=data["tipo"],
            ibs_cbs_na_base=data['ibs_cbs_na_base']
        )

        return jsonify({
            "preco_liquido": preco_liquido,
            "custo": resultado["custo"],
            "tributo_efetivo": resultado["tributo_efetivo"],
            "bc_tributo": resultado["bc_tributo"],
            "irpj_efetivo": resultado["irpj_efetivo"],
            "csll_efetivo": resultado["csll_efetivo"],
            "pis_cofins_efetivo": resultado["pis_cofins_efetivo"],
            "ibs": resultado["ibs"],
            "cbs": resultado["cbs"],
        })

    @app.post("/calculadora_real")
    def calcular_real():
        data = request.get_json(force=True)
        preco_liquido = get_preco_liquido_lucro_real(
            valor_total=float(data["valor_total"]),
            aliquota_tributo=float(data["aliquota_tributo"]),
            aliquota_pis_cofins=0.0925
        )

        

        resultado = calculadora_lucro_real(
            preco_liquido=preco_liquido,
            ano=int(data["ano"]),
            aliquota=float(data["aliquota_tributo"]),
            credito_pis_cofins=bool(data.get("credito_pis_cofins", False)),
            aliquota_ibs=data['aliquota_ibs'] * ( 1 - data['percentual_de_reducao_ibs_cbs']),
            aliquota_cbs=data['aliquota_cbs'] * ( 1 - data['percentual_de_reducao_ibs_cbs']),
            ibs_cbs_na_base=data['ibs_cbs_na_base'],
            tipo=data['tipo'],
            uf_entrada=data['uf_entrada'],
            uf_saida=data['uf_saida'],
        )

        return jsonify({
            "preco_liquido": preco_liquido,
            "custo": resultado["custo"],
            "tributo_efetivo": resultado["tributo_efetivo"],
            "bc_tributo": resultado["bc_tributo"],
            "pis_cofins_efetivo": resultado["pis_cofins_efetivo"],
            "ibs": resultado["ibs"],
            "cbs": resultado["cbs"],
        })

    return app


# para uso no gunicorn: "api:app"
app = create_app()

if __name__ == "__main__":
    # Em produção o Render injeta $PORT
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
