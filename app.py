import os
from datetime import datetime
from flask import Flask, render_template, redirect, request, jsonify
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env (Ambiente Local)
load_dotenv()

# NOVO SDK OFICIAL DA GOOGLE
from google import genai

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
PORTFOLIO_DIR = os.path.join(STATIC_DIR, "portfolio")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

# ============================================
# 📅 1. INJETA O ANO ATUAL AUTOMATICAMENTE
# ============================================
@app.context_processor
def inject_year():
    return {'ano_atual': datetime.now().year}

# ============================================
# ⚙️ 2. CONFIGURAÇÕES & WHATSAPP DA SANT;
# ============================================
SEU_WHATSAPP = "5521986010634"  # 👈 Coloque seu DDD + Número real aqui

ZAP_LINK_BASE = f"https://wa.me/{SEU_WHATSAPP}?text="

LINKS_ENCURTADOS = {
    "zap": f"{ZAP_LINK_BASE}Ol%C3%A1%20SANT%3B!%20Vim%20pelo%20link%20encurtado.",
    "whatsapp": f"https://wa.me/{SEU_WHATSAPP}",
    "insta": "https://www.instagram.com/sant.social/",
    "instagram": "https://www.instagram.com/sant.social/",
    "patinho": "https://bot-radio-habbler.onrender.com",
}

# ============================================
# 🤖 3. CONFIGURAÇÃO DA IA SANT; (SDK GOOGLE-GENAI)
# ============================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

client = None
if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        print("🤖 SANT; AI ativada com sucesso via SDK google-genai!", flush=True)
    except Exception as e:
        print(f"⚠️ Erro ao inicializar o cliente do Gemini: {e}", flush=True)
else:
    print("⚠️ GEMINI_API_KEY não encontrada no arquivo .env ou no Render.", flush=True)

PROMPT_SANT_AI = f"""
Você é a SANT; AI, a inteligência artificial oficial de atendimento da agência de aceleração digital SANT;.

SUA PERSONALIDADE & TOM DE VOZ:
- Sofisticada, direta, técnica, educada, humana e de alto padrão (High-Ticket).
- Você usa o estilo visual da marca: use pontuação com ponto e vírgula ";" em frases de destaque.
- Respostas curtas e elegantes de 1 a 2 parágrafos.

SOU A SANT;:
- Não vendemos sites comuns, construímos ecossistemas digitais de vendas autônomas.
- Método AGA;: Arquitetura (Brand + Web), Gestão (Ads + Social + BI) e Autonomia (Autobot IA 24/7).
- Plano SANT; CONTINUUM;: Entrada de R$ 390 (Fundador) ou R$ 490 (Oficial) + 11x de R$ 350 ou R$ 450/mês.
- Discord: Desenvolvemos bots em Python (a partir de R$ 150), economia, loja Pix automática e portais integrados (ex: Patinho Bot da Rádio Habbler).

SUA MISSÃO:
Responder a dúvida do cliente com clareza e SEMPRE incluir o link formatado [Falar no WhatsApp](https://wa.me/{SEU_WHATSAPP}) para ele agendar a reunião.
"""

# ============================================
# 🏠 4. ROTA 1: HOME (PÁGINA PRINCIPAL)
# ============================================
@app.route('/')
def index():
    portfolio_images = []
    if os.path.exists(PORTFOLIO_DIR):
        for filename in os.listdir(PORTFOLIO_DIR):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                portfolio_images.append(filename)
                
    return render_template('index.html', portfolio_images=portfolio_images)

# ============================================
# 📱 5. ROTA 2: LINKTREE / BIO EXCLUSIVO
# ============================================
@app.route('/links')
@app.route('/bio')
def bio_links():
    return render_template('links.html')

