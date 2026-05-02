interface RequestOptions<T> {
  method?: "GET" | "POST" | "PATCH" | "PUT" | "DELETE"
  body?: T
  auth?: boolean
}

function isUnauthorizedApiError(error: unknown) {
  const candidate = error as {
    status?: number
    statusCode?: number
    response?: {
      status?: number
    }
  }

  return candidate?.status === 401 || candidate?.statusCode === 401 || candidate?.response?.status === 401
}

function normalizeApiError(error: unknown) {
  const candidate = error as {
    data?: Record<string, unknown>
    message?: string
    statusMessage?: string
  }

  if (candidate?.data) {
    const first = Object.values(candidate.data)[0]
    if (Array.isArray(first) && first.length) {
      return String(first[0])
    }
    if (typeof first === "string") {
      return first
    }
  }

  return candidate?.statusMessage || candidate?.message || "Request failed."
}

export function useApiClient() {
  const config = useRuntimeConfig()
  const authStore = useAuthStore()

  async function request<ResponseType, BodyType = unknown>(path: string, options: RequestOptions<BodyType> = {}) {
    const headers: HeadersInit = {}
    if (options.auth !== false && authStore.access) {
      headers.Authorization = `Bearer ${authStore.access}`
    }

    try {
      return await $fetch<ResponseType>(path, {
        baseURL: config.public.apiBase,
        method: options.method || "GET",
        body: options.body,
        headers,
      })
    } catch (error) {
      if (options.auth !== false && isUnauthorizedApiError(error)) {
        authStore.clear()
        throw new Error("Session expired. Please sign in again.")
      }

      throw new Error(normalizeApiError(error))
    }
  }

  return {
    get: <T>(path: string, auth = true) => request<T>(path, { auth }),
    post: <T, B = unknown>(path: string, body?: B, auth = true) => request<T, B>(path, { method: "POST", body, auth }),
    patch: <T, B = unknown>(path: string, body?: B) => request<T, B>(path, { method: "PATCH", body }),
    put: <T, B = unknown>(path: string, body?: B) => request<T, B>(path, { method: "PUT", body }),
    delete: <T>(path: string) => request<T>(path, { method: "DELETE" }),
  }
}