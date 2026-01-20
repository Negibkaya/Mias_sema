import client from "./client";

export async function getProjects() {
  const response = await client.get("/projects/");
  return response.data;
}

export async function getProject(projectId) {
  const response = await client.get(`/projects/${projectId}`);
  return response.data;
}

export async function createProject(data) {
  const response = await client.post("/projects/", data);
  return response.data;
}

export async function updateProject(projectId, data) {
  const response = await client.patch(`/projects/${projectId}`, data);
  return response.data;
}

export async function deleteProject(projectId) {
  const response = await client.delete(`/projects/${projectId}`);
  return response.data;
}

export async function getProjectMembers(projectId) {
  const response = await client.get(`/projects/${projectId}/members`);
  return response.data;
}

// ИЗМЕНЕНО: добавлен параметр roleName
export async function addProjectMember(projectId, userId, roleName = null) {
  const params = roleName ? `?role_name=${encodeURIComponent(roleName)}` : "";
  const response = await client.post(
    `/projects/${projectId}/members/${userId}${params}`,
  );
  return response.data;
}

export async function removeProjectMember(projectId, userId) {
  const response = await client.delete(
    `/projects/${projectId}/members/${userId}`,
  );
  return response.data;
}
