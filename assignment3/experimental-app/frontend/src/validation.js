export const MAX_URL_LENGTH = 2048;
export function validateURL(value) {
  if (!value) return "Enter a URL to analyse.";
  if (value.length > MAX_URL_LENGTH)
    return "Keep the URL to 2,048 characters or fewer.";
  if (/\s|[\u0000-\u001f\u007f-\u009f]/u.test(value))
    return "Remove spaces and control characters from the URL.";
  if (!/^https?:\/\//i.test(value))
    return "Start the URL with http:// or https://.";
  if (value.includes("\\")) return "Use forward slashes, not backslashes.";
  if (/%(?![0-9a-f]{2})/i.test(value))
    return "Check the percent-encoded characters in the URL.";
  try {
    const parsed = new URL(value);
    if (!parsed.hostname || parsed.port === "0")
      return "Enter a valid hostname and port.";
  } catch {
    return "Enter a complete URL with a valid hostname and port.";
  }
  return "";
}

export function sessionEntry(result, number) {
  // Session comparisons deliberately exclude URLs, hosts and query strings.
  return {
    number,
    label: result.label,
    predictedClass: result.predicted_class,
    score: Math.round(result.dangerous_probability * 100),
    confidence: Math.round(result.confidence * 100),
    signals: result.signals.filter((item) => item.present).length,
    time: new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    }),
  };
}
