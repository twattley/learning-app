# apps/mobile — Expo Mobile App

iOS/Android learning app built with Expo 54 + React Native.

## Stack

| Component | Technology |
|---|---|
| Build/run | Expo 54 |
| Framework | React Native 0.81 |
| Navigation | React Navigation v7 (bottom tabs + native stack) |
| Server state | TanStack Query v5 |
| Markdown | react-native-markdown-display |
| Package manager | npm (workspace: @recall/mobile) |

## Source layout

```
App.tsx          — root: NavigationContainer + QueryClientProvider
index.ts         — Expo entry (registerRootComponent)
src/
  api/
    config.ts    — AsyncStorage URL management + testApiConnection
    client.ts    — apiFetch, apiPost, apiPut, apiDelete
    queryClient.ts — singleton QueryClient
  navigation/
    index.tsx    — RootNavigator (Stack → Tabs + QuestionForm modal)
  features/
    learn/screens/LearnScreen.tsx         — review flow
    questions/screens/QuestionsScreen.tsx — question list
    questions/screens/QuestionFormScreen.tsx — create/edit
    settings/screens/SettingsScreen.tsx   — API URL + LLM mode
```

## Commands

```bash
# From repo root:
make mobile       # Start Expo (scan QR with Expo Go)

# Direct:
cd apps/mobile
npx expo start
npx expo start --ios
npx expo start --android
```

## API URL configuration

The app stores the backend URL in AsyncStorage (configurable from the Settings tab).
Default: `http://server:8003/api/v1`

When running on a physical device, use your Tailscale hostname instead of `localhost`.

## Navigation structure

```
RootStack
├── Tabs (bottom tab navigator)
│   ├── Learn
│   ├── Questions
│   └── Settings
└── QuestionForm (modal — launched from Questions)
```

## Shared types

Types are imported from `@recall/domain-types` (workspace package).
Both web and mobile share the same TypeScript interfaces.
