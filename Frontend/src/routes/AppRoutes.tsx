import { Routes, Route, Navigate } from "react-router-dom";
import Home      from "../pages/Home";
import Results   from "../pages/Results";
import Login     from "../pages/Login";
import Signup    from "../pages/Signup";
import Profile   from "../pages/Profile";
import Dashboard from "../pages/Dashboard";
import Chat      from "../pages/Chat";
import Agencies  from "../pages/Agencies";
import ProtectedRoute from "../components/ProtectedRoute";

const AppRoutes = () => {
    return (
        <Routes>
            <Route path="/"          element={<Home />} />
            <Route path="/login"     element={<Login />} />
            <Route path="/signup"    element={<Signup />} />
            <Route path="/agencies"  element={<Agencies />} />
            <Route path="/results"   element={<ProtectedRoute><Results /></ProtectedRoute>} />
            <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/profile"   element={<ProtectedRoute><Profile /></ProtectedRoute>} />
            <Route path="/chat"      element={<ProtectedRoute><Chat /></ProtectedRoute>} />
            <Route path="*"          element={<Navigate to="/" replace />} />
        </Routes>
    );
};

export default AppRoutes;
