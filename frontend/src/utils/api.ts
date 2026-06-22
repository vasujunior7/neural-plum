const API_BASE = "https://vasiuuu-neural-plum-app.hf.space/v1"
const API_KEY = "super-secret-plum-key"

export async function fetchClaims() {
  const response = await fetch(`${API_BASE}/claims`, {
    headers: {
      "X-API-Key": API_KEY,
    },
  })
  if (!response.ok) {
    throw new Error("Failed to fetch claims")
  }
  return response.json()
}

export async function fetchClaim(id: string) {
  const response = await fetch(`${API_BASE}/claims/${id}`, {
    headers: {
      "X-API-Key": API_KEY,
    },
  })
  if (!response.ok) {
    throw new Error(`Failed to fetch claim ${id}`)
  }
  return response.json()
}

export async function submitClaim(formData: FormData) {
  const response = await fetch(`${API_BASE}/claims`, {
    method: "POST",
    headers: {
      "X-API-Key": API_KEY,
      // Note: do not set Content-Type header when using FormData, 
      // the browser will automatically set it with the correct boundary
    },
    body: formData,
  })
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => null)
    throw new Error(errorData?.detail || "Failed to submit claim")
  }
  return response.json()
}
