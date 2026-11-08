import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Search, Users, ChevronRight, AlertCircle, CheckCircle2, Clock, Hash, Phone, Filter, Trash2, Snowflake } from 'lucide-react';
import { format } from 'date-fns';
import { listMembers, deleteExpiredMembers } from './api';

const Members = ({ onSelectMember }) => {
  const [members, setMembers] = useState([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const searchInputRef = useRef(null);
  const debounceRef = useRef(null);

  const fetchMembers = useCallback(async (searchQuery = '') => {
    setLoading(true);
    setError('');
    try {
      const data = await listMembers(searchQuery);
      setMembers(data);
    } catch (err) {
      setError('Failed to load members.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMembers();
  }, [fetchMembers]);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      fetchMembers(query);
    }, 300);
    return () => clearTimeout(debounceRef.current);
  }, [query, fetchMembers]);

  const handleDeleteExpired = async () => {
    if (!window.confirm("Are you sure you want to delete all members with expired subscriptions? This cannot be undone.")) return;
    try {
      await deleteExpiredMembers();
      fetchMembers();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete expired members.');
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

  const getStatusIcon = (status) => {
    switch (status) {
      case 'Active':
      case 'نشط': return <CheckCircle2 className="w-3.5 h-3.5" />;
      case 'Owed Money': return <AlertCircle className="w-3.5 h-3.5" />;
      case 'Expired':
      case 'منتهي': return <Clock className="w-3.5 h-3.5" />;
      case 'Frozen': return <Snowflake className="w-3.5 h-3.5" />;
      default: return null;
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold text-black tracking-tight">الأعضاء</h1>
        <p className="text-gray-500">تصفح وابحث وقم بإدارة جميع أعضاء الصالة</p>
      </div>

      {/* Search Bar */}
      <div className="relative group">
        <div className="absolute inset-y-0 start-0 ps-6 flex items-center pointer-events-none text-black group-focus-within:text-cyan-400 transition-colors">
          <Search className="h-5 w-5" />
        </div>
        <input
          ref={searchInputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="البحث بالاسم، رقم العضو، أو رقم الهاتف..."
          className="w-full ps-14 pe-6 py-4 bg-white border-2 border-gray-200 rounded-2xl text-lg text-black placeholder:text-gray-500 focus:outline-none focus:border-black/50 focus:ring-4 focus:ring-gray-500/10 transition-all shadow-xl"
        />
        {query && (
          <button
            onClick={() => setQuery('')}
            className="absolute end-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 transition-colors text-sm bg-gray-200 px-2 py-1 rounded-lg"
          >مسح</button>
        )}
      </div>

      {/* Stats Bar */}
      <div className="flex items-center justify-between gap-4 text-sm">
        <div className="flex items-center gap-2 text-gray-500">
          <Filter className="w-4 h-4" />
          <span>{members.length} {members.length !== 1 ? 'أعضاء' : 'عضو'} {query ? 'متطابق' : 'إجمالي'}</span>
        </div>
        <button
          onClick={handleDeleteExpired}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-rose-500/10 text-rose-400 hover:bg-rose-500/20 transition-colors"
        >
          <Trash2 className="w-4 h-4" />
          إزالة المنتهي
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 flex items-center gap-3">
          <AlertCircle className="w-5 h-5" />
          {error}
        </div>
      )}

      {/* Members List */}
      {loading ? (
        <div className="flex items-center justify-center py-16">
          <div className="animate-spin rounded-full h-10 w-10 border-3 border-black border-t-transparent"></div>
        </div>
      ) : members.length === 0 ? (
        <div className="glass-panel p-16 text-center">
          <Users className="w-12 h-12 text-gray-500 mx-auto mb-4" />
          <p className="text-gray-500 text-lg">
            {query ? 'No members match your search.' : 'No members registered yet.'}
          </p>
          <p className="text-gray-500 text-sm mt-2">
            {query ? 'Try a different search term.' : 'Go to Onboarding to register new members.'}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {members.map((member) => {
            const latestSub = member.subscriptions?.[member.subscriptions.length - 1];
            return (
              <button
                key={member.id}
                onClick={() => onSelectMember(member.id)}
                className="w-full glass-panel p-5 flex items-center gap-5 hover:bg-gray-100/60 hover:border-gray-300 transition-all duration-200 cursor-pointer group text-start"
              >
                {/* ID Badge */}
                <div className="flex-shrink-0 w-14 h-14 bg-gray-200 rounded-xl flex items-center justify-center border border-gray-300 group-hover:border-black group-hover:bg-black transition-all">
                  <span className="text-black group-hover:text-white transition-colors font-bold text-lg">{member.id}</span>
                </div>

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-1">
                    <h3 className="text-black font-semibold text-lg truncate">{member.name}</h3>
                    <div className={`px-2.5 py-0.5 rounded-full border text-xs font-medium flex items-center gap-1.5 flex-shrink-0 ${getStatusColor(member.status)}`}>
                      {getStatusIcon(member.status)}
                      {member.status}
                    </div>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span className="flex items-center gap-1.5">
                      <Phone className="w-3.5 h-3.5" />
                      {member.phone}
                    </span>
                    {latestSub && (
                      <>
                        <span className="text-gray-400">•</span>
                        <span className="truncate">{latestSub.package_name.join(', ')}</span>
                        {latestSub.amount_owed > 0 && (
                          <>
                            <span className="text-gray-400">•</span>
                            <span className="text-rose-400 font-medium">
                              Owes £{latestSub.amount_owed.toFixed(0)}
                            </span>
                          </>
                        )}
                      </>
                    )}
                  </div>
                </div>

                {/* Arrow */}
                <ChevronRight className="w-5 h-5 text-gray-500 group-hover:text-cyan-400 transition-colors flex-shrink-0" />
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default Members;
