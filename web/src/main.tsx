import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import App from "./App";
import Learn from "./pages/Learn";
import Questions from "./pages/Questions";
import QuestionForm from "./pages/QuestionForm";
import "./index.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route element={<App />}>
          <Route index element={<Learn />} />
          <Route path="questions" element={<Questions />} />
          <Route path="questions/new" element={<QuestionForm />} />
          <Route path="questions/:id/edit" element={<QuestionForm />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </StrictMode>
);
