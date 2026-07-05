const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export async function fetchConversations() {
  const res = await fetch(`${API_URL}/conversations`);
  if (!res.ok) throw new Error("Failed to fetch conversations");
  return res.json();
}

export async function createConversation(title?: string) {
  const res = await fetch(`${API_URL}/conversations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title: title || "New Conversation" }),
  });
  if (!res.ok) throw new Error("Failed to create conversation");
  return res.json();
}

export async function getConversation(id: string) {
  const res = await fetch(`${API_URL}/conversations/${id}`);
  if (!res.ok) throw new Error("Failed to fetch conversation");
  return res.json();
}

export async function deleteConversation(id: string) {
  await fetch(`${API_URL}/conversations/${id}`, { method: "DELETE" });
}

export async function sendMessage(
  conversationId: string,
  content: string,
  model?: string,
  temperature?: number
) {
  const res = await fetch(`${API_URL}/conversations/${conversationId}/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content, model, temperature }),
  });
  if (!res.ok) throw new Error("Failed to send message");
  return res;
}

export async function getMessages(conversationId: string) {
  const res = await fetch(`${API_URL}/conversations/${conversationId}/messages`);
  if (!res.ok) throw new Error("Failed to fetch messages");
  return res.json();
}

export async function submitFeedback(
  conversationId: string,
  messageId: string,
  feedback: "thumbs_up" | "thumbs_down"
) {
  const res = await fetch(
    `${API_URL}/conversations/${conversationId}/messages/${messageId}/feedback`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ feedback }),
    }
  );
  if (!res.ok) throw new Error("Failed to submit feedback");
  return res.json();
}

export async function regenerateMessage(
  conversationId: string,
  model?: string,
  temperature?: number
) {
  const res = await fetch(`${API_URL}/conversations/${conversationId}/regenerate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model, temperature }),
  });
  if (!res.ok) throw new Error("Failed to regenerate");
  return res;
}
