import requests
import pprint


def rastrear_encomenda(codigo_rastreamento):
    url = f"https://api.linketrack.com/track/json?user=teste&token=1abcd00b2731640e886fb41a8a9671ad1434c599dbaa0a0de9a5aa619f29a83f&codigo={codigo_rastreamento}"

    response = requests.get(url)
    data = response.json()

    if "erro" in data:
        return {"error": "Código de rastreamento inválido."}
    else:
        eventos = data.get("eventos", [])
        eventos_formatados = []
        for i in eventos:
            data_evento = i.get("data", "")
            hora_evento = i.get("hora", "")
            local_evento = i.get("local", "")
            status_evento = i.get("status", "")
            subStatus = i.get("subStatus", "")

            evento_formatado = {
                "data": data_evento,
                "hora": hora_evento,
                "local": local_evento,
                "status": status_evento,
                subStatus: subStatus
            }
            eventos_formatados.append(evento_formatado)
        return eventos_formatados


codigo_rastreamento = "LB577473955HK"
result = rastrear_encomenda(codigo_rastreamento)
pp = pprint.PrettyPrinter(depth=6)
pp.pprint(result)
