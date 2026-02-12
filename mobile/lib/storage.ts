import AsyncStorage from "@react-native-async-storage/async-storage";

const API_URL_KEY = "api_base_url";
const DEFAULT_API_URL = "http://server:8000/api/v1";

export async function getApiUrl(): Promise<string> {
  const stored = await AsyncStorage.getItem(API_URL_KEY);
  return stored ?? DEFAULT_API_URL;
}

export async function setApiUrl(url: string): Promise<void> {
  await AsyncStorage.setItem(API_URL_KEY, url);
}

export async function testApiConnection(baseUrl: string): Promise<{ success: boolean; message: string }> {
  try {
    // Test the health endpoint (without /api/v1)
    const healthUrl = baseUrl.replace(/\/api\/v1\/?$/, "") + "/health";
    const res = await fetch(healthUrl, { 
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });
    
    if (res.ok) {
      const data = await res.json();
      return { success: true, message: `Connected! Status: ${data.status}` };
    }
    return { success: false, message: `Server returned ${res.status}` };
  } catch (error) {
    return { success: false, message: `Connection failed: ${error instanceof Error ? error.message : "Unknown error"}` };
  }
}
