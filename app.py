import os
from datetime import datetime
from flask import Flask, render_template, redirect

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
PORTFOLIO_DIR = os.path.join(STATIC_DIR, "portfolio")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

# ============================================
# ⚙️ CONFIGURAÇÕES & WHATSAPP DA SANT;
# ============================================
SEU_WHATSAPP = "5521986010634"  # 👈 COLOQUE SEU DDD + NÚMERO AQUI

LINKS_ENCURTADOS = {
    "zap": f"https://wa.me/{SEU_WHATSAPP}?text=Ol%C3%A1%20SANT%3B!%20Vim%20pelo%20link%20encurtado.",
    "whatsapp": f"https://wa.me/{SEU_WHATSAPP}",
    "insta": "https://www.instagram.com/sant.social/",
    "instagram": "https://www.instagram.com/sant.social/",
    "patinho": "https://bot-radio-habbler.onrender.com",
}

# ============================================
# 📅 INJETAR ANO ATUAL AUTOMÁTICO EM TODOS OS TEMPLATES
# ============================================
@app.context_processor
def inject_year():
    return {'ano_atual': datetime.now().year}

# ============================================
# 🏠 1. PÁGINA PRINCIPAL (HOME)
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
# 📱 2. PÁGINA LINKTREE / BIO EXCLUSIVA
# ============================================
@app.route('/links')
@app.route('/bio')
def bio_links():
    return render_template('links.html')

# ============================================
# 🚀 3. ENCURTADOR DE LINKS
# ============================================
@app.route('/<short_code>')
def redirecionar_link(short_code):
    codigo = short_code.lower().strip()
    if codigo in LINKS_ENCURTADOS:
        return redirect(LINKS_ENCURTADOS[codigo])
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
