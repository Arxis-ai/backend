export default {
  async scheduled(event, env, ctx) {
    if (!env.BACKEND_URL) {
      throw new Error("Missing worker variable: BACKEND_URL");
    }

    const backendUrl = env.BACKEND_URL.replace(/\/+$/, "");
    ctx.waitUntil(fetch(`${backendUrl}/health`));
  },
};
