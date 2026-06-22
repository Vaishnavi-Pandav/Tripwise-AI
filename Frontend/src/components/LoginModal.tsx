import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Plane, Mail, Lock, Eye, EyeOff, ArrowRight, User, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
  redirectTo?: string;
}

const GoogleIcon = () => (
  <svg viewBox="0 0 24 24" width="20" height="20" xmlns="http://www.w3.org/2000/svg">
    <g transform="matrix(1, 0, 0, 1, 27.009001, -39.238998)">
      <path fill="#4285F4" d="M -3.264 51.509 C -3.264 50.719 -3.334 49.969 -3.454 49.239 L -14.754 49.239 L -14.754 53.749 L -8.284 53.749 C -8.574 55.229 -9.424 56.479 -10.684 57.329 L -10.684 60.329 L -6.824 60.329 C -4.564 58.239 -3.264 55.159 -3.264 51.509 Z"/>
      <path fill="#34A853" d="M -14.754 63.239 C -11.514 63.239 -8.804 62.159 -6.824 60.329 L -10.684 57.329 C -11.764 58.049 -13.134 58.489 -14.754 58.489 C -17.884 58.489 -20.534 56.379 -21.484 53.529 L -25.464 53.529 L -25.464 56.619 C -23.494 60.539 -19.444 63.239 -14.754 63.239 Z"/>
      <path fill="#FBBC05" d="M -21.484 53.529 C -21.734 52.809 -21.864 52.039 -21.864 51.239 C -21.864 50.439 -21.724 49.669 -21.484 48.949 L -21.484 45.859 L -25.464 45.859 C -26.284 47.479 -26.754 49.299 -26.754 51.239 C -26.754 53.179 -26.284 54.999 -25.464 56.619 L -21.484 53.529 Z"/>
      <path fill="#EA4335" d="M -14.754 43.989 C -12.984 43.989 -11.404 44.599 -10.154 45.789 L -6.734 42.369 C -8.804 40.429 -11.514 39.239 -14.754 39.239 C -19.444 39.239 -23.494 41.939 -25.464 45.859 L -21.484 48.949 C -20.534 46.099 -17.884 43.989 -14.754 43.989 Z"/>
    </g>
  </svg>
);

