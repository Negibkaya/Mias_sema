import client from "./client";

export async function getMe() {
  const response = await client.get("/users/me");
  return response.data;
}

export async function updateMe(data) {
  const response = await client.put("/users/me", data);
  return response.data;
}

export async function getUsers() {
  const response = await client.get("/users/");
  return response.data;
}

export async function getUser(userId) {
  const response = await client.get(`/users/${userId}`);
  return response.data;
}
