/* SANT; — Home V2 | interações, conversão e chat seguro */

const SANT_CONFIG = {
  whatsapp: "5521986010634",
  whatsappMessages: {
    demo: "Olá, SANT;! Quero conhecer o CHATBOT.",
    diagnostico: "Olá, SANT;! Quero solicitar um diagnóstico do meu WhatsApp.",
    continuum: "Olá, SANT;! Quero receber a apresentação do Plano SANT; CONTINUUM;.",
    geral: "Olá, SANT;! Quero falar sobre a infraestrutura de crescimento com IA."
  },
  chatEndpoint: "/api/chat-ai"
};

function trackEvent(eventName, parameters = {}) {
  const payload = { event: eventName, ...parameters };
  document.dispatchEvent(new CustomEvent("sant:track", { detail: payload }));

  // Integrações só disparam se GA4/Meta forem configurados no servidor.
  if (typeof window.gtag === "function") window.gtag("event", eventName, parameters);
  if (typeof window.fbq === "function") window.fbq("trackCustom", eventName, parameters);
}

function openWhatsApp(source = "geral") {
  const message = SANT_CONFIG.whatsappMessages[source] || SANT_CONFIG.whatsappMessages.geral;
  const url = new URL(`https://wa.me/${SANT_CONFIG.whatsapp}`);
  url.searchParams.set("text", message);
  url.searchParams.set("utm_source", "site");
  url.searchParams.set("utm_medium", "cta");
  url.searchParams.set("utm_content", source);

  trackEvent("whatsapp_click", { source });
  window.open(url.toString(), "_blank", "noopener,noreferrer");
}

function setMobileMenu(open) {
  const button = document.querySelector("[data-menu-toggle]");
  const menu = document.querySelector("[data-mobile-menu]");
  if (!button || !menu) return;

  menu.hidden = !open;
  button.setAttribute("aria-expanded", String(open));
  button.setAttribute("aria-label", open ? "Fechar menu" : "Abrir menu");
}

function appendChatMessage(text, type = "bot", cta = null) {
  const log = document.querySelector("[data-chat-log]");
  if (!log) return null;

  const message = document.createElement("div");
  message.className = `chat-message ${type}`;

  const body = document.createElement("span");
  // textContent evita injeção de HTML de usuário ou resposta de API.
  body.textContent = String(text || "");
  message.appendChild(body);

  // CTA só é renderizado quando aponta para o domínio oficial do WhatsApp.
  if (type === "bot" && cta?.label && cta?.url) {
    try {
      const url = new URL(cta.url);
      if (url.protocol === "https:" && url.hostname === "wa.me") {
        const link = document.createElement("a");
        link.className = "chat-message-cta";
        link.href = url.toString();
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.textContent = cta.label;
        link.addEventListener("click", () => trackEvent("chat_whatsapp_click"));
        message.appendChild(link);
      }
    } catch (_) {
      // URL inválida: a resposta textual continua segura e visível.
    }
  }

  log.appendChild(message);
  log.scrollTop = log.scrollHeight;
  return message;
}

function setChatOpen(open) {
  const panel = document.getElementById("sant-chat");
  const button = document.querySelector("[data-chat-toggle]");
  if (!panel || !button) return;

  panel.hidden = !open;
  button.setAttribute("aria-expanded", String(open));
  if (open) {
    document.getElementById("chat-input")?.focus();
    trackEvent("chat_open");
  }
}

const chatQualification = {
  step: "context",
  context: "",
  name: "",
  company: ""
};

function setChatStage(label, placeholder) {
  const stage = document.querySelector("[data-chat-stage]");
  const input = document.getElementById("chat-input");
  if (stage) stage.textContent = label;
  if (input && placeholder) input.placeholder = placeholder;
}

