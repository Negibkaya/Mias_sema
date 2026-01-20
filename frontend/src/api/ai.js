import client from "./client";

export async function matchCandidates(projectId, roleName = null, topN = 3) {
  const payload = {
    project_id: projectId,
    top_n: topN,
  };
  if (roleName) {
    payload.role_name = roleName;
  }
  const response = await client.post("/ai/match", payload);
  return response.data;
}
