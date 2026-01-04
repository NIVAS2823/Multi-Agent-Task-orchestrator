import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

export default function AuthModal() {
  const [mode, setMode] = useState('login');
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    fullName: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login, register, loginWithGoogle } = useAuth();

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    let result;
    if (mode === 'login') {
      result = await login(formData.username, formData.password);
    } else {
      if (formData.password.length < 8) {
        setError('Password must be at least 8 characters');
        setLoading(false);
        return;
      }
      result = await register(
        formData.email,
        formData.username,
        formData.password,
        formData.fullName
      );
    }

    setLoading(false);
    if (!result.success) setError(result.error);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 overflow-hidden">
      {/* Neon animated background */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#05010d] via-[#0b0420] to-[#02010a]" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(168,85,247,0.25),transparent_55%)]" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom,_rgba(236,72,153,0.2),transparent_55%)]" />

      {/* Card */}
      <div className="relative w-full max-w-md rounded-2xl border border-white/10 bg-black/50 backdrop-blur-xl shadow-[0_0_60px_rgba(168,85,247,0.25)] animate-fade-in">
        {/* Header */}
        <div className="px-6 pt-6 pb-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 shadow-[0_0_20px_rgba(168,85,247,0.8)] flex items-center justify-center text-white font-extrabold text-lg">
              ⚡
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">
                {mode === 'login' ? 'Welcome Back' : 'Create Account'}
              </h2>
              <p className="text-sm text-gray-400">
                {mode === 'login'
                  ? 'Sign in to your AI workspace'
                  : 'Join the multi-agent future'}
              </p>
            </div>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="px-6 pb-6 space-y-4">
          {error && (
            <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300 shadow-[0_0_15px_rgba(239,68,68,0.3)]">
              {error}
            </div>
          )}

          {mode === 'register' && (
            <Input
              label="Email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleInputChange}
              placeholder="you@domain.com"
            />
          )}

          <Input
            label={`Username ${mode === 'login' ? '(or email)' : ''}`}
            name="username"
            value={formData.username}
            onChange={handleInputChange}
            placeholder="johndoe"
          />

          {mode === 'register' && (
            <Input
              label="Full Name"
              name="fullName"
              value={formData.fullName}
              onChange={handleInputChange}
              placeholder="John Doe"
            />
          )}

          <Input
            label="Password"
            name="password"
            type="password"
            value={formData.password}
            onChange={handleInputChange}
            placeholder="••••••••"
            helper={
              mode === 'register'
                ? 'Minimum 8 characters recommended'
                : null
            }
          />

          {/* Submit */}
          <button
            disabled={loading}
            className="relative w-full overflow-hidden rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 px-4 py-3 font-semibold text-white transition-all hover:scale-[1.02] hover:shadow-[0_0_25px_rgba(168,85,247,0.8)] disabled:opacity-60"
          >
            {loading ? 'Processing…' : mode === 'login' ? 'Sign In' : 'Create Account'}
          </button>

          {/* Divider */}
          <div className="relative py-4">
            <div className="h-px bg-gradient-to-r from-transparent via-gray-700 to-transparent" />
            <span className="absolute inset-x-0 -top-2 mx-auto w-fit bg-black px-3 text-xs text-gray-500">
              OR
            </span>
          </div>

          {/* Google */}
          <button
            type="button"
            onClick={loginWithGoogle}
            className="flex w-full items-center justify-center gap-3 rounded-lg bg-white px-4 py-3 font-semibold text-black transition hover:scale-[1.02] hover:shadow-[0_0_20px_rgba(255,255,255,0.6)]"
          >
            <GoogleIcon />
            Continue with Google
          </button>

          {/* Switch */}
          <div className="pt-4 text-center text-sm text-gray-400">
            <button
              type="button"
              onClick={() => {
                setMode(mode === 'login' ? 'register' : 'login');
                setError('');
                setFormData({ email: '', username: '', password: '', fullName: '' });
              }}
              className="hover:text-white"
            >
              {mode === 'login' ? (
                <>No account? <span className="text-purple-400">Sign up</span></>
              ) : (
                <>Already registered? <span className="text-purple-400">Sign in</span></>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

/* ---------- Reusable Components ---------- */

function Input({ label, helper, ...props }) {
  return (
    <div>
      <label className="mb-1 block text-sm text-gray-300">{label}</label>
      <input
        {...props}
        required
        className="w-full rounded-lg border border-white/10 bg-black/40 px-4 py-3 text-white placeholder-gray-500 outline-none transition focus:border-purple-500 focus:ring-2 focus:ring-purple-500/40"
      />
      {helper && <p className="mt-1 text-xs text-gray-500">{helper}</p>}
    </div>
  );
}

function GoogleIcon() {
  return (
    <svg className="h-5 w-5" viewBox="0 0 24 24">
      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22z"/>
      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
    </svg>
  );
}
