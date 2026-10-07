import os
from flask import Flask, render_template

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
PORTFOLIO_DIR = os.path.join(STATIC_DIR, "portfolio")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

@app.route('/')
def index():
    portfolio_images = []
    if os.path.exists(PORTFOLIO_DIR):
        for filename in os.listdir(PORTFOLIO_DIR):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                portfolio_images.append(filename)
                
    return render_template('index.html', portfolio_images=portfolio_images)

if __name__ == '__main__':
    print("=" * 40)
    print("🚀 Agência SANT; rodando!")
    print("🌐 Acesse: http://localhost:5000")
    print("=" * 40)
    app.run(host="0.0.0.0", port=5000, debug=True)
