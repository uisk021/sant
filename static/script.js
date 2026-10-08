// ============================================
// SANT; — LÓGICA DO CHATBOT, AUDIO, DRAG & ZAP
// ============================================

const SEU_WHATSAPP = "5521986010634"; // 👈 COLOQUE SEU DDD + NÚMERO AQUI

let fluxoAtual = 0;
let dadosLead = {};

// ----- 1. ABRIR WHATSAPP DIRETO -----
function abrirWhatsAppDirect() {
    const textoZap = encodeURIComponent("Olá SANT;! Gostaria de iniciar um novo projeto.");
    window.open(`https://wa.me/${SEU_WHATSAPP}?text=${textoZap}`, "_blank");
}

// ----- 2. CHATBOT INTERATIVO -----
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

    if (history) history.classList.remove("active");
    if (suggestions) suggestions.style.display = "flex";
    if (wrapper) wrapper.classList.remove("chat-ativo");

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

function enviarMensagem(textoUsuario) {
    abrirHistorico();
    addMsg(textoUsuario, 'user');
    
    setTimeout(() => {
        if (fluxoAtual === 0) {
            dadosLead.interesse = textoUsuario;
            addMsg("Entendi. Para eu te direcionar ao especialista correto, qual é o nome da sua empresa/projeto?", 'bot');
            fluxoAtual = 1;
        } 
        else if (fluxoAtual === 1) {
            dadosLead.empresa = textoUsuario;
            addMsg(`Perfeito, ${dadosLead.empresa}. Qual o orçamento estimado disponível para este investimento? (Ex: Até R$ 1k, R$ 2k-5k, Acima de 5k)`, 'bot');
            fluxoAtual = 2;
        }
        else if (fluxoAtual === 2) {
            dadosLead.orcamento = textoUsuario;
            addMsg("Excelente! Gerando seu atendimento VIP e direcionando para nossa equipe no WhatsApp...", 'bot');
            
            const textoZap = `Olá SANT;! Vim pelo Autobot do site.%0A%0A*Empresa:* ${dadosLead.empresa}%0A*Interesse:* ${dadosLead.interesse}%0A*Orçamento:* ${dadosLead.orcamento}`;
            const url = `https://wa.me/${SEU_WHATSAPP}?text=${textoZap}`;
            
            setTimeout(() => {
                window.open(url, '_blank');
                fecharChat();
            }, 1800);
        }
    }, 700);
}

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
    box.scrollTop = box.scrollHeight;
}

function comprar(produto) {
    const textoZap = `Olá SANT;! Quero adquirir o produto: *${produto}*.`;
    window.open(`https://wa.me/${SEU_WHATSAPP}?text=${textoZap}`, '_blank');
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

// ----- 4. MENU MOBILE (DRAWER) -----
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

// ----- 5. DRAG HORIZONTAL NAS PÍLULAS DO CHATBOT -----
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
        slider.classList.add("dragging");
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
        e.preventDefault();
        dragged = true;
        const x = e.pageX - slider.offsetLeft;
        const walk = (x - startX) * 1.4;
        slider.scrollLeft = scrollLeft - walk;
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
// ============================================
// ACORDEÃO DO FAQ (ABRIR E FECHAR PERGUNTAS)
// ============================================
function toggleFaq(button) {
    const item = button.parentElement;
    const isPrimary = item.classList.contains("active");

    // Fecha todos os outros que estiverem abertos
    document.querySelectorAll(".faq-item").forEach(el => {
        el.classList.remove("active");
    });

    // Se o clicado não estava aberto, abre ele
    if (!isPrimary) {
        item.classList.add("active");
    }
}
