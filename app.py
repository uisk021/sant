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

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("🤖 SANT; AI ativada com sucesso via Gemini!")
    except Exception as e:
        print(f"⚠️ Erro ao configurar Gemini: {e}")
        model = None
else:
    print("⚠️ GEMINI_API_KEY não encontrada. Usando modo de respostas padrão.")
    model = None

PROMPT_SANT_AI = """
Você é a SANT; AI, assistente virtual oficial da agência SANT;.
Responda de forma sofisticada, direta, técnica e em no máximo 2 parágrafos curtos.
Use ponto e vírgula ";" em frases de destaque.
Seu objetivo é explicar o Método AGA; (Arquitetura, Gestão, Autonomia) e convidar o cliente a qualificar o projeto no WhatsApp.
O Plano SANT; CONTINUUM; custa Entrada de R$ 390 (Fundador) ou R$ 490 (Oficial) + 11x R$ 350 ou R$ 450/mês.
"""

SEU_WHATSAPP = "5511999999999"  # 👈 Coloque seu número com DDD

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

# ROTA 1: HOME
@app.route('/')
def index():
    portfolio_images = []
    if os.path.exists(PORTFOLIO_DIR):
        for filename in os.listdir(PORTFOLIO_DIR):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                portfolio_images.append(filename)
                
    return render_template('index.html', portfolio_images=portfolio_images)

# ROTA 2: LINKTREE / BIO
@app.route('/links')
@app.route('/bio')
def bio_links():
    return render_template('links.html')

# ROTA 3: API DA INTELIGÊNCIA ARTIFICIAL DO CHATBOT 🤖
@app.route('/api/chat-ai', methods=['POST'])
def chat_ai():
    dados = request.get_json() or {}
    mensagem_usuario = dados.get("mensagem", "").strip()
    
    if not mensagem_usuario:
        return jsonify({"resposta": "Por favor, digite uma mensagem válida."})

    # Se tiver a chave da API do Gemini configurada:
    if model is not None:
        try:
            prompt_completo = f"{PROMPT_SANT_AI}\n\nCliente perguntou: {mensagem_usuario}\nSANT; AI:"
            response = model.generate_content(prompt_completo)
            return jsonify({"resposta": response.text})
        except Exception as e:
            print(f"Erro na geração da IA: {e}")

    # Fallback de respostas rápidas (se não tiver chave da API)
    msg_low = mensagem_usuario.lower()
    if "continuum" in msg_low or "plano" in msg_low or "preco" in msg_low or "preço" in msg_low:
        resp = "O **Plano SANT; CONTINUUM;** inclui o desenvolvimento do seu Site AEO-Native + Autobot de IA + 12 meses de suporte e reuniões de BI por **Entrada de R$ 390 (Lote Fundador) + 11x de R$ 350/mês**. Quer qualificar seu projeto agora no WhatsApp?"
    elif "discord" in msg_low or "bot" in msg_low or "patinho" in msg_low:
        resp = "Desenvolvemos bots personalizados em Python, sistemas de economia, lojas Pix automáticas e portais web integrados (como o Patinho Bot da Rádio Habbler). Nossos pacotes de bot partem de R$ 150!"
    elif "aga" in msg_low or "metodo" in msg_low or "método" in msg_low:
        resp = "O **Método AGA;** é nossa metodologia exclusiva baseada em 3 pilares: **Arquitetura** (Brand + Web), **Gestão** (Growth, Social Media e BI no DashSocial;) e **Autonomia** (Autobot de IA 24/7 no WhatsApp)."
    else:
        resp = f"Perfeito! Entendi sua dúvida sobre '{mensagem_usuario}'. Para analisarmos o escopo da sua empresa e apresentarmos a melhor arquitetura, clique no botão e fale com nossa equipe no WhatsApp ;"

    return jsonify({"resposta": resp})

# ROTA 4: ENCURTADOR
@app.route('/<short_code>')
def redirecionar_link(short_code):
    codigo = short_code.lower().strip()
    if codigo in LINKS_ENCURTADOS:
        return redirect(LINKS_ENCURTADOS[codigo])
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
