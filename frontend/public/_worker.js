export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Proxy API and WebSocket requests to the backend
    if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/ws/')) {
      const backendStr = env.BACKEND_URL;
      
      if (!backendStr || backendStr === 'https://your-backend-url.com' || backendStr.includes('your-backend.example.com')) {
        return new Response(JSON.stringify({ 
          error: "Backend not configured", 
          detail: "Please set the BACKEND_URL environment variable in your Cloudflare dashboard to your Python server address." 
        }), {
          status: 503,
          headers: { 'Content-Type': 'application/json' }
        });
      }

      try {
        const backendUrl = new URL(backendStr);
        const targetUrl = new URL(url.pathname + url.search, backendUrl);
        const proxyRequest = new Request(targetUrl, request);
        
        const response = await fetch(proxyRequest);
        const newResponse = new Response(response.body, response);
        newResponse.headers.set('Access-Control-Allow-Origin', '*');
        return newResponse;

      } catch (e) {
        return new Response(JSON.stringify({ error: `Proxy Error: ${e.message}` }), {
          status: 502,
          headers: { 'Content-Type': 'application/json' }
        });
      }
    }

    // Serve static frontend assets for all other routes
    try {
      const resp = await env.ASSETS.fetch(request);
      if (resp.status === 404 && !url.pathname.includes('.')) {
        const indexRequest = new Request(new URL('/', request.url));
        return env.ASSETS.fetch(indexRequest);
      }
      return resp;
    } catch {
      const indexRequest = new Request(new URL('/', request.url));
      return env.ASSETS.fetch(indexRequest);
    }
  }
};
