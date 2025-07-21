import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AppLayout } from "./components/layout/AppLayout";
import { AuthProvider } from "./contexts/AuthContext";
import { PrivateRoute } from "./components/PrivateRoute";
import Dashboard from "./pages/Dashboard";
import CandidateList from "./pages/CandidateList";
import AddCandidate from "./pages/AddCandidate";
import CandidateDetail from "./pages/CandidateDetail";
import EditCandidate from "./pages/EditCandidate";
import ChatPage from "./pages/ChatPage";
import Settings from "./pages/Settings";
import NotFound from "./pages/NotFound";
import Login from "./pages/Login";
import AdminDashboard from "./pages/AdminDashboard";
import UserDashboard from "./pages/UserDashboard";
import { RoleRoute } from "./components/RoleRoute";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            {/* Public route */}
            <Route path="/login" element={<Login />} />
            
            {/* Protected routes */}
            <Route element={<PrivateRoute />}>
              <Route path="/" element={<AppLayout children={<Dashboard />} />} />
              <Route path="/candidates" element={<AppLayout children={<CandidateList />} />} />
              <Route path="/candidates/new" element={<AppLayout children={<AddCandidate />} />} />
              <Route path="/candidates/:id" element={<AppLayout children={<CandidateDetail />} />} />
              <Route path="/candidates/:id/edit" element={<AppLayout children={<EditCandidate />} />} />
              <Route path="/chat" element={<AppLayout children={<ChatPage />} />} />
              <Route path="/settings" element={<AppLayout children={<Settings />} />} />
              {/* Role-based dashboards */}
              <Route element={<RoleRoute requiredRole="admin" />}>
                <Route path="/admin" element={<AppLayout children={<AdminDashboard />} />} />
              </Route>
              <Route element={<RoleRoute requiredRole="user" />}>
                <Route path="/user" element={<AppLayout children={<UserDashboard />} />} />
              </Route>
              {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
              <Route path="*" element={<AppLayout children={<NotFound />} />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </AuthProvider>
  </QueryClientProvider>
);

export default App;
