/**
 * Use the Create React App development proxy in package.json. Keeping API
 * requests relative makes the browser use the same origin as the React app,
 * while the proxy forwards them to Flask on port 5555.
 */
export async function apiRequest(endpoint, options = {}) {
  const headers = {
    Accept: "application/json",
    ...(options.body ? { "Content-Type": "application/json" } : {}),
    ...options.headers,
  };

  const response = await fetch(endpoint, {
    ...options,
    headers,
    credentials: "include",
  });

  const responseText = await response.text();
  let data = null;
  if (responseText) {
    try {
      data = JSON.parse(responseText);
    } catch {
      data = responseText;
    }
  }

  if (!response.ok) {
    const errors = data && data.errors;
    const message =
      (data && (data.error || data.message)) ||
      (Array.isArray(errors) ? errors.join(" ") : null) ||
      (errors && typeof errors === "object" ? JSON.stringify(errors) : null) ||
      (typeof data === "string" ? data : null) ||
      `Request failed (${response.status})`;
    throw new Error(message);
  }

  // DELETE routes may return 204 No Content.
  return data;
}
