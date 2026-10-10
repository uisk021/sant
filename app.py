import os
from datetime import datetime
from flask import Flask, render_template, redirect, request, jsonify
import google.generativeai as genai

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
PORTFOLIO_DIR = os.path.join(STATIC_DIR, "portfolio")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

# ============================================
# 🤖 CONFIGURAÇÃO DA IA SANT; (GEMINI)
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
else:
    print("⚠️ GEMINI_API_KEY não encontrada. Usando modo de respostas padrão.", flush=True)

PROMPT_SANT_AI = """
Você é a SANT; AI, assistente virtual oficial da agência de aceleração digital SANT;.

SUA PERSONALIDADE:
- Sofisticada, direta, técnica, educada e de alto padrão (High-Ticket).
- Use o estilo visual da marca: inclua ponto e vírgula ";" em frases de destaque.
- Respostas curtas de no máximo 2 parágrafos.

SOU A SANT;:
- Não vendemos sites comuns, construímos ecossistemas digitais de vendas autônomas.
- Método AGA;: Arquitetura (Brand + Web), Gestão (Ads + Social + BI) e Autonomia (Autobot IA 24/7).
- Plano SANT; CONTINUUM;: Entrada de R$ 390 (Fundador) ou R$ 490 (Oficial) + 11x de R$ 350 ou R$ 450/mês.
- Discord: Desenvolvemos bots em Python, economia, loja Pix automática e portais integrados (ex: Patinho Bot da Rádio Habbler).

SUA MISSÃO:
Responder a dúvida do cliente com clareza e sempre convidar para qualificar o projeto no WhatsApp comercial.
"""

SEU_WHATSAPP = "5511999999999"  # 👈 Coloque seu número real com DDD

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

# 3. API DA INTELIGÊNCIA ARTIFICIAL DO CHATBOT 🤖
@app.route('/api/chat-ai', methods=['POST'])
def chat_ai():
    dados = request.get_json() or {}
    mensagem_usuario = dados.get("mensagem", "").strip()
    
    if not mensagem_usuario:
        return jsonify({"resposta": "Por favor, digite uma mensagem válida."})

    # TENTA USAR A IA REAL DO GEMINI
    if model is not None:
        try:
            prompt_completo = f"{PROMPT_SANT_AI}\n\nCliente perguntou: {mensagem_usuario}\nSANT; AI:"
            response = model.generate_content(prompt_completo)
            if response and response.text:
                return jsonify({"resposta": response.text})
        except Exception as e:
            print(f"Erro na geração da IA: {e}", flush=True)

    # FALLBACK INTELIGENTE (Se a IA falhar ou estiver sem chave)
    msg = mensagem_usuario.lower()
    
    if any(p in msg for p in ["onde", "fica", "local", "endereco", "endereço", "cidade", "estado", "atendem"]):
        resp = "A SANT; é uma agência 100% digital AEO-Native! Nossos servidores e inteligências rodam na nuvem e atendemos empresas de todo o Brasil e do exterior. Todo o atendimento e implementação são feitos de forma remota e ágil ;"

    elif any(p in msg for p in ["como funciona", "como faço", "como contratar", "passo a passo", "funciona"]):
        resp = "É super simples! Nós aplicamos o **Método AGA;**: construímos seu site ultra-rápido integrado ao Autobot de IA que atende e qualifica clientes no WhatsApp 24/7. Clique no botão de WhatsApp para falar conosco ;"

    elif any(p in msg for p in ["preco", "preço", "valor", "quanto custa", "investimento", "custo"]):
        resp = "Nossos projetos empresariais operam pelo **Plano SANT; CONTINUUM;**: por **Entrada de R$ 390 (Lote Fundador) + 11x de R$ 350/mês**, você recebe o site completo, o Autobot de IA e 12 meses de suporte e reuniões de BI ;"

    elif any(p in msg for p in ["discord", "bot", "patinho", "servidor", "comunidade"]):
        resp = "Desenvolvemos bots personalizados em Python para Discord, sistemas de economia, lojas Pix automáticas e portais web integrados (como o famoso Patinho Bot da Rádio Habbler). Nossos pacotes de bot partem de R$ 150 ;"

    elif any(p in msg for p in ["prazo", "tempo", "demora", "entrega"]):
        resp = "O prazo médio de entrega do seu ecossistema completo (Site + Autobot de IA configurado) é de **7 a 15 dias úteis** após o envio das informações da sua empresa ;"

    else:
        resp = "Para analisarmos o escopo exato da sua empresa e apresentarmos a melhor arquitetura do Método AGA;, clique no botão de WhatsApp e fale direto com nossos especialistas ;"

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
