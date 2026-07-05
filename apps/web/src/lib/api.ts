const API_BASE = "/api";

async function apiFetch(path: string, options?: RequestInit) {
  const res = await fetch(`${API_BASE}${path}`, options);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res;
}

export async function fetchConversations() {
  const res = await apiFetch("/conversations");
  return res.json();
}

export async function createConversation(title?: string) {
  const res = await apiFetch("/conversations", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title: title || "New Conversation" }),
  });
  return res.json();
}

export async function getConversation(id: string) {
  const res = await apiFetch(`/conversations/${id}`);
  return res.json();
}

export async function deleteConversation(id: string) {
  await apiFetch(`/conversations/${id}`, { method: "DELETE" });
}

export async function sendMessage(
  conversationId: string,
  content: string,
  model?: string,
  temperature?: number
) {
  return apiFetch(`/conversations/${conversationId}/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content, model, temperature }),
  });
}

export async function getMessages(conversationId: string) {
  const res = await apiFetch(`/conversations/${conversationId}/messages`);
  return res.json();
}

export async function submitFeedback(
  conversationId: string,
  messageId: string,
  feedback: "thumbs_up" | "thumbs_down"
) {
  await apiFetch(`/conversations/${conversationId}/messages/${messageId}/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ feedback }),
  });
}

export async function regenerateMessage(
  conversationId: string,
  model?: string,
  temperature?: number
) {
  return apiFetch(`/conversations/${conversationId}/regenerate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model, temperature }),
  });
}
