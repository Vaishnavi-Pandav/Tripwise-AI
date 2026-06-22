import { Routes, Route, Navigate } from "react-router-dom";
import Home      from "../pages/Home";
import Results   from "../pages/Results";
import Login     from "../pages/Login";
import Signup    from "../pages/Signup";
import Profile   from "../pages/Profile";
import Dashboard from "../pages/Dashboard";
import ProtectedRoute from "../components/ProtectedRoute";

const AppRoutes = () => {
    return (
        <Routes>
            {/* Public */}
            <Route path="/"        element={<Home />} />
            <Route path="/login"   element={<Login />} />
            <Route path="/signup"  element={<Signup />} />

            {/* Protected */}
            <Route path="/results"   element={<ProtectedRoute><Results /></ProtectedRoute>} />
            <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/profile"   element={<ProtectedRoute><Profile /></ProtectedRoute>} />

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
    );
};

export default AppRoutes;
