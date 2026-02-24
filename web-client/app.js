const endpointInput = document.getElementById("endpoint");
const runpodApiKeyInput = document.getElementById("runpodApiKey");
const promptInput = document.getElementById("prompt");
const promptNodeIdInput = document.getElementById("promptNodeId");
const workflowInput = document.getElementById("workflow");
const sendBtn = document.getElementById("sendBtn");
const statusEl = document.getElementById("status");
const resultImage = document.getElementById("resultImage");
const resultMeta = document.getElementById("resultMeta");

endpointInput.value = "https://vs0ccl1dw5o7hn.api.runpod.ai";
promptNodeIdInput.value = "83:27";

function setStatus(message) {
  statusEl.textContent = message;
}

function setPromptInWorkflow(workflowObject, promptText, promptNodeId) {
  if (!workflowObject || typeof workflowObject !== "object") {
    throw new Error("Campo workflow inválido.");
  }

  const preferredNodeId = promptNodeId || "83:27";
  if (preferredNodeId) {
    const node = workflowObject[preferredNodeId];
    if (!node || !node.inputs || typeof node.inputs.text !== "string") {
      if (promptNodeId) {
        throw new Error(`Nó ${promptNodeId} não encontrado ou sem inputs.text.`);
      }
    } else {
      node.inputs.text = promptText;
      return;
    }
  }

  const candidates = Object.entries(workflowObject).filter(([, node]) => {
    return node?.class_type === "CLIPTextEncode" && node?.inputs && typeof node.inputs.text === "string";
  });

  if (candidates.length === 0) {
    throw new Error("Nenhum nó CLIPTextEncode com inputs.text encontrado.");
  }

  const [firstNodeId, firstNode] = candidates[0];
  firstNode.inputs.text = promptText;
  setStatus(`Prompt aplicado no nó ${firstNodeId}. Enviando...`);
}

async function onSend() {
  try {
    resultImage.removeAttribute("src");
    resultMeta.textContent = "";

    const endpoint = endpointInput.value.trim().replace(/\/+$/, "");
    const runpodApiKey = runpodApiKeyInput.value.trim();
    const prompt = promptInput.value.trim();
    const promptNodeId = promptNodeIdInput.value.trim();
    const workflowRaw = workflowInput.value.trim();

    if (!endpoint) throw new Error("Informe o Endpoint Base URL.");
    if (!runpodApiKey) throw new Error("Informe a RUNPOD_API_KEY.");
    if (!workflowRaw) throw new Error("Informe o Workflow API JSON.");

    let payload = JSON.parse(workflowRaw);
    if (!payload.workflow || typeof payload.workflow !== "object") {
      throw new Error("JSON deve ter o formato: { \"workflow\": { ... } }");
    }

    if (prompt) {
      setPromptInWorkflow(payload.workflow, prompt, promptNodeId);
    }

    payload.response_format = "base64";

    setStatus("Enviando requisição para /api/generate (proxy local)...");

    const response = await fetch("/api/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        endpoint,
        runpod_api_key: runpodApiKey,
        payload
      })
    });

    const body = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(JSON.stringify(body, null, 2) || `HTTP ${response.status}`);
    }

    const result = body.result || {};
    if (!result.image_base64) {
      throw new Error("Resposta não contém image_base64.");
    }

    const mimeType = result.mime_type || "image/png";
    resultImage.src = `data:${mimeType};base64,${result.image_base64}`;
    resultMeta.textContent = `Arquivo: ${result.filename || "desconhecido"} | MIME: ${mimeType}`;
    setStatus("Imagem recebida e renderizada com sucesso.");
  } catch (error) {
    if (error instanceof TypeError) {
      setStatus("Erro de rede ao acessar o proxy local. Verifique se o server.py está em execução na mesma origem.");
      return;
    }
    setStatus(`Erro: ${error.message}`);
  }
}

sendBtn.addEventListener("click", onSend);
