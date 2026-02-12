import { useCallback, useState } from "react";
import {
  View,
  Text,
  FlatList,
  Pressable,
  Alert,
  ActivityIndicator,
  StyleSheet,
} from "react-native";
import { useRouter, useFocusEffect } from "expo-router";
import { fetchQuestions, deleteQuestion, type Question } from "../../lib/api";

export default function QuestionsScreen() {
  const router = useRouter();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const data = await fetchQuestions();
      setQuestions(data);
    } catch {
      Alert.alert("Error", "Failed to load questions");
    } finally {
      setLoading(false);
    }
  };

  // Reload whenever the tab comes into focus (catches new/edited questions)
  useFocusEffect(
    useCallback(() => {
      load();
    }, []),
  );

  const handleDelete = (q: Question) => {
    Alert.alert("Delete", `Delete "${q.question_text.slice(0, 40)}…"?`, [
      { text: "Cancel", style: "cancel" },
      {
        text: "Delete",
        style: "destructive",
        onPress: async () => {
          try {
            await deleteQuestion(q.id);
            setQuestions((prev) => prev.filter((x) => x.id !== q.id));
          } catch {
            Alert.alert("Error", "Failed to delete question");
          }
        },
      },
    ]);
  };

  const renderItem = ({ item }: { item: Question }) => (
    <Pressable
      style={styles.card}
      onPress={() =>
        router.push({ pathname: "/question-form", params: { id: item.id } })
      }
      onLongPress={() => handleDelete(item)}
    >
      <View style={styles.cardHeader}>
        <View style={styles.topicBadge}>
          <Text style={styles.topicText}>{item.topic}</Text>
        </View>
        {item.answer_text == null && (
          <Text style={styles.noAnswer}>no answer</Text>
        )}
      </View>
      <Text style={styles.questionText} numberOfLines={3}>
        {item.question_text}
      </Text>
    </Pressable>
  );

  return (
    <View style={styles.container}>
      {loading ? (
        <ActivityIndicator
          size="large"
          color="#2563eb"
          style={{ marginTop: 40 }}
        />
      ) : (
        <FlatList
          data={questions}
          keyExtractor={(q) => q.id}
          renderItem={renderItem}
          contentContainerStyle={styles.list}
          ListEmptyComponent={
            <Text style={styles.emptyText}>
              No questions yet. Tap + to add one.
            </Text>
          }
        />
      )}

      <Pressable
        style={styles.fab}
        onPress={() => router.push("/question-form")}
      >
        <Text style={styles.fabText}>+</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#0f172a" },
  list: { padding: 16, paddingBottom: 100 },

  card: {
    backgroundColor: "#1e293b",
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: "#334155",
  },
  cardHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  topicBadge: {
    backgroundColor: "#1e3a5f",
    paddingHorizontal: 10,
    paddingVertical: 3,
    borderRadius: 10,
  },
  topicText: { color: "#7dd3fc", fontSize: 12, fontWeight: "600" },
  noAnswer: { color: "#64748b", fontSize: 11, fontStyle: "italic" },
  questionText: { color: "#e2e8f0", fontSize: 15, lineHeight: 21 },

  emptyText: {
    color: "#94a3b8",
    textAlign: "center",
    marginTop: 60,
    fontSize: 15,
  },

  fab: {
    position: "absolute",
    bottom: 24,
    right: 24,
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: "#2563eb",
    alignItems: "center",
    justifyContent: "center",
    shadowColor: "#000",
    shadowOpacity: 0.3,
    shadowRadius: 6,
    shadowOffset: { width: 0, height: 3 },
    elevation: 5,
  },
  fabText: { color: "#fff", fontSize: 28, fontWeight: "600", marginTop: -2 },
});
