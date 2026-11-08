import re

# ================= Dashboard.jsx =================
filepath = 'C:/Users/DELL/Desktop/GYM/frontend/src/Dashboard.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Imports
content = content.replace(
    "import { getDashboard, listPackages, createPackage, updatePackage, deletePackage, createReceptionist, updateReceptionist, deleteReceptionist, listStaff, createStaff, updateStaffPending, deleteStaff, createExpense, getFilteredFinances } from './api';",
    "import { getDashboard, listPackages, createPackage, updatePackage, deletePackage, createReceptionist, updateReceptionist, deleteReceptionist, listStaff, createStaff, updateStaffPending, deleteStaff, createExpense, getFilteredFinances, verifyPin, updatePin } from './api';"
)
content = content.replace("import { Users, Activity, Wallet, AlertTriangle, UserPlus, FileText, Package, Plus, Trash2, Edit3, Check, X, Save, Settings, UserCheck, Infinity, UserCircle, Briefcase, TrendingUp, TrendingDown, Receipt } from 'lucide-react';", "import { Users, Activity, Wallet, AlertTriangle, UserPlus, FileText, Package, Plus, Trash2, Edit3, Check, X, Save, Settings, UserCheck, Infinity, UserCircle, Briefcase, TrendingUp, TrendingDown, Receipt, Lock, Unlock } from 'lucide-react';")

# 2. Add PIN state & verify logic
pin_state = """  const [isUnlocked, setIsUnlocked] = useState(false);
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
"""
content = content.replace("  const [activeTab, setActiveTab] = useState('overview');", pin_state + "\n  const [activeTab, setActiveTab] = useState('overview');")

# 3. Wrap entire return inside an IF isUnlocked block, else return PIN screen
pin_screen = """
  if (!isUnlocked) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-6">
        <div className="glass-panel p-8 max-w-md w-full space-y-6 text-center">
          <div className="w-16 h-16 bg-black rounded-full flex items-center justify-center mx-auto mb-4">
            <Lock className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-black">Admin Access</h2>
          <p className="text-gray-500">Please enter your 4-digit PIN to access the dashboard.</p>
          <form onSubmit={handleVerifyPin} className="space-y-4">
            <input 
              type="password" 
              maxLength="4"
              value={pinInput} 
              onChange={e => setPinInput(e.target.value)}
              className="w-full text-center text-2xl tracking-[1em] bg-gray-50 border border-gray-200 rounded-xl p-4 focus:border-black focus:outline-none"
              placeholder="••••"
            />
            {pinError && <div className="text-rose-500 text-sm font-medium">{pinError}</div>}
            <button type="submit" className="w-full py-4 bg-black text-white font-bold rounded-xl hover:bg-gray-800 transition-colors">
              Unlock Dashboard
            </button>
          </form>
        </div>
      </div>
    );
  }
"""
content = content.replace("  return (\n    <div className=\"min-h-screen bg-gray-50 pb-20\">", pin_screen + "\n  return (\n    <div className=\"min-h-screen bg-gray-50 pb-20\">")

# 4. Add Change PIN button to top nav
change_pin_btn = """
          <button onClick={() => setShowChangePin(true)} className="flex items-center gap-2 px-4 py-2 bg-gray-200 hover:bg-gray-300 text-black font-semibold rounded-lg transition-colors text-sm">
            <Settings className="w-4 h-4" /> Change PIN
          </button>
        </div>
      </div>
      
      {showChangePin && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl p-6 max-w-sm w-full space-y-4 relative">
            <button onClick={() => setShowChangePin(false)} className="absolute top-4 right-4 text-gray-400 hover:text-black"><X className="w-5 h-5"/></button>
            <h3 className="text-lg font-bold text-black flex items-center gap-2"><Lock className="w-5 h-5"/> Change Admin PIN</h3>
            <form onSubmit={handleChangePin} className="space-y-4">
              <input type="text" maxLength="4" placeholder="New 4-Digit PIN" value={newPinInput} onChange={e => setNewPinInput(e.target.value)} className="w-full bg-gray-50 border border-gray-200 rounded-lg p-3 text-center text-xl tracking-[0.5em] focus:border-black focus:outline-none"/>
              <button type="submit" className="w-full py-3 bg-black text-white font-bold rounded-lg hover:bg-gray-800 transition-colors">Save New PIN</button>
            </form>
          </div>
        </div>
      )}
"""
content = content.replace("        </div>\n      </div>", change_pin_btn)

# 5. Fix handleUpdatePending to support pay_day
update_pending_new = """  const handleUpdatePending = async (staffId, bonus, deduction, payDay) => {
    try {
      await updateStaffPending(staffId, { bonus: parseFloat(bonus||0), deduction: parseFloat(deduction||0), pay_day: parseInt(payDay||1) });
      setPkgSuccess('Staff info updated.');
      setTimeout(() => setPkgSuccess(''), 3000);
      fetchStaff();
    } catch (err) {
      setPkgError('Failed to update staff info.');
    }
  };"""
content = re.sub(r"  const handleUpdatePending = async \(staffId, bonus, deduction\) => \{[\s\S]*?catch \(err\) \{[\s\S]*?\}\n  \};", update_pending_new, content)

