// ============================================
// SANT; — LÓGICA DO CHATBOT, IA, AUDIO, DRAG & ZAP
// ============================================

const SEU_WHATSAPP = "5521986010634"; // 👈 Sincronizado com o número configurado no seu app.py

let fluxoAtual = 0;
let dadosLead = {};

// ----- 1. ABRIR WHATSAPP DIRETO -----
function abrirWhatsAppDirect() {
    const textoZap = encodeURIComponent("Olá SANT;! Gostaria de iniciar um novo projeto.");
    window.open(`https://wa.me{SEU_WHATSAPP}?text=${textoZap}`, "_blank");
}

// ----- 2. CHATBOT COM IA (SANT; AI) -----
function focusChat() {
    const input = document.getElementById("chat-input");
    if (input) input.focus();
    const container = document.querySelector(".chat-input-container");
    if (container) {
        container.style.borderColor = "#E3E2E2";
        setTimeout(() => { container.style.borderColor = "rgba(227,226,226,0.25)"; }, 1000);
    }
}

function abrirHistorico() {
    const history = document.getElementById("chat-history");
    const suggestions = document.getElementById("chat-suggestions");
    const wrapper = document.getElementById("chatbot-wrapper");

    if (history) history.classList.add("active");
    if (suggestions) suggestions.style.display = "none";
    if (wrapper) wrapper.classList.add("chat-ativo");
}

function fecharChat() {
    const history = document.getElementById("chat-history");
    const suggestions = document.getElementById("chat-suggestions");
    const wrapper = document.getElementById("chatbot-wrapper");
    const fab = document.getElementById("chat-fab");

    if (history) history.classList.remove("active");
    if (suggestions) suggestions.style.display = "flex";

    if (wrapper) {
        wrapper.classList.remove("chat-ativo");
        wrapper.classList.remove("mobile-open");
    }

    if (fab) fab.classList.remove("hidden");

    fluxoAtual = 0;
    dadosLead = {};

    const messages = document.getElementById("chat-messages");
    if (messages) {
        messages.innerHTML = `
            <div class="msg bot-msg">
                <div class="msg-label">SANT; AI</div>
                <div class="msg-content">Olá! Sou a IA da SANT;. Como posso ajudar a escalar seu negócio hoje?</div>
            </div>
        `;
    }
}

function handleEnter(e) {
    if (e.key === 'Enter') {
        enviarInput();
    }
}

function enviarInput() {
    const inputField = document.getElementById("chat-input");
    if (!inputField) return;
    const texto = inputField.value.trim();
    if (texto !== "") {
        enviarMensagem(texto);
        inputField.value = "";
    }
}

// ----- CONECTADO À API DA IA NO PYTHON -----
async function enviarMensagem(textoUsuario) {
    if (!textoUsuario) return;

    abrirHistorico();
    addMsg(textoUsuario, 'user');
    
    // Indicador de "SANT; AI está analisando..."
    const box = document.getElementById("chat-messages");
    if (!box) return;

    const divDigitando = document.createElement("div");
    divDigitando.className = "msg bot-msg digitando-msg";
    divDigitando.innerHTML = `
        <div class="msg-label">SANT; AI</div>
        <div class="msg-content" style="color: #888; font-style: italic;">
            SANT; AI está analisando... 🤖
        </div>
    `;
    box.appendChild(divDigitando);
    box.scrollTop = box.scrollHeight;

    // Bloqueia temporariamente o input do chat para evitar spam
    const inputField = document.getElementById("chat-input");
    if (inputField) inputField.disabled = true;

    try {
        const resposta = await fetch('/api/chat-ai', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mensagem: textoUsuario })
        });

        const dados = await resposta.json();
        
        divDigitando.remove();
        addMsg(dados.resposta, 'bot');

    } catch (erro) {
        divDigitando.remove();
        addMsg("Desculpe, tive uma oscilação de conexão. Clique no botão de WhatsApp abaixo para falar direto com nossa equipe ;", 'bot');
        console.error("Erro na API da IA:", erro);
    } finally {
        if (inputField) {
            inputField.disabled = false;
            inputField.focus();
        }
    }
}

