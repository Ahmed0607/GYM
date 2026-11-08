import re
import os

filepath = 'C:/Users/DELL/Desktop/GYM/frontend/src/Dashboard.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add API imports
content = content.replace(
    "import { getDashboard, listPackages, createPackage, updatePackage, deletePackage, createReceptionist, updateReceptionist, deleteReceptionist } from './api';",
    "import { getDashboard, listPackages, createPackage, updatePackage, deletePackage, createReceptionist, updateReceptionist, deleteReceptionist, listStaff, createStaff, updateStaffPending, deleteStaff, createExpense } from './api';"
)

# 2. Add icon imports
content = content.replace(
    "Package, Plus, Trash2, Edit3, Check, X, Save, Settings, UserCheck, Infinity, UserCircle",
    "Package, Plus, Trash2, Edit3, Check, X, Save, Settings, UserCheck, Infinity, UserCircle, Briefcase, TrendingUp, TrendingDown, Receipt"
)

# 3. Add states
state_injections = """  const [showAddRec, setShowAddRec] = useState(false);
  const [newRecForm, setNewRecForm] = useState({ name: '' });

  // Finances state
  const [staffList, setStaffList] = useState([]);
  const [staffLoading, setStaffLoading] = useState(false);
  const [showAddStaff, setShowAddStaff] = useState(false);
  const [newStaffForm, setNewStaffForm] = useState({ name: '', role: '', base_salary: '' });
  const [showAddExpense, setShowAddExpense] = useState(false);
  const [newExpenseForm, setNewExpenseForm] = useState({ category: 'Maintenance', amount: '', description: '' });
"""
content = content.replace(
    "  const [showAddRec, setShowAddRec] = useState(false);\n  const [newRecForm, setNewRecForm] = useState({ name: '' });",
    state_injections
)

# 4. Add fetch logic and useEffect dependencies
fetch_logic = """  const fetchStaff = async () => {
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

  useEffect(() => {
    if (activeTab === 'packages') {
      fetchPackages();
    } else if (activeTab === 'finances') {
      fetchStaff();
      fetchDashboard();
    }
  }, [activeTab]);"""
content = re.sub(r"  useEffect\(\(\) => \{\n    if \(activeTab === 'packages'\) \{\n      fetchPackages\(\);\n    \}\n  \}, \[activeTab\]\);", fetch_logic, content)

# 5. Add Finance Handlers
finance_handlers = """
  const handleAddStaff = async () => {
    setPkgError('');
    if (!newStaffForm.name || !newStaffForm.role || !newStaffForm.base_salary) {
      setPkgError('All fields required.');
      return;
    }
    try {
      await createStaff({ name: newStaffForm.name, role: newStaffForm.role, base_salary: parseFloat(newStaffForm.base_salary) });
      setNewStaffForm({ name: '', role: '', base_salary: '' });
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
      setPkgSuccess('Pending bonus/deduction updated.');
      setTimeout(() => setPkgSuccess(''), 3000);
      fetchStaff();
    } catch (err) {
      setPkgError('Failed to update pending.');
    }
  };

  const handleAddExpense = async () => {
    setPkgError('');
    if (!newExpenseForm.amount) {
      setPkgError('Amount is required.');
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
"""
content = content.replace("  if (loading) {", finance_handlers + "\n  if (loading) {")

# 6. Add Finances Tab header
content = content.replace(
    "{ id: 'receptionists', label: 'Manage Receptionists', icon: UserCircle },",
    "{ id: 'receptionists', label: 'Manage Receptionists', icon: UserCircle },\n    { id: 'finances', label: 'Finances', icon: Briefcase },"
)

