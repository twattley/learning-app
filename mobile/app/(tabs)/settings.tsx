import { useState, useEffect } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert,
} from "react-native";
import { getApiUrl, setApiUrl, testApiConnection } from "../../lib/storage";
import { clearApiCache, getLLMMode, setLLMMode, type LLMMode } from "../../lib/api";

export default function SettingsScreen() {
  const [url, setUrl] = useState("");
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{
    success: boolean;
    message: string;
  } | null>(null);
  const [llmMode, setLlmMode] = useState<LLMMode | null>(null);
  const [switchingMode, setSwitchingMode] = useState(false);

  useEffect(() => {
    getApiUrl().then((u) => {
      setUrl(u);
      loadLLMMode();
    });
  }, []);

  const loadLLMMode = async () => {
    try {
      const mode = await getLLMMode();
      setLlmMode(mode);
    } catch (e) {
      console.log("[Settings] Failed to load LLM mode:", e);
    }
  };

  const handleToggleMode = async () => {
    if (!llmMode) return;
    setSwitchingMode(true);
    try {
      const newMode = llmMode.mode === "local" ? "web" : "local";
      const result = await setLLMMode(newMode);
      setLlmMode(result);
    } catch (e: any) {
      Alert.alert("Error", "Failed to switch LLM mode");
    } finally {
      setSwitchingMode(false);
    }
  };

  const handleTest = async () => {
    setTesting(true);
    setTestResult(null);
    const result = await testApiConnection(url);
    setTestResult(result);
    setTesting(false);
    if (result.success) loadLLMMode();
  };

  const handleSave = async () => {
    await setApiUrl(url);
    clearApiCache();
    Alert.alert("Saved", "API URL saved.");
    loadLLMMode();
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>API Configuration</Text>

      <Text style={styles.label}>API Base URL</Text>
      <TextInput
        style={styles.input}
        value={url}
        onChangeText={setUrl}
        placeholder="http://server:8003/api/v1"
        placeholderTextColor="#737373"
        autoCapitalize="none"
        autoCorrect={false}
        keyboardType="url"
      />

      <View style={styles.buttonRow}>
        <TouchableOpacity
          style={[styles.button, styles.testButton]}
          onPress={handleTest}
          disabled={testing}
        >
          {testing ? (
            <ActivityIndicator color="#fff" size="small" />
          ) : (
            <Text style={styles.buttonText}>Test Connection</Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.button, styles.saveButton]}
          onPress={handleSave}
        >
          <Text style={styles.buttonText}>Save</Text>
        </TouchableOpacity>
      </View>

      {testResult && (
        <View
          style={[
            styles.resultBox,
            testResult.success ? styles.successBox : styles.errorBox,
          ]}
        >
          <Text style={styles.resultText}>{testResult.message}</Text>
        </View>
      )}

      <Text style={styles.hint}>
        Use your Tailscale hostname (e.g., "server") instead of "localhost" when
        running on a physical device.
      </Text>

      {/* LLM Mode Toggle */}
      <View style={styles.divider} />
      <Text style={styles.title}>LLM Mode</Text>

      {llmMode ? (
        <View>
          <TouchableOpacity
            style={[
              styles.modeButton,
              llmMode.mode === "local" ? styles.modeLocal : styles.modeWeb,
            ]}
            onPress={handleToggleMode}
            disabled={switchingMode}
          >
            {switchingMode ? (
              <ActivityIndicator color="#fff" size="small" />
            ) : (
              <View style={styles.modeContent}>
                <Text style={styles.modeLabel}>
                  {llmMode.mode === "local" ? "🏠 Local" : "☁️ Web"}
                </Text>
                <Text style={styles.modeModel}>{llmMode.model}</Text>
              </View>
            )}
          </TouchableOpacity>
          <Text style={styles.hint}>
            {llmMode.mode === "local"
              ? "Using Ollama on your local machine. Tap to switch to Gemini."
              : "Using Gemini cloud API. Tap to switch to local Ollama."}
          </Text>
        </View>
      ) : (
        <Text style={styles.hint}>
          Connect to the API first to configure LLM mode.
        </Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#000000",
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: "700",
    color: "#fafafa",
    marginBottom: 24,
  },
  label: {
    fontSize: 14,
    fontWeight: "600",
    color: "#a3a3a3",
    marginBottom: 8,
  },
  input: {
    backgroundColor: "#111111",
    borderRadius: 8,
    padding: 14,
    fontSize: 16,
    color: "#fafafa",
    borderWidth: 1,
    borderColor: "#2a2a2a",
    marginBottom: 16,
  },
  buttonRow: {
    flexDirection: "row",
    gap: 12,
    marginBottom: 16,
  },
  button: {
    flex: 1,
    padding: 14,
    borderRadius: 8,
    alignItems: "center",
  },
  testButton: {
    backgroundColor: "#525252",
  },
  saveButton: {
    backgroundColor: "#2563eb",
  },
  buttonText: {
    color: "#fff",
    fontWeight: "600",
    fontSize: 16,
  },
  resultBox: {
    padding: 14,
    borderRadius: 8,
    marginBottom: 16,
  },
  successBox: {
    backgroundColor: "#166534",
  },
  errorBox: {
    backgroundColor: "#991b1b",
  },
  resultText: {
    color: "#fff",
    fontSize: 14,
  },
  hint: {
    color: "#737373",
    fontSize: 13,
    lineHeight: 20,
    marginTop: 8,
  },
  divider: {
    height: 1,
    backgroundColor: "#2a2a2a",
    marginVertical: 24,
  },
  modeButton: {
    padding: 16,
    borderRadius: 12,
    alignItems: "center",
    marginBottom: 8,
  },
  modeLocal: {
    backgroundColor: "#164e63",
    borderWidth: 1,
    borderColor: "#22d3ee",
  },
  modeWeb: {
    backgroundColor: "#3b0764",
    borderWidth: 1,
    borderColor: "#a855f7",
  },
  modeContent: {
    alignItems: "center",
    gap: 4,
  },
  modeLabel: {
    color: "#fff",
    fontSize: 20,
    fontWeight: "700",
  },
  modeModel: {
    color: "#d4d4d4",
    fontSize: 13,
    fontWeight: "500",
  },
});
