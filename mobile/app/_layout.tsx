import { Stack } from "expo-router";

export default function RootLayout() {
  return (
    <Stack>
      <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
      <Stack.Screen
        name="question-form"
        options={{
          title: "Question",
          presentation: "modal",
          headerStyle: { backgroundColor: "#1e293b" },
          headerTintColor: "#f8fafc",
        }}
      />
    </Stack>
  );
}
