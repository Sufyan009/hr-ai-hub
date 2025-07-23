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
import JobsPage from './pages/JobsPage';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import VerifyEmail from './pages/VerifyEmail';
import Register from './pages/Register';

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        {/* Add skip link at the top of the app */}
        <a href="#main-content" className="sr-only focus:not-sr-only absolute top-2 left-2 z-50 bg-primary text-white px-4 py-2 rounded shadow transition-all">Skip to main content</a>
        {/* Add ARIA live region for toasts/notifications */}
        <div id="aria-live-toast" aria-live="polite" aria-atomic="true" className="sr-only" />
        <BrowserRouter>
          <Routes>
            {/* Public route */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password/:uid/:token" element={<ResetPassword />} />
            <Route path="/verify-email/:uid/:token" element={<VerifyEmail />} />
            
            {/* Protected routes */}
            <Route element={<PrivateRoute />}>
              <Route path="/" element={<AppLayout children={<Dashboard />} />} />
              <Route path="/candidates" element={<AppLayout children={<CandidateList />} />} />
              <Route path="/candidates/new" element={<AppLayout children={<AddCandidate />} />} />
              <Route path="/candidates/:id" element={<AppLayout children={<CandidateDetail />} />} />
              <Route path="/candidates/:id/edit" element={<AppLayout children={<EditCandidate />} />} />
              <Route path="/chat" element={<AppLayout children={<ChatPage />} />} />
              <Route path="/settings" element={<AppLayout children={<Settings />} />} />
              <Route path="/jobs" element={<AppLayout children={<JobsPage />} />} />
              <Route path="/jobs/*" element={<AppLayout children={<NotFound />} />} />
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
