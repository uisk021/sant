# DashSocial; — conexão segura com Google Sheets

Planilha configurada:

```text
https://docs.google.com/spreadsheets/d/1g6IiDF-3lP7BAuNiwQg3mcqGp2D87v2gUuXI190w6Fk/edit
```

A planilha permanece privada. O DashSocial; lê somente a aba `Dados_Diarios` usando uma **Service Account** do Google com acesso de leitura.

> Nunca envie o arquivo JSON da chave, API keys, QR code ou senhas por chat, WhatsApp ou repositório Git.

## 1. Criar um projeto no Google Cloud

1. Abra `https://console.cloud.google.com/` com a conta que administra a planilha.
2. No seletor superior, clique em **New project / Novo projeto**.
3. Nome sugerido: `DashSocial SANT`.
4. Crie o projeto e confirme que ele está selecionado no topo da página.

## 2. Habilitar a Google Sheets API

1. Abra **APIs & Services** → **Library**.
2. Busque por `Google Sheets API`.
3. Abra o resultado e clique em **Enable / Ativar**.

## 3. Criar a Service Account de leitura

1. Abra **IAM & Admin** → **Service Accounts**.
2. Clique em **Create service account**.
3. Nome sugerido: `dashsocial-reader`.
4. Clique em **Create and continue**.
5. Não é necessário dar papel de Owner, Editor ou acesso ao projeto. Conclua a criação sem papéis adicionais.
6. Abra a Service Account recém-criada.
7. Na aba **Keys**, clique em **Add key** → **Create new key** → **JSON**.
8. Baixe o arquivo JSON e guarde-o em local seguro. Ele será usado uma única vez para configurar o Render.

Copie o e-mail da conta de serviço. Ele se parece com:

```text
dashsocial-reader@dashsocial-sant.iam.gserviceaccount.com
```

## 4. Dar acesso apenas à planilha

1. Abra a planilha no Google Sheets.
2. Clique em **Compartilhar**.
3. Cole o e-mail da Service Account.
4. Defina a permissão como **Leitor / Viewer**.
5. Não deixe a planilha pública e não habilite acesso por link para qualquer pessoa.

## 5. Converter a credencial em Base64 (Windows)

No PowerShell, substitua o caminho pelo local do JSON baixado:

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\caminho\para\dashsocial-reader.json")) | Set-Clipboard
```

O comando copia o valor codificado para a área de transferência. O arquivo JSON pode continuar guardado fora da pasta do site.

## 6. Configurar Environment Variables no Render

No serviço do site, abra **Environment** e configure:

```text
DASHSOCIAL_SHEET_ID=1g6IiDF-3lP7BAuNiwQg3mcqGp2D87v2gUuXI190w6Fk
DASHSOCIAL_SHEET_TAB=Dados_Diarios
DASHSOCIAL_GOOGLE_CREDENTIALS_B64=<cole o valor copiado no PowerShell>
DASHSOCIAL_ACCESS_CODE=<crie um código interno forte>
FLASK_SECRET_KEY=<crie uma sequência aleatória longa>
SESSION_COOKIE_SECURE=1
DASHSOCIAL_CACHE_SECONDS=120
```

Não preencha `DASHSOCIAL_GOOGLE_CREDENTIALS_JSON` se estiver usando a versão Base64.

## 7. Atualizar dependências e publicar

O projeto atualizado já inclui `google-api-python-client` e `google-auth` em `requirements.txt`.

No Render, faça um novo deploy. O comando de start continua:

```text
gunicorn app:app
```

## 8. Testar

1. Abra `https://SEU-DOMINIO/dashsocial`.
2. Informe o `DASHSOCIAL_ACCESS_CODE`.
3. O painel deve mostrar os dados da planilha.
4. Altere ou adicione uma linha em `Dados_Diarios`.
5. Aguarde até dois minutos (cache configurado) e atualize a página.

## Se der erro

- **Integração pendente**: credencial não está configurada ou o deploy ainda não instalou as dependências.
- **Não foi possível carregar**: confira se a Sheets API foi ativada e se a planilha foi compartilhada com o e-mail exato da Service Account.
- **Sem dados**: confira se a aba chama exatamente `Dados_Diarios`, se os cabeçalhos permanecem na primeira linha e se a coluna Data usa datas válidas.
- **Acesso não autorizado**: confirme o código informado no painel e a variável `DASHSOCIAL_ACCESS_CODE`.
