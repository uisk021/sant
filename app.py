import base64
import hmac
import json
import os
import time
from collections import defaultdict, deque
from datetime import date, datetime, timedelta
from urllib.parse import quote

from flask import Flask, Response, jsonify, redirect, render_template, request, session
from dotenv import load_dotenv

# A IA é opcional: a home continua funcionando com respostas guiadas
# mesmo quando o pacote google-genai não está instalado localmente.
try:
    from google import genai
except ImportError:
    genai = None

# Sheets é carregado apenas quando o DashSocial; estiver configurado.
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build as build_google_service
except ImportError:
    service_account = None
    build_google_service = None

# Carrega as variáveis do .env no ambiente local. No Render, use Environment Variables.
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.config.update(
    JSON_AS_ASCII=False,
    MAX_CONTENT_LENGTH=16 * 1024,
    SECRET_KEY=os.getenv("FLASK_SECRET_KEY", os.urandom(32)),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.getenv(
        "SESSION_COOKIE_SECURE", "0" if os.getenv("FLASK_DEBUG", "0") == "1" else "1"
    ) == "1",
)

# -----------------------------------------------------------------------------
# Configuração pública da SANT;
# -----------------------------------------------------------------------------
WHATSAPP_NUMBER = os.getenv("SANT_WHATSAPP", "5521986010634").strip()
CANONICAL_URL = os.getenv("CANONICAL_URL", "https://sant-agencia.onrender.com/").rstrip("/") + "/"
INSTAGRAM_URL = "https://www.instagram.com/sant.social/"

# -----------------------------------------------------------------------------
# DashSocial; — Google Sheets como fonte central da V1
# -----------------------------------------------------------------------------
DASHSOCIAL_SHEET_ID = os.getenv("DASHSOCIAL_SHEET_ID", "1g6IiDF-3lP7BAuNiwQg3mcqGp2D87v2gUuXI190w6Fk").strip()
DASHSOCIAL_SHEET_TAB = os.getenv("DASHSOCIAL_SHEET_TAB", "Dados_Diarios").strip()
DASHSOCIAL_ACCESS_CODE = os.getenv("DASHSOCIAL_ACCESS_CODE", "")
DASHSOCIAL_CACHE_SECONDS = max(30, int(os.getenv("DASHSOCIAL_CACHE_SECONDS", "120")))
DASHSOCIAL_SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
dashsocial_cache = {"expires_at": 0.0, "rows": None}


def dashsocial_credentials_info() -> dict:
    """Lê uma credencial de service account sem gravar a chave em arquivo."""
    raw_json = os.getenv("DASHSOCIAL_GOOGLE_CREDENTIALS_JSON", "").strip()
    raw_b64 = os.getenv("DASHSOCIAL_GOOGLE_CREDENTIALS_B64", "").strip()
    if raw_b64:
        try:
            raw_json = base64.b64decode(raw_b64).decode("utf-8")
        except Exception as error:
            raise RuntimeError("A credencial Base64 do DashSocial; é inválida.") from error
    if not raw_json:
        raise RuntimeError("A credencial do Google Sheets ainda não foi configurada.")
    try:
        payload = json.loads(raw_json)
    except json.JSONDecodeError as error:
        raise RuntimeError("A credencial JSON do DashSocial; é inválida.") from error
    if payload.get("type") != "service_account" or not payload.get("client_email"):
        raise RuntimeError("A credencial não parece ser uma service account do Google.")
    return payload


