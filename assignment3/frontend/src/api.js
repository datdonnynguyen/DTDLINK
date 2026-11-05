export const API_BASE =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export async function apiRequest(path, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 10000);
  try {
    const response = await fetch(`${API_BASE}${path}`, {
      ...options,
      signal: controller.signal,
      cache: "no-store",
    });
    const body = await response.json();
    if (!response.ok) {
      const message =
        body.error?.fields?.find((item) => item.field === "url")?.message ||
        body.error?.message ||
        "The request could not be completed.";
      const error = new Error(message.replace(/^Value error, /, ""));
      error.code = body.error?.code;
      error.requestId = body.request_id;
      throw error;
    }
    return body;
  } catch (error) {
    if (error.name === "AbortError")
      throw new Error("The analysis timed out. Please try again.");
    if (error instanceof TypeError)
      throw new Error(
        "Cannot reach the analysis service. Check that the backend is running.",
      );
    throw error;
  } finally {
    clearTimeout(timer);
  }
}
