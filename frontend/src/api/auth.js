import client from "./client";

export async function loginWithCode(code) {
  const response = await client.post("/auth/telegram/complete", { code });
  return response.data;
}
