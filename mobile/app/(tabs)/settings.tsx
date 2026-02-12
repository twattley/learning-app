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

export default function SettingsScreen() {
  const [url, setUrl] = useState("");
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{
    success: boolean;
    message: string;
  } | null>(null);

  useEffect(() => {
    getApiUrl().then(setUrl);
  }, []);

  const handleTest = async () => {
    setTesting(true);
    setTestResult(null);
    const result = await testApiConnection(url);
    setTestResult(result);
    setTesting(false);
  };

  const handleSave = async () => {
    await setApiUrl(url);
    Alert.alert(
      "Saved",
      "API URL saved. Restart the app for changes to take effect.",
    );
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>API Configuration</Text>

      <Text style={styles.label}>API Base URL</Text>
      <TextInput
        style={styles.input}
        value={url}
        onChangeText={setUrl}
        placeholder="http://server:8000/api/v1"
        placeholderTextColor="#64748b"
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
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#0f172a",
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: "700",
    color: "#f8fafc",
    marginBottom: 24,
  },
  label: {
    fontSize: 14,
    fontWeight: "600",
    color: "#94a3b8",
    marginBottom: 8,
  },
  input: {
    backgroundColor: "#1e293b",
    borderRadius: 8,
    padding: 14,
    fontSize: 16,
    color: "#f8fafc",
    borderWidth: 1,
    borderColor: "#334155",
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
    backgroundColor: "#475569",
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
    color: "#64748b",
    fontSize: 13,
    lineHeight: 20,
    marginTop: 8,
  },
});
