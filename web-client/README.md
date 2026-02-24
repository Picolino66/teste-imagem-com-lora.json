# Web Client

Página estática para testar o endpoint `/generate` do Runpod.

## Como usar

1. Abra a pasta `web-client`.
2. Rode um servidor estático simples:

```bash
python3 -m http.server 8080
```

3. Acesse:

```text
http://localhost:8080
```

4. Preencha:
- `Endpoint Base URL` (ex.: `https://SEU_ENDPOINT.api.runpod.ai`)
- `API Key`
- `Prompt` (opcional)
- `Workflow API JSON` no formato `{"workflow": {...}}`

5. Clique em `Enviar`.

## Observações

- O app envia `response_format: "base64"` para renderizar a imagem diretamente.
- `Prompt Node ID` é opcional. Se vazio, o app usa o primeiro nó `CLIPTextEncode` com `inputs.text`.
- A API Key não é persistida.