# 6. Redesign Staff Cards (Move delete icon, clear bonus/deduct fields, add pay day input)
old_staff_card = r"              \{staffList\.map\(staff => \([\s\S]*?<\/button>\n                <\/div>\n              \}\)\}"
new_staff_card = """              {staffList.map(staff => (
                <div key={staff.id} className="glass-panel p-5 space-y-4 relative group flex flex-col justify-between">
                  <div>
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <div className="text-2xl font-bold text-black">{staff.name}</div>
                        <div className="text-sm font-medium text-violet-600 mb-1">{staff.role}</div>
                        <div className="text-xs text-gray-500">{staff.phone ? `Phone: ${staff.phone}` : 'No phone listed'}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-xl font-bold text-black">${staff.base_salary}</div>
                        <div className="text-xs text-gray-400">/ month</div>
                      </div>
                    </div>
                    
                    <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 space-y-3">
                      <div className="flex items-center justify-between text-xs pb-2 border-b border-gray-200">
                        <span className="text-gray-500">Last Paid:</span>
                        <span className="font-semibold text-black">{format(new Date(staff.last_paid_date), 'MMM d, yyyy')}</span>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className="block text-xs font-semibold text-emerald-700 mb-1">Pending Bonus</label>
                          <input type="number" id={`bonus-${staff.id}`} className="w-full bg-white border border-gray-300 rounded-md px-3 py-2 text-sm focus:border-black focus:outline-none" defaultValue={staff.pending_bonus} />
                        </div>
                        <div>
                          <label className="block text-xs font-semibold text-rose-700 mb-1">Pending Deduction</label>
                          <input type="number" id={`deduct-${staff.id}`} className="w-full bg-white border border-gray-300 rounded-md px-3 py-2 text-sm focus:border-black focus:outline-none" defaultValue={staff.pending_deduction} />
                        </div>
                      </div>

                      <div>
                        <label className="block text-xs font-semibold text-gray-700 mb-1">Pay Day (1-31)</label>
                        <input type="number" id={`payday-${staff.id}`} className="w-full bg-white border border-gray-300 rounded-md px-3 py-2 text-sm focus:border-black focus:outline-none" defaultValue={staff.pay_day} />
                      </div>
                      
                    </div>
                  </div>
                  
                  <div className="flex gap-2 pt-2">
                    <button onClick={() => handleUpdatePending(staff.id, document.getElementById(`bonus-${staff.id}`).value, document.getElementById(`deduct-${staff.id}`).value, document.getElementById(`payday-${staff.id}`).value)} className="flex-1 bg-black text-white rounded-lg py-2 text-sm font-semibold hover:bg-gray-800 transition-colors">
                      Save Changes
                    </button>
                    <button onClick={() => deleteStaff(staff.id).then(fetchStaff)} className="px-4 bg-rose-100 text-rose-600 rounded-lg hover:bg-rose-500 hover:text-white transition-colors flex items-center justify-center">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}"""
content = re.sub(old_staff_card, new_staff_card, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

# ================= Onboarding.jsx =================
filepath_ob = 'C:/Users/DELL/Desktop/GYM/frontend/src/Onboarding.jsx'
with open(filepath_ob, 'r', encoding='utf-8') as f:
    content_ob = f.read()

# Add imports
content_ob = content_ob.replace("import { createMember, listPackages } from './api';", "import { createMember, listPackages, verifyPin } from './api';")
content_ob = content_ob.replace("import { Plus, User, Phone, Package, DollarSign, Loader2, CheckCircle2, UserCircle, Building2 } from 'lucide-react';", "import { Plus, User, Phone, Package, DollarSign, Loader2, CheckCircle2, UserCircle, Building2, Lock } from 'lucide-react';")

pin_state_ob = """  const [isUnlocked, setIsUnlocked] = useState(false);
  const [pinInput, setPinInput] = useState('');
  const [pinError, setPinError] = useState('');

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

"""
content_ob = content_ob.replace("  const navigate = useNavigate();", "  const navigate = useNavigate();\n" + pin_state_ob)

pin_screen_ob = """
  if (!isUnlocked) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-6">
        <div className="glass-panel p-8 max-w-md w-full space-y-6 text-center">
          <div className="w-16 h-16 bg-black rounded-full flex items-center justify-center mx-auto mb-4">
            <Lock className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-black">Onboarding Access</h2>
          <p className="text-gray-500">Please enter your 4-digit PIN to access this page.</p>
          <form onSubmit={handleVerifyPin} className="space-y-4">
            <input 
              type="password" 
              maxLength="4"
              value={pinInput} 
              onChange={e => setPinInput(e.target.value)}
              className="w-full text-center text-2xl tracking-[1em] bg-gray-50 border border-gray-200 rounded-xl p-4 focus:border-black focus:outline-none"
              placeholder="••••"
            />
            {pinError && <div className="text-rose-500 text-sm font-medium">{pinError}</div>}
            <button type="submit" className="w-full py-4 bg-black text-white font-bold rounded-xl hover:bg-gray-800 transition-colors">
              Unlock Onboarding
            </button>
          </form>
        </div>
      </div>
    );
  }
"""

content_ob = content_ob.replace("  return (\n    <div className=\"min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8\">\n", pin_screen_ob + "  return (\n    <div className=\"min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8\">\n")

with open(filepath_ob, 'w', encoding='utf-8') as f:
    f.write(content_ob)

print("Dashboard and Onboarding updated successfully")
