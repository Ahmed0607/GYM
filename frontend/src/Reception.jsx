import React, { useState, useRef, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, UserCheck, AlertCircle, CalendarClock, History, CheckCircle2, Clock, Snowflake } from 'lucide-react';
import { format } from 'date-fns';
import { searchMembers, checkinMember, createSingleSession, getSingleSessionPrice, getMember, consumeAddon } from './api';
import { ServerTimeContext } from './App';

const Reception = () => {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [member, setMember] = useState(null);
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const searchInputRef = useRef(null);
  const debounceRef = useRef(null);
  const serverTime = useContext(ServerTimeContext) || new Date();
  
  const [ssPrice, setSsPrice] = useState(30);
  const [ssName, setSsName] = useState('');
  const [ssLoading, setSsLoading] = useState(false);
  const [showWalkInModal, setShowWalkInModal] = useState(false);
  const [toast, setToast] = useState('');

  useEffect(() => {
    if (searchInputRef.current) {
      searchInputRef.current.focus();
    }
    const fetchPrice = async () => {
      try {
        const price = await getSingleSessionPrice();
        setSsPrice(price);
      } catch(e) {}
    };
    fetchPrice();
  }, []);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (!query.trim() || /^\d+$/.test(query.trim())) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }
    
    debounceRef.current = setTimeout(async () => {
      try {
        const results = await searchMembers(query);
        setSuggestions(results);
        setShowSuggestions(true);
      } catch (err) {
        console.error("Search failed:", err);
      }
    }, 300);
    return () => clearTimeout(debounceRef.current);
  }, [query]);


  const handleSingleSession = async (e) => {
    e.preventDefault();
    if (!ssName.trim()) return;
    setSsLoading(true);
    try {
      await createSingleSession(ssName, ssPrice);
      setToast(`Walk-in session recorded for ${ssName}`);
      setTimeout(() => setToast(''), 3000);
      setSsName('');
      setShowWalkInModal(false);
    } catch (err) {
      setToast("Failed to record walk-in session");
      setTimeout(() => setToast(''), 3000);
    } finally {
      setSsLoading(false);
    }
  };

  const handleSelectMember = async (selectedMember) => {
    setLoading(true);
    setError('');
    setShowSuggestions(false);
    try {
      const checkedInMember = await checkinMember(selectedMember.id);
      setMember(checkedInMember);
      setLogs(checkedInMember.attendance_logs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)));
    } catch (checkinErr) {
      let errDetail = checkinErr.response?.data?.detail;
      if (errDetail === "No sessions remaining") {
        errDetail = 'لا يوجد جلسات متبقية';
      } else if (errDetail === "Subscription expired") {
        errDetail = 'انتهت صلاحية الاشتراك';
      } else if (errDetail === "No active subscription found") {
        errDetail = 'لا يوجد اشتراك نشط';
      } else if (errDetail === "Member not found") {
        errDetail = 'العضو غير موجود';
      }
      setError(errDetail || 'Failed to check in.');
      try {
        const updatedMember = await getMember(selectedMember.id);
        setMember(updatedMember);
        setLogs(updatedMember.attendance_logs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)));
      } catch (err) {
        setMember(selectedMember);
        setLogs(selectedMember.attendance_logs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)));
      }
    } finally {
      setLoading(false);
      setQuery('');
      if (searchInputRef.current) searchInputRef.current.focus();
    }
  };

  const handleConsumeAddon = async (addonName) => {
    if (!member) return;
    try {
      const updatedMember = await consumeAddon(member.id, addonName);
      setMember(updatedMember);
      setLogs(updatedMember.attendance_logs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)));
      setToast(`تم تسجيل الدخول في ${addonName} بنجاح`);
      setTimeout(() => setToast(''), 3000);
    } catch (err) {
      let detail = err.response?.data?.detail;
      if (typeof detail !== 'string') detail = JSON.stringify(detail);
      setError(detail || 'Failed to consume addon.');
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    const cleanQuery = query.trim();
    if (!cleanQuery) return;
    
    if (!/^\d+$/.test(cleanQuery)) {
        if (suggestions.length > 0) setShowSuggestions(true);
        return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const results = await searchMembers(cleanQuery);
      if (results.length > 0) {
        handleSelectMember(results[0]);
      } else {
        setError('Member ID not found.');
      }
    } catch (err) {
      setError('Search failed.');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Active':
      case 'نشط': return 'text-white bg-green-600 border-green-700';
      case 'Owed Money': return 'text-white bg-amber-500 border-amber-600';
      case 'Expired':
      case 'منتهي': return 'text-white bg-red-600 border-red-700';
      case 'Frozen': return 'text-white bg-sky-500 border-sky-600';
      default: return 'text-gray-500 bg-gray-200/50 border-gray-300';
    }
  };

  return (
    <div className="w-[85%] mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold text-black tracking-tight">الاستقبال</h1>
        <p className="text-gray-500">امسح البطاقة أو ابحث بالاسم لتسجيل الدخول</p>
      </div>

      <div className="glass-panel p-6 sm:p-8 z-50">
        <div className="flex flex-col md:flex-row gap-6">
          {/* Left: Standard Check-in (75%) */}
          <div className="w-full md:w-3/4 relative">
            <h2 className="text-xl font-bold text-black mb-4">دخول عضو</h2>
            <form onSubmit={handleSearch} className="relative group w-full">
              <div className="absolute inset-y-0 start-0 ps-6 flex items-center pointer-events-none text-black group-focus-within:text-black transition-colors">
                <Search className="h-6 w-6" />
              </div>
              <input
                ref={searchInputRef}
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onFocus={() => {
                  if (query.trim() && !/^\d+$/.test(query.trim()) && suggestions.length > 0) setShowSuggestions(true);
                }}
                onBlur={() => {
                  setTimeout(() => setShowSuggestions(false), 200);
                }}
                placeholder="Enter ID or Name..."
                className="w-full ps-16 pe-6 py-5 bg-white border-2 border-gray-200 rounded-2xl text-xl text-black placeholder:text-gray-500 focus:outline-none focus:border-black/50 focus:ring-4 focus:ring-gray-500/10 transition-all shadow-xl"
                disabled={loading}
              />
              {loading && (
                <div className="absolute end-6 top-1/2 -translate-y-1/2">
                  <div className="animate-spin rounded-full h-6 w-6 border-2 border-black border-t-transparent"></div>
                </div>
              )}
              
              {showSuggestions && suggestions.length > 0 && (
                <div className="absolute top-full start-0 end-0 mt-2 bg-white border border-gray-200 rounded-xl shadow-2xl overflow-hidden max-h-80 overflow-y-auto custom-scrollbar z-50">
                  {suggestions.map((sug) => (
                    <div 
                      key={sug.id} 
                      onClick={() => handleSelectMember(sug)}
                      className="flex items-center justify-between p-4 hover:bg-gray-100/80 cursor-pointer border-b border-gray-200/50 last:border-0 transition-colors"
                    >
                      <div>
                        <div className="font-bold text-black">{sug.name}</div>
                        <div className="text-sm text-gray-500">ID: {sug.id}</div>
                      </div>
                      <div className="text-end flex flex-col items-end">
                        <div className={`text-xs px-2 py-1 rounded-md mb-1 ${getStatusColor(sug.status)}`}>
                          {sug.status}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </form>
          </div>

          {/* Right: Walk-in Single Session (25%) */}
          <div className="w-full md:w-1/4 flex flex-col justify-end relative">
            <button 
              onClick={() => setShowWalkInModal(true)} 
              className="w-full py-5 bg-black text-white font-bold rounded-2xl hover:bg-gray-800 transition-colors shadow-xl text-lg flex items-center justify-center gap-3"
            >
              <UserCheck className="w-6 h-6" />
              تسجيل زائر
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 flex items-center gap-3">
          <AlertCircle className="w-5 h-5" />
          {error}
        </div>
      )}

      {member && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2 glass-panel p-8 space-y-6 relative overflow-hidden">

            
            <div className="flex justify-between items-start">
              <div>
                <h2 
                  className="text-3xl font-bold text-black mb-2 cursor-pointer hover:text-violet-600 transition-colors"
                  onClick={() => navigate(`/members?id=${member.id}`)}
                >
                  {member.name}
                </h2>
                <p className="text-gray-500 text-lg">ID: {member.id} • {member.phone}</p>
              </div>
              
              <div className="flex items-center gap-3">
                {(() => {
                  if (!member.subscriptions || member.subscriptions.length === 0) return null;
                  const sub = member.subscriptions[member.subscriptions.length - 1];
                  if (member.status === 'Expired' || member.status === 'منتهي') return null;

                  const daysLeft = Math.ceil((new Date(sub.end_date).getTime() - serverTime.getTime()) / (1000 * 3600 * 24));
                  const sessionsLeft = sub.total_sessions > 0 ? sub.total_sessions - sub.attended_sessions : null;

                  let warningMessage = null;
                  if (daysLeft > 0 && daysLeft <= 7) {
                    if (daysLeft === 1) warningMessage = 'متبقي يوم واحد فقط';
                    else if (daysLeft === 2) warningMessage = 'متبقي يومين فقط';
                    else warningMessage = `متبقي ${daysLeft} أيام فقط`;
                  } else if (sessionsLeft !== null && sessionsLeft > 0 && sessionsLeft <= 3) {
                    if (sessionsLeft === 1) warningMessage = 'متبقي جلسة واحدة فقط';
                    else if (sessionsLeft === 2) warningMessage = 'متبقي جلستان فقط';
                    else warningMessage = `متبقي ${sessionsLeft} جلسات فقط`;
                  }

                  if (!warningMessage) return null;

                  return (
                    <div className="px-4 py-2 rounded-full font-bold bg-rose-500 text-white shadow-lg flex items-center gap-2 animate-in fade-in zoom-in duration-300">
                      <AlertCircle className="w-4 h-4" />
                      {warningMessage}
                    </div>
                  );
                })()}

                <div className={`px-4 py-2 rounded-full border font-medium flex items-center gap-2 ${getStatusColor(member.status)}`}>
                  {(member.status === 'نشط' || member.status === 'Active') && <CheckCircle2 className="w-4 h-4" />}
                  {member.status === 'Owed Money' && <AlertCircle className="w-4 h-4" />}
                  {(member.status === 'منتهي' || member.status === 'Expired') && <Clock className="w-4 h-4" />}
                  {member.status === 'Frozen' && <Snowflake className="w-4 h-4" />}
                  {member.status}
                </div>
              </div>
            </div>

            {member.subscriptions && member.subscriptions.length > 0 && (
              <div className="grid grid-cols-2 gap-4 pt-6 border-t border-gray-200/50">
                {(() => {
                  const sub = member.subscriptions[member.subscriptions.length - 1];
                  return (
                    <>
                      <div className="bg-gray-200/30 p-4 rounded-xl border border-gray-200/50">
                        <p className="text-sm text-gray-500 mb-1">نشط Package</p>
                        <p className="font-semibold text-black truncate">{sub.package_name.join(', ')}</p>
                      </div>
                      <div className={`p-4 rounded-xl border ${sub.total_sessions > 0 && sub.attended_sessions >= sub.total_sessions ? 'bg-red-600 border-red-700 text-white' : 'bg-green-600 border-green-700 text-white'}`}>
                        <p className="text-sm text-white/80 mb-1">الجلسات المحضورة</p>
                        <p className="font-semibold text-white">
                          <span className="text-white">{sub.attended_sessions}</span>
                          <span className="text-white/80 mx-1">/</span>
                          {sub.total_sessions || '∞'}
                        </p>
                      </div>
                      <div className={`p-4 rounded-xl border ${ (new Date(sub.end_date).getTime() < serverTime.getTime()) || member.status === 'Expired' || member.status === 'منتهي' ? 'bg-red-600 border-red-700 text-white' : 'bg-green-600 border-green-700 text-white'}`}>
                        <p className="text-sm text-white/80 mb-1">الصلاحية</p>
                        <div className="font-semibold text-white text-sm">
                          {format(new Date(sub.start_date), 'MMM d, yyyy')} — {format(new Date(sub.end_date), 'MMM d, yyyy')}
                        </div>
                      </div>
                      <div className={`bg-gray-200/30 p-4 rounded-xl border ${sub.amount_owed > 0 ? 'border-rose-500/20' : 'border-gray-200/50'}`}>
                        <p className="text-sm text-gray-500 mb-1">المالية</p>
                        <div className="font-semibold text-sm">
                          <span className="text-gray-700">Total: ${sub.total_price.toFixed(2)} | Paid: ${sub.amount_paid.toFixed(2)}</span>
                          <br/>
                          <span className={`${sub.amount_owed > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                            Owed: ${sub.amount_owed.toFixed(2)}
                          </span>
                        </div>
                      </div>

                      {/* Addons Usage */}
                      {sub.addons_usage && Object.keys(sub.addons_usage).length > 0 && (
                        <div className="col-span-2 grid grid-cols-2 gap-4 mt-2">
                          {Object.entries(sub.addons_usage).map(([addonName, usage]) => {
                            const isExhausted = usage.total > 0 && usage.used >= usage.total;
                            return (
                              <div key={addonName} className={`p-4 rounded-xl border flex flex-col justify-between ${isExhausted ? 'bg-red-600 border-red-700 text-white' : 'bg-purple-600 border-purple-700 text-white'}`}>
                                <div>
                                  <p className="text-sm text-white/80 mb-1">{addonName} (إضافية)</p>
                                  <p className="font-semibold text-white mb-3">
                                    <span className="text-white">{usage.used}</span>
                                    <span className="text-white/80 mx-1">/</span>
                                    {usage.total || '∞'}
                                  </p>
                                </div>
                                {!isExhausted && (
                                  <button
                                    onClick={() => handleConsumeAddon(addonName)}
                                    className="w-full py-2 bg-white/20 hover:bg-white/30 rounded-lg text-white font-medium text-sm transition-colors"
                                  >
                                    دخول ({addonName})
                                  </button>
                                )}
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </>
                  );
                })()}
              </div>
            )}
          </div>

          <div className="glass-panel p-6 flex flex-col h-[400px]">
            <div className="flex items-center gap-2 text-gray-700 mb-6 font-medium border-b border-gray-200 pb-4">
              <History className="w-5 h-5 text-black" />
              عمليات الدخول الأخيرة
            </div>
            <div className="flex-1 overflow-y-auto pe-2 space-y-3 custom-scrollbar">
              {logs.length > 0 ? (
                logs.map((log) => (
                  <div key={log.id} className="flex justify-between items-center p-3 rounded-lg bg-gray-200/30 border border-gray-200/50">
                    <span className="text-gray-700">{format(new Date(log.timestamp), 'MMM d, yyyy')}</span>
                    <div className="flex items-center gap-2">
                      {log.addon_tag && (
                        <span className="text-xs font-bold text-white bg-purple-500 px-2 py-0.5 rounded uppercase">
                          {log.addon_tag}
                        </span>
                      )}
                      <span className="text-gray-500 font-mono text-sm bg-white px-2 py-1 rounded">
                        {format(new Date(log.timestamp), 'HH:mm')}
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center text-gray-500 pt-8">لا يوجد سجل حضور</div>
              )}
            </div>
          </div>
        </div>
      )}
      {toast && (
        <div className="fixed bottom-4 end-4 bg-black text-white px-6 py-3 rounded-xl shadow-2xl animate-in fade-in slide-in-from-bottom-4 flex items-center gap-2 z-50">
          <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          {toast}
        </div>
      )}

      {/* Walk-in Modal */}
      {showWalkInModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[100] flex items-center justify-center p-4 animate-in fade-in duration-200">
          <div className="bg-white rounded-2xl max-w-sm w-full p-6 shadow-2xl space-y-6">
            <h3 className="text-xl font-bold text-black border-b border-gray-100 pb-3">تسجيل زائر جديد</h3>
            <form onSubmit={handleSingleSession} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-500 mb-1">اسم الزائر</label>
                <input
                  type="text"
                  value={ssName}
                  onChange={(e) => setSsName(e.target.value)}
                  className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-black focus:outline-none focus:border-black/50 focus:ring-2 focus:ring-gray-500/10 transition-all"
                  placeholder="أدخل الاسم..."
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500 mb-1">السعر ($)</label>
                <input
                  type="number"
                  value={ssPrice}
                  onChange={(e) => setSsPrice(e.target.value)}
                  className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-black focus:outline-none focus:border-black/50 focus:ring-2 focus:ring-gray-500/10 transition-all"
                  min="0"
                  required
                />
              </div>
              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowWalkInModal(false)}
                  className="flex-1 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold rounded-xl transition-colors"
                >
                  إلغاء
                </button>
                <button
                  type="submit"
                  disabled={ssLoading}
                  className="flex-1 py-3 bg-black hover:bg-gray-800 text-white font-bold rounded-xl transition-colors disabled:opacity-50"
                >
                  {ssLoading ? 'جاري التسجيل...' : 'تأكيد'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Reception;
