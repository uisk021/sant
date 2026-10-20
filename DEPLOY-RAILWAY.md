# Deploy da SANT; no Railway

## Antes de enviar ao GitHub

- Não envie `.env`.
- Se um segredo já foi enviado ao GitHub, revogue/regenere-o no provedor antes do deploy.
- Envie todos os arquivos deste pacote para a raiz do repositório. O `Dockerfile` deve ficar ao lado de `app.py`.

## Railway

1. Crie um serviço usando o repositório GitHub.
2. Deixe **Build Command** e **Start Command** vazios: o `Dockerfile` define ambos.
3. Em **Variables**, cadastre no mínimo:
   - `FLASK_SECRET_KEY`: uma chave aleatória longa;
   - `SANT_WHATSAPP`: número com DDI e DDD;
   - `CANONICAL_URL`: domínio público terminado em `/`;
   - `FLASK_DEBUG=0`.
4. `GEMINI_API_KEY` é opcional. Sem ela, o chat funciona com respostas guiadas.
5. Gere um domínio em **Networking** ou conecte um domínio próprio.

O site responde na porta `PORT` fornecida pelo Railway.
