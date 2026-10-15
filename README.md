# SANT; — Home V2 Reformulada

Esta pasta contém a reformulação da home da SANT; na direção **híbrida** escolhida: base preto/cinza das referências, com Brass (`#C9A24B`) e Signal (`#7FD8C4`) usados de modo pontual para método, dados, IA e CTAs.

## Arquivos entregues

```text
sant-reformulado/
├── app.py
├── requirements.txt
├── .env.example
├── templates/
│   └── index.html
└── static/
    ├── style.css
    ├── script.js
    ├── logo.png
    └── portfolio/
        ├── a.WebP
        └── b.WebP
```

Os arquivos estão na estrutura padrão Flask/Jinja. O pacote inclui uma versão revisada de `app.py`; substitua os equivalentes do projeto atual ou use-o como referência para incorporar as rotas, segurança e o chat atualizado.

## O que foi reformulado

- Copy e arquitetura da Home V2: **infraestrutura de crescimento com IA**, não agência/promocional;
- hero, dor, sistema, demonstração, Plano SANT; CONTINUUM; completo, Método AGA, prova, FAQ e CTA final;
- visual responsivo com a identidade original da SANT;: preto/cinza, branco e contraste alto;
- mobile menu acessível e chat redesenhado;
- links de WhatsApp centralizados em um único lugar (`SANT_CONFIG.whatsapp`);
- chat com inserção segura de texto (`textContent`, não `innerHTML`);
- eventos genéricos de CTA/chat prontos para GA4 e Meta Pixel;
- metatags SEO/OG, canonical e schema `ProfessionalService`;
- remoção de áudio externo, cursor customizado, preço riscado, selo OFF e links de WhatsApp placeholder.

## Identidade visual aplicada

A nova versão preserva o layout, mas agora usa os materiais enviados no Drive:

- **Cores:** `#161616`, `#292929`, `#949494`, `#E3E2E2` e `#FAFAFA`;
- **Tipografia:** Bruno Ace SC para títulos e Montserrat para leitura, navegação e CTAs;
- **Ativos locais:** logo vetorial, assinatura SANT; e arquivos de fonte dentro de `static/brand` e `static/fonts`.

Assim, o site não depende do Google Fonts para carregar a identidade correta.

## Antes de publicar

1. **Confirme o número** em `static/script.js`:
   ```js
   whatsapp: "5521986010634"
   ```

2. **Confirme a condição comercial.** A Home V2 está com a condição definida no plano estratégico:
   - R$ 390 de ativação;
   - 11 parcelas de R$ 350;
   - TCV fundador de R$ 4.240.

   Altere essa informação somente se o preço e a capacidade real de implantação forem outros.

3. **Confirme o domínio canônico** via variável `CANONICAL_URL`. Quando `sant.com.br` estiver publicado, defina `CANONICAL_URL=https://sant.com.br/` no Render.

4. **Conecte o tracking.** O front-end já envia eventos para `gtag` e `fbq` se esses scripts estiverem configurados no backend/head. Eventos importantes:
   - `whatsapp_click`
   - `cta_click`
   - `chat_open`
   - `chat_message`
   - `chat_error`
   - `demo_interaction`

   Para mensuração completa, implementar Pixel + CAPI + GA4, UTMs e CRM com origem obrigatória.

5. **Mantenha somente provas autorizadas.** Os dois visuais carregados na seção de prova mostram a interface e conteúdo da SANT;, não resultados de clientes. Antes de publicar cases, incluir contexto, evidência e autorização do cliente.

6. **Política de privacidade/LGPD.** Como há chat, adicionar uma rota/página de privacidade e um aviso com finalidade de contato e tratamento de dados.

## Backend e deploy

O `app.py` incluído entrega a Home, `/links`, `/bio`, `/robots.txt`, `/sitemap.xml`, links curtos e a API de chat. Ele também adiciona headers de segurança, rate limit simples do chat e respostas guiadas se o Gemini não estiver configurado.

A home chama:

```http
POST /api/chat-ai
Content-Type: application/json

{ "mensagem": "...", "origem": "site_home_v2" }
```

A resposta contém texto e um CTA de WhatsApp seguro:

```json
{
  "resposta": "texto simples da resposta",
  "cta_label": "Falar com a equipe no WhatsApp",
  "cta_url": "https://wa.me/..."
}
```

A resposta de texto é exibida com `textContent`, sem renderizar HTML. O CTA só é mostrado se a URL usar o domínio oficial `wa.me`.

### Variáveis do Render

Crie as variáveis abaixo, usando `.env.example` como referência:
- `GEMINI_API_KEY` — opcional; sem ela o chat continua com respostas guiadas;
- `SANT_WHATSAPP` — número com DDI e DDD;
- `CANONICAL_URL` — URL pública do domínio;
- `GEMINI_MODELS` — modelos habilitados na conta Google;
- `FLASK_DEBUG=0` em produção.

**Start command no Render:** `gunicorn app:app`.

## DashSocial; V1

A rota interna `/dashsocial` lê a aba `Dados_Diarios` de uma planilha privada do Google Sheets e mostra somente as métricas comerciais aprovadas: leads, CPL, MQL/SQL, conversão, funil e origem.

### Conexão segura da planilha

1. No Google Cloud, crie uma **Service Account** e gere uma chave JSON;
2. Ative a **Google Sheets API** no mesmo projeto Cloud;
3. Compartilhe a planilha com o e-mail da Service Account como **Leitor**;
4. No Render, configure `DASHSOCIAL_GOOGLE_CREDENTIALS_JSON` com o JSON da chave (ou `DASHSOCIAL_GOOGLE_CREDENTIALS_B64`);
5. Configure `DASHSOCIAL_ACCESS_CODE` e `FLASK_SECRET_KEY` para proteger o acesso interno.

A chave da Service Account nunca deve ser enviada por WhatsApp, chat ou commitada no repositório. Sem a credencial configurada, o painel mostra uma mensagem de integração pendente e não expõe os dados da planilha.

### Rodar localmente no Windows

No Prompt de Comando, dentro da pasta do projeto:

```bat
python -m pip install -r requirements.txt
python app.py
```

O pacote `google-genai` é opcional para iniciar o site: caso ele não esteja instalado, a Home e o chat com respostas guiadas continuam funcionando. Para usar respostas do Gemini, instale as dependências e preencha `GEMINI_API_KEY` no arquivo `.env`.
