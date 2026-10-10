import os
from datetime import datetime
from flask import Flask, render_template, redirect, request, jsonify
import google.generativeai as genai

# Tenta carregar o .env local no seu PC. No Render, as variáveis entram direto!
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
PORTFOLIO_DIR = os.path.join(STATIC_DIR, "portfolio")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
# ============================================
# 🤖 CONFIGURAÇÃO DA IA SANT; (GEMINI + FALLBACK HIGH-TICKET)
# ============================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

model = None
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("🤖 SANT; AI ativada com sucesso via Gemini!", flush=True)
    except Exception as e:
        print(f"⚠️ Erro ao configurar Gemini: {e}", flush=True)

PROMPT_SANT_AI = """
Você é a SANT; AI, a inteligência artificial oficial de atendimento da agência de aceleração digital SANT;.

SUA PERSONALIDADE & TOM DE VOZ:
- Sofisticada, direta, técnica, educada, humana e de alto padrão (High-Ticket).
- Use o estilo visual da marca: use pontuação com ponto e vírgula ";" em frases de destaque.
- Respostas curtas e elegantes de 1 a 2 parágrafos. Nunca seja robótica.

REGRAS DE RESPOSTA PARA VALORES/PREÇOS:
- Se perguntarem "quanto é?", "valores", "quanto custa" ou "preços":
  Explique que os projetos empresariais operam pelo PLANO SANT; CONTINUUM; (Site + Autobot IA + 12 meses de suporte) por Entrada de R$ 390,00 (Lote Fundador) ou R$ 490,00 (Tabela Oficial) + 11x de R$ 350,00 ou R$ 450,00/mês. Para bots de Discord, partem de R$ 150,00.
"""

@app.route('/api/chat-ai', methods=['POST'])
def chat_ai():
    dados = request.get_json() or {}
    mensagem_usuario = dados.get("mensagem", "").strip()
    
    if not mensagem_usuario:
        return jsonify({"resposta": "Como posso te ajudar a escalar sua presença digital hoje?"})

    # 1. TENTA RESPOSTA COM GEMINI IA
    if model is not None:
        try:
            prompt_completo = f"{PROMPT_SANT_AI}\n\nCliente perguntou: {mensagem_usuario}\nSANT; AI:"
            response = model.generate_content(prompt_completo)
            if response and response.text:
                return jsonify({"resposta": response.text.strip()})
        except Exception as e:
            print(f"Erro na IA Gemini: {e}", flush=True)

    # 2. MODO HIGH-TICKET INTELIGENTE (Trata todas as variações em português natural)
    msg = mensagem_usuario.lower()

    # Pergunta de Preço / Valores ("quanto é?", "quanto fica?", "valores?", "preço")
    if any(p in msg for p in ["quanto", "preco", "preço", "valor", "custo", "investimento", "orcamento", "orçamento", "cotacao", "cotação", "tabela"]):
        resp = "Nossos ecossistemas empresariais operam pelo **Plano SANT; CONTINUUM;**: por **Entrada de R$ 390 (Lote Fundador) + 11x de R$ 350/mês**, você recebe o site completo, o Autobot de IA e 12 meses de acompanhamento e reuniões de BI ;\n\nPara bots e comunidades do Discord, os projetos partem de R$ 150. Qual é a necessidade atual da sua empresa?"

    # Pergunta de Onde Fica / Localização ("onde fica?", "aonde fica?", "endereço", "cidade")
    elif any(p in msg for p in ["onde", "aonde", "fica", "local", "endereco", "endereço", "cidade", "estado", "atendem"]):
        resp = "A SANT; é uma agência 100% digital e AEO-Native. Atendemos empresas e criadores de todo o Brasil e do exterior de forma remota, ágil e segura. Onde está localizada a sua empresa?"

    # Pergunta de Funcionamento / Método ("como funciona?", "como faço?", "metodo")
    elif any(p in msg for p in ["como", "funciona", "passo", "processo", "metodo", "método", "aga"]):
        resp = "Operamos através do **Método AGA;**: construímos seu site AEO-Native integrado ao Autobot de IA que atende, qualifica e envia o lead pronto para o seu WhatsApp 24/7. Quer ver uma demonstração do processo?"

    # Pergunta sobre Discord / Bots ("discord", "bot", "patinho")
    elif any(p in msg for p in ["discord", "bot", "patinho", "servidor", "comunidade"]):
        resp = "Desenvolvemos bots sob medida em Python, lojas Pix automáticas e portais web integrados (como o famoso Patinho Bot da Rádio Habbler). Seus projetos no Discord partem de R$ 150 ;"

    # Pergunta de Prazos ("prazo", "demora", "tempo")
    elif any(p in msg for p in ["prazo", "tempo", "demora", "entrega", "dias"]):
        resp = "O prazo médio de entrega do seu ecossistema completo (Site + Autobot de IA configurado) é de **7 a 15 dias úteis** após o envio das informações do seu negócio ;"

    # Saudações ("oi", "olá", "boa tarde")
    elif any(p in msg for p in ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite", "hey", "fala"]):
        resp = "Olá! Seja bem-vindo à SANT;. Como posso ajudar a escalar a presença digital do seu negócio hoje?"

    # Qualquer outra pergunta genérica -> Resposta elegante sem parecer robô
    else:
        resp = f"Entendi sua dúvida sobre '{mensagem_usuario}'. Para apresentarmos a arquitetura exata do Método AGA; para o seu caso, clique no botão e fale direto com nossos especialistas no WhatsApp ;"

    return jsonify({"resposta": resp})
