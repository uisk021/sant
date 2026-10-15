/* DashSocial; V1 — painel comercial alimentado por Google Sheets */
(() => {
  const formatNumber = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 0 });
  const formatCurrency = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
  const formatPercent = (value) => `${(Number(value || 0) * 100).toFixed(1).replace(".", ",")}%`;
  let selectedDays = 30;

  const setText = (selector, value) => {
    const element = document.querySelector(selector);
    if (element) element.textContent = value;
  };

  function setStatus(text, isError = false) {
    const status = document.querySelector("[data-status]");
    if (!status) return;
    status.textContent = text;
    status.style.color = isError ? "#b8a6a6" : "";
  }

  function render(data) {
    const metrics = data.metrics || {};
    setText("[data-leads]", formatNumber(metrics.leads));
    setText("[data-cpl]", formatCurrency.format(metrics.cpl || 0));
    setText("[data-investment]", formatCurrency.format(metrics.investment || 0));
    setText("[data-mql]", formatNumber(metrics.mql));
    setText("[data-sql]", formatNumber(metrics.sql));
    setText("[data-conversion]", formatPercent(metrics.conversion));
    setText("[data-visitors]", formatNumber(metrics.visitors));
    setText("[data-funnel-leads]", formatNumber(metrics.leads));
    setText("[data-opportunities]", formatNumber(metrics.opportunities));
    setText("[data-clients]", formatNumber(metrics.clients));
    setText("[data-visitor-conversion]", formatPercent(metrics.visitor_conversion));
    setText("[data-range]", `${data.start_date} — ${data.end_date}`.toUpperCase());
    setStatus(`ATUALIZADO ${data.updated_at}`);

    const sources = data.sources || {};
    const maximum = Math.max(1, ...Object.values(sources));
    document.querySelectorAll("[data-source]").forEach((card) => {
      const name = card.dataset.source;
      const count = Number(sources[name] || 0);
      const value = card.querySelector("b");
      const bar = card.querySelector(".source-bar i");
      if (value) value.textContent = formatNumber(count);
      if (bar) bar.style.width = `${Math.max(0, Math.min(100, (count / maximum) * 100))}%`;
    });
  }

  async function loadMetrics(days) {
    setStatus("CARREGANDO DADOS");
    try {
      const response = await fetch(`/api/dashsocial/metrics?days=${encodeURIComponent(days)}`, { headers: { Accept: "application/json" } });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.erro || `Erro ${response.status}`);
      render(payload);
    } catch (error) {
      setStatus("CONEXÃO COM DADOS PENDENTE", true);
      console.error("DashSocial:", error);
    }
  }

  document.querySelector("[data-theme-toggle]")?.addEventListener("click", () => {
    const isLight = document.body.classList.toggle("light");
    const toggle = document.querySelector("[data-theme-toggle]");
    if (!toggle) return;
    toggle.setAttribute("aria-pressed", String(!isLight));
    const label = toggle.querySelector("span");
    if (label) label.textContent = isLight ? "MODO ESCURO" : "MODO CLARO";
  });

  document.querySelectorAll("[data-days]").forEach((button) => {
    button.addEventListener("click", () => {
      selectedDays = Number(button.dataset.days) || 30;
      document.querySelectorAll("[data-days]").forEach((item) => item.classList.toggle("active", item === button));
      loadMetrics(selectedDays);
    });
  });

  loadMetrics(selectedDays);
})();