def dashsocial_sheet_rows() -> list[list]:
    """Busca e mantém em cache curto as linhas da planilha privada."""
    now = time.monotonic()
    if dashsocial_cache["rows"] is not None and dashsocial_cache["expires_at"] > now:
        return dashsocial_cache["rows"]
    if service_account is None or build_google_service is None:
        raise RuntimeError("As bibliotecas do Google Sheets não estão instaladas no servidor.")
    credentials = service_account.Credentials.from_service_account_info(
        dashsocial_credentials_info(), scopes=DASHSOCIAL_SCOPES
    )
    service = build_google_service("sheets", "v4", credentials=credentials, cache_discovery=False)
    response = service.spreadsheets().values().get(
        spreadsheetId=DASHSOCIAL_SHEET_ID,
        range=f"{DASHSOCIAL_SHEET_TAB}!A2:J",
        valueRenderOption="FORMATTED_VALUE",
    ).execute()
    rows = response.get("values", [])
    dashsocial_cache["rows"] = rows
    dashsocial_cache["expires_at"] = now + DASHSOCIAL_CACHE_SECONDS
    return rows


def dashsocial_number(value) -> float:
    if value is None or value == "":
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace("R$", "").replace(" ", "")
    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".")
    elif "," in text:
        text = text.replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return 0.0


def dashsocial_date(value) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value or "").strip()
    for pattern in ("%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(text, pattern).date()
        except ValueError:
            continue
    return None


def dashsocial_source(value: str) -> str | None:
    normalized = str(value or "").casefold().strip()
    if "pago" in normalized:
        return "Tráfego Pago"
    if "org" in normalized:
        return "Orgânico"
    if "rede" in normalized or "social" in normalized:
        return "Redes Sociais"
    if "indica" in normalized or "direto" in normalized:
        return "Indicações / Direto"
    return None


def dashsocial_metrics(days: int) -> dict:
    rows = []
    for raw_row in dashsocial_sheet_rows():
        values = list(raw_row) + [""] * max(0, 10 - len(raw_row))
        row_date = dashsocial_date(values[0])
        if row_date:
            rows.append((row_date, values))
    if not rows:
        raise RuntimeError("A aba Dados_Diarios ainda não possui linhas válidas.")

    days = min(max(int(days), 1), 366)
    end_date = max(row_date for row_date, _ in rows)
    start_date = end_date - timedelta(days=days - 1)
    sources = {name: 0.0 for name in ("Tráfego Pago", "Orgânico", "Redes Sociais", "Indicações / Direto")}
    totals = {"visitors": 0.0, "leads": 0.0, "investment": 0.0, "mql": 0.0, "sql": 0.0, "opportunities": 0.0, "clients": 0.0}

    for row_date, values in rows:
        if not start_date <= row_date <= end_date:
            continue
        totals["visitors"] += dashsocial_number(values[3])
        totals["leads"] += dashsocial_number(values[4])
        totals["investment"] += dashsocial_number(values[5])
        totals["mql"] += dashsocial_number(values[6])
        totals["sql"] += dashsocial_number(values[7])
        totals["opportunities"] += dashsocial_number(values[8])
        totals["clients"] += dashsocial_number(values[9])
        source = dashsocial_source(values[1])
        if source:
            sources[source] += dashsocial_number(values[4])

    leads = totals["leads"]
    visitors = totals["visitors"]
    return {
        "updated_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "start_date": start_date.strftime("%d/%m/%Y"),
        "end_date": end_date.strftime("%d/%m/%Y"),
        "metrics": {
            **{key: round(value, 2) for key, value in totals.items()},
            "cpl": round(totals["investment"] / leads, 2) if leads else 0.0,
            "conversion": round(totals["clients"] / leads, 4) if leads else 0.0,
            "visitor_conversion": round(totals["clients"] / visitors, 4) if visitors else 0.0,
        },
        "sources": {key: round(value, 2) for key, value in sources.items()},
    }


def dashsocial_is_authorized() -> bool:
    return not DASHSOCIAL_ACCESS_CODE or session.get("dashsocial_authorized") is True


def whatsapp_url(message: str = "") -> str:
    """Cria um link de WhatsApp seguro e com texto pré-preenchido."""
    base_url = f"https://wa.me/{WHATSAPP_NUMBER}"
    return f"{base_url}?text={quote(message)}" if message else base_url


LINKS_ENCURTADOS = {
    "zap": whatsapp_url("Olá, SANT;! Vim pelo link encurtado."),
    "whatsapp": whatsapp_url(),
    "insta": INSTAGRAM_URL,
    "instagram": INSTAGRAM_URL,
    "patinho": "https://bot-radio-habbler.onrender.com",
}


@app.context_processor
def inject_global_context():
    return {
        "ano_atual": datetime.now().year,
        "canonical_url": CANONICAL_URL,
        "whatsapp_url": whatsapp_url("Olá, SANT;! Vim pela página de links."),
    }


# -----------------------------------------------------------------------------
# Segurança básica de resposta HTTP
# -----------------------------------------------------------------------------
@app.after_request
def set_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "script-src 'self'; "
        "connect-src 'self'; "
        "base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
    )
    # Só envie HSTS quando estiver servido por HTTPS (Render/Cloudflare em produção).
    if request.headers.get("X-Forwarded-Proto", request.scheme) == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


