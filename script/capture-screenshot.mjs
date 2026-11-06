import { mkdir } from "node:fs/promises";
import { createRequire } from "node:module";
import { dirname, resolve } from "node:path";
import { parseArgs } from "node:util";

// Resolve from the checkout even when this harness is copied to session storage.
const { chromium } = createRequire(resolve("package.json"))("playwright");
const { values } = parseArgs({
  options: {
    url: { type: "string", default: "http://127.0.0.1:5173/?section=tracks" },
    output: { type: "string" },
    "wait-for": { type: "string" },
    "full-page": { type: "boolean", default: false },
  },
});

if (!values.output || !values["wait-for"]) {
  throw new Error(
    "Usage: node script/capture-screenshot.mjs --output /absolute/path.png --wait-for 'Unique visible text' [--url URL] [--full-page]",
  );
}

const url = new URL(values.url);
if (
  !["localhost", "127.0.0.1"].includes(url.hostname) ||
  !["http:", "https:"].includes(url.protocol)
) {
  throw new Error("Screenshots must use the local seeded app, not production");
}

const output = resolve(values.output);
const browser = await chromium.launch();
try {
  const context = await browser.newContext({
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 1,
    reducedMotion: "reduce",
    serviceWorkers: "block",
  });
  const page = await context.newPage();
  const failures = [];
  let mockedAuth = false;
  page.on("pageerror", (error) => failures.push(error.message));
  page.on("response", (response) => {
    if (new URL(response.url()).pathname.startsWith("/api/") && !response.ok()) {
      failures.push(`${response.status()} ${response.url()}`);
    }
  });
  await page.route(new URL("/api/spotify-auth/status", url).href, async (route) => {
    mockedAuth = true;
    await route.fulfill({ json: { status: "ok" } });
  });

  await page.goto(url.href, { waitUntil: "networkidle" });
  await page.getByText(values["wait-for"], { exact: true }).waitFor();
  await page.evaluate(async () => {
    await document.fonts.ready;
    await Promise.all(Array.from(document.images, (image) => image.decode()));
    window.scrollTo(0, 0);
  });
  if (!mockedAuth) {
    throw new Error("The auth-status mock was not exercised; check the app URL");
  }
  if (
    await page
      .getByText("Spotify authorization needs attention", { exact: true })
      .isVisible()
  ) {
    throw new Error("The Spotify auth banner must not appear in screenshots");
  }
  if (failures.length) {
    throw new Error(`Screenshot page failed:\n${failures.join("\n")}`);
  }

  await mkdir(dirname(output), { recursive: true });
  await page.screenshot({
    path: output,
    fullPage: values["full-page"],
    scale: "css",
    animations: "disabled",
  });
  console.log(
    JSON.stringify({
      output,
      url: url.href,
      viewport: { width: 390, height: 844 },
      authStatus: "mocked in browser only",
      fullPage: values["full-page"],
    }),
  );
} finally {
  await browser.close();
}
