# SANT; — Playbook do CHATBOT no WhatsApp

## Objetivo da V1

Um único fluxo no WhatsApp com triagem logo na entrada:

1. **Novo projeto**: entende a necessidade, coleta somente nome e empresa e conduz ao Calendly.
2. **Cliente SANT;**: recebe o pedido, mede urgência e direciona ao time humano.
3. **Atendimento humano**: interrompe o bot imediatamente e avisa a equipe no mesmo número.

A Evolution API é a camada de WhatsApp e status de sessão. O Typebot é a camada de diálogo, variáveis, lógica e webhooks.

---

## Variáveis do Typebot

Crie estas variáveis como texto. Nunca exponha no chat tokens, URLs internas ou chaves da Evolution.

| Variável | Uso |
|---|---|
| `tipo_atendimento` | `novo_projeto`, `cliente_atual` ou `humano` |
| `interesse` | Frente que motivou a conversa |
| `gargalo` | Cenário contado pela pessoa |
| `nome` | Primeiro nome ou como prefere ser chamada |
| `empresa` | Nome da empresa |
| `area_cliente` | Frente de um cliente ativo |
| `urgencia` | `bloqueado`, `importante` ou `duvida` |
| `resumo` | Contexto final enviado ao time |
| `calendly_url` | `https://calendly.com/selectup-co/diagnostico-sant-20-min` |
| `contact_jid` | JID/identificador do contato recebido da integração Evolution |
| `telefone` | Telefone, se a integração já fornecer esse dado |

> O nome exato da variável com o JID depende da configuração da integração. Mapeie o identificador que a Evolution entrega para `contact_jid` antes de ativar o handoff.

---

## Mensagem de abertura

**Texto**

> Olá. Sou o CHATBOT da SANT;. Posso direcionar um novo projeto, organizar uma solicitação de cliente ou chamar uma pessoa da equipe.

**Botões**

1. Quero conhecer a SANT;
2. Já sou cliente
3. Falar com uma pessoa

A escolha deve preencher `tipo_atendimento` e abrir uma das três ramificações abaixo.

---

## Ramificação 1 — Novo projeto e agendamento

### 1. Interesse principal

**Pergunta**

> O que você quer organizar primeiro?

**Botões / valor de `interesse`**

- Marca e posicionamento
- Tráfego e crescimento
- Conteúdo e autoridade
- Site ou CHATBOT
- Dados e BI
- Conhecer o CONTINUUM;
- Outro cenário

### 2. Cenário

**Pergunta aberta**

> Em uma frase: onde sua operação mais perde oportunidade hoje?

Salvar em `gargalo`.

### 3. Diagnóstico curto

Use blocos condicionais por `interesse`. Cada resposta deve ter no máximo dois parágrafos, explicar o problema operacional e conectar com a frente correspondente do CONTINUUM;.

**Exemplo para Site ou CHATBOT**

> Quando a conversa chega e ninguém responde ou entende a demanda, o lead perde contexto antes de virar oportunidade. Web + CHATBOT organiza a primeira resposta, a qualificação e o próximo passo sem substituir o comercial.

### 4. Identificação mínima

**Pergunta**

> Para eu organizar o diagnóstico, como posso te chamar?

Salvar em `nome`.

**Pergunta**

> Qual é o nome da sua empresa?

Salvar em `empresa`.

### 5. Resumo e Calendly

Monte `resumo` com:

```text
Novo projeto — SANT;
Nome: {{nome}}
Empresa: {{empresa}}
Interesse: {{interesse}}
Cenário: {{gargalo}}
Canal: WhatsApp / Typebot
```

**Mensagem**

> Perfeito, {{nome}}. O próximo passo é escolher um horário para um diagnóstico breve. A equipe já receberá este contexto e você não precisará explicar tudo de novo.

**Botão de URL**

```text
https://calendly.com/selectup-co/diagnostico-sant-20-min?utm_source=whatsapp&utm_medium=chatbot&utm_campaign=diagnostico
```

Se o Calendly aceitar parâmetros de pré-preenchimento na sua configuração, use `{{nome}}` apenas onde for oficialmente suportado. O próprio Calendly coleta os dados necessários para a reunião.

### 6. Alerta interno

Logo depois de apresentar o Calendly, dispare um webhook interno com `resumo`, `contact_jid`, `telefone` e data/hora. Isso registra o interesse mesmo que a pessoa não conclua o agendamento.

---

## Ramificação 2 — Cliente SANT;

### 1. Área da solicitação

> Em qual frente você precisa de ajuda?

- Brand & Rebrand;
- Growth & Ads;
- Social Media Strategy;
- Métricas & BI;
- Site ou CHATBOT;
- Financeiro / contrato;
- Outro

Salvar em `area_cliente`.

### 2. Urgência

> Como está essa situação?

- Estou bloqueado(a)
- Preciso resolver nesta semana
- É uma dúvida ou ajuste

Salvar em `urgencia`.

### 3. Descrição

> Me conte em uma frase o que aconteceu ou o que você precisa ajustar.

Salvar em `gargalo`.

### 4. Handoff

Monte `resumo`:

