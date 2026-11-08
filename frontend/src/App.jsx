import React, { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import { Dumbbell, Users, LayoutDashboard, UserPlus, Database, UserCircle } from 'lucide-react';
import Reception from './Reception';
import Onboarding from './Onboarding';
import Dashboard from './Dashboard';
import AdminAuthWrapper from './AdminAuthWrapper';
import Members from './Members';
import MemberDetail from './MemberDetail';
import { listReceptionists, getMockTime, setMockTime } from './api';
import { format } from 'date-fns';

export const ReceptionistContext = createContext({
  activeReceptionist: null,
  setActiveReceptionist: () => {},
  receptionists: [],
  refreshReceptionists: () => {}
});

export const ServerTimeContext = createContext(new Date());
export const MockTimeEnabledContext = createContext(true);

const GlobalTimeBar = () => {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState('');

  const handleSave = async () => {
    try {
      if (!editValue) return;
      // editValue is a datetime-local string like "2023-10-15T14:30"
      // Convert it to ISO
      const isoString = new Date(editValue).toISOString();
      await setMockTime(isoString);
      setIsEditing(false);
      // Reload the page to reflect time across all components easily
      window.location.reload();
    } catch (e) {
      console.error(e);
    }
  };

  const currentTime = useContext(ServerTimeContext);
  const mockEnabled = useContext(MockTimeEnabledContext);
  if (!currentTime || !mockEnabled) return null;

  return (
    <div className="fixed top-0 start-0 end-0 h-12 bg-black text-white z-[100] flex items-center justify-center gap-4 text-sm shadow-md">
      <span className="font-semibold text-cyan-400">الوقت الوهمي:</span>
      {!isEditing ? (
        <>
          <span>{format(currentTime, 'PPpp')}</span>
          <button 
            onClick={() => {
              setEditValue(format(currentTime, "yyyy-MM-dd'T'HH:mm"));
              setIsEditing(true);
            }} 
            className="px-3 py-1 bg-white/10 hover:bg-white/20 rounded transition-colors"
          >تعديل</button>
        </>
      ) : (
        <div className="flex items-center gap-2 text-black">
          <input 
            type="datetime-local" 
            value={editValue} 
            onChange={(e) => setEditValue(e.target.value)}
            className="px-2 py-1 rounded outline-none"
          />
          <button onClick={handleSave} className="px-3 py-1 bg-emerald-500 text-white rounded hover:bg-emerald-600 transition-colors">حفظ</button>
          <button onClick={() => setIsEditing(false)} className="px-3 py-1 bg-rose-500 text-white rounded hover:bg-rose-600 transition-colors">إلغاء</button>
        </div>
      )}
    </div>
  );
};

const Navigation = () => {
  const location = useLocation();
  const navItems = [
    { path: '/', label: 'الاستقبال', icon: Dumbbell },
    { path: '/onboarding', label: 'تسجيل جديد', icon: UserPlus },
    { path: '/members', label: 'الأعضاء', icon: Database },
    { path: '/dashboard', label: 'لوحة التحكم', icon: LayoutDashboard },
  ];

  return (
    <nav className="fixed top-12 start-0 h-[calc(100vh-3rem)] w-20 bg-white border-e border-gray-200 flex flex-col items-center py-8 z-50">
      <div className="w-12 h-12 bg-black text-white rounded-xl flex items-center justify-center mb-12 shadow-lg shadow-gray-500/20">
        <Dumbbell className="text-white w-7 h-7" />
      </div>
      <div className="flex flex-col gap-6">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path || 
            (item.path === '/members' && location.pathname.startsWith('/members'));
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`p-3 rounded-xl transition-all duration-300 relative group ${
                isActive ? 'bg-black text-white shadow-lg' : 'bg-white text-black hover:bg-gray-100'
              }`}
            >
              <Icon className="w-6 h-6" />
              <div className="absolute start-full ms-4 px-2 py-1 bg-gray-200 text-gray-900 text-sm rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all whitespace-nowrap z-50 pointer-events-none border border-gray-300">
                {item.label}
              </div>
            </Link>
          );
        })}
      </div>
    </nav>
  );
};

const MembersPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const selectedMemberId = searchParams.get('id');

  if (selectedMemberId) {
    return (
      <MemberDetail
        memberId={parseInt(selectedMemberId)}
        onBack={() => {
          setSearchParams({});
        }}
      />
    );
  }

  return (
    <Members
      onSelectMember={(id) => {
        setSearchParams({ id: id });
      }}
    />
  );
};

