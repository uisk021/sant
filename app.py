import os
from datetime import datetime
from flask import Flask, render_template, redirect, request, jsonify
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

from google import genai

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
PORTFOLIO_DIR = os.path.join(STATIC_DIR, "portfolio")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

# ============================================
# 🤖 CONFIGURAÇÃO DA IA SANT; (TESTE ÚNICO NO STARTUP)
# ============================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

client = None
WORKING_MODEL = None

if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        # Teste único de inicialização para não gerar atraso nos usuários
        test_resp = client.models.generate_content(
            model='gemini-1.5-flash',
            contents='ping'
        )
        if test_resp and test_resp.text:
            WORKING_MODEL = 'gemini-1.5-flash'
            print("🤖 SANT; AI ativada e testada no modelo gemini-1.5-flash!", flush=True)
    except Exception as e:
        print(f"⚠️ Gemini indisponível no startup ({e}). Ativando modo inteligente de alta velocidade.", flush=True)
else:
    print("⚠️ GEMINI_API_KEY não encontrada no .env ou Render.", flush=True)

PROMPT_SANT_AI = """
Você é a SANT; AI, a inteligência artificial oficial de atendimento da agência de aceleração digital SANT;.

SUA PERSONALIDADE & TOM DE VOZ:
- Sofisticada, direta, técnica, educada, humana e de alto padrão (High-Ticket).
- Você usa o estilo visual da marca: use pontuação com ponto e vírgula ";" em frases de destaque.
- Respostas curtas de no máximo 1 a 2 parágrafos curtos.

SOU A SANT;:
- Não vendemos sites comuns, construímos ecossistemas digitais de vendas autônomas.
- Método AGA;: Arquitetura (Brand + Web), Gestão (Ads + Social + BI) e Autonomia (Autobot IA 24/7).
- Plano SANT; CONTINUUM;: Entrada de R$ 390 (Fundador) ou R$ 490 (Oficial) + 11x de R$ 350 ou R$ 450/mês.
- Discord: Desenvolvemos bots em Python, economia, loja Pix automática e portais integrados (ex: Patinho Bot da Rádio Habbler).

SUA MISSÃO:
Responder a dúvida do cliente com clareza e sempre convidar para qualificar o projeto no WhatsApp comercial.
"""

SEU_WHATSAPP = "5511999999999"  # 👈 Coloque seu DDD + Número real aqui

LINKS_ENCURTADOS = {
    "zap": f"https://wa.me/{SEU_WHATSAPP}?text=Ol%C3%A1%20SANT%3B!%20Vim%20pelo%20link%20encurtado.",
    "whatsapp": f"https://wa.me/{SEU_WHATSAPP}",
    "insta": "https://www.instagram.com/sant.social/",
    "instagram": "https://www.instagram.com/sant.social/",
    "patinho": "https://bot-radio-habbler.onrender.com",
}

@app.context_processor
def inject_year():
    return {'ano_atual': datetime.now().year}

# 1. HOME
@app.route('/')
def index():
    portfolio_images = []
    if os.path.exists(PORTFOLIO_DIR):
        for filename in os.listdir(PORTFOLIO_DIR):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                portfolio_images.append(filename)
                
    return render_template('index.html', portfolio_images=portfolio_images)

# 2. LINKTREE / BIO
@app.route('/links')
@app.route('/bio')
def bio_links():
    return render_template('links.html')

# 3. API DA INTELIGÊNCIA ARTIFICIAL (RESPOSTA INSTANTÂNEA EM < 1 SEGUNDO)
@app.route('/api/chat-ai', methods=['POST'])
def chat_ai():
    dados = request.get_json() or {}
    mensagem_usuario = dados.get("mensagem", "").strip()
    
    if not mensagem_usuario:
        return jsonify({"resposta": "Como posso te ajudar a escalar sua presença digital hoje?"})

    # 1. CHAMADA DIRETA DA IA (Sem loops de atraso)
    if client is not None and WORKING_MODEL is not None:
        try:
            prompt_completo = f"{PROMPT_SANT_AI}\n\nCliente perguntou: {mensagem_usuario}\nSANT; AI:"
            response = client.models.generate_content(
                model=WORKING_MODEL,
                contents=prompt_completo
            )
            if response and response.text:
                print(f"✅ [GEMINI RESPONDEU]: {response.text[:50]}...", flush=True)
                return jsonify({"resposta": response.text.strip()})
        except Exception as e:
            print(f"⚠️ Instabilidade na IA: {e}", flush=True)

    # 2. RESPOSTA DE ALTA VELOCIDADE (Executa em 0.05 segundos)
    msg = mensagem_usuario.lower()

    if any(p in msg for p in ["quanto", "preco", "preço", "valor", "custo", "investimento", "orcamento", "orçamento"]):
        resp = "Nossos ecossistemas empresariais operam pelo **Plano SANT; CONTINUUM;**: por **Entrada de R$ 390 + 11x de R$ 350/mês**, você recebe o site completo, o Autobot e 12 meses de acompanhamento ;"
    elif any(p in msg for p in ["onde", "aonde", "fica", "local", "cidade", "estado"]):
        resp = "A SANT; é uma agência 100% digital e AEO-Native. Atendemos empresas de todo o Brasil e do exterior de forma remota e ágil ;"
    elif any(p in msg for p in ["como", "funciona", "passo", "processo", "metodo", "método", "aga"]):
        resp = "Operamos através do **Método AGA;**: construímos seu site AEO-Native integrado ao Autobot de IA que atende, qualifica e envia o lead pronto para o seu WhatsApp 24/7. Quer ver uma demonstração do processo?"
    elif any(p in msg for p in ["discord", "bot", "patinho", "servidor", "comunidade"]):
        resp = "Desenvolvemos bots sob medida em Python, lojas Pix automáticas e portais web integrados (como o famoso Patinho Bot da Rádio Habbler). Seus projetos no Discord partem de R$ 150 ;"
    elif any(p in msg for p in ["prazo", "tempo", "demora", "entrega", "dias"]):
        resp = "O prazo médio de entrega do seu ecossistema completo (Site + Autobot de IA configurado) é de **7 a 15 dias úteis** após o envio das informações do seu negócio ;"
    elif any(p in msg for p in ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite", "hey"]):
        resp = "Olá! Seja bem-vindo à SANT;. Como posso ajudar a escalar a presença digital do seu negócio hoje?"
    else:
        resp = "Para analisarmos a arquitetura exata para o seu caso, clique no botão e fale direto com nossos especialistas no WhatsApp ;"

    return jsonify({"resposta": resp})

# 4. ENCURTADOR DE LINKS
@app.route('/<short_code>')
def redirecionar_link(short_code):
    codigo = short_code.lower().strip()
    if codigo in LINKS_ENCURTADOS:
        return redirect(LINKS_ENCURTADOS[codigo])
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
