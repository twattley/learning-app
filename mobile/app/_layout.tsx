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
          headerStyle: { backgroundColor: "#111111" },
          headerTintColor: "#fafafa",
        }}
      />
    </Stack>
  );
}
