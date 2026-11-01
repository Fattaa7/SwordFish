import React, { useState } from 'react';
import { apiClient, isDemoMode } from '../../api/client';
import { User } from '../../types';

interface AuthViewProps {
  onLoginSuccess: (user: User, token: string) => void;
}

export const AuthView: React.FC<AuthViewProps> = ({ onLoginSuccess }) => {
  const [isRegistering, setIsRegistering] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (isRegistering) {
        await apiClient.register(email, password);
      }
      const { token, user } = await apiClient.login(email, password);
      localStorage.setItem('sf_token', token.access_token);
      localStorage.setItem('sf_user', JSON.stringify(user));
      onLoginSuccess(user, token.access_token);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Authentication failed';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleContinue = async () => {
    setError(null);
    if (!isDemoMode()) {
      window.location.href = apiClient.getGoogleLoginUrl(email);
      return;
    }
    setLoading(true);
    try {
      const { token, user } = await apiClient.login('ahmed1999fattah@gmail.com', 'password123');
      localStorage.setItem('sf_token', token.access_token);
      localStorage.setItem('sf_user', JSON.stringify(user));
      onLoginSuccess(user, token.access_token);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full bg-[#F8FAFC] dark:bg-slate-950 flex items-center justify-center p-4">
      <div className="w-full max-w-[400px] bg-white dark:bg-slate-900 rounded-xl shadow-[0_10px_40px_rgba(15,23,42,0.07)] border border-slate-100 dark:border-slate-800 px-8 py-9 transition-all">
        <div className="text-center mb-6">
          <h1 className="text-[26px] font-bold text-slate-900 dark:text-white tracking-tight">
            {isRegistering ? 'Create Account' : 'Sign In'}
          </h1>
          <p className="text-[13px] text-slate-500 dark:text-slate-400 mt-1.5">
            {isRegistering
              ? 'Sign up to start querying your documents with SwordFish AI.'
              : 'Welcome back! Please sign in to your account.'}
          </p>
        </div>

        {error && (
          <div className="mb-4 rounded-lg bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800/60 px-3.5 py-2.5 text-xs text-red-600 dark:text-red-300">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-[13px] font-medium text-slate-800 dark:text-slate-200 mb-1.5">
              Email <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your username"
              className="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-3.5 py-2.5 text-[13px] text-slate-800 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 transition-all"
            />
          </div>

          <div>
            <label className="block text-[13px] font-medium text-slate-800 dark:text-slate-200 mb-1.5">
              Password <span className="text-red-500">*</span>
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              className="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-3.5 py-2.5 text-[13px] text-slate-800 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 transition-all"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 bg-[#3762F0] hover:bg-blue-600 active:bg-blue-700 text-white font-medium py-2.5 rounded-lg text-[13px] shadow-sm transition-all disabled:opacity-60 cursor-pointer"
          >
            {loading ? 'Signing in...' : isRegistering ? 'Sign Up' : 'Sign In'}
          </button>
        </form>

        <div className="relative my-5 flex items-center justify-center">
          <div className="border-t border-slate-100 dark:border-slate-800 w-full" />
          <span className="bg-white dark:bg-slate-900 px-3 text-[11px] text-slate-400 whitespace-nowrap">
            Or continue with
          </span>
          <div className="border-t border-slate-100 dark:border-slate-800 w-full" />
        </div>

        <button
          type="button"
          onClick={handleGoogleContinue}
          className="w-full border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700/60 text-slate-800 dark:text-slate-100 font-medium py-2.5 rounded-lg text-[13px] transition-all flex items-center justify-center gap-2 cursor-pointer"
        >
          <span>Continue with Google</span>
        </button>

        <p className="text-center text-[12px] text-slate-500 dark:text-slate-400 mt-5">
          {isRegistering ? 'Already have an account? ' : "Don't have an account? "}
          <button
            type="button"
            onClick={() => setIsRegistering(!isRegistering)}
            className="text-[#3762F0] hover:underline font-medium cursor-pointer"
          >
            {isRegistering ? 'Sign in here' : 'Sign up here'}
          </button>
        </p>
      </div>
    </div>
  );
};
