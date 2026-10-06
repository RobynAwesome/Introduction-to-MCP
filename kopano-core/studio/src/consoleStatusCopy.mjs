/**
 * Describe why Studio cannot show proof status without claiming that checks failed.
 * @param {string} apiBase
 * @param {number | undefined} responseStatus
 */
export function getApiUnavailableMessage(apiBase, responseStatus) {
  let localApi = false;
  try {
    const hostname = new URL(apiBase).hostname;
    localApi = hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '::1';
  } catch {
    // An invalid configured URL is still a configured endpoint problem.
  }

  const source = localApi ? 'Local API' : 'Configured API';
  if (responseStatus !== undefined) {
    const response = `${source} returned HTTP ${responseStatus}; status could not be loaded.`;
    return localApi
      ? `${response} Confirm the API is running, then retry.`
      : `${response} Check the configured endpoint and network, then retry.`;
  }

  return localApi
    ? `${source} is unavailable. Start it with “python main.py serve api” from the repository root, then retry.`
    : `${source} is unavailable. Check the configured endpoint and network, then retry.`;
}
