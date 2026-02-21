import { useCallback, useState } from "react";
import {
  View,
  Text,
  FlatList,
  Pressable,
  Switch,
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
  const [workOnly, setWorkOnly] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const data = await fetchQuestions(undefined, workOnly ? "work" : undefined);
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
    }, [workOnly]),
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
        {(item.is_work || item.tags?.includes("work")) && (
          <View style={styles.workBadge}>
            <Text style={styles.workText}>work</Text>
          </View>
        )}
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
      <View style={styles.filterRow}>
        <Text style={styles.filterLabel}>Work only</Text>
        <Switch value={workOnly} onValueChange={setWorkOnly} />
      </View>

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
  container: { flex: 1, backgroundColor: "#000000" },
  list: { padding: 16, paddingBottom: 100 },
  filterRow: {
    paddingHorizontal: 16,
    paddingTop: 12,
    paddingBottom: 4,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  filterLabel: {
    color: "#d4d4d4",
    fontSize: 14,
    fontWeight: "600",
  },

  card: {
    backgroundColor: "#111111",
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: "#2a2a2a",
  },
  cardHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  topicBadge: {
    backgroundColor: "#1a1a2e",
    paddingHorizontal: 10,
    paddingVertical: 3,
    borderRadius: 10,
  },
  topicText: { color: "#7dd3fc", fontSize: 12, fontWeight: "600" },
  workBadge: {
    backgroundColor: "#1e3a8a",
    paddingHorizontal: 10,
    paddingVertical: 3,
    borderRadius: 10,
    marginLeft: 8,
  },
  workText: { color: "#dbeafe", fontSize: 11, fontWeight: "600" },
  noAnswer: { color: "#737373", fontSize: 11, fontStyle: "italic" },
  questionText: { color: "#e5e5e5", fontSize: 15, lineHeight: 21 },

  emptyText: {
    color: "#a3a3a3",
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
