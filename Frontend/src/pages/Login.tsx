import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Mail, Lock, Eye, EyeOff, ArrowLeft, Plane } from 'lucide-react';

const Login = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Frontend validation only
    if (!email || !password) {
      alert("Please fill in all fields");
      return;
    }
    console.log("Login attempted for", email);
  };

  return (
    <div className="min-h-screen relative flex items-center justify-center overflow-hidden bg-[#020817]">
      {/* Full-screen Background Image */}
      <div className="absolute inset-0 z-0">
        <img 
          src="/switzerland.png" 
          alt="Switzerland Background" 
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-[#020817]/60 backdrop-blur-[2px]"></div>
      </div>

      {/* Back to Home Link */}
      <Link 
        to="/" 
        className="absolute top-8 left-8 z-20 flex items-center gap-2 text-white/70 hover:text-white transition-colors"
      >
        <ArrowLeft size={20} />
        <span className="font-medium">Back to Home</span>
      </Link>

      {/* Login Card */}
      <motion.div 
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.25, 0.4, 0.25, 1] }}
        className="relative z-10 w-full max-w-md mx-4"
      >
        <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-3xl p-8 shadow-2xl overflow-hidden relative">
          
          {/* Decorative gradients */}
          <div className="absolute -top-24 -right-24 w-48 h-48 bg-emerald-500/20 rounded-full blur-3xl"></div>
          <div className="absolute -bottom-24 -left-24 w-48 h-48 bg-blue-500/20 rounded-full blur-3xl"></div>

          <div className="relative z-20">
            {/* Logo */}
            <div className="flex justify-center mb-8">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-sky-500 flex items-center justify-center shadow-lg shadow-emerald-500/20">
                <Plane size={24} className="text-white" />
              </div>
            </div>

            {/* Headers */}
            <div className="text-center mb-8">
              <h1 className="text-3xl font-playfair font-bold text-white mb-2">Welcome Back</h1>
              <p className="text-white/60 text-sm">Sign in to continue your journey</p>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-5">
              
              {/* Email Field */}
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-white/80 ml-1">Email Address</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Mail size={18} className="text-white/40" />
                  </div>
                  <input 
                    type="email" 
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full bg-white/5 border border-white/10 text-white rounded-xl py-3 pl-11 pr-4 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 transition-all placeholder:text-white/30"
                    placeholder="you@example.com"
                    required
                  />
                </div>
              </div>

              {/* Password Field */}
              <div className="space-y-1.5">
                <div className="flex justify-between items-center ml-1">
                  <label className="text-sm font-medium text-white/80">Password</label>
                  <a href="#" className="text-xs text-emerald-400 hover:text-emerald-300 transition-colors">Forgot password?</a>
                </div>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Lock size={18} className="text-white/40" />
                  </div>
                  <input 
                    type={showPassword ? 'text' : 'password'} 
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full bg-white/5 border border-white/10 text-white rounded-xl py-3 pl-11 pr-12 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 transition-all placeholder:text-white/30"
                    placeholder="••••••••"
                    required
                  />
                  <button 
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-4 flex items-center text-white/40 hover:text-white/70 transition-colors"
                  >
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
              </div>

              {/* Remember Me */}
              <div className="flex items-center gap-2 ml-1">
                <input 
                  type="checkbox" 
                  id="remember" 
                  className="w-4 h-4 rounded border-white/20 bg-white/5 text-emerald-500 focus:ring-emerald-500/50 focus:ring-offset-0 cursor-pointer"
                />
                <label htmlFor="remember" className="text-sm text-white/60 cursor-pointer">Remember me for 30 days</label>
              </div>

              {/* Submit Button */}
              <button 
                type="submit"
                className="w-full py-3.5 mt-2 rounded-xl bg-gradient-to-r from-emerald-500 to-sky-500 text-white font-semibold shadow-lg shadow-emerald-500/25 hover:shadow-emerald-500/40 active:scale-[0.98] transition-all"
              >
                Sign In
              </button>
            </form>

            {/* Divider */}
            <div className="flex items-center gap-4 my-6">
              <div className="h-px flex-1 bg-white/10"></div>
              <span className="text-xs text-white/40 font-medium uppercase tracking-wider">Or continue with</span>
              <div className="h-px flex-1 bg-white/10"></div>
            </div>

            {/* Google Login */}
            <button 
              type="button"
              className="w-full py-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-white font-medium flex items-center justify-center gap-3 transition-colors active:scale-[0.98]"
            >
              <svg viewBox="0 0 24 24" width="20" height="20" xmlns="http://www.w3.org/2000/svg">
                <g transform="matrix(1, 0, 0, 1, 27.009001, -39.238998)">
                  <path fill="#4285F4" d="M -3.264 51.509 C -3.264 50.719 -3.334 49.969 -3.454 49.239 L -14.754 49.239 L -14.754 53.749 L -8.284 53.749 C -8.574 55.229 -9.424 56.479 -10.684 57.329 L -10.684 60.329 L -6.824 60.329 C -4.564 58.239 -3.264 55.159 -3.264 51.509 Z"/>
                  <path fill="#34A853" d="M -14.754 63.239 C -11.514 63.239 -8.804 62.159 -6.824 60.329 L -10.684 57.329 C -11.764 58.049 -13.134 58.489 -14.754 58.489 C -17.884 58.489 -20.534 56.379 -21.484 53.529 L -25.464 53.529 L -25.464 56.619 C -23.494 60.539 -19.444 63.239 -14.754 63.239 Z"/>
                  <path fill="#FBBC05" d="M -21.484 53.529 C -21.734 52.809 -21.864 52.039 -21.864 51.239 C -21.864 50.439 -21.724 49.669 -21.484 48.949 L -21.484 45.859 L -25.464 45.859 C -26.284 47.479 -26.754 49.299 -26.754 51.239 C -26.754 53.179 -26.284 54.999 -25.464 56.619 L -21.484 53.529 Z"/>
                  <path fill="#EA4335" d="M -14.754 43.989 C -12.984 43.989 -11.404 44.599 -10.154 45.789 L -6.734 42.369 C -8.804 40.429 -11.514 39.239 -14.754 39.239 C -19.444 39.239 -23.494 41.939 -25.464 45.859 L -21.484 48.949 C -20.534 46.099 -17.884 43.989 -14.754 43.989 Z"/>
                </g>
              </svg>
              Continue with Google
            </button>

            {/* Footer */}
            <p className="mt-8 text-center text-sm text-white/60">
              Don't have an account?{' '}
              <Link to="/signup" className="text-emerald-400 hover:text-emerald-300 font-medium transition-colors">
                Sign up
              </Link>
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default Login;