# -----------------------------------------------------------------------------
# Gemini / SANT; AI
# -----------------------------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODELS = [
    model.strip()
    for model in os.getenv("GEMINI_MODELS", "gemini-2.0-flash,gemini-1.5-flash").split(",")
    if model.strip()
]

client = None
if GEMINI_API_KEY and genai is not None:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        print("SANT; AI: cliente Gemini inicializado.", flush=True)
    except Exception as error:
        print(f"SANT; AI: falha ao iniciar Gemini: {error}", flush=True)
elif GEMINI_API_KEY and genai is None:
    print("SANT; AI: google-genai não está instalado; usando respostas guiadas.", flush=True)
else:
    print("SANT; AI: GEMINI_API_KEY não configurada; usando respostas guiadas.", flush=True)

PROMPT_SANT_AI = """
Você é a SANT; AI, assistente oficial da SANT; — infraestrutura de crescimento com IA.

TOM:
- Fale em português do Brasil.
- Seja direto, sóbrio, técnico e educado. Não use emojis, hype, desconto ou urgência artificial.
- Responda em no máximo dois parágrafos curtos, sem Markdown e sem links.
- Diagnóstico antes de oferta: explique a perda operacional e depois a solução.

SOBRE A SANT;:
- A SANT; instala uma operação para empresas aparecerem, responderem e decidirem com dados.
- Método AGA;: Arquitetura, Gestão e Autonomia.
- O Plano SANT; CONTINUUM; é uma operação de 12 meses que integra:
  1) Brand & Rebrand; — identidade visual e posicionamento;
  2) Growth & Ads; — tráfego pago focado em ROI;
  3) Social Media Strategy; — conteúdo e roteiros de retenção;
  4) Métricas & BI; — painel próprio no DashSocial;;
  5) Web + Autobot IA 24/7; — site e atendimento autônomo;
  6) Seguro de Evolução Digital; — 12 meses de suporte e otimização;
  7) Reuniões Mensais de BI; — 12 encontros no ano com o CEO.
- O Autobot atende a primeira camada: responde, entende a demanda e organiza o contexto. Ele não substitui a equipe comercial.
- Nunca invente resultados, clientes, vagas, métricas, prazo ou garantia.
- Nunca diga que há desconto ou "20% OFF".

Seu objetivo é esclarecer a dúvida e convidar a pessoa a solicitar uma demonstração ou diagnóstico com a equipe.
""".strip()

# Rate limit simples em memória para reduzir abuso e custo de IA.
CHAT_WINDOW_SECONDS = 60
CHAT_LIMIT_PER_WINDOW = 12
chat_requests = defaultdict(deque)


def client_ip() -> str:
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    return forwarded_for.split(",")[0].strip() if forwarded_for else (request.remote_addr or "unknown")


def is_rate_limited(ip_address: str) -> bool:
    now = time.monotonic()
    history = chat_requests[ip_address]
    while history and now - history[0] > CHAT_WINDOW_SECONDS:
        history.popleft()
    if len(history) >= CHAT_LIMIT_PER_WINDOW:
        return True
    history.append(now)
    return False


