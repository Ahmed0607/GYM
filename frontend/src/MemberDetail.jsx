import React, { useState, useEffect, useMemo, useContext } from 'react';
import {
  ArrowLeft, Edit3, Trash2, DollarSign, RefreshCw, CheckCircle2,
  AlertCircle, Clock, Phone, Hash, Package, Calendar, CreditCard,
  Activity, History, Check, X, Save, AlertTriangle, Tag, Snowflake
} from 'lucide-react';
import { format } from 'date-fns';
import { getMember, updateMember, deleteMember, payDebt, updateSubscription, listPackages, freezeMember, unfreezeMember, consumeAddon, verifyAdminPassword } from './api';
import { ServerTimeContext, ReceptionistContext } from './App';

const MemberDetail = ({ memberId, onBack }) => {
  const serverTime = useContext(ServerTimeContext) || new Date();
  const { activeReceptionist, setActiveReceptionist } = useContext(ReceptionistContext) || {};
  
  const [member, setMember] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Admin auth state for protected actions
  const [showAdminLogin, setShowAdminLogin] = useState(false);
  const [adminPassword, setAdminPassword] = useState('');
  const [adminLoginError, setAdminLoginError] = useState('');
  const [adminActionType, setAdminActionType] = useState(null);

  // Edit Profile state
  const [editingProfile, setEditingProfile] = useState(false);
  const [editName, setEditName] = useState('');
  const [editPhone, setEditPhone] = useState('');

  // Pay Debt state
  const [showPayDebt, setShowPayDebt] = useState(false);
  const [paymentAmount, setPaymentAmount] = useState('');

  // Change Subscription state
  const [showChangeSub, setShowChangeSub] = useState(false);
  const [selectedPackages, setSelectedPackages] = useState(new Set());
  const [subAmountPaid, setSubAmountPaid] = useState('');
  const [subDiscount, setSubDiscount] = useState('');
  const [packages, setPackages] = useState([]);

  // Freeze state
  const [showFreeze, setShowFreeze] = useState(false);
  const [freezeWeeks, setFreezeWeeks] = useState(2);

  // Delete confirmation
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  // Saving states
  const [savingProfile, setSavingProfile] = useState(false);
  const [savingPayment, setSavingPayment] = useState(false);
  const [savingSub, setSavingSub] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [freezing, setFreezing] = useState(false);

  const fetchMember = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await getMember(memberId);
      setMember(data);
      setEditName(data.name);
      setEditPhone(data.phone);
    } catch (err) {
      setError('Failed to load member details.');
    } finally {
      setLoading(false);
    }
  };

  const fetchPackages = async () => {
    try {
      const data = await listPackages();
      setPackages(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchMember();
    fetchPackages();
  }, [memberId]);

  const showSuccessMessage = (msg) => {
    setSuccess(msg);
    setTimeout(() => setSuccess(''), 3000);
  };

  // ─── Profile Edit ──────────────────────────────────────────────────────

  const handleSaveProfile = async () => {
    setSavingProfile(true);
    try {
      const updated = await updateMember(memberId, { name: editName, phone: editPhone });
      setMember(updated);
      setEditingProfile(false);
      showSuccessMessage('Profile updated successfully.');
    } catch (err) {
      setError('Failed to update profile.');
    } finally {
      setSavingProfile(false);
    }
  };

  // ─── Pay Debt ──────────────────────────────────────────────────────────

  const handlePayDebt = async () => {
    const amount = parseFloat(paymentAmount);
    if (!amount || amount <= 0) return;
    setSavingPayment(true);
    try {
      const updated = await payDebt(memberId, amount);
      setMember(updated);
      setShowPayDebt(false);
      setPaymentAmount('');
      showSuccessMessage(`Payment من $${amount.toFixed(2)} recorded.`);
    } catch (err) {
      setError('Failed to record payment.');
    } finally {
      setSavingPayment(false);
    }
  };

  // ─── Change Subscription / Renew ───────────────────────────────────────

  const latestSub = member?.subscriptions?.[member.subscriptions.length - 1];

  const handleRenewClick = () => {
    if (activeReceptionist !== 'admin') {
      setAdminActionType('renew');
      setShowAdminLogin(true);
      return;
    }
    
    if (!showChangeSub) {
      if (latestSub && latestSub.package_name) {
        const ids = packages.filter(p => latestSub.package_name.includes(p.name)).map(p => p.id);
        setSelectedPackages(new Set(ids));
      } else {
        setSelectedPackages(new Set());
      }
    }
    setShowChangeSub(!showChangeSub);
  };

  const handlePayDebtClick = () => {
    if (activeReceptionist !== 'admin') {
      setAdminActionType('pay_debt');
      setShowAdminLogin(true);
      return;
    }
    setShowPayDebt(!showPayDebt);
  };

  const handleAdminLoginSubmit = async (e) => {
    e.preventDefault();
    if (!adminPassword) return;
    try {
      setAdminLoginError('');
      await verifyAdminPassword(adminPassword);
      sessionStorage.setItem('adminAuthenticated', 'true');
      if (setActiveReceptionist) setActiveReceptionist('admin');
      setShowAdminLogin(false);
      setAdminPassword('');
      
      if (adminActionType === 'renew') {
        if (!showChangeSub) {
          if (latestSub && latestSub.package_name) {
            const ids = packages.filter(p => latestSub.package_name.includes(p.name)).map(p => p.id);
            setSelectedPackages(new Set(ids));
          } else {
            setSelectedPackages(new Set());
          }
        }
        setShowChangeSub(true);
      } else if (adminActionType === 'pay_debt') {
        setShowPayDebt(true);
      }
      setAdminActionType(null);
    } catch (err) {
      setAdminLoginError(err.response?.data?.detail || 'كلمة المرور غير صحيحة');
    }
  };

  const selectedItems = useMemo(() => {
    return packages.filter(p => selectedPackages.has(p.id));
  }, [selectedPackages, packages]);

  const newSubTotal = useMemo(() => {
    return selectedItems.reduce((sum, pkg) => sum + pkg.price, 0);
  }, [selectedItems]);

  const newSubDiscount = useMemo(() => {
    const d = parseFloat(subDiscount) || 0;
    return Math.min(Math.max(0, d), newSubTotal);
  }, [subDiscount, newSubTotal]);

  const newEffectivePrice = useMemo(() => {
    return Math.max(0, newSubTotal - newSubDiscount);
  }, [newSubTotal, newSubDiscount]);

  const newSubOwed = useMemo(() => {
    const paid = parseFloat(subAmountPaid) || 0;
    return Math.max(0, newEffectivePrice - paid);
  }, [newEffectivePrice, subAmountPaid]);

  const togglePackage = (pkgId) => {
    const newSelected = new Set(selectedPackages);
    if (newSelected.has(pkgId)) newSelected.delete(pkgId);
    else newSelected.add(pkgId);
    setSelectedPackages(newSelected);
  };

  const handleChangeSub = async () => {
    if (selectedItems.length === 0) return;
    setSavingSub(true);
    try {
      const updated = await updateSubscription(memberId, {
        packages: selectedItems.map(p => p.name),
        amount_paid: parseFloat(subAmountPaid) || 0,
        discount: parseFloat(subDiscount) || 0,
      });
      setMember(updated);
      setShowChangeSub(false);
      setSelectedPackages(new Set());
      setSubAmountPaid('');
      setSubDiscount('');
      showSuccessMessage('Subscription updated. New charges applied.');
    } catch (err) {
      setError('Failed to update subscription.');
    } finally {
      setSavingSub(false);
    }
  };

  // ─── Freeze / Unfreeze ─────────────────────────────────────────────────

  const handleFreezeClick = () => {
    if (member.status !== 'Frozen') {
      setShowFreeze(!showFreeze);
    } else {
      handleUnfreeze();
    }
  };

  const handleUnfreeze = async () => {
    setFreezing(true);
    setError('');
    try {
      const updated = await unfreezeMember(memberId);
      setMember(updated);
      showSuccessMessage('تم إلغاء تجميد العضو بنجاح.');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to change freeze status.');
    } finally {
      setFreezing(false);
    }
  };

  const handleConfirmFreeze = async () => {
    setFreezing(true);
    setError('');
    try {
      const updated = await freezeMember(memberId, freezeWeeks);
      setMember(updated);
      setShowFreeze(false);
      showSuccessMessage(`تم تجميد العضو لمدة ${freezeWeeks === 1 ? 'أسبوع' : 'أسبوعين'}.`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to change freeze status.');
    } finally {
      setFreezing(false);
    }
  };

  // ─── حذف العضو ─────────────────────────────────────────────────────

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await deleteMember(memberId);
      onBack();
    } catch (err) {
      setError('Failed to delete member.');
      setDeleting(false);
    }
  };

  // ─── Addon Consume ───────────────────────────────────────────────────

  const handleConsumeAddon = async (addonName) => {
    try {
      const updatedMember = await consumeAddon(memberId, addonName);
      setMember(updatedMember);
      showSuccessMessage(`تم تسجيل الدخول في ${addonName} بنجاح`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to consume addon.');
    }
  };

  // ─── Render ────────────────────────────────────────────────────────────

  const getStatusColor = (status) => {
    switch (status) {
      case 'Active': return 'text-white bg-green-600 border-green-700';
      case 'Owed Money': return 'text-white bg-amber-500 border-amber-600';
      case 'Expired': return 'text-white bg-red-600 border-red-700';
      case 'Frozen': return 'text-white bg-sky-500 border-sky-600';
      default: return 'text-gray-500 bg-gray-200/50 border-gray-300';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-black border-t-transparent"></div>
      </div>
    );
  }

  if (!member) {
    return (
      <div className="text-center py-16">
        <AlertCircle className="w-12 h-12 text-rose-400 mx-auto mb-4" />
        <p className="text-gray-500 text-lg">{error || 'Member not found.'}</p>
        <button onClick={onBack} className="mt-4 text-cyan-400 hover:text-cyan-300 transition-colors">
          ← العودة للأعضاء
        </button>
      </div>
    );
  }

  const logs = [...(member.attendance_logs || [])].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Back button */}
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-gray-500 hover:text-cyan-400 transition-colors group"
      >
        <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
        <span>العودة للأعضاء</span>
      </button>

      {/* Alerts */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          {error}
          <button onClick={() => setError('')} className="ms-auto hover:text-rose-300">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}
      {success && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center gap-3">
          <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
          {success}
        </div>
      )}

      {/* Header Card */}
      <div className="glass-panel p-8 relative overflow-hidden">

        <div className="flex flex-col md:flex-row justify-between items-start gap-6 relative z-10">
          <div className="flex items-start gap-6">
            {/* ID Badge */}
            <div className="w-20 h-20 bg-gray-200 rounded-2xl flex items-center justify-center border border-gray-300 flex-shrink-0">
              <span className="text-black font-bold text-2xl">#{member.id}</span>
            </div>

            <div>
              {editingProfile ? (
                <div className="space-y-3">
                  <input
                    type="text"
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    className="bg-gray-200 border border-gray-300 rounded-lg px-4 py-2 text-black text-xl font-bold focus:outline-none focus:border-black/50 focus:ring-2 focus:ring-gray-500/10 w-full"
                  />
                  <input
                    type="text"
                    value={editPhone}
                    onChange={(e) => setEditPhone(e.target.value)}
                    className="bg-gray-200 border border-gray-300 rounded-lg px-4 py-2 text-gray-700 focus:outline-none focus:border-black/50 focus:ring-2 focus:ring-gray-500/10 w-full"
                  />
                  <div className="flex gap-2">
                    <button
                      onClick={handleSaveProfile}
                      disabled={savingProfile}
                      className="px-4 py-2 bg-black text-white hover:bg-gray-800 text-white font-semibold rounded-lg transition-colors flex items-center gap-2 text-sm disabled:opacity-50"
                    >
                      {savingProfile ? <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" /> : <Save className="w-4 h-4" />}
                      Save
                    </button>
                    <button
                      onClick={() => { setEditingProfile(false); setEditName(member.name); setEditPhone(member.phone); }}
                      className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg transition-colors text-sm"
                    >
                      إلغاء
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  <h1 className="text-3xl font-bold text-black mb-1">{member.name}</h1>
                  <p className="text-gray-500 text-lg flex items-center gap-2">
                    <Phone className="w-4 h-4" />
                    {member.phone}
                  </p>
                </>
              )}
            </div>
          </div>

          <div className="flex flex-col items-end gap-3">
            <div className={`px-4 py-2 rounded-full border font-medium flex items-center gap-2 ${getStatusColor(member.status)}`}>
              {member.status === 'Active' && <CheckCircle2 className="w-4 h-4" />}
              {member.status === 'Owed Money' && <AlertCircle className="w-4 h-4" />}
              {member.status === 'Expired' && <Clock className="w-4 h-4" />}
              {member.status === 'Frozen' && <Snowflake className="w-4 h-4" />}
              {member.status}
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        <button
          onClick={() => { setEditingProfile(true); setEditName(member.name); setEditPhone(member.phone); }}
          className="glass-panel p-4 flex items-center gap-3 hover:bg-gray-100/60 hover:border-gray-300 transition-all text-start group"
        >
          <div className="p-2 rounded-lg bg-gray-200">
            <Edit3 className="w-5 h-5 text-cyan-400" />
          </div>
          <span className="text-gray-700 font-medium text-sm">تعديل الملف الشخصي</span>
        </button>

        <button
          onClick={handleFreezeClick}
          disabled={freezing}
          className="glass-panel p-4 flex items-center gap-3 hover:bg-gray-100/60 hover:border-gray-300 transition-all text-start group disabled:opacity-50"
        >
          <div className="p-2 rounded-lg bg-sky-500/10">
            {freezing ? (
              <div className="animate-spin rounded-full h-5 w-5 border-2 border-sky-400 border-t-transparent" />
            ) : (
              <Snowflake className="w-5 h-5 text-sky-400" />
            )}
          </div>
          <span className="text-gray-700 font-medium text-sm">{member.status === 'Frozen' ? 'إلغاء التجميد' : 'تجميد'}</span>
        </button>

        <button
          onClick={handlePayDebtClick}
          className="glass-panel p-4 flex items-center gap-3 hover:bg-gray-100/60 hover:border-gray-300 transition-all text-start group"
        >
          <div className="p-2 rounded-lg bg-emerald-500/10">
            <DollarSign className="w-5 h-5 text-emerald-400" />
          </div>
          <span className="text-gray-700 font-medium text-sm">سداد الدين</span>
        </button>

        <button
          onClick={handleRenewClick}
          className="glass-panel p-4 flex items-center gap-3 hover:bg-gray-100/60 hover:border-gray-300 transition-all text-start group"
        >
          <div className="p-2 rounded-lg bg-violet-500/10">
            <RefreshCw className="w-5 h-5 text-violet-400" />
          </div>
          <span className="text-gray-700 font-medium text-sm">تجديد</span>
        </button>

        <button
          onClick={() => setShowDeleteConfirm(true)}
          className="glass-panel p-4 flex items-center gap-3 hover:bg-rose-500/5 hover:border-rose-500/20 transition-all text-start group"
        >
          <div className="p-2 rounded-lg bg-rose-500/10">
            <Trash2 className="w-5 h-5 text-rose-400" />
          </div>
          <span className="text-gray-700 font-medium text-sm">حذف</span>
        </button>
      </div>

      {/* Pay Debt Panel */}
      {showPayDebt && (
        <div className="glass-panel p-6 space-y-4 border-emerald-500/20 animate-in fade-in slide-in-from-top-2 duration-300">
          <div className="flex items-center gap-2 text-black font-semibold border-b border-gray-200 pb-4">
            <DollarSign className="w-5 h-5 text-emerald-500" />تسجيل الدفعة</div>
          {latestSub && (
            <div className="flex items-center gap-6 text-sm">
              <span className="text-gray-500">الدين الحالي:</span>
              <span className={`font-bold text-lg ${latestSub.amount_owed > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                ${latestSub.amount_owed.toFixed(2)}
              </span>
            </div>
          )}
          <div className="flex gap-3">
            <div className="flex-1">
              <input
                type="number"
                min="0"
                step="0.01"
                value={paymentAmount}
                onChange={(e) => setPaymentAmount(e.target.value)}
                placeholder="Enter payment amount..."
                className="w-full bg-white border border-gray-200 rounded-lg px-4 py-3 text-black placeholder-gray-400 focus:outline-none focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/10 transition-all text-lg"
              />
            </div>
            {latestSub && latestSub.amount_owed > 0 && (
              <button
                onClick={() => setPaymentAmount(latestSub.amount_owed.toFixed(2))}
                className="px-4 py-3 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg transition-colors text-sm whitespace-nowrap"
              >
                Pay Full (${latestSub.amount_owed.toFixed(2)})
              </button>
            )}
          </div>
          <div className="flex gap-3">
            <button
              onClick={handlePayDebt}
              disabled={savingPayment || !paymentAmount}
              className="px-6 py-3 bg-emerald-500 hover:bg-emerald-400 text-white font-bold rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {savingPayment ? <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent" /> : <Check className="w-5 h-5" />}
              Confirm Payment
            </button>
            <button
              onClick={() => { setShowPayDebt(false); setPaymentAmount(''); }}
              className="px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-xl transition-colors"
            >
              إلغاء
            </button>
          </div>
        </div>
      )}

      {/* Freeze Panel */}
      {showFreeze && member.status !== 'Frozen' && (
        <div className="glass-panel p-6 space-y-4 border-sky-500/20 animate-in fade-in slide-in-from-top-2 duration-300">
          <div className="flex items-center gap-2 text-black font-semibold border-b border-gray-200 pb-4">
            <Snowflake className="w-5 h-5 text-sky-500" />تجميد الاشتراك
          </div>
          <p className="text-gray-500 text-sm">اختر مدة تجميد الاشتراك.</p>
          
          <div className="flex gap-3">
            <button
              onClick={() => setFreezeWeeks(1)}
              className={`flex-1 py-3 rounded-xl border-2 font-semibold transition-all ${freezeWeeks === 1 ? 'border-sky-500 bg-sky-500/10 text-sky-700' : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'}`}
            >
              أسبوع واحد
            </button>
            <button
              onClick={() => setFreezeWeeks(2)}
              className={`flex-1 py-3 rounded-xl border-2 font-semibold transition-all ${freezeWeeks === 2 ? 'border-sky-500 bg-sky-500/10 text-sky-700' : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'}`}
            >
              أسبوعين
            </button>
          </div>

          <div className="flex gap-3 pt-2">
            <button
              onClick={handleConfirmFreeze}
              disabled={freezing}
              className="px-6 py-3 bg-sky-500 hover:bg-sky-400 text-white font-bold rounded-xl transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              {freezing ? <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent" /> : <Check className="w-5 h-5" />}
              تأكيد التجميد
            </button>
            <button
              onClick={() => setShowFreeze(false)}
              className="px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-xl transition-colors"
            >
              إلغاء
            </button>
          </div>
        </div>
      )}

      {/* Change Subscription Panel */}
      {showChangeSub && (
        <div className="glass-panel p-6 space-y-6 border-violet-500/20 animate-in fade-in slide-in-from-top-2 duration-300">
          <div className="flex items-center gap-2 text-black font-semibold border-b border-gray-200 pb-4">
            <RefreshCw className="w-5 h-5 text-violet-500" />
            تجديد / تغيير الاشتراك
          </div>
          <p className="text-gray-500 text-sm">
            Select packages. This creates a new subscription — any unpaid balance from previous plans becomes additional debt.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">
            {packages.filter(p => !p.is_addon).map((pkg) => (
              <label
                key={pkg.id}
                className={`relative flex flex-col p-4 cursor-pointer rounded-xl border-2 transition-all duration-200 ${
                  selectedPackages.has(pkg.id)
                    ? 'border-violet-500 bg-violet-500/10'
                    : 'border-gray-200 bg-white/80 hover:border-gray-300'
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <span className="font-semibold text-black text-sm">{pkg.name}</span>
                  <div className={`w-5 h-5 rounded border flex items-center justify-center transition-colors ${
                    selectedPackages.has(pkg.id) ? 'bg-violet-500 border-violet-500 text-black' : 'border-gray-400'
                  }`}>
                    {selectedPackages.has(pkg.id) && <Check className="w-3 h-3" />}
                  </div>
                </div>
                <div className="text-xl font-bold text-black mb-1">${pkg.price}</div>
                <div className="text-xs text-gray-500 mt-auto">
                  {pkg.duration_days} Days {pkg.sessions && `• ${pkg.sessions} Sessions`}
                </div>
                <input
                  type="checkbox"
                  className="sr-only"
                  checked={selectedPackages.has(pkg.id)}
                  onChange={() => togglePackage(pkg.id)}
                />
              </label>
            ))}
          </div>

          {packages.some(p => p.is_addon) && (
            <>
              <div className="flex items-center gap-2 text-black font-semibold border-b border-gray-200 pb-4 mt-6 mb-4">
                باقات إضافية (Add-ons)
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">
                {packages.filter(p => p.is_addon).map((pkg) => (
                  <label
                    key={pkg.id}
                    className={`relative flex flex-col p-4 cursor-pointer rounded-xl border-2 transition-all duration-200 ${
                      selectedPackages.has(pkg.id)
                        ? 'border-purple-600 bg-purple-50'
                        : 'border-gray-200 bg-white/80 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-semibold text-black text-sm">{pkg.name}</span>
                      <div className={`w-5 h-5 rounded border flex items-center justify-center transition-colors ${
                        selectedPackages.has(pkg.id) ? 'bg-purple-600 text-white border-purple-600' : 'border-gray-400'
                      }`}>
                        {selectedPackages.has(pkg.id) && <Check className="w-3 h-3" />}
                      </div>
                    </div>
                    <div className="text-xl font-bold text-black mb-1">${pkg.price}</div>
                    <div className="text-xs text-gray-500 mt-auto">
                      {pkg.duration_days} Days {pkg.sessions && `• ${pkg.sessions} Sessions`}
                    </div>
                    <input
                      type="checkbox"
                      className="sr-only"
                      checked={selectedPackages.has(pkg.id)}
                      onChange={() => togglePackage(pkg.id)}
                    />
                  </label>
                ))}
              </div>
            </>
          )}

          {selectedItems.length > 0 && (
            <div className="bg-white rounded-xl p-5 border border-gray-200 space-y-4">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4">
                <div>
                  <p className="text-sm text-gray-500 mb-1">مطلوب</p>
                  <p className="text-3xl font-bold text-black">${newSubTotal}</p>
                </div>

                <div className="w-full sm:w-72">
                  <label className="block text-sm font-bold text-gray-700 mb-1">المبلغ المدفوع اليوم</label>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={subAmountPaid}
                    onChange={(e) => setSubAmountPaid(e.target.value)}
                    className="w-full bg-white border-2 border-gray-300 rounded-lg px-4 py-3 text-black placeholder-gray-400 focus:outline-none focus:border-black focus:ring-2 focus:ring-black/10 transition-all text-2xl font-semibold"
                    placeholder="0.00"
                  />
                </div>

                <div className="w-full sm:w-48">
                  <label className="block text-sm text-gray-500 mb-1 flex items-center gap-1.5">
                    <Tag className="w-3.5 h-3.5" />
                    Discount
                    <span className="text-gray-500 text-xs ms-1">اختياري</span>
                  </label>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={subDiscount}
                    onChange={(e) => setSubDiscount(e.target.value)}
                    className="w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-3 text-black placeholder-gray-400 focus:outline-none focus:border-violet-500/50 focus:ring-2 focus:ring-violet-500/10 transition-all text-lg"
                    placeholder="0.00"
                  />
                </div>
                <div className="text-end">
                  <p className="text-sm text-gray-500 mb-1">سيتبقى (دين)</p>
                  <p className={`text-3xl font-bold ${newSubOwed > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                    ${newSubOwed.toFixed(2)}
                  </p>
                </div>
              </div>

              {newSubDiscount > 0 && (
                <div className="p-3 rounded-lg bg-violet-500/5 border border-violet-500/20 flex items-center gap-3 text-sm">
                  <Tag className="w-4 h-4 text-violet-400 flex-shrink-0" />
                  <span className="text-violet-300">
                    Discount من <span className="font-bold">${newSubDiscount.toFixed(2)}</span> applied — effective price is <span className="font-bold">${newEffectivePrice.toFixed(2)}</span>.
                  </span>
                </div>
              )}

              <div className="flex gap-3 pt-2">
                <button
                  onClick={handleChangeSub}
                  disabled={savingSub}
                  className="px-6 py-3 bg-violet-500 hover:bg-violet-400 text-black font-bold rounded-xl transition-colors disabled:opacity-50 flex items-center gap-2"
                >
                  {savingSub ? <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent" /> : <Check className="w-5 h-5" />}
                  Apply New Subscription
                </button>
                <button
                  onClick={() => { setShowChangeSub(false); setSelectedPackages(new Set()); setSubAmountPaid(''); }}
                  className="px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-xl transition-colors"
                >
                  إلغاء
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="glass-panel p-6 border-rose-500/20 animate-in fade-in slide-in-from-top-2 duration-300">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 rounded-full bg-rose-500/10">
              <AlertTriangle className="w-6 h-6 text-rose-400" />
            </div>
            <div>
              <h3 className="text-black font-bold text-lg">Delete {member.name}?</h3>
              <p className="text-gray-500 text-sm">
                This will permanently delete all data for this member. Their ID (#{member.id}) will become available for new registrations.
              </p>
            </div>
          </div>
          <div className="flex gap-3">
            <button
              onClick={handleDelete}
              disabled={deleting}
              className="px-6 py-3 bg-rose-500 hover:bg-rose-400 text-black font-bold rounded-xl transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              {deleting ? <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent" /> : <Trash2 className="w-5 h-5" />}
              Yes, Delete
            </button>
            <button
              onClick={() => setShowDeleteConfirm(false)}
              className="px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-xl transition-colors"
            >
              إلغاء
            </button>
          </div>
        </div>
      )}

      {showAdminLogin && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/20 backdrop-blur-sm">
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

            <form onSubmit={handleAdminLoginSubmit} className="space-y-4">
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
              <div className="flex gap-3">
                <button
                  type="submit"
                  className="w-full bg-black text-white rounded-xl py-3 font-semibold hover:bg-gray-800 transition-colors"
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
                  className="w-full bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-xl py-3 font-semibold transition-colors"
                >
                  إلغاء
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Subscription & Attendance Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* الاشتراك الحالي Card */}
        <div className="lg:col-span-2 glass-panel p-6 space-y-5">
          <div className="flex items-center gap-2 text-black font-semibold border-b border-gray-200 pb-4">
            <Package className="w-5 h-5 text-black" />
            الاشتراك الحالي
          </div>

          {latestSub ? (
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-200/30 p-4 rounded-xl border border-gray-200/50">
                <p className="text-sm text-gray-500 mb-1">الباقات</p>
                <p className="font-semibold text-black text-sm">{latestSub.package_name.join(', ')}</p>
              </div>
              <div className={`p-4 rounded-xl border ${latestSub.total_sessions > 0 && latestSub.attended_sessions >= latestSub.total_sessions ? 'bg-red-600 border-red-700 text-white' : 'bg-green-600 border-green-700 text-white'}`}>
                <p className="text-sm text-white/80 mb-1">جلسات (أساسية)</p>
                <p className="font-semibold text-white">
                  <span className="text-white">{latestSub.attended_sessions}</span>
                  <span className="text-white/80 mx-1">/</span>
                  {latestSub.total_sessions || '∞'}
                </p>
              </div>
              <div className={`p-4 rounded-xl border ${ (new Date(latestSub.end_date).getTime() < serverTime.getTime()) || member.status === 'Expired' || member.status === 'منتهي' ? 'bg-red-600 border-red-700 text-white' : 'bg-green-600 border-green-700 text-white'}`}>
                <p className="text-sm text-white/80 mb-1">فترة الصلاحية</p>
                <p className="font-semibold text-white text-sm">
                  {format(new Date(latestSub.start_date), 'MMM d, yyyy')} — {format(new Date(latestSub.end_date), 'MMM d, yyyy')}
                </p>
              </div>
              
              {/* Addons Render */}
              {latestSub.addons_usage && Object.keys(latestSub.addons_usage).length > 0 && (
                <div className="col-span-2 grid grid-cols-2 gap-4">
                  {Object.entries(latestSub.addons_usage).map(([addonName, usage]) => {
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
              <div className={`bg-gray-200/30 p-4 rounded-xl border ${latestSub.amount_owed > 0 ? 'border-rose-500/20' : 'border-gray-200/50'}`}>
                <p className="text-sm text-gray-500 mb-1">المالية</p>
                <div className="font-semibold text-sm space-y-1">
                  <div className="text-gray-700">Original Total: ${latestSub.total_price.toFixed(2)}</div>
                  {latestSub.discount > 0 && (
                    <div className="text-violet-600">Discount: -${latestSub.discount.toFixed(2)}</div>
                  )}
                  <div className="text-gray-700">Final Price: ${(latestSub.total_price - (latestSub.discount || 0)).toFixed(2)} | المدفوع: ${latestSub.amount_paid.toFixed(2)}</div>
                  <div className={latestSub.amount_owed > 0 ? 'text-rose-400' : 'text-emerald-400'}>
                    Owed: ${latestSub.amount_owed.toFixed(2)}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              لا يوجد اشتراك نشط.
            </div>
          )}

          {/* سجل الاشتراكات */}
          {member.subscriptions && member.subscriptions.length > 0 && (
            <div className="pt-4 border-t border-gray-200">
              <p className="text-sm text-gray-500 font-medium mb-3">سجل الاشتراكات</p>
              <div className="space-y-2">
                {member.subscriptions.slice().reverse().map((sub, idx) => (
                  <div key={sub.id} className="flex items-center justify-between p-3 rounded-lg bg-gray-200/20 border border-gray-200/30 text-sm">
                    <div>
                      <span className="text-gray-700">{sub.package_name.join(', ')}</span>
                      <span className="text-gray-500 ms-2">
                        ({format(new Date(sub.start_date), 'MMM d')} – {format(new Date(sub.end_date), 'MMM d, yyyy')})
                      </span>
                      {sub.discount > 0 && (
                        <span className="ms-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-violet-100 text-violet-800">
                          Discount: ${sub.discount.toFixed(2)}
                        </span>
                      )}
                    </div>
                    <div className="text-end flex flex-col items-end">
                      {sub.discount > 0 ? (
                        <>
                          <div className="text-gray-500 line-through text-xs">${sub.total_price.toFixed(2)}</div>
                          <div className="text-gray-800 font-bold">Price: ${(sub.total_price - sub.discount).toFixed(2)}</div>
                        </>
                      ) : (
                        <div className="text-gray-800 font-bold">Price: ${sub.total_price.toFixed(2)}</div>
                      )}
                      <div className="font-semibold text-gray-500 text-xs mt-1">المدفوع: ${sub.amount_paid.toFixed(2)}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Attendance Log */}
        <div className="glass-panel p-6 flex flex-col h-[500px]">
          <div className="flex items-center gap-2 text-black font-semibold border-b border-gray-200 pb-4 mb-4">
            <History className="w-5 h-5 text-black" />
            Attendance
            <div className="ms-auto bg-black text-white font-bold text-sm py-1 px-3 rounded-lg shadow-sm">
              {logs.length}
            </div>
          </div>
          <div className="flex-1 overflow-y-auto pe-2 space-y-2 custom-scrollbar">
            {logs.length > 0 ? (
              logs.map((log) => (
                <div key={log.id} className="flex justify-between items-center p-3 rounded-lg bg-gray-200/30 border border-gray-200/50">
                  <span className="text-gray-700 text-sm">{format(new Date(log.timestamp), 'MMM d, yyyy')}</span>
                  <div className="flex items-center gap-2">
                    {log.addon_tag && (
                      <span className="text-xs font-bold text-white bg-purple-500 px-2 py-0.5 rounded uppercase">
                        {log.addon_tag}
                      </span>
                    )}
                    <span className="text-gray-500 font-mono text-xs bg-white px-2 py-1 rounded">
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
    </div>
  );
};

export default MemberDetail;
