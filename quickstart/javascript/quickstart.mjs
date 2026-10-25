// Quote, generate and poll one Raywake generation (Node.js 18+, no dependencies).
//
// By default this only requests a free quote. Add --generate to start the paid run.
//
//   export RAYWAKE_API_KEY=...
//   node quickstart.mjs              # price only
//   node quickstart.mjs --generate   # spend the quote and wait for the result

const BASE = process.env.RAYWAKE_API_BASE ?? "https://api.raywake.com";
const TERMINAL = ["succeeded", "failed", "needs_review", "submission_unknown", "needs_reconciliation"];

const model = "kling/v4/text-to-video";
const input = {
  prompt: "A perfume bottle on a stone table. Slow camera push in, soft window light, one continuous shot.",
  duration: 5,
  resolution: "720p",
  aspect_ratio: "16:9",
};

async function call(method, path, body, extraHeaders = {}) {
  const response = await fetch(`${BASE}${path}`, {
    method,
    headers: {
      Authorization: `Bearer ${process.env.RAYWAKE_API_KEY}`,
      ...(body ? { "Content-Type": "application/json" } : {}),
      ...extraHeaders,
    },
    body: body ? JSON.stringify(body) : undefined,
    signal: AbortSignal.timeout(60_000),
  });
  if (!response.ok) throw new Error(`${method} ${path} failed with ${response.status}: ${await response.text()}`);
  return response.json();
}

// 1. Price the exact input. Quotes are free and valid for up to 10 minutes.
const quote = await call("POST", "/v1/quotes", { model, input });
console.log(`Quote ${quote.quote_id}: $${quote.price_usd} (expires ${quote.expires_at})`);

if (!process.argv.includes("--generate")) {
  console.log("Run again with --generate to start this generation.");
} else {
  // 2. Start the generation with the same model and input. Keep the key if you retry this request.
  let job = await call("POST", "/v1/generate", { model, input, quote_id: quote.quote_id },
    { "Idempotency-Key": crypto.randomUUID() });

  // 3. Poll until the job reaches a terminal status.
  while (!TERMINAL.includes(job.status)) {
    await new Promise((resolve) => setTimeout(resolve, 3000));
    job = await call("GET", `/v1/jobs/${job.job_id}`);
    console.log("status:", job.status);
  }
  for (const output of job.outputs ?? []) console.log(output.type, output.url);
}
