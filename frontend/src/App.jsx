import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./AuthContext";
import Layout from "./Layout";
import ProtectedRoute from "./ProtectedRoute";
import Home from "./pages/Home";
import SubmitSheet from "./pages/SubmitSheet";
import Result from "./pages/Result";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import CreateTest from "./pages/CreateTest";
import TestDetails from "./pages/TestDetails";
import TestResults from "./pages/TestResults";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Home />} />
            <Route path="/submit" element={<SubmitSheet />} />
            <Route path="/results/:submissionId" element={<Result />} />
            <Route path="/teacher/login" element={<Login />} />
            <Route path="/teacher/register" element={<Register />} />
            <Route element={<ProtectedRoute />}>
              <Route path="/teacher" element={<Dashboard />} />
              <Route path="/teacher/tests/new" element={<CreateTest />} />
              <Route path="/teacher/tests/:testId" element={<TestDetails />} />
              <Route path="/teacher/tests/:testId/results" element={<TestResults />} />
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
