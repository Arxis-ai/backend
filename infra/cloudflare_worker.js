export default {
  async scheduled(event, env, ctx) {
    if (!env.BACKEND_URL) {
      throw new Error("Missing worker variable: BACKEND_URL");
    }

    const backendUrl = env.BACKEND_URL.replace(/\/+$/, "");
    ctx.waitUntil(assertHealthy(`${backendUrl}/health/db`));
  },
};

async function assertHealthy(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Health check failed with status ${response.status}`);
  }
}