# 7. Add Finances Tab Body
finances_tab = """
      {/* ═══ FINANCES TAB ═══ */}
      {activeTab === 'finances' && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-300">
          {pkgError && (
            <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 flex items-center gap-3">
              <AlertTriangle className="w-5 h-5 flex-shrink-0" />
              {pkgError}
              <button onClick={() => setPkgError('')} className="ml-auto hover:text-rose-300"><X className="w-4 h-4" /></button>
            </div>
          )}
          {pkgSuccess && (
            <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center gap-3">
              <Check className="w-5 h-5 flex-shrink-0" />
              {pkgSuccess}
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="glass-panel p-6">
              <div className="text-sm font-medium text-gray-500 mb-1 flex items-center gap-2"><TrendingUp className="w-4 h-4 text-emerald-500"/> All Time Net Revenue</div>
              <div className="text-3xl font-bold text-black">${data.net_revenue?.toFixed(2) || '0.00'}</div>
            </div>
            <div className="glass-panel p-6">
              <div className="text-sm font-medium text-gray-500 mb-1 flex items-center gap-2"><Briefcase className="w-4 h-4 text-rose-500"/> Salaries</div>
              <div className="text-3xl font-bold text-black">${data.total_salaries?.toFixed(2) || '0.00'}</div>
            </div>
            <div className="glass-panel p-6">
              <div className="text-sm font-medium text-gray-500 mb-1 flex items-center gap-2"><Settings className="w-4 h-4 text-amber-500"/> Repairs & Maintenance</div>
              <div className="text-3xl font-bold text-black">${data.total_maintenance?.toFixed(2) || '0.00'}</div>
            </div>
            <div className="glass-panel p-6">
              <div className="text-sm font-medium text-gray-500 mb-1 flex items-center gap-2"><Receipt className="w-4 h-4 text-cyan-500"/> Bills</div>
              <div className="text-3xl font-bold text-black">${data.total_bills?.toFixed(2) || '0.00'}</div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Add Expense */}
            <div className="glass-panel p-6 space-y-4">
              <div className="flex items-center justify-between border-b border-gray-200 pb-3">
                <h3 className="font-semibold text-black flex items-center gap-2"><TrendingDown className="w-5 h-5"/> Record Expense</h3>
                <button onClick={() => setShowAddExpense(!showAddExpense)} className="p-2 bg-gray-200 hover:bg-gray-300 rounded-lg text-black transition-colors"><Plus className="w-4 h-4"/></button>
              </div>
              {showAddExpense && (
                <div className="space-y-3">
                  <select value={newExpenseForm.category} onChange={e=>setNewExpenseForm({...newExpenseForm, category: e.target.value})} className="w-full bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm">
                    <option value="Maintenance">Repairs & Maintenance</option>
                    <option value="Bill">Bill</option>
                  </select>
                  <input type="number" placeholder="Amount ($)" value={newExpenseForm.amount} onChange={e=>setNewExpenseForm({...newExpenseForm, amount: e.target.value})} className="w-full bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm"/>
                  <input type="text" placeholder="Description (Optional)" value={newExpenseForm.description} onChange={e=>setNewExpenseForm({...newExpenseForm, description: e.target.value})} className="w-full bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm"/>
                  <button onClick={handleAddExpense} className="w-full py-3 bg-black text-white font-semibold rounded-lg hover:bg-gray-800 transition-colors">Record Expense</button>
                </div>
              )}
            </div>

            {/* Add Staff */}
            <div className="glass-panel p-6 space-y-4">
              <div className="flex items-center justify-between border-b border-gray-200 pb-3">
                <h3 className="font-semibold text-black flex items-center gap-2"><Briefcase className="w-5 h-5"/> Staff Members</h3>
                <button onClick={() => setShowAddStaff(!showAddStaff)} className="p-2 bg-gray-200 hover:bg-gray-300 rounded-lg text-black transition-colors"><Plus className="w-4 h-4"/></button>
              </div>
              {showAddStaff && (
                <div className="space-y-3">
                  <input type="text" placeholder="Name" value={newStaffForm.name} onChange={e=>setNewStaffForm({...newStaffForm, name: e.target.value})} className="w-full bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm"/>
                  <input type="text" placeholder="Role (e.g. Trainer, Cleaner)" value={newStaffForm.role} onChange={e=>setNewStaffForm({...newStaffForm, role: e.target.value})} className="w-full bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm"/>
                  <input type="number" placeholder="Base Salary (Monthly)" value={newStaffForm.base_salary} onChange={e=>setNewStaffForm({...newStaffForm, base_salary: e.target.value})} className="w-full bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm"/>
                  <button onClick={handleAddStaff} className="w-full py-3 bg-black text-white font-semibold rounded-lg hover:bg-gray-800 transition-colors">Add Staff Member</button>
                </div>
              )}
              
              <div className="mt-4 space-y-3">
                {staffList.map(staff => (
                  <div key={staff.id} className="p-4 bg-gray-50 border border-gray-200 rounded-xl space-y-3">
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="font-semibold text-black">{staff.name}</div>
                        <div className="text-xs text-gray-500">{staff.role} • ${staff.base_salary}/mo</div>
                        <div className="text-xs text-gray-400 mt-1">Last Paid: {format(new Date(staff.last_paid_date), 'MMM d, yyyy')}</div>
                      </div>
                      <div className="flex gap-2">
                         <span className="text-xs font-semibold text-emerald-500 bg-emerald-100 px-2 py-1 rounded">Pending Bonus: ${staff.pending_bonus}</span>
                         <span className="text-xs font-semibold text-rose-500 bg-rose-100 px-2 py-1 rounded">Pending Deduction: ${staff.pending_deduction}</span>
                      </div>
                    </div>
                    <div className="flex gap-2">
                       <input type="number" id={`bonus-${staff.id}`} placeholder="Add Bonus" className="w-24 bg-white border border-gray-200 rounded px-2 py-1 text-xs" defaultValue={staff.pending_bonus}/>
                       <input type="number" id={`deduct-${staff.id}`} placeholder="Deduct" className="w-24 bg-white border border-gray-200 rounded px-2 py-1 text-xs" defaultValue={staff.pending_deduction}/>
                       <button onClick={() => handleUpdatePending(staff.id, document.getElementById(`bonus-${staff.id}`).value, document.getElementById(`deduct-${staff.id}`).value)} className="bg-black text-white px-3 py-1 rounded text-xs hover:bg-gray-800">Apply</button>
                       <button onClick={() => deleteStaff(staff.id).then(fetchStaff)} className="bg-rose-500 text-white px-3 py-1 rounded text-xs hover:bg-rose-600 ml-auto">Remove</button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
"""

content = content.replace("    </div>\n  );\n};\n\nexport default Dashboard;", finances_tab + "\n    </div>\n  );\n};\n\nexport default Dashboard;")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Dashboard updated successfully.")
