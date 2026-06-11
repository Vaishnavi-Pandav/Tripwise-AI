import { Routes, Route } from "react-router-dom";
import Home from "../pages/Home";
import Results from "../pages/Results";
import Login from "../pages/Login";
import Signup from "../pages/Signup";
import Profile from "../pages/Profile";

const AppRoutes = () => {
    return (
        <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/results" element={<Results />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/profile" element={<Profile />} />
        </Routes>
    );
};

export default AppRoutes;