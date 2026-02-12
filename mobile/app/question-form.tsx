import { useEffect, useState } from "react";
import {
  View,
  Text,
  TextInput,
  Pressable,
  ScrollView,
  Alert,
  ActivityIndicator,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
} from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import {
  getQuestion,
  createQuestion,
  updateQuestion,
  type Question,
} from "../lib/api";

export default function QuestionFormScreen() {
  const router = useRouter();
  const { id } = useLocalSearchParams<{ id?: string }>();
  const isEditing = !!id;

  const [questionText, setQuestionText] = useState("");
  const [answerText, setAnswerText] = useState("");
  const [topic, setTopic] = useState("");
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(false);

  // Load existing question when editing
  useEffect(() => {
    if (!id) return;
    setLoading(true);
    getQuestion(id)
      .then((q) => {
        setQuestionText(q.question_text);
        setAnswerText(q.answer_text ?? "");
        setTopic(q.topic);
      })
      .catch(() => Alert.alert("Error", "Failed to load question"))
      .finally(() => setLoading(false));
  }, [id]);

  const handleSave = async () => {
    if (!questionText.trim() || !topic.trim()) {
      Alert.alert("Required", "Question and topic are required.");
      return;
    }

    setSaving(true);
    try {
      const data = {
        question_text: questionText.trim(),
        answer_text: answerText.trim() || undefined,
        topic: topic.trim().toLowerCase(),
      };

      if (isEditing) {
        await updateQuestion(id!, data);
      } else {
        await createQuestion(data as any);
      }

      router.back();
    } catch {
      Alert.alert("Error", "Failed to save question");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <View style={[styles.container, styles.center]}>
        <ActivityIndicator size="large" color="#2563eb" />
      </View>
    );
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      <ScrollView
        contentContainerStyle={styles.scroll}
        keyboardShouldPersistTaps="handled"
      >
        <Text style={styles.label}>Topic *</Text>
        <TextInput
          style={styles.inputSmall}
          placeholder="e.g. python, sql, networking"
          placeholderTextColor="#64748b"
          value={topic}
          onChangeText={setTopic}
          autoCapitalize="none"
        />

        <Text style={styles.label}>Question *</Text>
        <TextInput
          style={styles.inputLarge}
          placeholder="What do you want to test?"
          placeholderTextColor="#64748b"
          multiline
          value={questionText}
          onChangeText={setQuestionText}
          textAlignVertical="top"
        />

        <Text style={styles.label}>
          Reference Answer <Text style={styles.optional}>(optional)</Text>
        </Text>
        <TextInput
          style={styles.inputLarge}
          placeholder="The ideal answer — leave blank to let the LLM grade on its own"
          placeholderTextColor="#64748b"
          multiline
          value={answerText}
          onChangeText={setAnswerText}
          textAlignVertical="top"
        />

        <Pressable
          style={[styles.button, saving && styles.buttonDisabled]}
          onPress={handleSave}
          disabled={saving}
        >
          {saving ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.buttonText}>
              {isEditing ? "Update" : "Create"}
            </Text>
          )}
        </Pressable>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#0f172a" },
  center: { justifyContent: "center", alignItems: "center" },
  scroll: { padding: 20, paddingBottom: 60 },

  label: {
    color: "#cbd5e1",
    fontSize: 14,
    fontWeight: "600",
    marginBottom: 6,
    marginTop: 16,
  },
  optional: { color: "#64748b", fontWeight: "400" },

  inputSmall: {
    backgroundColor: "#1e293b",
    color: "#f1f5f9",
    borderRadius: 10,
    padding: 14,
    fontSize: 15,
    borderWidth: 1,
    borderColor: "#334155",
  },
  inputLarge: {
    backgroundColor: "#1e293b",
    color: "#f1f5f9",
    borderRadius: 10,
    padding: 14,
    fontSize: 15,
    minHeight: 110,
    borderWidth: 1,
    borderColor: "#334155",
  },

  button: {
    backgroundColor: "#2563eb",
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: "center",
    marginTop: 28,
  },
  buttonDisabled: { opacity: 0.5 },
  buttonText: { color: "#fff", fontSize: 16, fontWeight: "700" },
});
