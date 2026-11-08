import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  DollarSign, Users, Activity, AlertTriangle, ArrowRight, Wallet, Clock,
  Package, Plus, Trash2, Edit3, Check, X, Save, Settings, UserCheck, Infinity, UserCircle, Briefcase, TrendingUp, TrendingDown, Receipt, Sliders, ToggleLeft, ToggleRight
} from 'lucide-react';
import { format } from 'date-fns';
import { getDashboard, listPackages, createPackage, updatePackage, deletePackage, createReceptionist, updateReceptionist, deleteReceptionist, listStaff, createStaff, updateStaffPending, deleteStaff, createExpense, getFilteredFinances, verifyPin, updatePin, getSingleSessionPrice, updateSingleSessionPrice, updateAdminPassword, adminReset, toggleMockTime } from './api';
import { ReceptionistContext, ServerTimeContext, MockTimeEnabledContext } from './App';

const Dashboard = () => {
  const serverTime = React.useContext(ServerTimeContext);
  const mockEnabled = React.useContext(MockTimeEnabledContext);
  const navigate = useNavigate();
  const [isUnlocked, setIsUnlocked] = useState(false);
  const [pinInput, setPinInput] = useState('');
  const [pinError, setPinError] = useState('');
  const [showChangePin, setShowChangePin] = useState(false);
  const [newPinInput, setNewPinInput] = useState('');

  const handleVerifyPin = async (e) => {
    e.preventDefault();
    try {
      await verifyPin(pinInput);
      setIsUnlocked(true);
      setPinError('');
    } catch (err) {
      setPinError('Invalid PIN');
    }
  };

  const handleChangePin = async (e) => {
    e.preventDefault();
    try {
      await updatePin(newPinInput);
      setShowChangePin(false);
      setNewPinInput('');
      setPkgSuccess('PIN changed successfully.');
      setTimeout(() => setPkgSuccess(''), 3000);
    } catch (err) {
      setPkgError('Failed to change PIN');
    }
  };

  const [activeTab, setActiveTab] = useState('overview');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Package management state
  const [packages, setPackages] = useState([]);
  const [singleSessionPrice, setSingleSessionPrice] = useState(30);
  const [editingSessionPrice, setEditingSessionPrice] = useState(false);
  const [pkgLoading, setPkgLoading] = useState(false);
  const [editingPkg, setEditingPkg] = useState(null); // id of package being edited
  const [editForm, setEditForm] = useState({ name: '', price: '', duration_days: '', sessions: '', is_addon: false });
  const [showAddPkg, setShowAddPkg] = useState(false);
  const [newPkgForm, setNewPkgForm] = useState({ name: '', price: '', duration_days: '', sessions: '', is_addon: false });
  const [pkgError, setPkgError] = useState('');
  const [pkgSuccess, setPkgSuccess] = useState('');

  const { receptionists, refreshReceptionists } = React.useContext(ReceptionistContext);

  // Receptionist management state
  const [editingRec, setEditingRec] = useState(null);
  const [editRecForm, setEditRecForm] = useState({ name: '' });
  const [showAddRec, setShowAddRec] = useState(false);
  const [newRecForm, setNewRecForm] = useState({ name: '' });
  
  // Admin Password state
  const [oldPasswordForm, setOldPasswordForm] = useState('');
  const [newPasswordForm, setNewPasswordForm] = useState('');
  const [isChangingPassword, setIsChangingPassword] = useState(false);

  const handleChangeAdminPassword = async () => {
    setPkgError('');
    if (!oldPasswordForm || !newPasswordForm) {
      setPkgError('يرجى إدخال كلمة المرور الحالية والجديدة.');
      return;
    }
    setIsChangingPassword(true);
    try {
      await updateAdminPassword(oldPasswordForm, newPasswordForm);
      setOldPasswordForm('');
      setNewPasswordForm('');
      setPkgSuccess('تم تغيير كلمة مرور الإدارة بنجاح.');
      setTimeout(() => setPkgSuccess(''), 3000);
    } catch (err) {
      setPkgError(err.response?.data?.detail || 'فشل تغيير كلمة المرور.');
    } finally {
      setIsChangingPassword(false);
    }
  };

  const handleFactoryReset = async () => {
    if (window.confirm("تحذير: هذا سيؤدي إلى مسح جميع بيانات الأعضاء، الاشتراكات، سجلات الحضور، والمصروفات بالكامل! \n\nهل أنت متأكد من رغبتك في إعادة ضبط المصنع استعداداً للاستخدام التجاري؟")) {
      setPkgError('');
      try {
        await adminReset();
        setPkgSuccess('تم إعادة ضبط النظام بالكامل بنجاح!');
        setTimeout(() => setPkgSuccess(''), 5000);
        fetchDashboard();
      } catch (err) {
        setPkgError('فشل إعادة ضبط النظام.');
      }
    }
  };

  // Finances state
  const [staffList, setStaffList] = useState([]);
  const [staffLoading, setStaffLoading] = useState(false);
  const [showAddStaff, setShowAddStaff] = useState(false);
  const [newStaffForm, setNewStaffForm] = useState({ name: '', phone: '', role: '', base_salary: '', pay_day: 1 });
  const [showAddExpense, setShowAddExpense] = useState(false);
  const [newExpenseForm, setNewExpenseForm] = useState({ category: 'Maintenance', amount: '', description: '' });
  
  const [financePeriod, setFinancePeriod] = useState('lifetime');
  const [financeStart, setFinanceStart] = useState('');
  const [financeEnd, setFinanceEnd] = useState('');
  const [filteredFinances, setFilteredFinances] = useState(null);


  const fetchDashboard = async () => {
    try {
      const result = await getDashboard();
      setData(result);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchPackages = async () => {
    setPkgLoading(true);
    try {
      const result = await listPackages();
      setPackages(result);
    } catch (err) {
      console.error(err);
    } finally {
      setPkgLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchStaff = async () => {
    setStaffLoading(true);
    try {
      const result = await listStaff();
      setStaffList(result);
    } catch (err) {
      console.error(err);
    } finally {
      setStaffLoading(false);
    }
  };


  const fetchSessionPrice = async () => {
    try {
      const price = await getSingleSessionPrice();
      setSingleSessionPrice(price);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    if (activeTab === 'packages') {
      fetchPackages();
      fetchSessionPrice();
    } else if (activeTab === 'finances') {
      fetchDashboard();
    } else if (activeTab === 'staff') {
      fetchStaff();
      fetchDashboard();
    }
  }, [activeTab]);

  const handleSaveSessionPrice = async () => {
    try {
      await updateSingleSessionPrice(parseFloat(singleSessionPrice));
      alert("Single Session price updated!");
    } catch (e) {
      alert("Failed to update price");
    }
  };

  const handleAddPackage = async () => {
    setPkgError('');
    if (!newPkgForm.name || !newPkgForm.price || !newPkgForm.duration_days) {
      setPkgError('الاسم, Price, and المدة are required.');
      return;
    }
    try {
      await createPackage({
        name: newPkgForm.name,
        price: parseFloat(newPkgForm.price),
        duration_days: parseInt(newPkgForm.duration_days),
        sessions: newPkgForm.sessions ? parseInt(newPkgForm.sessions) : null,
        is_addon: newPkgForm.is_addon || false
      });
      setNewPkgForm({ name: '', price: '', duration_days: '', sessions: '', is_addon: false });
      setShowAddPkg(false);
      setPkgSuccess('Package created successfully.');
      setTimeout(() => setPkgSuccess(''), 3000);
      fetchPackages();
    } catch (err) {
      setPkgError(err.response?.data?.detail || 'Failed to create package.');
    }
  };

  const handleEditPackage = async (pkgId) => {
    setPkgError('');
    if (!editForm.name || !editForm.price || !editForm.duration_days) {
      setPkgError('الاسم, السعر, والمدة مطلوبة');
      return;
    }
    try {
      await updatePackage(pkgId, {
        name: editForm.name,
        price: parseFloat(editForm.price),
        duration_days: parseInt(editForm.duration_days),
        sessions: editForm.sessions ? parseInt(editForm.sessions) : null,
        is_addon: editForm.is_addon || false
      });
      setEditingPkg(null);
      setPkgSuccess('Package updated successfully.');
      setTimeout(() => setPkgSuccess(''), 3000);
      fetchPackages();
    } catch (err) {
      setPkgError(err.response?.data?.detail || 'Failed to update package.');
    }
  };

  const handleDeletePackage = async (pkgId) => {
    setPkgError('');
    try {
      await deletePackage(pkgId);
      setPkgSuccess('Package deleted.');
      setTimeout(() => setPkgSuccess(''), 3000);
      fetchPackages();
    } catch (err) {
      setPkgError(err.response?.data?.detail || 'Failed to delete package.');
    }
  };

  const startEditPkg = (pkg) => {
    setEditingPkg(pkg.id);
    setEditForm({
      name: pkg.name,
      price: pkg.price.toString(),
      duration_days: pkg.duration_days.toString(),
      sessions: pkg.sessions !== null ? pkg.sessions.toString() : '',
      is_addon: pkg.is_addon || false
    });
  };

  const handleAddReceptionist = async () => {
    setPkgError('');
    if (!newRecForm.name) {
      setPkgError('الاسم is required.');
      return;
    }
    try {
      await createReceptionist({ name: newRecForm.name });
      setNewRecForm({ name: '' });
      setShowAddRec(false);
      setPkgSuccess('Receptionist created.');
      setTimeout(() => setPkgSuccess(''), 3000);
      refreshReceptionists();
    } catch (err) {
      setPkgError(err.response?.data?.detail || 'Failed to create receptionist.');
    }
  };

  const handleEditReceptionist = async (recId) => {
    setPkgError('');
    if (!editRecForm.name) {
      setPkgError('الاسم is required.');
      return;
    }
    try {
      await updateReceptionist(recId, { name: editRecForm.name });
      setEditingRec(null);
      setPkgSuccess('Receptionist updated.');
      setTimeout(() => setPkgSuccess(''), 3000);
      refreshReceptionists();
    } catch (err) {
      setPkgError(err.response?.data?.detail || 'Failed to update receptionist.');
    }
  };

  const handleDeleteReceptionist = async (recId) => {
    setPkgError('');
    try {
      await deleteReceptionist(recId);
      setPkgSuccess('Receptionist deleted.');
      setTimeout(() => setPkgSuccess(''), 3000);
      refreshReceptionists();
    } catch (err) {
      setPkgError(err.response?.data?.detail || 'Failed to delete receptionist.');
    }
  };


  const handleAddStaff = async () => {
    setPkgError('');
    if (!newStaffForm.name || !newStaffForm.role || !newStaffForm.base_salary || !newStaffForm.pay_day) {
      setPkgError('All fields required.');
      return;
    }
    try {
      await createStaff({ name: newStaffForm.name, phone: newStaffForm.phone || null, role: newStaffForm.role, base_salary: parseFloat(newStaffForm.base_salary), pay_day: parseInt(newStaffForm.pay_day) });
      setNewStaffForm({ name: '', phone: '', role: '', base_salary: '', pay_day: 1 });
      setShowAddStaff(false);
      setPkgSuccess('Staff created.');
      setTimeout(() => setPkgSuccess(''), 3000);
      fetchStaff();
    } catch (err) {
      setPkgError('Failed to create staff.');
    }
  };

  const handleUpdatePending = async (staffId, bonus, deduction) => {
    try {
      await updateStaffPending(staffId, { pending_bonus: parseFloat(bonus||0), pending_deduction: parseFloat(deduction||0) });
      setPkgSuccess('Staff info updated.');
      setTimeout(() => setPkgSuccess(''), 3000);
      fetchStaff();
    } catch (err) {
      setPkgError('Failed to update staff info.');
    }
  };


  const handleCalculateFinances = async () => {
    if (!financeStart || !financeEnd) {
      setPkgError('Please select both start and end dates.');
      return;
    }
    setPkgError('');
    try {
      const res = await getFilteredFinances(financeStart, financeEnd);
      setFilteredFinances(res);
    } catch (err) {
      setPkgError('Failed to fetch filtered finances.');
    }
  };

  useEffect(() => {
    if (financePeriod === 'lifetime') {
      setFilteredFinances(null);
      setFinanceStart('');
      setFinanceEnd('');
    } else if (financePeriod !== 'custom') {
      let start = new Date(serverTime);
      let end = new Date(serverTime);
      if (financePeriod === 'last_month') {
        start.setDate(start.getDate() - 30);
      } else if (financePeriod === 'last_3_months') {
        start.setDate(start.getDate() - 90);
      } else if (financePeriod === 'last_6_months') {
        start.setDate(start.getDate() - 180);
      } else if (financePeriod === 'this_year') {
        start.setFullYear(start.getFullYear(), 0, 1);
      }
      
      const startStr = start.toISOString().split('T')[0];
      const endStr = end.toISOString().split('T')[0];
      setFinanceStart(startStr);
      setFinanceEnd(endStr);
      
      const fetchFinances = async () => {
        try {
          const res = await getFilteredFinances(startStr, endStr);
          setFilteredFinances(res);
        } catch (err) {
          setPkgError('Failed to fetch filtered finances.');
        }
      };
      fetchFinances();
    }
  }, [financePeriod, serverTime]);

  const handleAddExpense = async () => {
    setPkgError('');
    if (!newExpenseForm.amount) {
      setPkgError('المبلغ is required.');
      return;
    }
    try {
      await createExpense({ category: newExpenseForm.category, amount: parseFloat(newExpenseForm.amount), description: newExpenseForm.description });
      setNewExpenseForm({ category: 'Maintenance', amount: '', description: '' });
      setShowAddExpense(false);
      setPkgSuccess('Expense recorded.');
      setTimeout(() => setPkgSuccess(''), 3000);
      fetchDashboard();
    } catch (err) {
      setPkgError('Failed to add expense.');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-black border-t-transparent"></div>
      </div>
    );
  }

  if (!data) return <div className="text-black text-center">فشل تحميل لوحة التحكم.</div>;

  const kpis = [
    { label: "Live Occupancy", value: data.kpis.live_occupancy, icon: Users, color: 'text-violet-400', bg: 'bg-violet-400/10' },
    { label: "Today's Check-ins", value: data.kpis.today_checkins, icon: Activity, color: 'text-emerald-400', bg: 'bg-emerald-400/10' },
    { label: "الأعضاء النشطين", value: data.kpis.total_active_members, icon: Users, color: 'text-cyan-400', bg: 'bg-cyan-400/10' },
    { label: "Money Owed", value: `£${data.kpis.total_money_owed.toFixed(0)}`, icon: AlertTriangle, color: 'text-rose-400', bg: 'bg-rose-400/10' },
    { label: "Revenue Today", value: `£${data.kpis.revenue_today.toFixed(0)}`, icon: Wallet, color: 'text-amber-400', bg: 'bg-amber-400/10' },
  ];

  const tabs = [
    { id: 'overview', label: 'نظرة عامة', icon: Activity },
    { id: 'packages', label: 'إدارة الباقات', icon: Settings },
    { id: 'receptionists', label: 'إدارة موظفي الاستقبال', icon: UserCircle },
    { id: 'finances', label: 'Finances', icon: Receipt },
    { id: 'staff', label: 'إدارة الموظفين', icon: Briefcase },
    { id: 'settings', label: 'إعدادات', icon: Sliders },
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold text-black tracking-tight">لوحة تحكم المسؤول</h1>
        <p className="text-gray-500">نظرة عامة of gym performance and member status</p>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6">
        {kpis.map((kpi, index) => {
          const Icon = kpi.icon;
          return (
            <div key={index} className="glass-panel p-6 flex items-start gap-4">
              <div className={`p-3 rounded-xl ${kpi.bg}`}>
                <Icon className={`w-6 h-6 ${kpi.color}`} />
              </div>
              <div>
                <div className="text-sm font-medium text-gray-500 mb-1">{kpi.label}</div>
                <div className="text-2xl font-bold text-black">{kpi.value}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Tab Switcher */}
      <div className="flex gap-2">
        {tabs.map((tab) => {
          const TabIcon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-5 py-3 rounded-xl font-medium text-sm flex items-center gap-2 transition-all duration-200 ${
                activeTab === tab.id
                  ? 'bg-black text-white text-white shadow-lg shadow-gray-500/20'
                  : 'bg-white/80 text-gray-500 border border-gray-200 hover:bg-gray-100/60 hover:text-gray-900'
              }`}
            >
              <TabIcon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* ═══ OVERVIEW TAB ═══ */}
      {activeTab === 'overview' && (
        <div className="space-y-8">
          {/* Today's Check-ins + Owing Money + ينتهي قريباً + Recent Subs */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

            {/* Today's Check-ins Panel */}
            <div className="glass-panel p-6 flex flex-col h-[500px]">
              <div className="flex items-center gap-2 text-black font-semibold border-b border-gray-200 pb-4 mb-4">
                <UserCheck className="w-5 h-5 text-emerald-500" />
                Today's Check-ins
                <div className="ms-auto bg-black text-white font-bold text-sm py-1 px-3 rounded-lg shadow-sm">
                  {data.today_checkin_list?.length || 0}
                </div>
              </div>

              <div className="flex-1 overflow-auto custom-scrollbar pe-2">
                {data.today_checkin_list && data.today_checkin_list.length > 0 ? (
                  <div className="space-y-2">
                    {data.today_checkin_list.map((checkin, idx) => (
                      <button
                        key={idx}
                        onClick={() => { if (checkin.member_id !== 'G') navigate(`/members?id=${checkin.member_id}`) }}
                        className={`w-full flex items-center gap-4 p-3 rounded-lg border transition-all text-start ${checkin.member_id !== 'G' ? 'bg-gray-200/30 border-gray-200/50 hover:bg-gray-100/60 hover:border-black/20 cursor-pointer group' : 'bg-gray-50 border-gray-100 cursor-default'}`}
                      >
                        <div className="flex-shrink-0 w-10 h-10 bg-gray-200 rounded-lg flex items-center justify-center border border-gray-300 group-hover:border-black/30 transition-colors">
                          <span className="text-black font-bold text-sm">{checkin.member_id}</span>
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="text-black font-medium text-sm truncate">{checkin.member_name}</div>
                        </div>
                        <span className="text-gray-500 font-mono text-xs bg-white px-2 py-1 rounded flex-shrink-0">
                          {checkin.timestamp ? format(new Date(checkin.timestamp), 'hh:mm a') : '--:--'}
                        </span>
                        <ArrowRight className="w-4 h-4 text-gray-500 group-hover:text-cyan-400 transition-colors flex-shrink-0" />
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="text-center text-gray-500 pt-8">لا توجد عمليات دخول اليوم.</div>
                )}
              </div>
            </div>

            {/* Owing Money */}
            <div className="glass-panel p-6 flex flex-col h-[500px]">
              <div className="flex items-center gap-2 text-black font-semibold border-b border-gray-200 pb-4 mb-4">
                <DollarSign className="w-5 h-5 text-rose-500" />
                أعضاء عليهم ديون
                <div className="ms-auto bg-black text-white font-bold text-sm py-1 px-3 rounded-lg shadow-sm">
                  {data.members_owing_money.length}
                </div>
              </div>

              <div className="flex-1 overflow-auto custom-scrollbar pe-2">
                <table className="w-full text-start border-collapse">
                  <thead>
                    <tr className="border-b border-gray-200 text-gray-500 text-sm">
                      <th className="pb-3 font-medium">الاسم</th>
                      <th className="pb-3 font-medium text-end">مدين</th>
                      <th className="pb-3 w-8"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.members_owing_money.map((member) => {
                      const activeSub = member.subscriptions[member.subscriptions.length - 1];
                      return (
                        <tr
                          key={member.id}
                          className="border-b border-gray-200/50 hover:bg-gray-100/20 transition-colors cursor-pointer"
                          onClick={() => navigate(`/members?id=${member.id}`)}
                        >
                          <td className="py-4">
                            <div className="font-medium text-black text-sm">{member.name}</div>
                            <div className="text-xs text-gray-500">{member.id}</div>
                          </td>
                          <td className="py-4 text-end">
                            <div className="font-bold text-rose-400 text-sm">£{activeSub?.amount_owed.toFixed(0)}</div>
                          </td>
                          <td className="py-4 text-end">
                            <ArrowRight className="w-4 h-4 text-gray-500" />
                          </td>
                        </tr>
                      )
                    })}
                    {data.members_owing_money.length === 0 && (
                      <tr>
                        <td colSpan="3" className="py-8 text-center text-gray-500">لا يوجد أعضاء عليهم ديون حالياً.</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* ينتهي قريباً */}
            <div className="glass-panel p-6 flex flex-col h-[500px]">
              <div className="flex items-center gap-2 text-black font-semibold border-b border-gray-200 pb-4 mb-4">
                <Clock className="w-5 h-5 text-amber-500" />
                Expiring within 7 Days
                <div className="ms-auto bg-black text-white font-bold text-sm py-1 px-3 rounded-lg shadow-sm">
                  {data.expiring_soon.length}
                </div>
              </div>

              <div className="flex-1 overflow-auto custom-scrollbar pe-2">
                <table className="w-full text-start border-collapse">
                  <thead>
                    <tr className="border-b border-gray-200 text-gray-500 text-sm">
                      <th className="pb-3 font-medium">الاسم</th>
                      <th className="pb-3 font-medium text-end">تاريخ الانتهاء</th>
                      <th className="pb-3 w-8"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.expiring_soon.map((member) => {
                      const activeSub = member.subscriptions[member.subscriptions.length - 1];
                      return (
                        <tr
                          key={member.id}
                          className="border-b border-gray-200/50 hover:bg-gray-100/20 transition-colors cursor-pointer"
                          onClick={() => navigate(`/members?id=${member.id}`)}
                        >
                          <td className="py-4">
                            <div className="font-medium text-black text-sm">{member.name}</div>
                            <div className="text-xs text-gray-500">{activeSub?.package_name.join(', ')}</div>
                          </td>
                          <td className="py-4 text-end">
                            <div className="font-bold text-amber-400 text-sm">
                              {format(new Date(activeSub.end_date), 'MMM d, yyyy')}
                            </div>
                          </td>
                          <td className="py-4 text-end">
                            <ArrowRight className="w-4 h-4 text-gray-500" />
                          </td>
                        </tr>
                      )
                    })}
                    {data.expiring_soon.length === 0 && (
                      <tr>
                        <td colSpan="3" className="py-8 text-center text-gray-500">لا يوجد أعضاء تنتهي اشتراكاتهم قريباً.</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* New Subscriptions */}
            <div className="glass-panel p-6 flex flex-col h-[500px]">
              <div className="flex items-center gap-2 text-black font-semibold border-b border-gray-200 pb-4 mb-4">
                <Package className="w-5 h-5 text-purple-500" />
                New Subscriptions
                <div className="ms-auto bg-black text-white font-bold text-sm py-1 px-3 rounded-lg shadow-sm">
                  {data.recent_subscriptions?.length || 0}
                </div>
              </div>

              <div className="flex-1 overflow-auto custom-scrollbar pe-2">
                <table className="w-full text-start border-collapse">
                  <thead>
                    <tr className="border-b border-gray-200 text-gray-500 text-sm">
                      <th className="pb-3 font-medium">الاسم & Package</th>
                      <th className="pb-3 font-medium text-end">المدفوع</th>
                      <th className="pb-3 w-8"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.recent_subscriptions?.map((sub, idx) => (
                      <tr
                        key={idx}
                        className={`border-b border-gray-200/50 transition-colors ${sub.member_id !== 'G' ? 'hover:bg-gray-100/20 cursor-pointer' : ''}`}
                        onClick={() => { if (sub.member_id !== 'G') navigate(`/members?id=${sub.member_id}`) }}
                      >
                        <td className="py-4">
                          <div className="font-medium text-black text-sm">{sub.member_name}</div>
                          <div className="text-xs text-gray-500">{sub.packages.join(', ')}</div>
                        </td>
                        <td className="py-4 text-end">
                          <div className="font-bold text-emerald-400 text-sm">
                            £{sub.amount_paid.toFixed(0)}
                          </div>
                          <div className="text-xs text-gray-500">
                            {sub.start_date ? format(new Date(sub.start_date), 'MMM d') : ''}
                          </div>
                        </td>
                        <td className="py-4 text-end">
                          <ArrowRight className="w-4 h-4 text-gray-500" />
                        </td>
                      </tr>
                    ))}
                    {(!data.recent_subscriptions || data.recent_subscriptions.length === 0) && (
                      <tr>
                        <td colSpan="3" className="py-8 text-center text-gray-500">لا توجد اشتراكات أخيرة.</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

          </div>
        </div>
      )}

      {/* ═══ PACKAGES TAB ═══ */}
      {activeTab === 'packages' && (
        <div className="space-y-6">
          {pkgError && (
            <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 flex items-center gap-3">
              <AlertTriangle className="w-5 h-5 flex-shrink-0" />
              {pkgError}
              <button onClick={() => setPkgError('')} className="ms-auto hover:text-rose-300">
                <X className="w-4 h-4" />
              </button>
            </div>
          )}

          {pkgSuccess && (
            <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center gap-3">
              <Check className="w-5 h-5 flex-shrink-0" />
              {pkgSuccess}
            </div>
          )}

          <div className="glass-panel p-6 space-y-4 mb-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-black font-semibold">
                <Settings className="w-5 h-5 text-black" />
                إعدادات الجلسة الفردية (للزوار)
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex-1 max-w-xs">
                <label className="block text-xs text-gray-500 mb-1">سعر الجلسة الفردية ($)</label>
                <div className="flex gap-2">
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={singleSessionPrice}
                    onChange={(e) => setSingleSessionPrice(e.target.value)}
                    className="w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-2 text-black placeholder-gray-400 focus:outline-none focus:border-black/50 focus:ring-2 focus:ring-gray-500/10 transition-all text-sm"
                  />
                  <button
                    onClick={handleSaveSessionPrice}
                    className="px-4 py-2 bg-black text-white hover:bg-gray-800 rounded-lg text-sm font-semibold transition-colors whitespace-nowrap"
                  >
                    حفظ Price
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div className="glass-panel p-6 space-y-6">
            <div className="flex items-center justify-between border-b border-gray-200 pb-4">
              <div className="flex items-center gap-2 text-black font-semibold">
                <Package className="w-5 h-5 text-black" />باقات الاشتراك</div>
              <button
                onClick={() => { setShowAddPkg(!showAddPkg); setPkgError(''); }}
                className="px-4 py-2 bg-black text-white hover:bg-gray-800 text-white font-semibold rounded-lg transition-colors flex items-center gap-2 text-sm"
              >
                <Plus className="w-4 h-4" />إضافة باقة</button>
            </div>

            {/* Add Package Form */}
            {showAddPkg && (
              <div className="bg-white rounded-xl p-5 border border-black/20 space-y-4 animate-in fade-in slide-in-from-top-2 duration-300">
                <p className="text-sm text-gray-500 font-medium">باقة جديدة</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Package الاسم</label>
                    <input
                      type="text"
                      value={newPkgForm.name}
                      onChange={(e) => setNewPkgForm({ ...newPkgForm, name: e.target.value })}
                      className="w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-2.5 text-black placeholder-gray-400 focus:outline-none focus:border-black/50 focus:ring-2 focus:ring-gray-500/10 transition-all text-sm"
                      placeholder="e.g. 6-Month Access"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">السعر ($)</label>
                    <input
                      type="number"
                      min="0"
                      step="0.01"
                      value={newPkgForm.price}
                      onChange={(e) => setNewPkgForm({ ...newPkgForm, price: e.target.value })}
                      className="w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-2.5 text-black placeholder-gray-400 focus:outline-none focus:border-black/50 focus:ring-2 focus:ring-gray-500/10 transition-all text-sm"
                      placeholder="0.00"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">المدة (أيام)</label>
                    <input
                      type="number"
                      min="1"
                      value={newPkgForm.duration_days}
                      onChange={(e) => setNewPkgForm({ ...newPkgForm, duration_days: e.target.value })}
                      className="w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-2.5 text-black placeholder-gray-400 focus:outline-none focus:border-black/50 focus:ring-2 focus:ring-gray-500/10 transition-all text-sm"
                      placeholder="30"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">جلسات (فارغ = غير محدود)</label>
                    <input
                      type="number"
                      min="1"
                      value={newPkgForm.sessions}
                      onChange={(e) => setNewPkgForm({ ...newPkgForm, sessions: e.target.value })}
                      className="w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-2.5 text-black placeholder-gray-400 focus:outline-none focus:border-black/50 focus:ring-2 focus:ring-gray-500/10 transition-all text-sm"
                      placeholder="∞"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">النوع (إضافية؟)</label>
                    <div className="flex items-center h-[42px]">
                      <button
                        type="button"
                        onClick={() => setNewPkgForm({ ...newPkgForm, is_addon: !newPkgForm.is_addon })}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-200 ease-in-out focus:outline-none ${newPkgForm.is_addon ? 'bg-emerald-500' : 'bg-gray-200'}`}
                      >
                        <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition duration-200 ease-in-out ${newPkgForm.is_addon ? '-translate-x-6' : '-translate-x-1'}`} />
                      </button>
                    </div>
                  </div>
                </div>
                <div className="flex gap-3">
                  <button
                    onClick={handleAddPackage}
                    className="px-5 py-2.5 bg-black text-white hover:bg-gray-800 text-white font-semibold rounded-lg transition-colors flex items-center gap-2 text-sm"
                  >
                    <Check className="w-4 h-4" />إنشاء</button>
                  <button
                    onClick={() => { setShowAddPkg(false); setNewPkgForm({ name: '', price: '', duration_days: '', sessions: '', is_addon: false }); }}
                    className="px-5 py-2.5 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg transition-colors text-sm"
                  >إلغاء</button>
                </div>
              </div>
            )}

            {/* Packages Table */}
            {pkgLoading ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-3 border-black border-t-transparent"></div>
              </div>
            ) : packages.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                لا توجد باقات معدّة. Add your first package above.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-start border-collapse">
                  <thead>
                    <tr className="border-b border-gray-200 text-gray-500 text-sm">
                      <th className="pb-3 font-medium">Package الاسم</th>
                      <th className="pb-3 font-medium text-end">السعر</th>
                      <th className="pb-3 font-medium text-end">المدة (أيام)</th>
                      <th className="pb-3 font-medium text-end">الجلسات</th>
                      <th className="pb-3 font-medium text-end">النوع</th>
                      <th className="pb-3 font-medium text-end w-32">إجراءات</th>
                    </tr>
                  </thead>
                  <tbody>
                    {packages.map((pkg) => (
                      <tr key={pkg.id} className="border-b border-gray-200/50 hover:bg-gray-100/20 transition-colors">
                        {editingPkg === pkg.id ? (
                          <>
                            <td className="py-3">
                              <input
                                type="text"
                                value={editForm.name}
                                onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                                className="w-full bg-gray-50 border border-gray-300 rounded-lg px-3 py-2 text-black text-sm focus:outline-none focus:border-black/50"
                              />
                            </td>
                            <td className="py-3">
                              <input
                                type="number"
                                min="0"
                                step="0.01"
                                value={editForm.price}
                                onChange={(e) => setEditForm({ ...editForm, price: e.target.value })}
                                className="w-24 bg-gray-50 border border-gray-300 rounded-lg px-3 py-2 text-black text-sm text-end focus:outline-none focus:border-black/50 ms-auto block"
                              />
                            </td>
                            <td className="py-3">
                              <input
                                type="number"
                                min="1"
                                value={editForm.duration_days}
                                onChange={(e) => setEditForm({ ...editForm, duration_days: e.target.value })}
                                className="w-20 bg-gray-50 border border-gray-300 rounded-lg px-3 py-2 text-black text-sm text-end focus:outline-none focus:border-black/50 ms-auto block"
                              />
                            </td>
                            <td className="py-3">
                              <input
                                type="number"
                                min="0"
                                value={editForm.sessions}
                                onChange={(e) => setEditForm({ ...editForm, sessions: e.target.value })}
                                className="w-20 bg-gray-50 border border-gray-300 rounded-lg px-3 py-2 text-black text-sm text-end focus:outline-none focus:border-black/50 ms-auto block"
                                placeholder="∞"
                              />
                            </td>
                            <td className="py-3 text-end">
                              <div className="flex justify-end">
                                <button
                                  type="button"
                                  onClick={() => setEditForm({ ...editForm, is_addon: !editForm.is_addon })}
                                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-200 ease-in-out focus:outline-none ${editForm.is_addon ? 'bg-emerald-500' : 'bg-gray-200'}`}
                                >
                                  <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition duration-200 ease-in-out ${editForm.is_addon ? '-translate-x-6' : '-translate-x-1'}`} />
                                </button>
                              </div>
                            </td>
                            <td className="py-3 text-end">
                              <div className="flex gap-2 justify-end">
                                <button
                                  onClick={() => handleEditPackage(pkg.id)}
                                  className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 transition-colors"
                                >
                                  <Save className="w-4 h-4" />
                                </button>
                                <button
                                  onClick={() => setEditingPkg(null)}
                                  className="p-2 rounded-lg bg-gray-200 text-gray-500 hover:bg-gray-300 transition-colors"
                                >
                                  <X className="w-4 h-4" />
                                </button>
                              </div>
                            </td>
                          </>
                        ) : (
                          <>
                            <td className="py-4">
                              <span className="font-medium text-black">{pkg.name}</span>
                            </td>
                            <td className="py-4 text-end">
                              <span className="font-bold text-emerald-400">£{pkg.price.toFixed(0)}</span>
                            </td>
                            <td className="py-4 text-end">
                              <span className="text-gray-700">{pkg.duration_days} أيام</span>
                            </td>
                            <td className="py-4 text-end">
                              {pkg.sessions !== null ? (
                                <span className="text-gray-700">{pkg.sessions}</span>
                              ) : (
                                <span className="text-gray-500 flex items-center gap-1 justify-end">
                                  <Infinity className="w-4 h-4" />غير محدود</span>
                              )}
                            </td>
                            <td className="py-4 text-end">
                              <span className={`px-2 py-1 text-xs rounded ${pkg.is_addon ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-600'}`}>
                                {pkg.is_addon ? 'إضافية (Add-on)' : 'أساسية'}
                              </span>
                            </td>
                            <td className="py-4 text-end">
                              <div className="flex gap-2 justify-end">
                                <button
                                  onClick={() => startEditPkg(pkg)}
                                  className="p-2 rounded-lg bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors"
                                  title="Edit"
                                >
                                  <Edit3 className="w-4 h-4" />
                                </button>
                                <button
                                  onClick={() => handleDeletePackage(pkg.id)}
                                  className="p-2 rounded-lg bg-rose-500/10 text-rose-400 hover:bg-rose-500/20 transition-colors"
                                  title="Delete"
                                >
                                  <Trash2 className="w-4 h-4" />
                                </button>
                              </div>
                            </td>
                          </>
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ═══ RECEPTIONISTS TAB ═══ */}
      {activeTab === 'receptionists' && (
        <div className="space-y-6">
          {pkgError && (
            <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 flex items-center gap-3">
              <AlertTriangle className="w-5 h-5 flex-shrink-0" />
              {pkgError}
              <button onClick={() => setPkgError('')} className="ms-auto hover:text-rose-300">
                <X className="w-4 h-4" />
              </button>
            </div>
          )}

          {pkgSuccess && (
            <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center gap-3">
              <Check className="w-5 h-5 flex-shrink-0" />
              {pkgSuccess}
            </div>
          )}

          <div className="glass-panel p-6 space-y-6">
            <div className="flex items-center justify-between border-b border-gray-200 pb-4">
              <div className="flex items-center gap-2 text-black font-semibold">
                <UserCircle className="w-5 h-5 text-black" />موظفو الاستقبال</div>
              <button
                onClick={() => { setShowAddRec(!showAddRec); setPkgError(''); }}
                className="px-4 py-2 bg-black text-white hover:bg-gray-800 text-white font-semibold rounded-lg transition-colors flex items-center gap-2 text-sm"
              >
                <Plus className="w-4 h-4" />
                إضافة موظف استقبال
              </button>
            </div>

            {/* إضافة موظف استقبال Form */}
            {showAddRec && (
              <div className="bg-white rounded-xl p-5 border border-black/20 space-y-4 animate-in fade-in slide-in-from-top-2 duration-300">
                <p className="text-sm text-gray-500 font-medium">موظف استقبال جديد</p>
                <div className="max-w-md">
                  <label className="block text-xs text-gray-500 mb-1">الاسم</label>
                  <input
                    type="text"
                    value={newRecForm.name}
                    onChange={(e) => setNewRecForm({ ...newRecForm, name: e.target.value })}
                    className="w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-2.5 text-black placeholder-gray-400 focus:outline-none focus:border-black/50 focus:ring-2 focus:ring-gray-500/10 transition-all text-sm"
                    placeholder="e.g. John Doe"
                  />
                </div>
                <div className="flex gap-3">
                  <button
                    onClick={handleAddReceptionist}
                    className="px-5 py-2.5 bg-black text-white hover:bg-gray-800 text-white font-semibold rounded-lg transition-colors flex items-center gap-2 text-sm"
                  >
                    <Check className="w-4 h-4" />إنشاء</button>
                  <button
                    onClick={() => { setShowAddRec(false); setNewRecForm({ name: '' }); }}
                    className="px-5 py-2.5 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg transition-colors text-sm"
                  >إلغاء</button>
                </div>
              </div>
            )}

            {/* Receptionists Table */}
            {receptionists.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                لا يوجد موظفي استقبال.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-start border-collapse">
                  <thead>
                    <tr className="border-b border-gray-200 text-gray-500 text-sm">
                      <th className="pb-3 font-medium">رقم</th>
                      <th className="pb-3 font-medium">الاسم</th>
                      <th className="pb-3 font-medium text-end w-32">إجراءات</th>
                    </tr>
                  </thead>
                  <tbody>
                    {receptionists.map((rec) => (
                      <tr key={rec.id} className="border-b border-gray-200/50 hover:bg-gray-100/20 transition-colors">
                        {editingRec === rec.id ? (
                          <>
                            <td className="py-3">
                              <span className="text-gray-500 text-sm">#{rec.id}</span>
                            </td>
                            <td className="py-3">
                              <input
                                type="text"
                                value={editRecForm.name}
                                onChange={(e) => setEditRecForm({ ...editRecForm, name: e.target.value })}
                                className="w-full bg-gray-50 border border-gray-300 rounded-lg px-3 py-2 text-black text-sm focus:outline-none focus:border-black/50"
                              />
                            </td>
                            <td className="py-3 text-end">
                              <div className="flex gap-2 justify-end">
                                <button
                                  onClick={() => handleEditReceptionist(rec.id)}
                                  className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 transition-colors"
                                >
                                  <Save className="w-4 h-4" />
                                </button>
                                <button
                                  onClick={() => setEditingRec(null)}
                                  className="p-2 rounded-lg bg-gray-200 text-gray-500 hover:bg-gray-300 transition-colors"
                                >
                                  <X className="w-4 h-4" />
                                </button>
                              </div>
                            </td>
                          </>
                        ) : (
                          <>
                            <td className="py-4">
                              <span className="text-gray-500 text-sm">#{rec.id}</span>
                            </td>
                            <td className="py-4">
                              <span className="font-medium text-black">{rec.name}</span>
                            </td>
                            <td className="py-4 text-end">
                              <div className="flex gap-2 justify-end">
                                <button
                                  onClick={() => {
                                    setEditingRec(rec.id);
                                    setEditRecForm({ name: rec.name });
                                  }}
                                  className="p-2 rounded-lg bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors"
                                  title="Edit"
                                >
                                  <Edit3 className="w-4 h-4" />
                                </button>
                                <button
                                  onClick={() => handleDeleteReceptionist(rec.id)}
                                  className="p-2 rounded-lg bg-rose-500/10 text-rose-400 hover:bg-rose-500/20 transition-colors"
                                  title="Delete"
                                >
                                  <Trash2 className="w-4 h-4" />
                                </button>
                              </div>
                            </td>
                          </>
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      
      {/* ═══ FINANCES TAB ═══ */}
      {activeTab === 'finances' && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-300">
          {pkgError && (
            <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 flex items-center gap-3">
              <AlertTriangle className="w-5 h-5 flex-shrink-0" />
              {pkgError}
              <button onClick={() => setPkgError('')} className="ms-auto hover:text-rose-300"><X className="w-4 h-4" /></button>
            </div>
          )}
          {pkgSuccess && (
            <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center gap-3">
              <Check className="w-5 h-5 flex-shrink-0" />
              {pkgSuccess}
            </div>
          )}

          {/* التاريخ Filter */}
          <div className="glass-panel p-6 flex flex-wrap items-end gap-4">
            <div>
              <label className="block text-sm text-gray-500 mb-1">الفترة الزمنية</label>
              <select value={financePeriod} onChange={e => setFinancePeriod(e.target.value)} className="bg-gray-50 border border-gray-200 rounded-lg px-4 py-2 text-sm text-black">
                <option value="lifetime">كل الوقت</option>
                <option value="last_month">الشهر الماضي</option>
                <option value="last_3_months">آخر 3 أشهر</option>
                <option value="last_6_months">آخر 6 أشهر</option>
                <option value="this_year">هذا العام</option>
                <option value="custom">مخصص</option>
              </select>
            </div>
            {financePeriod === 'custom' && (
              <>
                <div>
                  <label className="block text-sm text-gray-500 mb-1">تاريخ البدء</label>
                  <input type="date" value={financeStart} onChange={e=>setFinanceStart(e.target.value)} className="bg-gray-50 border border-gray-200 rounded-lg px-4 py-2 text-sm text-black" />
                </div>
                <div>
                  <label className="block text-sm text-gray-500 mb-1">تاريخ الانتهاء</label>
                  <input type="date" value={financeEnd} onChange={e=>setFinanceEnd(e.target.value)} className="bg-gray-50 border border-gray-200 rounded-lg px-4 py-2 text-sm text-black" />
                </div>
                <button onClick={handleCalculateFinances} className="px-6 py-2 bg-black text-white rounded-lg font-semibold hover:bg-gray-800 transition-colors text-sm h-[38px]">حساب</button>
              </>
            )}
            {financePeriod === 'custom' && filteredFinances && (
              <button onClick={() => { setFinancePeriod('lifetime'); }} className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 transition-colors text-sm h-[38px]">مسح التصفية</button>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6">
            <div className="glass-panel p-6 border-emerald-500/20 border-2">
              <div className="text-sm font-medium text-gray-500 mb-1 flex items-center gap-2"><TrendingUp className="w-4 h-4 text-emerald-500"/> صافي الأرباح</div>
              <div className="text-3xl font-bold text-black">${(filteredFinances ? filteredFinances.net_revenue : data.net_revenue)?.toFixed(2) || '0.00'}</div>
            </div>
            <div className="glass-panel p-6">
              <div className="text-sm font-medium text-gray-500 mb-1 flex items-center gap-2"><Briefcase className="w-4 h-4 text-rose-500"/>رواتب</div>
              <div className="text-3xl font-bold text-black">${(filteredFinances ? filteredFinances.total_salaries : data.total_salaries)?.toFixed(2) || '0.00'}</div>
            </div>
            <div className="glass-panel p-6">
              <div className="text-sm font-medium text-gray-500 mb-1 flex items-center gap-2"><Settings className="w-4 h-4 text-amber-500"/> إصلاح وصيانة</div>
              <div className="text-3xl font-bold text-black">${(filteredFinances ? filteredFinances.total_maintenance : data.total_maintenance)?.toFixed(2) || '0.00'}</div>
            </div>
            <div className="glass-panel p-6">
              <div className="text-sm font-medium text-gray-500 mb-1 flex items-center gap-2"><Receipt className="w-4 h-4 text-cyan-500"/>فواتير</div>
              <div className="text-3xl font-bold text-black">${(filteredFinances ? filteredFinances.total_bills : data.total_bills)?.toFixed(2) || '0.00'}</div>
            </div>
            <div className="glass-panel p-6">
              <div className="text-sm font-medium text-gray-500 mb-1 flex items-center gap-2"><Settings className="w-4 h-4 text-purple-500"/>أخرى</div>
              <div className="text-3xl font-bold text-black">${(filteredFinances ? filteredFinances.total_other : data.total_other)?.toFixed(2) || '0.00'}</div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="glass-panel p-6 space-y-4">
              <div className="flex items-center justify-between border-b border-gray-200 pb-3">
                <h3 className="font-semibold text-black flex items-center gap-2"><TrendingDown className="w-5 h-5"/> تسجيل المصروف</h3>
                <button onClick={() => setShowAddExpense(!showAddExpense)} className="p-2 bg-gray-200 hover:bg-gray-300 rounded-lg text-black transition-colors"><Plus className="w-4 h-4"/></button>
              </div>
              {showAddExpense && (
                <div className="space-y-3">
                  <select value={newExpenseForm.category} onChange={e=>setNewExpenseForm({...newExpenseForm, category: e.target.value})} className="w-full bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm">
                    <option value="Maintenance">إصلاح وصيانة</option>
                    <option value="Bill">فاتورة</option>
                    <option value="Other">أخرى</option>
                  </select>
                  <input type="number" placeholder="المبلغ ($)" value={newExpenseForm.amount} onChange={e=>setNewExpenseForm({...newExpenseForm, amount: e.target.value})} className="w-full bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm"/>
                  <input type="text" placeholder="الوصف (Optional)" value={newExpenseForm.description} onChange={e=>setNewExpenseForm({...newExpenseForm, description: e.target.value})} className="w-full bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm"/>
                  <button onClick={handleAddExpense} className="w-full py-3 bg-black text-white font-semibold rounded-lg hover:bg-gray-800 transition-colors">تسجيل المصروف</button>
                </div>
              )}
            </div>
            
            <div className="glass-panel p-6">
              <h3 className="font-semibold text-black flex items-center gap-2 mb-4 border-b border-gray-200 pb-3"><Activity className="w-5 h-5"/>سجل المصروفات والأرباح</h3>
              <div className="overflow-auto max-h-[400px] custom-scrollbar pe-2">
                <table className="w-full text-start border-collapse">
                  <thead>
                    <tr className="border-b border-gray-200 text-gray-500 text-sm">
                      <th className="pb-3 font-medium">النوع</th>
                      <th className="pb-3 font-medium">الوصف</th>
                      <th className="pb-3 font-medium">التاريخ والوقت</th>
                      <th className="pb-3 font-medium text-end">القيمة</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(filteredFinances ? filteredFinances.finance_history : data.finance_history)?.map((item, idx) => (
                      <tr key={idx} className="border-b border-gray-200/50">
                        <td className="py-3">
                          <span className={`px-2 py-1 text-xs font-bold rounded-lg text-white ${
                            item.type === 'Maintenance' ? 'bg-amber-500' :
                            item.type === 'Bill' ? 'bg-cyan-500' :
                            item.type === 'Salary' ? 'bg-rose-500' :
                            item.type === 'Income' ? 'bg-emerald-500' :
                            'bg-purple-500'
                          }`}>
                            {item.type === 'Maintenance' ? 'إصلاح وصيانة' :
                             item.type === 'Bill' ? 'فاتورة' :
                             item.type === 'Salary' ? 'راتب' :
                             item.type === 'Income' ? 'دخل' : 'أخرى'}
                          </span>
                        </td>
                        <td className="py-3 text-sm text-gray-700">{item.description || '-'}</td>
                        <td className="py-3 text-sm text-gray-500">{new Date(item.date).toLocaleString('ar-EG')}</td>
                        <td className="py-3 text-end font-bold text-sm">
                          <span className={item.amount > 0 ? 'text-black' : 'text-emerald-500'}>
                            {item.amount > 0 ? '-' : '+'}${Math.abs(item.amount).toFixed(2)}
                          </span>
                        </td>
                      </tr>
                    ))}
                    {(!filteredFinances && !data.finance_history?.length) || (filteredFinances && !filteredFinances.finance_history?.length) ? (
                      <tr>
                        <td colSpan="4" className="py-8 text-center text-gray-500">لا يوجد سجلات متاحة.</td>
                      </tr>
                    ) : null}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ═══ MANAGE STAFF TAB ═══ */}
      {activeTab === 'staff' && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-300">
          {pkgError && (
            <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 flex items-center gap-3">
              <AlertTriangle className="w-5 h-5 flex-shrink-0" />
              {pkgError}
              <button onClick={() => setPkgError('')} className="ms-auto hover:text-rose-300"><X className="w-4 h-4" /></button>
            </div>
          )}
          {pkgSuccess && (
            <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center gap-3">
              <Check className="w-5 h-5 flex-shrink-0" />
              {pkgSuccess}
            </div>
          )}

          <div className="glass-panel p-6 space-y-6">
            <div className="flex items-center justify-between border-b border-gray-200 pb-3">
              <h3 className="font-semibold text-black flex items-center gap-2"><Briefcase className="w-5 h-5"/>الموظفين</h3>
              <button onClick={() => setShowAddStaff(!showAddStaff)} className="px-4 py-2 bg-black text-white hover:bg-gray-800 font-semibold rounded-lg transition-colors flex items-center gap-2 text-sm"><Plus className="w-4 h-4"/> إضافة موظف</button>
            </div>
            {showAddStaff && (
              <div className="bg-white rounded-xl p-5 border border-black/20 space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
                  <input type="text" placeholder="الاسم" value={newStaffForm.name} onChange={e=>setNewStaffForm({...newStaffForm, name: e.target.value})} className="w-full bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm"/>
                  <input type="text" placeholder="Phone" value={newStaffForm.phone} onChange={e=>setNewStaffForm({...newStaffForm, phone: e.target.value})} className="w-full bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm"/>
                  <input type="text" placeholder="Role (e.g. Trainer)" value={newStaffForm.role} onChange={e=>setNewStaffForm({...newStaffForm, role: e.target.value})} className="w-full bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm"/>
                  <input type="number" placeholder="الراتب/mo" value={newStaffForm.base_salary} onChange={e=>setNewStaffForm({...newStaffForm, base_salary: e.target.value})} className="w-full bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm"/>
                  <div className="flex items-center gap-2">
                    <label className="text-xs text-gray-500">يوم الدفع</label>
                    <input type="number" min="1" max="31" placeholder="Day (1-31)" value={newStaffForm.pay_day} onChange={e=>setNewStaffForm({...newStaffForm, pay_day: e.target.value})} className="w-full bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm"/>
                  </div>
                </div>
                <div className="flex gap-3">
                  <button onClick={handleAddStaff} className="px-5 py-2.5 bg-black text-white font-semibold rounded-lg hover:bg-gray-800 transition-colors text-sm">إضافة موظف العضو</button>
                  <button onClick={() => setShowAddStaff(false)} className="px-5 py-2.5 bg-gray-200 text-gray-700 font-semibold rounded-lg hover:bg-gray-300 transition-colors text-sm">إلغاء</button>
                </div>
              </div>
            )}
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-4">
              {staffList.map(staff => (
                <div key={staff.id} className="glass-panel p-6 space-y-5 relative group min-h-[180px]">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="text-2xl font-bold text-black flex items-center gap-3">
                        {staff.name}
                        <button onClick={() => deleteStaff(staff.id).then(fetchStaff)} className="opacity-0 group-hover:opacity-100 transition-opacity p-2 bg-rose-500/10 text-rose-500 hover:bg-rose-500 hover:text-white rounded-lg">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                      <div className="text-sm font-medium text-violet-600 mb-1">{staff.role}</div>
                      <div className="text-sm text-gray-500">{staff.phone ? `Phone: ${staff.phone}` : 'No phone listed'}</div>
                      <div className="text-sm text-gray-500">Pays on the {staff.pay_day} of every month</div>
                    </div>
                    <div className="text-end">
                      <div className="text-3xl font-bold text-black">${staff.base_salary}</div>
                      <div className="text-sm text-gray-400">/ شهر</div>
                    </div>
                  </div>
                  
                  <div className="bg-gray-50 rounded-lg p-5 border border-gray-200 space-y-4">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-500">آخر دفعة:</span>
                      <span className="font-semibold text-black">{format(new Date(staff.last_paid_date), 'MMM d, yyyy')}</span>
                    </div>
                    <div className="flex gap-4">
                      <div className="flex-1 bg-emerald-100 rounded px-3 py-2 text-sm flex justify-between items-center border border-emerald-200">
                        <span className="text-emerald-700 font-semibold">مكافأة معلقة:</span> <span className="font-bold text-emerald-800">${staff.pending_bonus}</span>
                      </div>
                      <div className="flex-1 bg-rose-100 rounded px-3 py-2 text-sm flex justify-between items-center border border-rose-200">
                        <span className="text-rose-700 font-semibold">خصم معلق:</span> <span className="font-bold text-rose-800">${staff.pending_deduction}</span>
                      </div>
                    </div>
                    
                    <div className="flex gap-3 pt-4 border-t border-gray-200 mt-4 items-end">
                      <div className="flex-1">
                        <label className="block text-xs font-semibold text-emerald-700 mb-1.5">إضافة مكافأة (+)</label>
                        <input type="number" id={`bonus-${staff.id}`} placeholder="+ مكافأة" className="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-black focus:ring-1 focus:ring-black" defaultValue={staff.pending_bonus}/>
                      </div>
                      <div className="flex-1">
                        <label className="block text-xs font-semibold text-rose-700 mb-1.5">إضافة خصم (-)</label>
                        <input type="number" id={`deduct-${staff.id}`} placeholder="- خصم" className="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-black focus:ring-1 focus:ring-black" defaultValue={staff.pending_deduction}/>
                      </div>
                      <button onClick={() => handleUpdatePending(staff.id, document.getElementById(`bonus-${staff.id}`).value, document.getElementById(`deduct-${staff.id}`).value)} className="w-[100px] h-[38px] bg-black text-white rounded-lg text-sm font-semibold hover:bg-gray-800 transition-colors">تطبيق</button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
      {/* ═══ SETTINGS TAB ═══ */}
      {activeTab === 'settings' && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
           
           {/* Mock Time Settings */}
           <div className="glass-panel p-6 space-y-4">
             <div className="flex items-center gap-2 text-black font-semibold border-b border-gray-200 pb-4">
               <Clock className="w-5 h-5 text-cyan-500" />
               إعدادات الوقت الوهمي (Mock Clock)
             </div>
             
             <div className="max-w-md space-y-4 pt-2 flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-black">تفعيل الوقت الوهمي</p>
                  <p className="text-xs text-gray-500 mt-1">عند التعطيل، سيعمل النظام كاملاً بتوقيت القاهرة الفعلي ولن يتم عرض شريط الوقت الوهمي.</p>
                </div>
                <button 
                  onClick={async () => {
                    try {
                      await toggleMockTime(!mockEnabled);
                      window.location.reload();
                    } catch (e) {
                      setPkgError("فشل تغيير إعدادات الوقت الوهمي");
                    }
                  }}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-200 ease-in-out focus:outline-none ${mockEnabled ? 'bg-emerald-500' : 'bg-gray-200'}`}
                >
                  <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition duration-200 ease-in-out ${mockEnabled ? '-translate-x-6' : '-translate-x-1'}`} />
                </button>
             </div>
           </div>

           {/* Change Password Block */}
           <div className="glass-panel p-6 space-y-4">
            <div className="flex items-center gap-2 text-black font-semibold border-b border-gray-200 pb-4">
              <Settings className="w-5 h-5 text-black" />
              تغيير كلمة مرور الإدارة
            </div>
            
            <div className="max-w-md space-y-4 pt-2">
              <div>
                <label className="block text-sm text-gray-500 mb-1">كلمة المرور الحالية</label>
                <input
                  type="password"
                  value={oldPasswordForm}
                  onChange={(e) => setOldPasswordForm(e.target.value)}
                  className="w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-2 text-black focus:outline-none focus:border-black/50"
                  placeholder="أدخل كلمة المرور الحالية"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-500 mb-1">كلمة المرور الجديدة</label>
                <input
                  type="password"
                  value={newPasswordForm}
                  onChange={(e) => setNewPasswordForm(e.target.value)}
                  className="w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-2 text-black focus:outline-none focus:border-black/50"
                  placeholder="أدخل كلمة المرور الجديدة"
                />
              </div>
              <button
                onClick={handleChangeAdminPassword}
                disabled={isChangingPassword}
                className="w-full bg-black text-white hover:bg-gray-800 font-semibold py-2.5 rounded-lg transition-colors flex justify-center items-center gap-2"
              >
                {isChangingPassword ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                ) : (
                  <>
                    <Save className="w-4 h-4" />
                    حفظ كلمة المرور
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Factory Reset Block */}
          <div className="glass-panel p-6 space-y-4 border-rose-500/20 border-2 mt-6">
            <div className="flex items-center gap-2 text-rose-500 font-semibold border-b border-rose-500/20 pb-4">
              <AlertTriangle className="w-5 h-5" />
              منطقة الخطر (إعادة ضبط المصنع)
            </div>
            
            <div className="max-w-md space-y-4 pt-2">
              <p className="text-sm text-gray-600">
                سيؤدي هذا الإجراء إلى مسح جميع السجلات وقواعد البيانات (الأعضاء، الاشتراكات، المصروفات، المدفوعات). سيتم الاحتفاظ فقط بإعدادات الباقات، الموظفين، وحسابات الاستقبال. استخدم هذا الخيار لتجهيز النظام للاستخدام التجاري بعد الانتهاء من فترة التجربة.
              </p>
              <button
                onClick={handleFactoryReset}
                className="w-full bg-rose-500 text-white hover:bg-rose-600 font-semibold py-2.5 rounded-lg transition-colors flex justify-center items-center gap-2"
              >
                <Trash2 className="w-4 h-4" />
                مسح جميع السجلات والبيانات
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default Dashboard;
