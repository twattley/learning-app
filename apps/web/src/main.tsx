import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import App from "./App";
import LearnPage from "./features/learn/LearnPage";
import QuestionsPage from "./features/questions/QuestionsPage";
import QuestionFormPage from "./features/questions/QuestionFormPage";
import { ApiProvider } from "./api/ApiProvider";
import "./index.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ApiProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<App />}>
            <Route index element={<LearnPage />} />
            <Route path="questions" element={<QuestionsPage />} />
            <Route path="questions/new" element={<QuestionFormPage />} />
            <Route path="questions/:id/edit" element={<QuestionFormPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ApiProvider>
  </StrictMode>
);