# ============================================
# 🤖 6. ROTA 3: API DA IA (SANT; AI - RESPOSTAS ESPECÍFICAS)
# ============================================
@app.route('/api/chat-ai', methods=['POST'])
def chat_ai():
    dados = request.get_json() or {}
    mensagem_usuario = dados.get("mensagem", "").strip()
    
    if not mensagem_usuario:
        return jsonify({"resposta": "Como posso te ajudar a escalar sua presença digital hoje?"})

    msg = mensagem_usuario.lower().strip()

      if len(msg) < 3 and msg not in ["oi", "ok", "bi", "ia"]:
        resp = (
            "Não consegui compreender totalmente sua mensagem. Como a SANT; pode ajudar sua empresa hoje? "
            "Você pode escolher uma das opções acima ou [Falar no WhatsApp](https://wa.me/" + SEU_WHATSAPP + ") com nossos especialistas ;"
        )
        return jsonify({"resposta": resp})

    # 1. RESPOSTAS DIRETAS DAS PÍLULAS DO SITE (RESPOSTA INSTANTÂNEA + LINK WHATSAPP)
    
    # Pílula: Discord & Bots
    if any(p in msg for p in ["discord", "bot", "patinho", "servidor", "comunidade", "serviços para discord"]):
        resp = (
            "Desenvolvemos soluções completas para Discord! Criamos Bots personalizados em Python (a partir de R$ 150), "
            "Sistemas de Loja Pix automáticos e Portais Web integrados com ranking e rádio (como o famoso Patinho Bot) ;\n\n"
            f"👉 [Solicitar Projeto para Discord no WhatsApp](https://wa.me/{SEU_WHATSAPP}?text=Ol%C3%A1%20SANT%3B!%20Tenho%20interesse%20em%20projetos%20para%20Discord.)"
        )
        return jsonify({"resposta": resp})

    # Pílula: Plano Continuum
    elif any(p in msg for p in ["continuum", "plano continuum", "fidelidade", "anual"]):
        resp = (
            "O **Plano SANT; CONTINUUM;** é nosso programa de aceleração anual com 20% OFF: por **Entrada de R$ 390 (Lote Fundador) + 11x de R$ 350/mês**, "
            "sua empresa recebe o site completo AEO-Native, o Autobot de IA e 12 meses de suporte, atualizações e reuniões de BI ;\n\n"
            f"👉 [Garantir Vaga de Fundador no WhatsApp](https://wa.me/{SEU_WHATSAPP}?text=Ol%C3%A1%20SANT%3B!%20Quero%20garantir%20minha%20vaga%20no%20Plano%20Continuum.)"
        )
        return jsonify({"resposta": resp})

    # Pílula: Brand & Rebrand
    elif any(p in msg for p in ["brand", "rebrand", "marca", "logo", "identidade"]):
        resp = (
            "No **Brand & Rebrand;**, redefinimos o posicionamento da sua empresa com identidade visual High-Ticket, "
            "manual de marca, tipografia e paleta estratégica para você transmitir autoridade imediata e parar de dar desconto ;\n\n"
            f"👉 [Solicitar Rebrand no WhatsApp](https://wa.me/{SEU_WHATSAPP}?text=Ol%C3%A1%20SANT%3B!%20Quero%20fazer%20o%20Rebrand%20da%20minha%20empresa.)"
        )
        return jsonify({"resposta": resp})

    # Pílula: Growth & Ads
    elif any(p in msg for p in ["growth", "ads", "trafego", "tráfego", "anúncio", "anuncio"]):
        resp = (
            "No **Growth & Ads;**, gerenciamos suas campanhas de tráfego pago no Meta e Google Ads com foco em menor Custo por Lead "
            "e ROI real, tudo integrado ao Autobot e acompanhado pelo painel **DashSocial;** ;\n\n"
            f"👉 [Acelerar Vendas com Tráfego Pago](https://wa.me/{SEU_WHATSAPP}?text=Ol%C3%A1%20SANT%3B!%20Quero%20acelerar%20minhas%20vendas%20com%20Growth.)"
        )
        return jsonify({"resposta": resp})

    # Pílula: Social Media
    elif any(p in msg for p in ["social", "media", "mídia", "reels", "post", "conteudo", "conteúdo"]):
        resp = (
            "No **Social Media Strategy;**, produzimos conteúdo de alta retenção com copywriting visceral e design de elite "
            "para transformar seguidores em compradores no WhatsApp, sem perder tempo com posts irrelevantes ;\n\n"
            f"👉 [Estruturar meu Social Media no WhatsApp](https://wa.me/{SEU_WHATSAPP}?text=Ol%C3%A1%20SANT%3B!%20Quero%20aumentar%20as%20vendas%20com%20Social%20Media.)"
        )
        return jsonify({"resposta": resp})

    # Pílula: Métricas & BI
    elif any(p in msg for p in ["métricas", "metricas", "bi", "dash", "dashboard", "dashsocial"]):
        resp = (
            "Com nosso módulo de **Métricas & BI;**, você acompanha todas as vendas e atendimentos do Autobot em tempo real "
            "através do seu painel exclusivo **DashSocial;** no celular ou computador ;\n\n"
            f"👉 [Ver Demonstração do DashSocial; no WhatsApp](https://wa.me/{SEU_WHATSAPP}?text=Ol%C3%A1%20SANT%3B!%20Quero%20conhecer%20o%20DashSocial.)"
        )
        return jsonify({"resposta": resp})

    # Afirmativas ("sim", "ok", "quero", "claro", "bora")
    elif msg in ["sim", "sim!", "ok", "claro", "com certeza", "quero", "bora", "pode ser", "vamos"]:
        resp = (
            "Excelente! 🚀 Clique no link abaixo para abrir a conversa direta com nosso time comercial no WhatsApp e qualificar seu projeto agora mesmo:\n\n"
            f"👉 [Iniciar Atendimento no WhatsApp](https://wa.me/{SEU_WHATSAPP}?text=Ol%C3%A1%20SANT%3B!%20Quero%20iniciar%20meu%20projeto.)"
        )
        return jsonify({"resposta": resp})

    # 2. TENTA RESPOSTA VIA SDK GOOGLE-GENAI (Para perguntas livres)
    if client is not None:
        modelos_validos = ['gemini-2.0-flash', 'gemini-1.5-flash']
        for modelo_nome in modelos_validos:
            try:
                prompt_completo = f"{PROMPT_SANT_AI}\n\nCliente perguntou: {mensagem_usuario}\nSANT; AI:"
                
                response = client.models.generate_content(
                    model=modelo_nome,
                    contents=prompt_completo
                )
                
                texto_resposta = None
                try:
                    if response and response.text:
                        texto_resposta = response.text.strip()
                except Exception:
                    pass

                if texto_resposta:
                    print(f"✅ [GEMINI ({modelo_nome}) RESPONDEU]: {texto_resposta[:50]}...", flush=True)
                    return jsonify({"resposta": texto_resposta})

            except Exception as e:
                print(f"⚠️ Alerta Gemini ({modelo_nome}): {e}", flush=True)
                continue

    # 3. FALLBACK GENÉRICO COM LINK DE WHATSAPP (Para qualquer outra dúvida)
    resp = (
        f"Entendi perfeitamente sua dúvida sobre '{mensagem_usuario}'! Para analisarmos a arquitetura exata do Método AGA; para o seu caso, fale direto com nossos especialistas no WhatsApp comercial ;\n\n"
        f"👉 [Falar com a Equipe no WhatsApp](https://wa.me/{SEU_WHATSAPP}?text=Ol%C3%A1%20SANT%3B!%20Tenho%20uma%20d%C3%BAvida%20sobre%20{mensagem_usuario}.)"
    )

    return jsonify({"resposta": resp})

# ============================================
# 🚀 7. ROTA 4: ENCURTADOR DE LINKS
# ============================================
@app.route('/<short_code>')
def redirecionar_link(short_code):
    codigo = short_code.lower().strip()
    if codigo in LINKS_ENCURTADOS:
        return redirect(LINKS_ENCURTADOS[codigo])
    return redirect('/')

# ============================================
# EXECUÇÃO LOCAL / RENDER
# ============================================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
