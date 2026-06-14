import { createBottomTabNavigator } from '@react-navigation/bottom-tabs'
import { createNativeStackNavigator } from '@react-navigation/native-stack'
import { Ionicons } from '@expo/vector-icons'
import LearnScreen from '../features/learn/screens/LearnScreen'
import QuestionsScreen from '../features/questions/screens/QuestionsScreen'
import QuestionFormScreen from '../features/questions/screens/QuestionFormScreen'
import SettingsScreen from '../features/settings/screens/SettingsScreen'

export type RootStackParamList = {
  Tabs: undefined
  QuestionForm: { id?: string }
}

type TabParamList = {
  Learn: undefined
  Questions: undefined
  Settings: undefined
}

const Tab = createBottomTabNavigator<TabParamList>()
const Stack = createNativeStackNavigator<RootStackParamList>()

function TabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={{
        tabBarActiveTintColor: '#2563eb',
        tabBarInactiveTintColor: '#a3a3a3',
        tabBarStyle: { paddingBottom: 4 },
        headerStyle: { backgroundColor: '#111111' },
        headerTintColor: '#fafafa',
        headerTitleStyle: { fontWeight: '700' },
      }}
    >
      <Tab.Screen
        name="Learn"
        component={LearnScreen}
        options={{
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="school" size={size} color={color} />
          ),
        }}
      />
      <Tab.Screen
        name="Questions"
        component={QuestionsScreen}
        options={{
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="list" size={size} color={color} />
          ),
        }}
      />
      <Tab.Screen
        name="Settings"
        component={SettingsScreen}
        options={{
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="settings" size={size} color={color} />
          ),
        }}
      />
    </Tab.Navigator>
  )
}

export default function RootNavigator() {
  return (
    <Stack.Navigator>
      <Stack.Screen name="Tabs" component={TabNavigator} options={{ headerShown: false }} />
      <Stack.Screen
        name="QuestionForm"
        component={QuestionFormScreen}
        options={{
          title: 'Question',
          presentation: 'modal',
          headerStyle: { backgroundColor: '#111111' },
          headerTintColor: '#fafafa',
        }}
      />
    </Stack.Navigator>
  )
}