```text
Cliente SANT;
Área: {{area_cliente}}
Urgência: {{urgencia}}
Solicitação: {{gargalo}}
Contato: {{contact_jid}}
```

**Mensagem**

> Recebi sua solicitação. Vou avisar a equipe responsável e o atendimento humano continua por aqui.

Em seguida: envie o alerta interno e pause a sessão do Typebot para que ele não responda em paralelo ao humano.

---

## Ramificação 3 — Atendimento humano imediato

Essa escolha não deve exigir formulário nem perguntas adicionais.

**Mensagem**

> Certo. Vou chamar uma pessoa da equipe agora. O atendimento humano continua por este WhatsApp.

Em seguida:

1. envie o alerta interno com `contact_jid`, telefone, data/hora e o motivo `pedido_humano`;
2. altere o status da sessão Typebot para `paused`;
3. registre a conversa como pendente para a equipe responder.

---

## Handoff: regra operacional obrigatória

| Situação | Estado do bot | Ação da equipe |
|---|---|---|
| Início e automação normal | `opened` | Bot responde |
| Pessoa pede humano | `paused` | Equipe responde no mesmo WhatsApp |
| Cliente ativo encaminhado | `paused` | Equipe responde no mesmo WhatsApp |
| Encerramento sem retorno | `closed` | Nova mensagem reinicia um novo atendimento, conforme regra da instância |

A API da Evolution possui recurso de alteração de status de sessão do Typebot, incluindo estados como `opened`, `closed` e `paused`. Use o endpoint/versão exibido na documentação da sua própria instância para executar a pausa — instalações e versões podem ter rotas ou autenticação diferentes.

Nunca deixe o bot e o humano respondendo ao mesmo contato ao mesmo tempo.

---

## Estrutura do webhook interno

Em vez de pôr a API key da Evolution diretamente dentro de um bloco exposto, o ideal é enviar o webhook para uma automação protegida (n8n, Make, servidor próprio ou função serverless). Essa automação deve:

1. validar uma chave secreta do webhook;
2. registrar o lead/solicitação no destino definido pela SANT;;
3. enviar uma notificação à equipe;
4. quando existir handoff, chamar a Evolution para pausar a sessão;
5. responder `200` rapidamente ao Typebot.

### Payload sugerido

```json
{
  "origem": "typebot_whatsapp",
  "tipo_atendimento": "{{tipo_atendimento}}",
  "nome": "{{nome}}",
  "empresa": "{{empresa}}",
  "interesse": "{{interesse}}",
  "area_cliente": "{{area_cliente}}",
  "urgencia": "{{urgencia}}",
  "gargalo": "{{gargalo}}",
  "resumo": "{{resumo}}",
  "contact_jid": "{{contact_jid}}",
  "telefone": "{{telefone}}",
  "evento": "novo_lead | cliente_handoff | humano_solicitado"
}
```

Não registre senhas, documentos, cartões, códigos de autenticação ou dados sensíveis. Não envie dados pessoais para plataformas que não sejam necessárias ao atendimento.

---

## Configuração da Evolution API

1. Confirme que a instância conectada é o número correto da SANT;.
2. Confira o Typebot apontado para a URL de produção, não para um preview.
3. Mantenha o gatilho em `Keyword`. Como a SANT; também conversa manualmente por esse número, usar `All messages` faria o bot interceptar atendimentos humanos.
4. Configure `CHATBOT` como palavra-chave de entrada para novo projeto. Crie `SUPORTE` como segunda palavra-chave quando o fluxo de clientes ativos estiver pronto.
5. Garanta que cada conversa receba o identificador do contato (`contact_jid`) como variável.
6. Configure o comportamento de sessão para iniciar o Typebot em novo contato e respeitar `paused` no handoff.
7. Ative logs sem gravar tokens ou conteúdo sensível em canais públicos.
8. Teste os três caminhos usando um número de teste antes de liberar a instância principal.

## Atendimento humano

A equipe da SANT; atenderá no próprio **WhatsApp Business / WhatsApp Web** vinculado ao número da instância. Quando houver handoff, o bot deve enviar sua mensagem final, ficar em `paused` e uma pessoa assume exatamente a mesma conversa no WhatsApp. Não deixe o Typebot continuar ativo enquanto a equipe responde.

---

## Checklist de aceite

- [ ] Os três botões iniciais levam para a ramificação correta.
- [ ] Novo projeto coleta apenas cenário, nome e empresa antes do Calendly.
- [ ] O link do Calendly tem UTM de WhatsApp/CHATBOT.
- [ ] Cliente ativo informa área, urgência e descrição.
- [ ] Pedido por humano pausa o Typebot imediatamente.
- [ ] A equipe recebe o resumo do atendimento com o identificador do contato.
- [ ] O bot nunca pede dados sensíveis.
- [ ] O humano e o bot não respondem ao mesmo tempo.
- [ ] Todos os caminhos foram testados em um número externo ao da instância.

---

## Informações pendentes para ativar

1. URL definitiva do Calendly;
2. destino do alerta interno: grupo/equipe/CRM/planilha;
3. URL do webhook protegido que receberá os resumos;
4. nome da variável do JID/telefone entregue pela integração Evolution;
5. regra de reativação do bot depois que o atendimento humano terminar.
