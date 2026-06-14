import AsyncStorage from '@react-native-async-storage/async-storage'

const API_URL_KEY = 'api_base_url'
export const DEFAULT_API_BASE = 'http://server:8004/api/v1'

let _cached: string | null = null

export async function getApiBase(): Promise<string> {
  if (_cached) return _cached
  const stored = await AsyncStorage.getItem(API_URL_KEY)
  _cached = stored ?? DEFAULT_API_BASE
  return _cached
}

export async function setApiBase(url: string): Promise<void> {
  await AsyncStorage.setItem(API_URL_KEY, url)
  _cached = url
}

export function clearApiCache(): void {
  _cached = null
}

export async function testApiConnection(
  baseUrl: string,
): Promise<{ success: boolean; message: string }> {
  try {
    const healthUrl = baseUrl.replace(/\/api\/v1\/?$/, '') + '/health'
    const res = await fetch(healthUrl, { headers: { 'Content-Type': 'application/json' } })
    if (res.ok) {
      const data = await res.json()
      return { success: true, message: `Connected! Status: ${data.status}` }
    }
    return { success: false, message: `Server returned ${res.status}` }
  } catch (error) {
    return {
      success: false,
      message: `Connection failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
    }
  }
}
