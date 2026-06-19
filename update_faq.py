import json
import re

faq_replacements = {
    "J\\u00e1 sou cliente Ambev, como cadastrar no Coca Cola?": "Para garantir a segurança e a agilidade no atendimento, informamos que todo o processo de cadastro, compras e suporte deve ser realizado de forma obrigatória com um de nossos agentes oficiais pelo WhatsApp. Por favor, clique no botão de atendimento para iniciar o seu processo de forma segura.",
    
    "Ainda n\\u00e3o sou cliente Ambev, como ser cliente e cadastrar no Coca Cola?": "O cadastramento de novos clientes é realizado exclusivamente por intermédio de um agente oficial através do nosso canal de WhatsApp. Para se tornar nosso cliente e realizar suas compras, pedimos que entre em contato conosco pelo WhatsApp, onde nossa equipe auxiliará em todas as etapas de aprovação.",
    
    "Como recuperar minha senha no Coca Cola?": "Qualquer solicitação referente a recuperação de acesso, redefinição de senha ou suporte à conta deve ser tratada obrigatoriamente com um de nossos agentes oficiais pelo WhatsApp. Entre em contato pelo nosso canal oficial de atendimento para que possamos validar seus dados e restaurar o seu acesso.",
    
    "Como baixar o Coca Cola?": "Para sua comodidade e segurança, todo o processo de acesso e downloads deve ser assistido por nossa equipe. Por favor, acesse o WhatsApp oficial disponível no site e fale com um agente para receber as instruções e links seguros para acessar nossa plataforma de atendimento.",
    
    "Como fazer um pedido pelo Coca Cola?": "Ressaltamos que todas as compras, cotações e emissão de novos pedidos são obrigatoriamente guiadas e validadas por um agente oficial da nossa equipe. Para fazer um pedido, entre em contato imediatamente com o nosso WhatsApp de atendimento, onde seu processo será conduzido com total transparência e segurança.",
    
    "Como consultar meus pedidos anteriores?": "O histórico completo de pedidos, status de faturamento e detalhes de entregas estão centralizados no nosso canal de atendimento humanizado. Para consultar qualquer informação referente às suas transações anteriores, basta solicitar diretamente a um agente oficial através do WhatsApp.",
    
    "Como abrir uma solicita\\u00e7\\u00e3o no Coca Cola?": "Toda e qualquer assistência técnica, abertura de chamados, envio de comprovantes ou suporte geral deve ser feita impreterivelmente através de um de nossos agentes pelo WhatsApp. Desta maneira, conseguimos dar andamento ao seu chamado de forma oficial e protocolada."
}

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
if match:
    data = json.loads(match.group(1))
    
    def replace_faq_answers(node):
        if isinstance(node, dict):
            # If this is a Collapse block (FAQ question)
            if node.get("blockType") == "Collapse" and "title" in node.get("attributes", {}):
                question_title = node["attributes"]["title"]
                
                # Check if this question matches one of ours (handling decoded unicode)
                for q_key, new_answer in faq_replacements.items():
                    # Compare decoded version
                    decoded_q_key = q_key.encode('utf-8').decode('unicode_escape')
                    if decoded_q_key == question_title or q_key == question_title:
                        # Find the text block inside this Collapse and replace its text
                        def set_answer(n):
                            if isinstance(n, dict):
                                if n.get("blockType") == "Text" and "text" in n:
                                    n["text"] = new_answer
                                    return True
                                for k, v in n.items():
                                    if set_answer(v): return True
                            elif isinstance(n, list):
                                for item in n:
                                    if set_answer(item): return True
                            return False
                        
                        set_answer(node["blocks"])
                        
            for k, v in node.items():
                replace_faq_answers(v)
        elif isinstance(node, list):
            for item in node:
                replace_faq_answers(item)

    replace_faq_answers(data)
    new_json = json.dumps(data, separators=(',', ':'))
    html = html[:match.start(1)] + new_json + html[match.end(1):]
    
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
    
print("FAQ answers updated successfully!")