export default function LoginModal({ isOpen, onClose, redirectTo = '/dashboard' }: LoginModalProps) {
  const { signInWithGoogle, signInWithEmail, signUpWithEmail } = useAuth();
  const navigate = useNavigate();

  const [tab, setTab]               = useState<'login' | 'signup'>('login');
  const [name, setName]             = useState('');
  const [email, setEmail]           = useState('');
  const [password, setPassword]     = useState('');
  const [showPassword, setShow]     = useState(false);
  const [loading, setLoading]       = useState(false);
  const [googleLoading, setGoogle]  = useState(false);
  const [error, setError]           = useState('');

  const resetForm = () => { setName(''); setEmail(''); setPassword(''); setError(''); };

  const handleGoogle = async () => {
    setError(''); setGoogle(true);
    try {
      await signInWithGoogle();
      onClose(); resetForm();
      navigate(redirectTo);
    } catch {
      setError('Google sign-in failed. Please try again.');
    } finally {
      setGoogle(false);
    }
  };

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(''); setLoading(true);
    try {
      if (tab === 'login') {
        await signInWithEmail(email, password);
      } else {
        if (!name.trim()) { setError('Name is required'); setLoading(false); return; }
        await signUpWithEmail(name, email, password);
      }
      onClose(); resetForm();
      navigate(redirectTo);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : '';
      if (msg.includes('wrong-password') || msg.includes('user-not-found') || msg.includes('invalid-credential'))
        setError('Invalid email or password');
      else if (msg.includes('email-already-in-use'))
        setError('Email already registered — try logging in');
      else if (msg.includes('weak-password'))
        setError('Password must be at least 6 characters');
      else
        setError(tab === 'login' ? 'Login failed. Please try again.' : 'Signup failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div key="backdrop" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            onClick={onClose} className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm" />

          {/* Modal */}
          <motion.div key="modal"
            initial={{ opacity: 0, scale: 0.95, y: 20 }} animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }} transition={{ duration: 0.25 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
            <div className="w-full max-w-md pointer-events-auto rounded-3xl overflow-hidden relative"
              style={{ background: 'rgba(2,8,23,0.97)', border: '1px solid rgba(255,255,255,0.1)', boxShadow: '0 40px 100px rgba(0,0,0,0.6)' }}>

              {/* Orbs */}
              <div className="absolute -top-20 -right-20 w-40 h-40 rounded-full pointer-events-none"
                style={{ background: 'radial-gradient(circle, rgba(16,185,129,0.2), transparent)' }} />
              <div className="absolute -bottom-20 -left-20 w-40 h-40 rounded-full pointer-events-none"
                style={{ background: 'radial-gradient(circle, rgba(14,165,233,0.15), transparent)' }} />

              <div className="relative z-10 p-8">
                {/* Close */}
                <button onClick={onClose} className="absolute top-5 right-5 w-8 h-8 rounded-full flex items-center justify-center"
                  style={{ background: 'rgba(255,255,255,0.08)' }}>
                  <X size={16} className="text-white/70" />
                </button>

                {/* Logo */}
                <div className="flex justify-center mb-5">
                  <div className="w-12 h-12 rounded-xl flex items-center justify-center"
                    style={{ background: 'linear-gradient(135deg,#10b981,#0ea5e9)' }}>
                    <Plane size={22} className="text-white" />
                  </div>
                </div>

                {/* Tabs */}
                <div className="flex rounded-xl p-1 mb-5" style={{ background: 'rgba(255,255,255,0.06)' }}>
                  {(['login','signup'] as const).map(t => (
                    <button key={t} onClick={() => { setTab(t); setError(''); }}
                      className="flex-1 py-2 rounded-lg text-sm font-medium transition-all capitalize"
                      style={{ background: tab === t ? 'rgba(255,255,255,0.1)' : 'transparent',
                               color: tab === t ? 'white' : 'rgba(255,255,255,0.5)' }}>
                      {t === 'login' ? 'Log In' : 'Sign Up'}
                    </button>
                  ))}
                </div>

                <h2 className="text-xl font-bold text-white text-center mb-1">
                  {tab === 'login' ? 'Welcome back' : 'Create your account'}
                </h2>
                <p className="text-white/50 text-sm text-center mb-5">
                  {tab === 'login' ? 'Sign in to plan your next trip' : 'Join 50,000+ travelers on TripWise AI'}
                </p>

                {/* Google */}
                <button onClick={handleGoogle} disabled={googleLoading}
                  className="w-full py-3 rounded-xl font-medium flex items-center justify-center gap-3 transition-all mb-4 disabled:opacity-60"
                  style={{ background: 'white', color: '#1f2937' }}>
                  {googleLoading
                    ? <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="#1f2937" strokeWidth="4"/><path className="opacity-75" fill="#1f2937" d="M4 12a8 8 0 018-8v8z"/></svg>
                    : <GoogleIcon />}
                  {googleLoading ? 'Signing in…' : 'Continue with Google'}
                </button>

                {/* Divider */}
                <div className="flex items-center gap-3 mb-4">
                  <div className="h-px flex-1" style={{ background: 'rgba(255,255,255,0.1)' }} />
                  <span className="text-xs text-white/30 uppercase tracking-wider">or</span>
                  <div className="h-px flex-1" style={{ background: 'rgba(255,255,255,0.1)' }} />
                </div>

                {/* Error */}
                {error && (
                  <div className="flex items-center gap-2 p-3 rounded-xl mb-4 text-xs"
                    style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.25)' }}>
                    <AlertCircle size={14} className="text-red-400 flex-shrink-0" />
                    <p className="text-red-300">{error}</p>
                  </div>
                )}

                {/* Email form */}
                <form onSubmit={handleEmailSubmit} className="space-y-3">
                  {tab === 'signup' && (
                    <div className="relative">
                      <User size={15} className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40" />
                      <input type="text" placeholder="Full Name" value={name} onChange={e => setName(e.target.value)}
                        required className="w-full px-4 py-3 pl-10 rounded-xl text-sm text-white placeholder:text-white/30 outline-none"
                        style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)' }} />
                    </div>
                  )}
                  <div className="relative">
                    <Mail size={15} className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40" />
                    <input type="email" placeholder="Email address" value={email} onChange={e => setEmail(e.target.value)}
                      required className="w-full px-4 py-3 pl-10 rounded-xl text-sm text-white placeholder:text-white/30 outline-none"
                      style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)' }} />
                  </div>
                  <div className="relative">
                    <Lock size={15} className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40" />
                    <input type={showPassword ? 'text' : 'password'} placeholder="Password" value={password}
                      onChange={e => setPassword(e.target.value)} required
                      className="w-full px-4 py-3 pl-10 pr-12 rounded-xl text-sm text-white placeholder:text-white/30 outline-none"
                      style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)' }} />
                    <button type="button" onClick={() => setShow(!showPassword)}
                      className="absolute right-4 top-1/2 -translate-y-1/2 text-white/40 hover:text-white/70">
                      {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
                    </button>
                  </div>

                  <button type="submit" disabled={loading}
                    className="w-full py-3 rounded-xl font-semibold text-white flex items-center justify-center gap-2 transition-all disabled:opacity-60"
                    style={{ background: 'linear-gradient(135deg,#10b981,#0ea5e9)' }}>
                    {loading
                      ? <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/></svg>
                      : null}
                    {loading ? 'Please wait…' : tab === 'login' ? 'Sign In' : 'Create Account'}
                    {!loading && <ArrowRight size={15} />}
                  </button>
                </form>

                <p className="text-center text-xs text-white/40 mt-5">
                  {tab === 'login' ? "Don't have an account? " : 'Already have an account? '}
                  <button onClick={() => { setTab(tab === 'login' ? 'signup' : 'login'); setError(''); }}
                    className="text-emerald-400 hover:text-emerald-300 font-medium">
                    {tab === 'login' ? 'Sign up' : 'Log in'}
                  </button>
                </p>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