// ----- ADICIONAR MENSAGENS COM INJEÇÃO DE BOTÃO INTERATIVO -----
function addMsg(texto, tipo) {
    const box = document.getElementById("chat-messages");
    if (!box) return;

    const div = document.createElement("div");
    div.className = `msg ${tipo}-msg`;

    if (tipo === "bot") {
        div.innerHTML = `
            <div class="msg-label">SANT; AI</div>
            <div class="msg-content">${texto}</div>
        `;
    } else {
        div.innerHTML = `
            <div class="msg-content">${texto}</div>
        `;
    }

    box.appendChild(div);

    // ⚡ INTERCEPTADOR: Cria o botão se a IA convidar para o WhatsApp comercial
    if (tipo === "bot") {
        const tMinusculo = texto.toLowerCase();
        if (tMinusculo.includes("whatsapp") || tMinusculo.includes("especialistas") || tMinusculo.includes("clicar") || tMinusculo.includes("conversa direta")) {
            const divBotao = document.createElement("div");
            divBotao.style.margin = "8px 0 16px 36px";
            divBotao.style.textAlign = "left";
            
            // O link usa a rota encurtada '/zap' do backend Python para manter a consistência de métricas
            divBotao.innerHTML = `
                <a href="/zap" target="_blank" style="display: inline-flex; align-items: center; justify-content: center; background: #25D366; color: #ffffff; text-decoration: none; padding: 10px 18px; border-radius: 6px; font-weight: bold; font-family: sans-serif; font-size: 0.9rem; box-shadow: 0 4px 12px rgba(37, 211, 102, 0.25); transition: transform 0.2s, background 0.2s; gap: 8px;">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style="vertical-align: middle;">
                        <path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946C.06 5.348 5.397 0 12.008 0c3.202.001 6.212 1.246 8.477 3.514 2.266 2.268 3.507 5.28 3.505 8.484-.004 6.657-5.34 12.004-11.95 12.004-.001 0-.001 0 0 0-2.003-.001-3.975-.511-5.728-1.483L0 24zm6.59-4.846c1.6.95 3.188 1.449 4.825 1.451 5.436 0 9.86-4.42 9.864-9.852.002-2.632-1.023-5.105-2.887-6.97s-4.341-2.893-6.976-2.895c-5.442 0-9.867 4.42-9.871 9.853-.001 1.748.475 3.447 1.378 4.951l-.926 3.386 3.473-.911zM17.91 14.542c-.326-.163-1.93-.953-2.227-1.062-.296-.109-.513-.163-.73.163-.216.325-.838 1.062-1.027 1.28-.188.217-.378.244-.704.082-.326-.163-1.375-.507-2.62-1.617-.968-.865-1.622-1.933-1.812-2.259-.189-.325-.02-.501.142-.662.147-.144.327-.38.491-.57.163-.19.217-.326.326-.543.109-.217.055-.407-.027-.57-.082-.163-.73-1.762-.999-2.413-.263-.635-.53-.55-.73-.56h-.625c-.216 0-.57.081-.868.407-.299.325-1.139 1.113-1.139 2.715 0 1.602 1.167 3.149 1.329 3.366.163.216 2.297 3.509 5.565 4.919.777.336 1.384.537 1.857.688.78.248 1.49.213 2.052.129.626-.094 1.93-.789 2.2-1.511.271-.722.271-1.343.19-1.472-.08-.13-.296-.213-.623-.376z"/>
                    </svg>
                    Falar com Especialista no WhatsApp;
                </a>
            `;
            box.appendChild(divBotao);
        }
    }

    box.scrollTop = box.scrollHeight;
}

function comprar(produto) {
    const textoZap = `Olá SANT;! Quero adquirir o produto: *${produto}*.`;
    window.open(`https://wa.me{SEU_WHATSAPP}?text=${textoZap}`, '_blank');
}

// ----- 3. CONTROLE DA TRILHA SONORA AMBIENTE -----
function toggleAudio() {
    const bgMusic = document.getElementById("bg-music");
    const audioBtn = document.getElementById("audio-toggle");
    const audioIcon = document.getElementById("audio-icon");
    const audioText = document.getElementById("audio-text");

    if (!bgMusic) return;

    bgMusic.volume = 0.25;

    if (bgMusic.paused) {
        bgMusic.play().then(() => {
            if (audioBtn) audioBtn.classList.add("playing");
            if (audioIcon) audioIcon.textContent = "🔊";
            if (audioText) audioText.textContent = "SOUND ON";
        }).catch((erro) => {
            console.error("Erro áudio:", erro);
        });
    } else {
        bgMusic.pause();
        if (audioBtn) audioBtn.classList.remove("playing");
        if (audioIcon) audioIcon.textContent = "🔇";
        if (audioText) audioText.textContent = "SOUND OFF";
    }
}

// ----- 4. ACORDEÃO DO FAQ -----
function toggleFaq(button) {
    button.parentElement.classList.toggle("active");
}