def chat_payload(reply: str, cta_label: str = "Falar com a equipe no WhatsApp"):
    """Padroniza resposta de chat; o front-end exibe o CTA sem renderizar HTML vindo da IA."""
    return jsonify({
        "resposta": reply,
        "cta_label": cta_label,
        "cta_url": whatsapp_url("Olá, SANT;! Quero continuar meu diagnóstico iniciado no CHATBOT."),
    })


def direct_response(message: str):
    """Respostas objetivas para as principais intenções comerciais."""
    msg = message.casefold()

    if any(term in msg for term in ("discord", "patinho", "servidor", "comunidade", "bot para discord")):
        return chat_payload(
            "A SANT; também desenvolve soluções para Discord: bots em Python, automações, loja Pix e portais conectados. O escopo é definido conforme a comunidade e as integrações necessárias.",
            "Conversar sobre projeto para Discord",
        )

    if any(term in msg for term in ("continuum", "plano", "anual", "12 meses", "preço", "valor", "investimento")):
        return chat_payload(
            "O Plano SANT; CONTINUUM; é uma operação integrada de 12 meses: marca, tráfego, conteúdo, BI, site, Autobot e evolução contínua. A condição fundadora atual é R$ 390 de ativação mais 11 parcelas de R$ 350, sujeita à capacidade real de implantação.",
            "Solicitar apresentação do CONTINUUM;",
        )

    if any(term in msg for term in ("brand", "rebrand", "marca", "logo", "identidade", "posicionamento")):
        return chat_payload(
            "Brand & Rebrand; organiza posicionamento, identidade visual e linguagem para a empresa transmitir valor com coerência em site, conteúdo, proposta e vendas. A marca precisa sustentar o preço antes de pedir atenção.",
            "Conversar sobre Brand & Rebrand;",
        )

    if any(term in msg for term in ("growth", "ads", "tráfego", "trafego", "anúncio", "anuncio", "meta ads", "google ads")):
        return chat_payload(
            "Growth & Ads; conecta mídia, criativo e conversa qualificada. A leitura não para no clique: acompanhamos a origem até a qualificação, proposta e receita para decidir onde escalar.",
            "Conversar sobre Growth & Ads;",
        )

    if any(term in msg for term in ("social", "reels", "post", "conteúdo", "conteudo", "mídia", "midia")):
        return chat_payload(
            "Social Media Strategy; transforma o conteúdo em ativo de autoridade e venda. A pauta parte da dor do cliente, demonstra o sistema e cria prova para aquecer a próxima conversa comercial.",
            "Conversar sobre Social Media Strategy;",
        )

    if any(term in msg for term in ("métrica", "metrica", "bi", "dash", "dashboard", "dashsocial", "dado", "dados")):
        return chat_payload(
            "Métricas & BI; torna o funil legível: conversas, qualificações, reuniões, propostas e pagamentos. O DashSocial; existe para transformar dado em próxima decisão, não em relatório decorativo.",
            "Ver a lógica do DashSocial;",
        )

    if any(term in msg for term in ("site", "whatsapp", "autobot", "automação", "automacao", "atendimento")):
        return chat_payload(
            "Web + Autobot IA 24/7; conecta descoberta, resposta e qualificação. O objetivo é evitar que uma conversa com intenção fique sem contexto ou sem retorno quando a equipe não está disponível.",
            "Ver o CHATBOT em ação",
        )

    return None


def ask_gemini(user_message: str) -> str | None:
    if client is None:
        return None

    prompt = f"{PROMPT_SANT_AI}\n\nCliente: {user_message}\nSANT; AI:"
    for model_name in GEMINI_MODELS:
        try:
            response = client.models.generate_content(model=model_name, contents=prompt)
            text = getattr(response, "text", None)
            if text:
                return text.strip()[:1800]
        except Exception as error:
            print(f"SANT; AI: Gemini indisponível em {model_name}: {error}", flush=True)
    return None


