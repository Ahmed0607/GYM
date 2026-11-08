import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { UserPlus, Calculator, Check, AlertCircle, Tag } from 'lucide-react';
import { createMember, listPackages, verifyPin, checkinMember } from './api';

const Onboarding = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ name: '', phone: '', amountPaid: '', discount: '', gender: 'رجل', startDate: new Date().toISOString().split('T')[0] });
  const [selectedPackages, setSelectedPackages] = useState(new Set());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [newMember, setNewMember] = useState(null);
  const [checkinLoading, setCheckinLoading] = useState(false);
  const [packages, setPackages] = useState([]);
  const [pkgsLoading, setPkgsLoading] = useState(true);

  useEffect(() => {
    const fetchPkgs = async () => {
      try {
        const data = await listPackages();
        setPackages(data);
      } catch (err) {
        console.error('Failed to load packages', err);
      } finally {
        setPkgsLoading(false);
      }
    };
    fetchPkgs();
  }, []);

  const togglePackage = (pkgId) => {
    const newSelected = new Set(selectedPackages);
    if (newSelected.has(pkgId)) newSelected.delete(pkgId);
    else newSelected.add(pkgId);
    setSelectedPackages(newSelected);
  };

  const selectedItems = useMemo(() => {
    return packages.filter(p => selectedPackages.has(p.id));
  }, [selectedPackages, packages]);

  const totalRequired = useMemo(() => {
    return selectedItems.reduce((sum, pkg) => sum + pkg.price, 0);
  }, [selectedItems]);

  const discount = useMemo(() => {
    const d = parseFloat(formData.discount) || 0;
    return Math.min(Math.max(0, d), totalRequired); // Cap discount to total
  }, [formData.discount, totalRequired]);

  const effectivePrice = useMemo(() => {
    return Math.max(0, totalRequired - discount);
  }, [totalRequired, discount]);

  const amountOwed = useMemo(() => {
    const paid = parseFloat(formData.amountPaid) || 0;
    return Math.max(0, effectivePrice - paid);
  }, [effectivePrice, formData.amountPaid]);

  
  const handleCheckin = async () => {
    if (!newMember) return;
    setCheckinLoading(true);
    try {
      await checkinMember(newMember.id);
      alert('First session recorded successfully!');
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to checkin');
    } finally {
      setCheckinLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name) {
      setError('Name is required.');
      return;
    }
    if (selectedItems.length === 0) {
      setError('Select at least one package.');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess(false);
    
    const payload = {
      name: formData.name,
      phone: formData.phone || null,
      gender: formData.gender,
      subscription: {
        packages: selectedItems.map(p => p.name),
        amount_paid: parseFloat(formData.amountPaid) || 0,
        discount: parseFloat(formData.discount) || 0,
        start_date: formData.startDate ? new Date(formData.startDate).toISOString() : null
      }
    };

    try {
      const res = await createMember(payload);
      setSuccess(true);
      setNewMember(res);
      setFormData({ name: '', phone: '', amountPaid: '', discount: '', gender: 'رجل', startDate: new Date().toISOString().split('T')[0] });
      setSelectedPackages(new Set());
    } catch (err) {
      setError('Failed to create member. Try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold text-black tracking-tight">تسجيل عضو جديد</h1>
        <p className="text-gray-500">تسجيل الأعضاء الجدد وإعداد الباقات</p>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 flex items-center gap-3">
          <AlertCircle className="w-5 h-5" />
          {error}
        </div>
      )}

      {success && newMember && (
        <div className="p-6 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="bg-emerald-500/20 p-3 rounded-full text-emerald-500">
              <Check className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-emerald-500 font-bold text-lg">تم إنشاء العضو بنجاح!</h3>
              <p className="text-emerald-600/80">رقم العضوية: <span className="font-mono text-black font-bold text-lg bg-white px-2 py-1 rounded">{newMember.id}</span> لـ <strong>{newMember.name}</strong></p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button onClick={() => navigate(`/members?id=${newMember.id}`)} className="px-4 py-2 bg-white text-black font-medium rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
              عرض المعلومات
            </button>
            <button 
              onClick={handleCheckin} 
              disabled={checkinLoading}
              className="px-4 py-2 bg-emerald-500 text-white font-medium rounded-lg hover:bg-emerald-600 transition-colors disabled:opacity-50"
            >
              {checkinLoading ? 'جاري التسجيل...' : 'بدء الجلسة الأولى'}
            </button>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Column: Member Details */}
        <div className="lg:col-span-4 space-y-6">
          <div className="glass-panel p-6 space-y-6">
            <div className="flex items-center gap-2 text-black font-semibold border-b border-gray-200 pb-4">
              <UserPlus className="w-5 h-5 text-black" />
              الملف الشخصي للعضو
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-500 mb-2">الاسم الكامل</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full bg-white border border-gray-200 rounded-lg px-4 py-3 text-black placeholder-gray-400 focus:outline-none focus:border-black/50 focus:ring-2 focus:ring-gray-500/10 transition-all"
                  placeholder="John Doe"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-500 mb-2">رقم الهاتف (اختياري)</label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  className="w-full bg-white border border-gray-200 rounded-lg px-4 py-3 text-black placeholder-gray-300 focus:outline-none focus:border-black/50 focus:ring-2 focus:ring-gray-500/10 transition-all"
                  placeholder="+1 (555) 000-0000"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-500 mb-2">النوع</label>
                <select
                  value={formData.gender}
                  onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                  className="w-full bg-white border border-gray-200 rounded-lg px-4 py-3 text-black focus:outline-none focus:border-black/50 focus:ring-2 focus:ring-gray-500/10 transition-all"
                >
                  <option value="رجل">رجل</option>
                  <option value="Lady">سيدة</option>
                  <option value="Kid">طفل</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-500 mb-2">تاريخ البدء (اختياري)</label>
                <input
                  type="date"
                  value={formData.startDate}
                  onChange={(e) => setFormData({ ...formData, startDate: e.target.value })}
                  className="w-full bg-white border border-gray-200 rounded-lg px-4 py-3 text-black focus:outline-none focus:border-black/50 focus:ring-2 focus:ring-gray-500/10 transition-all"
                />
                <p className="text-xs text-gray-400 mt-1">الافتراضي هو اليوم إذا تُرك فارغاً.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: منشئ الباقات & Payment */}
        <div className="lg:col-span-8 space-y-6">
          <div className="glass-panel p-6">
            <div className="flex items-center gap-2 text-black font-semibold border-b border-gray-200 pb-4 mb-6">
              <Calculator className="w-5 h-5 text-black" />
              منشئ الباقات
            </div>

            {pkgsLoading ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-3 border-black border-t-transparent"></div>
              </div>
            ) : packages.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                لا توجد باقات متاحة. يجب على المسؤول إعداد الباقات في لوحة التحكم أولاً.
              </div>
            ) : (
              <>
                <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4 mb-8">
                  {packages.filter(p => !p.is_addon).map((pkg) => (
                    <label
                      key={pkg.id}
                      className={`relative flex flex-col p-4 cursor-pointer rounded-xl border-2 transition-all duration-200 ${
                        selectedPackages.has(pkg.id)
                          ? 'border-black bg-gray-200'
                          : 'border-gray-200 bg-white/80 hover:border-gray-300'
                      }`}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <span className="font-semibold text-black">{pkg.name}</span>
                        <div className={`w-5 h-5 rounded border flex items-center justify-center transition-colors ${
                          selectedPackages.has(pkg.id) ? 'bg-black text-white border-black text-white' : 'border-gray-400'
                        }`}>
                          {selectedPackages.has(pkg.id) && <Check className="w-3 h-3" />}
                        </div>
                      </div>
                      <div className="text-2xl font-bold text-black mb-1">${pkg.price}</div>
                      <div className="text-sm text-gray-500 mt-auto">
                        {pkg.duration_days} أيام {pkg.sessions && `• ${pkg.sessions} جلسات`}
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
                    <div className="flex items-center gap-2 text-black font-semibold border-b border-gray-200 pb-4 mb-6">
                      باقات إضافية (Add-ons)
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4 mb-8">
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
                            <span className="font-semibold text-black">{pkg.name}</span>
                            <div className={`w-5 h-5 rounded border flex items-center justify-center transition-colors ${
                              selectedPackages.has(pkg.id) ? 'bg-purple-600 text-white border-purple-600' : 'border-gray-400'
                            }`}>
                              {selectedPackages.has(pkg.id) && <Check className="w-3 h-3" />}
                            </div>
                          </div>
                          <div className="text-2xl font-bold text-black mb-1">${pkg.price}</div>
                          <div className="text-sm text-gray-500 mt-auto">
                            {pkg.duration_days} أيام {pkg.sessions && `• ${pkg.sessions} جلسات`}
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

                <div className="bg-white rounded-xl p-6 border border-gray-200">
                  <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-6 mb-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-500 mb-2">الإجمالي المطلوب</label>
                      <div className="text-4xl font-bold text-black">${totalRequired}</div>
                    </div>

                    <div className="w-full sm:w-72">
                      <label className="block text-sm font-bold text-gray-700 mb-2">المبلغ المدفوع اليوم ($)</label>
                      <input
                        type="number"
                        min="0"
                        step="0.01"
                        value={formData.amountPaid}
                        onChange={(e) => setFormData({ ...formData, amountPaid: e.target.value })}
                        className="w-full bg-white border-2 border-gray-300 rounded-lg px-4 py-3 text-black placeholder-gray-400 focus:outline-none focus:border-black focus:ring-2 focus:ring-black/10 transition-all text-2xl font-semibold"
                        placeholder="0.00"
                      />
                    </div>

                    {/* Discount Field */}
                    <div className="w-full sm:w-48">
                      <label className="block text-sm font-medium text-gray-500 mb-2 flex items-center gap-1.5">
                        <Tag className="w-3.5 h-3.5" />
                        Discount ($)
                        <span className="text-gray-400 text-xs font-normal">اختياري</span>
                      </label>
                      <input
                        type="number"
                        min="0"
                        step="0.01"
                        value={formData.discount}
                        onChange={(e) => setFormData({ ...formData, discount: e.target.value })}
                        className="w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-3 text-black placeholder-gray-400 focus:outline-none focus:border-violet-500/50 focus:ring-2 focus:ring-violet-500/10 transition-all text-lg"
                        placeholder="0.00"
                      />
                    </div>
                    
                    <div className="text-end">
                      <label className="block text-sm font-medium text-gray-500 mb-2">المبلغ المتبقي (دين)</label>
                      <div className={`text-4xl font-bold ${amountOwed > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                        ${amountOwed.toFixed(2)}
                      </div>
                    </div>
                  </div>

                  {/* Discount breakdown hint */}
                  {discount > 0 && (
                    <div className="mb-4 p-3 rounded-lg bg-violet-500/5 border border-violet-500/20 flex items-center gap-3 text-sm">
                      <Tag className="w-4 h-4 text-violet-400 flex-shrink-0" />
                      <span className="text-violet-300">
                        Discount of <span className="font-bold">${discount.toFixed(2)}</span> applied — effective price is <span className="font-bold">${effectivePrice.toFixed(2)}</span>.
                        The system will show the member as fully paid لـ the discounted amount.
                      </span>
                    </div>
                  )}

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-black text-white hover:bg-gray-800 text-white font-bold text-lg py-4 rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg shadow-gray-500/20"
                  >
                    {loading ? (
                      <div className="animate-spin rounded-full h-6 w-6 border-2 border-white border-t-transparent"></div>
                    ) : (
                      <>إنشاء عضو</>
                    )}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>

      </form>
    </div>
  );
};

export default Onboarding;
