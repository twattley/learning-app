import { useEffect, useState } from "react";
import {
  View,
  Text,
  TextInput,
  Pressable,
  ScrollView,
  ActivityIndicator,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
} from "react-native";
import {
  fetchNextQuestion,
  submitAnswer,
  type Question,
  type Review,
} from "../../lib/api";
import Markdown from "react-native-markdown-display";

type Phase = "loading" | "question" | "feedback" | "error" | "empty";

export default function LearnScreen() {
  const [phase, setPhase] = useState<Phase>("loading");
  const [question, setQuestion] = useState<Question | null>(null);
  const [userAnswer, setUserAnswer] = useState("");
  const [review, setReview] = useState<Review | null>(null);
  const [error, setError] = useState("");

  const loadQuestion = async () => {
    setPhase("loading");
    setUserAnswer("");
    setReview(null);
    try {
      const q = await fetchNextQuestion();
      setQuestion(q);
      setPhase("question");
    } catch (e: any) {
      if (e.message?.includes("404")) {
        setPhase("empty");
      } else {
        setError(e.message);
        setPhase("error");
      }
    }
  };

  const handleSubmit = async () => {
    if (!question || !userAnswer.trim()) return;
    setPhase("loading");
    try {
      const r = await submitAnswer({
        question_id: question.id,
        question_type: question.question_type ?? "regular",
        user_answer: userAnswer.trim(),
      });
      setReview(r);
      setPhase("feedback");
    } catch (e: any) {
      setError(e.message);
      setPhase("error");
    }
  };

  // Load first question on mount
  useEffect(() => {
    loadQuestion();
  }, []);

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      <ScrollView
        contentContainerStyle={styles.scroll}
        keyboardShouldPersistTaps="handled"
      >
        {phase === "loading" && (
          <View style={styles.center}>
            <ActivityIndicator size="large" color="#2563eb" />
          </View>
        )}

        {phase === "empty" && (
          <View style={styles.center}>
            <Text style={styles.emptyText}>No questions yet.</Text>
            <Text style={styles.emptySubtext}>
              Add some in the Questions tab to get started.
            </Text>
          </View>
        )}

        {phase === "error" && (
          <View style={styles.center}>
            <Text style={styles.errorText}>Something went wrong</Text>
            <Text style={styles.errorDetail}>{error}</Text>
            <Pressable style={styles.button} onPress={loadQuestion}>
              <Text style={styles.buttonText}>Try Again</Text>
            </Pressable>
          </View>
        )}

        {phase === "question" && question && (
          <View>
            <View style={styles.topicBadge}>
              <Text style={styles.topicText}>{question.topic}</Text>
            </View>
            <Markdown style={mdStyles}>
              {question.display_text ?? question.question_text}
            </Markdown>
            <TextInput
              style={styles.input}
              placeholder="Type your answer..."
              placeholderTextColor="#a3a3a3"
              multiline
              value={userAnswer}
              onChangeText={setUserAnswer}
              textAlignVertical="top"
            />
            <Pressable
              style={[
                styles.button,
                !userAnswer.trim() && styles.buttonDisabled,
              ]}
              onPress={handleSubmit}
              disabled={!userAnswer.trim()}
            >
              <Text style={styles.buttonText}>Submit</Text>
            </Pressable>
          </View>
        )}

        {phase === "feedback" && review && (
          <View>
            <View style={styles.scoreRow}>
              <Text style={styles.scoreLabel}>Score</Text>
              <Text style={styles.scoreValue}>
                {review.score != null ? `${review.score}/5` : "—"}
              </Text>
            </View>
            <View style={styles.feedbackCard}>
              <Markdown style={mdStyles}>
                {review.llm_feedback}
              </Markdown>
            </View>
            <Pressable style={styles.button} onPress={loadQuestion}>
              <Text style={styles.buttonText}>Next Question</Text>
            </Pressable>
          </View>
        )}
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#000000" },
  scroll: { padding: 20, paddingBottom: 60 },
  center: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    marginTop: 80,
  },

  topicBadge: {
    alignSelf: "flex-start",
    backgroundColor: "#1a1a2e",
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
    marginBottom: 16,
  },
  topicText: { color: "#7dd3fc", fontSize: 13, fontWeight: "600" },

  questionText: {
    color: "#f5f5f5",
    fontSize: 20,
    fontWeight: "600",
    lineHeight: 28,
    marginBottom: 24,
  },

  input: {
    backgroundColor: "#111111",
    color: "#f5f5f5",
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    minHeight: 140,
    borderWidth: 1,
    borderColor: "#2a2a2a",
    marginBottom: 16,
  },

  button: {
    backgroundColor: "#2563eb",
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: "center",
  },
  buttonDisabled: { opacity: 0.4 },
  buttonText: { color: "#fff", fontSize: 16, fontWeight: "700" },

  scoreRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 16,
  },
  scoreLabel: { color: "#a3a3a3", fontSize: 16 },
  scoreValue: { color: "#22d3ee", fontSize: 28, fontWeight: "700" },

  feedbackCard: {
    backgroundColor: "#111111",
    borderRadius: 12,
    padding: 16,
    marginBottom: 24,
    borderWidth: 1,
    borderColor: "#2a2a2a",
  },
  feedbackText: { color: "#e5e5e5", fontSize: 15, lineHeight: 22 },

  emptyText: { color: "#f5f5f5", fontSize: 18, fontWeight: "600" },
  emptySubtext: { color: "#a3a3a3", fontSize: 14, marginTop: 8 },

  errorText: { color: "#f87171", fontSize: 18, fontWeight: "600" },
  errorDetail: {
    color: "#a3a3a3",
    fontSize: 13,
    marginTop: 8,
    marginBottom: 20,
    textAlign: "center",
  },
});

const mdStyles = StyleSheet.create({
  body: { color: "#e5e5e5", fontSize: 15, lineHeight: 22 },
  heading1: { color: "#f5f5f5", fontSize: 22, fontWeight: "700", marginBottom: 8 },
  heading2: { color: "#f5f5f5", fontSize: 19, fontWeight: "700", marginBottom: 6 },
  heading3: { color: "#f5f5f5", fontSize: 17, fontWeight: "600", marginBottom: 4 },
  strong: { color: "#f5f5f5", fontWeight: "700" },
  em: { color: "#d4d4d4", fontStyle: "italic" },
  bullet_list: { marginVertical: 4 },
  ordered_list: { marginVertical: 4 },
  list_item: { marginVertical: 2 },
  code_inline: {
    backgroundColor: "#2a2a2a",
    color: "#7dd3fc",
    fontFamily: Platform.OS === "ios" ? "Menlo" : "monospace",
    fontSize: 13,
    paddingHorizontal: 5,
    paddingVertical: 1,
    borderRadius: 4,
  },
  fence: {
    backgroundColor: "#111111",
    borderColor: "#525252",
    borderWidth: 1,
    borderRadius: 8,
    padding: 12,
    marginVertical: 8,
  },
  code_block: {
    color: "#e5e5e5",
    fontFamily: Platform.OS === "ios" ? "Menlo" : "monospace",
    fontSize: 13,
    lineHeight: 20,
  },
});