# -----------------------------------------------------------------------------
# Rotas de páginas
# -----------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/links")
@app.route("/bio")
def bio_links():
    return render_template("links.html")


@app.route("/dashsocial")
def dashsocial():
    if not dashsocial_is_authorized():
        return redirect("/dashsocial/acesso")
    return render_template("dashsocial.html")


@app.route("/dashsocial/acesso", methods=["GET", "POST"])
def dashsocial_access():
    if not DASHSOCIAL_ACCESS_CODE:
        return redirect("/dashsocial")
    error = ""
    if request.method == "POST":
        submitted = request.form.get("access_code", "")
        if hmac.compare_digest(submitted, DASHSOCIAL_ACCESS_CODE):
            session["dashsocial_authorized"] = True
            return redirect("/dashsocial")
        error = "Código de acesso inválido."
    return render_template("dashsocial_access.html", error=error)


@app.route("/api/dashsocial/metrics")
def dashsocial_api_metrics():
    if not dashsocial_is_authorized():
        return jsonify({"erro": "Acesso não autorizado."}), 401
    try:
        days = int(request.args.get("days", "30"))
    except ValueError:
        return jsonify({"erro": "Período inválido."}), 400
    try:
        response = jsonify(dashsocial_metrics(days))
        response.headers["Cache-Control"] = "private, max-age=60"
        return response
    except RuntimeError as error:
        return jsonify({"erro": str(error)}), 503
    except Exception as error:
        print(f"DashSocial; erro ao ler a planilha: {error}", flush=True)
        return jsonify({"erro": "Não foi possível carregar os dados do DashSocial; agora."}), 503


@app.route("/robots.txt")
def robots():
    content = f"User-agent: *\nAllow: /\nSitemap: {CANONICAL_URL}sitemap.xml\n"
    return Response(content, mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap():
    updated_at = datetime.now().date().isoformat()
    content = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{CANONICAL_URL}</loc><lastmod>{updated_at}</lastmod></url>
  <url><loc>{CANONICAL_URL}links</loc><lastmod>{updated_at}</lastmod></url>
</urlset>'''
    return Response(content, mimetype="application/xml")


# -----------------------------------------------------------------------------
# API de chat
# -----------------------------------------------------------------------------
@app.route("/api/chat-ai", methods=["POST"])
def chat_ai():
    if is_rate_limited(client_ip()):
        return jsonify({"erro": "Muitas mensagens em pouco tempo. Tente novamente em um minuto."}), 429

    data = request.get_json(silent=True) or {}
    user_message = data.get("mensagem", "")
    if not isinstance(user_message, str):
        return jsonify({"erro": "Mensagem inválida."}), 400

    user_message = " ".join(user_message.split())[:1200]
    if not user_message:
        return chat_payload("Como sua operação atende e qualifica oportunidades hoje?")

    if len(user_message) < 2:
        return chat_payload("Não consegui compreender totalmente. Conte em uma frase onde sua operação mais perde oportunidades.")

    guided_reply = direct_response(user_message)
    if guided_reply is not None:
        return guided_reply

    ai_reply = ask_gemini(user_message)
    if ai_reply:
        return chat_payload(ai_reply, "Solicitar diagnóstico de 20 min")

    return chat_payload(
        "Posso ajudar a mapear onde a operação perde oportunidades. Conte se o principal gargalo hoje é resposta, qualificação, tráfego ou leitura dos dados.",
        "Falar com a equipe no WhatsApp",
    )


# -----------------------------------------------------------------------------
# Encurtador de links
# -----------------------------------------------------------------------------
@app.route("/<short_code>")
def short_link(short_code):
    target = LINKS_ENCURTADOS.get(short_code.casefold().strip())
    return redirect(target or "/", code=302)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
