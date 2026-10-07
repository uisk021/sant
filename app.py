import os
from flask import Flask, render_template, redirect # 👈 Adicionou o redirect aqui!

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
PORTFOLIO_DIR = os.path.join(STATIC_DIR, "portfolio")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

# ============================================
# 🔗 DICIONÁRIO DE LINKS ENCURTADOS DA SANT;
# ============================================
SEU_WHATSAPP = "5511999999999" # 👈 Coloque seu WhatsApp real aqui

LINKS_ENCURTADOS = {
    "zap": f"https://wa.me/{SEU_WHATSAPP}?text=Ol%C3%A1%20SANT%3B!%20Vim%20pelo%20link%20encurtado.",
    "whatsapp": f"https://wa.me/{SEU_WHATSAPP}",
    "insta": "https://www.instagram.com/sant.social/",
    "instagram": "https://www.instagram.com/sant.social/",
    "patinho": "https://bot-radio-habbler.onrender.com",
    "github": "https://github.com",
}

@app.route('/')
def index():
    portfolio_images = []
    if os.path.exists(PORTFOLIO_DIR):
        for filename in os.listdir(PORTFOLIO_DIR):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                portfolio_images.append(filename)
                
    return render_template('index.html', portfolio_images=portfolio_images)


# ============================================
# 🚀 ROTA DO ENCURTADOR DE LINKS
# ============================================
@app.route('/<short_code>')
def redirecionar_link(short_code):
    """
    Se a pessoa acessar: sant-agencia.onrender.com/zap
    o Python procura 'zap' na lista e redireciona automaticamente!
    """
    codigo = short_code.lower().strip()
    
    if codigo in LINKS_ENCURTADOS:
        # Redireciona para o link verdadeiro correspondente
        return redirect(LINKS_ENCURTADOS[codigo])
    else:
        # Se o link encurtado não existir, manda de volta pra Home
        return redirect('/')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

@app.route('/links')
@app.route('/bio')
def bio_links():
    """Página estilo Linktree própria da SANT;"""
    return render_template('links.html')