function App() {
  const [activeReceptionist, setActiveReceptionist] = useState(
    sessionStorage.getItem('adminAuthenticated') === 'true' ? 'admin' : null
  ); // 'admin' or {id, name}
  const [receptionists, setReceptionists] = useState([]);
  const [showAdminLogin, setShowAdminLogin] = useState(false);
  const [adminPassword, setAdminPassword] = useState('');
  const [adminLoginError, setAdminLoginError] = useState('');

  const refreshReceptionists = async () => {
    try {
      const res = await listReceptionists();
      setReceptionists(res);
      const authStatus = sessionStorage.getItem('adminAuthenticated');
      if (authStatus === 'true') {
        setActiveReceptionist('admin');
      } else if (res.length > 0 && !activeReceptionist) {
        setActiveReceptionist(res[0]);
      }
    } catch (e) {
      console.error("Failed to load receptionists", e);
    }
  };

  useEffect(() => {
    refreshReceptionists();
  }, []);

  const [serverTime, setServerTime] = useState(new Date());
  const [mockEnabled, setMockEnabled] = useState(true);

  const fetchServerTime = async () => {
    try {
      const res = await getMockTime();
      setServerTime(new Date(res.current_time));
      setMockEnabled(res.mock_enabled);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchServerTime();
    const interval = setInterval(fetchServerTime, 60000); // refresh every minute
    return () => clearInterval(interval);
  }, []);

  return (
    <ServerTimeContext.Provider value={serverTime}>
      <MockTimeEnabledContext.Provider value={mockEnabled}>
      <ReceptionistContext.Provider value={{ activeReceptionist, setActiveReceptionist, receptionists, refreshReceptionists }}>
      <BrowserRouter>
        <div className="min-h-screen bg-gray-50 ps-20 pt-12 relative">
          <GlobalTimeBar />
          {/* Top Right Corner Receptionist Info */}
          <div className="absolute top-16 end-8 z-50 flex items-center gap-2 glass-panel px-4 py-2 rounded-full border border-gray-200">
            <UserCircle className="w-5 h-5 text-cyan-400" />
            <select
              className="bg-transparent text-gray-700 text-sm font-medium focus:outline-none cursor-pointer appearance-none pe-2"
              value={activeReceptionist === 'admin' ? 'admin' : (activeReceptionist?.id || '')}
              onChange={(e) => {
                const val = e.target.value;
                if (val === 'admin') {
                  setShowAdminLogin(true);
                } else {
                  const rec = receptionists.find(r => r.id === parseInt(val));
                  if (rec) {
                    setActiveReceptionist(rec);
                    sessionStorage.removeItem('adminAuthenticated');
                  }
                }
              }}
            >
              <option value="admin" className="bg-white text-gray-700 font-bold">المسئول</option>
              {receptionists.map(r => (
                <option key={r.id} value={r.id} className="bg-white text-gray-700">{r.name}</option>
              ))}
            </select>
          </div>

          {showAdminLogin && (
            <div className="fixed inset-0 z-[110] flex items-center justify-center bg-black/20 backdrop-blur-sm">
              <div className="bg-white p-8 rounded-2xl shadow-2xl w-full max-w-sm mx-4 animate-in fade-in zoom-in duration-300">
                <div className="flex flex-col items-center mb-6">
                  <div className="w-12 h-12 bg-rose-100 text-rose-600 rounded-full flex items-center justify-center mb-4">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                  </div>
                  <h2 className="text-xl font-bold text-gray-900">صلاحيات المسئول</h2>
                  <p className="text-sm text-gray-500 mt-1">الرجاء إدخال كلمة المرور للمتابعة</p>
                </div>

                <form onSubmit={async (e) => {
                  e.preventDefault();
                  if (!adminPassword) return;
                  try {
                    setAdminLoginError('');
                    const { verifyAdminPassword } = await import('./api');
                    await verifyAdminPassword(adminPassword);
                    setActiveReceptionist('admin');
                    sessionStorage.setItem('adminAuthenticated', 'true');
                    setShowAdminLogin(false);
                    setAdminPassword('');
                  } catch (err) {
                    setAdminLoginError(err.response?.data?.detail || 'كلمة المرور غير صحيحة');
                  }
                }} className="space-y-4">
                  <div>
                    <input
                      type="password"
                      value={adminPassword}
                      onChange={(e) => setAdminPassword(e.target.value)}
                      placeholder="كلمة المرور"
                      className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-center text-black placeholder-gray-400 focus:outline-none focus:border-black/50 focus:ring-2 focus:ring-black/10 transition-all"
                      autoFocus
                    />
                  </div>
                  {adminLoginError && <p className="text-sm text-rose-600 text-center">{adminLoginError}</p>}
                  <div className="flex gap-2">
                    <button
                      type="submit"
                      className="flex-1 bg-black text-white rounded-xl py-3 font-semibold hover:bg-gray-800 transition-colors"
                    >
                      دخول
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setShowAdminLogin(false);
                        setAdminPassword('');
                        setAdminLoginError('');
                      }}
                      className="flex-1 bg-gray-200 text-gray-800 rounded-xl py-3 font-semibold hover:bg-gray-300 transition-colors"
                    >
                      إلغاء
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}


          <Navigation />
          <main className="p-8 w-full mx-auto pt-24">
            <Routes>
              <Route path="/" element={<Reception />} />
              <Route path="/onboarding" element={<AdminAuthWrapper><Onboarding /></AdminAuthWrapper>} />
              <Route path="/members" element={<MembersPage />} />
              <Route path="/dashboard" element={<AdminAuthWrapper><Dashboard /></AdminAuthWrapper>} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </ReceptionistContext.Provider>
    </MockTimeEnabledContext.Provider>
    </ServerTimeContext.Provider>
  );
}

export default App;