function buildQualificationWhatsAppUrl() {
  const url = new URL(`https://wa.me/${SANT_CONFIG.whatsapp}`);
  const summary = [
    "Olá, SANT;!",
    `Sou ${chatQualification.name}, da ${chatQualification.company}.`,
    "Falei com o CHATBOT pelo site e quero continuar o diagnóstico.",
    `Contexto informado: ${chatQualification.context}`
  ].join(" ");
  url.searchParams.set("text", summary.slice(0, 900));
  url.searchParams.set("utm_source", "site");
  url.searchParams.set("utm_medium", "chatbot");
  url.searchParams.set("utm_content", "qualificacao");
  return url.toString();
}

function finishQualification() {
  chatQualification.step = "complete";
  setChatStage("03 / pronto para encaminhar", "Qualificação concluída");
  const chips = document.querySelector("[data-chat-chips]");
  if (chips) chips.hidden = true;
  appendChatMessage(
    `Perfeito, ${chatQualification.name}. Organizei o seu contexto para a equipe. Clique abaixo para continuar no WhatsApp sem precisar repetir tudo.`,
    "bot",
    { label: "Continuar no WhatsApp", url: buildQualificationWhatsAppUrl() }
  );
  trackEvent("chat_qualified", { has_name: true, has_company: true });
}

async function sendChatMessage(rawMessage) {
  const message = String(rawMessage || "").trim();
  if (!message) return;

  if (chatQualification.step === "complete") {
    appendChatMessage("Seu diagnóstico já está pronto para ser encaminhado. Use o botão acima para continuar no WhatsApp.", "bot");
    return;
  }

  appendChatMessage(message, "user");
  trackEvent("chat_message", { step: chatQualification.step, length: message.length });

  if (chatQualification.step === "name") {
    chatQualification.name = message.slice(0, 80);
    chatQualification.step = "company";
    setChatStage("03 / empresa", "Nome da sua empresa");
    appendChatMessage(`Prazer, ${chatQualification.name}. Qual é o nome da sua empresa?`, "bot");
    return;
  }

  if (chatQualification.step === "company") {
    chatQualification.company = message.slice(0, 100);
    finishQualification();
    return;
  }

  chatQualification.context = message.slice(0, 700);
  const chips = document.querySelector("[data-chat-chips]");
  if (chips) chips.hidden = true;
  const typing = appendChatMessage("O CHATBOT está organizando sua resposta…", "bot");
  typing.classList.add("is-typing");

  try {
    const response = await fetch(SANT_CONFIG.chatEndpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mensagem: message, origem: "site_home_v2_chatbot" })
    });

    if (!response.ok) throw new Error(`Chat API respondeu ${response.status}`);
    const data = await response.json();
    typing.remove();
    appendChatMessage(
      data.resposta || "Entendi o cenário. A SANT; pode organizar essa operação com mais contexto e velocidade.",
      "bot"
    );
  } catch (error) {
    typing.remove();
    const fallback = appendChatMessage("Entendi o cenário. Mesmo sem conexão com a IA agora, consigo organizar seu encaminhamento para a equipe.", "bot");
    fallback.classList.add("error");
    trackEvent("chat_error", { message: String(error.message || "unknown") });
  }

  chatQualification.step = "name";
  setChatStage("02 / identificação", "Como podemos te chamar?");
  appendChatMessage("Para eu encaminhar um contexto melhor para a equipe, como posso te chamar?", "bot");
}

function setupDemo() {
  const response = document.querySelector("[data-demo-response]");
  const answers = {
    "fora do horário": "Entendi. O Autobot pode responder a primeira mensagem fora do horário, capturar contexto e deixar a oportunidade organizada para sua equipe continuar.",
    "muitas mensagens": "Entendi. O fluxo começa separando intenção, necessidade e urgência para que sua equipe priorize as conversas certas.",
    "sem dados": "Entendi. Cada etapa pode ser registrada: conversa, qualificação, reunião, proposta e pagamento. Assim a operação deixa de decidir no escuro."
  };

  document.querySelectorAll("[data-demo-answer]").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll("[data-demo-answer]").forEach((item) => item.classList.remove("is-active"));
      button.classList.add("is-active");
      const key = button.dataset.demoAnswer;
      if (response) response.textContent = answers[key] || "Vamos entender sua operação e definir o próximo passo.";
      trackEvent("demo_interaction", { answer: key });
    });
  });
}

