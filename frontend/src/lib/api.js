const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

async function request(path) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { Accept: 'application/json' },
  })

  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`
    try {
      const body = await response.json()
      if (body?.detail) detail = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail)
    } catch {
      // Keep the fallback error message.
    }
    throw new Error(detail)
  }

  return response.json()
}

function query(params = {}) {
  const search = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') search.set(key, value)
  })
  const text = search.toString()
  return text ? `?${text}` : ''
}

export const api = {
  baseUrl: API_BASE_URL,
  health: () => request('/health'),
  forecasts: (filters = {}) => request(`/api/v1/forecasts${query(filters)}`),
  forecast: (state, fertilizerType) =>
    request(`/api/v1/forecasts/${encodeURIComponent(state)}/${encodeURIComponent(fertilizerType)}`),
  sales: (filters = {}) => request(`/api/v1/history/sales${query(filters)}`),
  requirement: (filters = {}) => request(`/api/v1/history/requirement${query(filters)}`),
  availability: (filters = {}) => request(`/api/v1/history/availability${query(filters)}`),
  trend: (state, fertilizerType) =>
    request(`/api/v1/analytics/trend${query({ state, fertilizer_type: fertilizerType })}`),
  iffcoProduction: (filters = {}) => request(`/api/v1/iffco/production${query(filters)}`),
  rajasthanSupply: (filters = {}) => request(`/api/v1/iffco/rajasthan/supply${query(filters)}`),
  summary: () => request('/api/v1/dashboard/summary'),
  topDemand: (limit = 10) => request(`/api/v1/dashboard/top-demand${query({ limit })}`),
}
