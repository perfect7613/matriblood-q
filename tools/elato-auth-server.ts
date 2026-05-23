const encoder = new TextEncoder();

const jwtSecret = Deno.env.get("JWT_SECRET_KEY");
const port = Number(Deno.env.get("PORT") ?? "3000");

if (!jwtSecret) {
  throw new Error("JWT_SECRET_KEY is required");
}

function base64Url(bytes: Uint8Array): string {
  return btoa(String.fromCharCode(...bytes))
    .replaceAll("+", "-")
    .replaceAll("/", "_")
    .replaceAll("=", "");
}

async function signJwt(payload: Record<string, unknown>): Promise<string> {
  const header = { alg: "HS256", typ: "JWT" };
  const now = Math.floor(Date.now() / 1000);
  const body = {
    aud: "authenticated",
    role: "authenticated",
    sub: "5af62b0e-3da4-4c44-adf7-5b1b7c9c4cb6",
    email: "admin@elatoai.com",
    iat: now,
    exp: now + 60 * 60 * 24 * 365,
    user_metadata: payload,
  };

  const unsigned = [
    base64Url(encoder.encode(JSON.stringify(header))),
    base64Url(encoder.encode(JSON.stringify(body))),
  ].join(".");

  const key = await crypto.subtle.importKey(
    "raw",
    encoder.encode(jwtSecret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const signature = await crypto.subtle.sign("HMAC", key, encoder.encode(unsigned));
  return `${unsigned}.${base64Url(new Uint8Array(signature))}`;
}

Deno.serve({ hostname: "0.0.0.0", port }, async (request) => {
  const url = new URL(request.url);

  if (url.pathname === "/health") {
    return Response.json({ ok: true, service: "elato-auth-shim" });
  }

  if (url.pathname !== "/api/generate_auth_token") {
    return Response.json({ error: "not found" }, { status: 404 });
  }

  const macAddress = url.searchParams.get("macAddress");
  if (!macAddress) {
    return Response.json({ error: "macAddress is required" }, { status: 400 });
  }

  const token = await signJwt({
    email: "admin@elatoai.com",
    user_id: "5af62b0e-3da4-4c44-adf7-5b1b7c9c4cb6",
    mac_address: macAddress,
    created_time: new Date().toISOString(),
  });

  console.log(`[elato-auth] issued token for ${macAddress}`);
  return Response.json({ token });
});
