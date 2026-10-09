// ============================================
// SANT; — LÓGICA DO CHATBOT, AUDIO, DRAG & ZAP
// ============================================

const SEU_WHATSAPP = "5511999999999"; // 👈 COLOQUE SEU DDD + NÚMERO AQUI

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

// ----- 6. DRAG HORIZONTAL NAS PÍLULAS (COM THRESHOLD PARA NÃO BLOQUEAR CLIQUES) -----
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

        // Só considera ARRASTE se moveu mais de 6 pixels (evita bloquear o clique simples)
        if (Math.abs(x - startX) > 6) {
            dragged = true;
            slider.classList.add("dragging");
            e.preventDefault();
            slider.scrollLeft = scrollLeft - walk;
        }
    });

    // Bloqueia clique apenas se REALMENTE arrastou
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
// ✨ OBSERVADOR DE SCROLL (REVEAL ON SCROLL)
// ============================================
document.addEventListener("DOMContentLoaded", () => {
    const observerOptions = {
        root: null,
        rootMargin: "0px 0px -60px 0px", // Ativa o efeito pouco antes de entrar totalmente na tela
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("active");
            }
        });
    }, observerOptions);

    // Observa todos os elementos com as classes de revelação
    document.querySelectorAll(".reveal, .reveal-left, .reveal-scale").forEach(el => {
        observer.observe(el);
    });
});
// ============================================
// 🐭 LÓGICA DO MOUSE CUSTOMIZADO SANT;
// ============================================
(function () {
    const cursor = document.getElementById("custom-cursor");
    if (!cursor) return;

    let mouseX = -100;
    let mouseY = -100;

    // Atualiza a posição do cursor em tempo real
    window.addEventListener("mousemove", (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
        
        cursor.style.left = `${mouseX}px`;
        cursor.style.top = `${mouseY}px`;
        
        if (!cursor.classList.contains("active")) {
            cursor.classList.add("active");
        }
    });

    // Esconde o cursor quando sai da janela do navegador
    document.addEventListener("mouseleave", () => {
        cursor.classList.remove("active");
    });
    document.addEventListener("mouseenter", () => {
        cursor.classList.add("active");
    });

    // Efeito de Pressionar (Click)
    window.addEventListener("mousedown", () => {
        cursor.classList.add("clicked");
    });
    window.addEventListener("mouseup", () => {
        cursor.classList.remove("clicked");
    });

    // Efeito Hover ao passar sobre elementos interativos
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
// ============================================
// 📱 CHAT MOBILE (BOLINHA → ABRE O AUTOBOT)
// ============================================
function abrirChatMobile() {
    const wrapper = document.getElementById("chatbot-wrapper");
    const fab = document.getElementById("chat-fab");

    if (!wrapper) return;

    wrapper.classList.add("mobile-open");
    wrapper.classList.add("chat-ativo");

    if (fab) fab.classList.add("hidden");

    // Abre direto o histórico com boas-vindas
    abrirHistorico();

    // Foca no input
    setTimeout(() => {
        const input = document.getElementById("chat-input");
        if (input) input.focus();
    }, 150);
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
        wrapper.classList.remove("mobile-open"); // fecha no mobile
    }

    // volta a bolinha no mobile
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