function setupMotion() {
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const hasFinePointer = window.matchMedia("(pointer: fine)").matches;
  if (reduceMotion || !hasFinePointer) return;

  const hero = document.querySelector(".hero");
  const consoleWrap = document.querySelector("[data-parallax]");
  if (hero && consoleWrap) {
    hero.addEventListener("pointermove", (event) => {
      const rect = hero.getBoundingClientRect();
      const x = (event.clientX - rect.left) / rect.width - 0.5;
      const y = (event.clientY - rect.top) / rect.height - 0.5;
      consoleWrap.style.transform = `perspective(900px) rotateX(${y * -2.5}deg) rotateY(${x * 3.5}deg) rotate(1.7deg)`;
    });
    hero.addEventListener("pointerleave", () => {
      consoleWrap.style.transform = "rotate(1.7deg)";
    });
  }

  document.querySelectorAll("[data-magnetic]").forEach((button) => {
    button.addEventListener("pointermove", (event) => {
      const rect = button.getBoundingClientRect();
      const x = (event.clientX - rect.left) / rect.width - 0.5;
      const y = (event.clientY - rect.top) / rect.height - 0.5;
      button.style.transform = `translate(${x * 7}px, ${y * 5}px)`;
    });
    button.addEventListener("pointerleave", () => {
      button.style.transform = "";
    });
  });

  document.querySelectorAll("[data-spotlight], .spotlight-card").forEach((card) => {
    card.addEventListener("pointermove", (event) => {
      const rect = card.getBoundingClientRect();
      card.style.setProperty("--spotlight-x", `${event.clientX - rect.left}px`);
      card.style.setProperty("--spotlight-y", `${event.clientY - rect.top}px`);
    });
  });
}

function setupReveal() {
  const targets = document.querySelectorAll(".reveal");
  if (!("IntersectionObserver" in window)) {
    targets.forEach((element) => element.classList.add("is-visible"));
    return;
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("is-visible");
      observer.unobserve(entry.target);
    });
  }, { threshold: 0.08, rootMargin: "0px 0px -30px" });

  targets.forEach((element) => observer.observe(element));
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelector("[data-current-year]").textContent = new Date().getFullYear();

  document.querySelectorAll("[data-whatsapp]").forEach((button) => {
    button.addEventListener("click", () => openWhatsApp(button.dataset.whatsapp));
  });

  document.querySelectorAll("[data-track]").forEach((element) => {
    element.addEventListener("click", () => trackEvent("cta_click", { cta: element.dataset.track }));
  });

  const header = document.querySelector("[data-header]");
  const updateHeader = () => header?.classList.toggle("is-scrolled", window.scrollY > 8);
  updateHeader();
  window.addEventListener("scroll", updateHeader, { passive: true });

  const menuToggle = document.querySelector("[data-menu-toggle]");
  menuToggle?.addEventListener("click", () => {
    const isOpen = menuToggle.getAttribute("aria-expanded") === "true";
    setMobileMenu(!isOpen);
  });
  document.querySelectorAll("[data-mobile-menu] a").forEach((link) => link.addEventListener("click", () => setMobileMenu(false)));

  document.querySelector("[data-chat-toggle]")?.addEventListener("click", () => {
    const button = document.querySelector("[data-chat-toggle]");
    setChatOpen(button?.getAttribute("aria-expanded") !== "true");
  });
  document.querySelector("[data-chat-close]")?.addEventListener("click", () => setChatOpen(false));

  document.querySelectorAll("[data-chat-prompt]").forEach((button) => {
    button.addEventListener("click", () => sendChatMessage(button.dataset.chatPrompt));
  });
  document.querySelector("[data-chat-form]")?.addEventListener("submit", (event) => {
    event.preventDefault();
    const input = document.getElementById("chat-input");
    const message = input?.value || "";
    if (input) input.value = "";
    sendChatMessage(message);
  });

  setupDemo();
  setupReveal();
  setupMotion();
});
