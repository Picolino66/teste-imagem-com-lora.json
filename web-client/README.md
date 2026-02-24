# Web Client

Página estática para testar o endpoint `/generate` do Runpod sem bloqueio de CORS no navegador.

## Como usar

1. Abra a pasta `web-client`.
2. Rode o servidor local com proxy:

```bash
python3 server.py
```

3. Acesse:

```text
http://localhost:8000
```

4. Preencha:
- `Endpoint Base URL` (ex.: `https://SEU_ENDPOINT.api.runpod.ai`)
- `RUNPOD_API_KEY`
- `Prompt` (opcional)
- `Workflow API JSON` no formato `{"workflow": {...}}`

5. Clique em `Enviar`.

## Observações

- O app envia a requisição para `POST /api/generate` no servidor local.
- O proxy local encaminha para `https://SEU_ENDPOINT.api.runpod.ai/generate` com `Authorization: Bearer ...`.
- O app envia `response_format: "base64"` para renderizar a imagem diretamente.
- `Prompt Node ID` é opcional. Se vazio, o app usa o primeiro nó `CLIPTextEncode` com `inputs.text`.
- A API Key não é persistida.