// ----- 5. MENU DRAWER MOBILE -----
function toggleMobileMenu() {
    const drawer = document.getElementById("mobile-drawer");
    if (drawer) {
        drawer.classList.toggle("active");
        if (drawer.classList.contains("active")) {
            document.body.style.overflow = "hidden";
        } else {
            document.body.style.overflow = "";
        }
    }
}

// ----- 6. CHAT MOBILE (BOLINHA → ABRE O AUTOBOT) -----
function abrirChatMobile() {
    const wrapper = document.getElementById("chatbot-wrapper");
    const fab = document.getElementById("chat-fab");

    if (!wrapper) return;

    wrapper.classList.add("mobile-open");
    wrapper.classList.add("chat-ativo");

    if (fab) fab.classList.add("hidden");

    abrirHistorico();

    setTimeout(() => {
        const input = document.getElementById("chat-input");
        if (input) input.focus();
    }, 150);
}

// ----- 7. DRAG HORIZONTAL NAS PÍLULAS -----
(function () {
    const slider = document.getElementById("chat-suggestions");
    if (!slider) return;

    let isDown = false;
    let startX = 0;
    let scrollLeft = 0;
    let dragged = false;

    slider.addEventListener("mousedown", (e) => {
        isDown = true;
        dragged = false;
        startX = e.pageX - slider.offsetLeft;
        scrollLeft = slider.scrollLeft;
    });

    slider.addEventListener("mouseleave", () => {
        isDown = false;
        slider.classList.remove("dragging");
    });
slider.addEventListener("mouseup", () => {
isDown = false;
slider.classList.remove("dragging");
});
slider.addEventListener("mousemove", (e) => {
if (!isDown) return;
const x = e.pageX - slider.offsetLeft;
const walk = (x - startX) * 1.4;
if (Math.abs(x - startX) > 6) {
dragged = true;
slider.classList.add("dragging");
e.preventDefault();
slider.scrollLeft = scrollLeft - walk;
}
});
slider.querySelectorAll("button").forEach((btn) => {
btn.addEventListener("click", (e) => {
if (dragged) {
e.preventDefault();
e.stopPropagation();
}
});
});
// Touch no celular
let touchStartX = 0;
let touchScrollLeft = 0;
slider.addEventListener("touchstart", (e) => {
touchStartX = e.touches[0].pageX - slider.offsetLeft;
touchScrollLeft = slider.scrollLeft;
}, { passive: true });
slider.addEventListener("touchmove", (e) => {
const x = e.touches[0].pageX - slider.offsetLeft;
const walk = (x - touchStartX) * 1.4;
slider.scrollLeft = touchScrollLeft - walk;
}, { passive: true });
})();
// ----- 8. OBSERVADOR DE SCROLL (REVEAL) -----
document.addEventListener("DOMContentLoaded", () => {
const observerOptions = {
root: null,
rootMargin: "0px 0px -60px 0px",
threshold: 0.1
};
const observer = new IntersectionObserver((entries) => {
entries.forEach(entry => {
if (entry.isIntersecting) {
entry.target.classList.add("active");
}
});
}, observerOptions);
document.querySelectorAll(".reveal, .reveal-left, .reveal-scale").forEach(el => {
observer.observe(el);
});
});
// ----- 9. MOUSE CUSTOMIZADO SANT; -----
(function () {
const cursor = document.getElementById("custom-cursor");
if (!cursor) return;
let mouseX = -100;
let mouseY = -100;
window.addEventListener("mousemove", (e) => {
mouseX = e.clientX;
mouseY = e.clientY;
cursor.style.left = ${mouseX}px;
cursor.style.top = ${mouseY}px;
if (!cursor.classList.contains("active")) {
cursor.classList.add("active");
}
});
document.addEventListener("mouseleave", () => {
cursor.classList.remove("active");
});
document.addEventListener("mouseenter", () => {
cursor.classList.add("active");
});
window.addEventListener("mousedown", () => {
cursor.classList.add("clicked");
});
window.addEventListener("mouseup", () => {
cursor.classList.remove("clicked");
});
const elementosInterativos = "a, button, input, select, textarea, .btn, .card, .social-btn, .timeline-item, .faq-question";
document.addEventListener("mouseover", (e) => {
if (e.target.closest(elementosInterativos)) {
cursor.classList.add("hovered");
}
});
document.addEventListener("mouseout", (e) => {
if (e.target.closest(elementosInterativos)) {
cursor.classList.remove("hovered");
}
});
})();
