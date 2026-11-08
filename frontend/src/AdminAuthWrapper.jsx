import React, { useState, useEffect, useContext } from 'react';
import { verifyAdminPassword } from './api';
import { ReceptionistContext } from './App';

const AdminAuthWrapper = ({ children }) => {
  const { activeReceptionist, setActiveReceptionist } = useContext(ReceptionistContext);
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  
  const isAuthenticated = activeReceptionist === 'admin';

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!password) return;
    try {
      setError('');
      await verifyAdminPassword(password);
      sessionStorage.setItem('adminAuthenticated', 'true');
      setActiveReceptionist('admin');
    } catch (err) {
      setError(err.response?.data?.detail || 'كلمة المرور غير صحيحة');
    }
  };

  return (
    <div className="relative w-full h-full min-h-screen">
      <div className={isAuthenticated ? '' : 'blur-md pointer-events-none select-none'}>
        {children}
      </div>

      {!isAuthenticated && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/20 backdrop-blur-sm">
          <div className="bg-white p-8 rounded-2xl shadow-2xl w-full max-w-sm mx-4 animate-in fade-in zoom-in duration-300">
            <div className="flex flex-col items-center mb-6">
              <div className="w-12 h-12 bg-rose-100 text-rose-600 rounded-full flex items-center justify-center mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <h2 className="text-xl font-bold text-gray-900">الوصول مقيد</h2>
              <p className="text-sm text-gray-500 mt-1">الرجاء إدخال كلمة المرور للمتابعة</p>
            </div>

            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="كلمة المرور"
                  className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-center text-black placeholder-gray-400 focus:outline-none focus:border-black/50 focus:ring-2 focus:ring-black/10 transition-all"
                  autoFocus
                />
              </div>
              {error && <p className="text-sm text-rose-600 text-center">{error}</p>}
              <button
                type="submit"
                className="w-full bg-black text-white rounded-xl py-3 font-semibold hover:bg-gray-800 transition-colors"
              >
                دخول
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminAuthWrapper;
