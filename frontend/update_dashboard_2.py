import re

filepath = 'C:/Users/DELL/Desktop/GYM/frontend/src/Dashboard.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update API import
content = content.replace(
    "deleteStaff, createExpense } from './api';",
    "deleteStaff, createExpense, getFilteredFinances } from './api';"
)

# 2. Add Filter states & update Staff form states
state_injections = """  const [staffList, setStaffList] = useState([]);
  const [staffLoading, setStaffLoading] = useState(false);
  const [showAddStaff, setShowAddStaff] = useState(false);
  const [newStaffForm, setNewStaffForm] = useState({ name: '', phone: '', role: '', base_salary: '', pay_day: 1 });
  
  const [showAddExpense, setShowAddExpense] = useState(false);
  const [newExpenseForm, setNewExpenseForm] = useState({ category: 'Maintenance', amount: '', description: '' });
  
  const [financeStart, setFinanceStart] = useState('');
  const [financeEnd, setFinanceEnd] = useState('');
  const [filteredFinances, setFilteredFinances] = useState(null);
"""
content = re.sub(
    r"  const \[staffList, setStaffList\].*?description: '' \} \);",
    state_injections.strip(),
    content,
    flags=re.DOTALL
)

# 3. Add fetch logic for filtered finances
finance_handlers = """
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
"""
content = content.replace("  const handleAddExpense = async () => {", finance_handlers + "\n  const handleAddExpense = async () => {")

# 4. Update Tabs
content = content.replace(
    "{ id: 'finances', label: 'Finances', icon: Briefcase },",
    "{ id: 'finances', label: 'Finances', icon: Receipt },\n    { id: 'staff', label: 'Manage Staff', icon: Briefcase },"
)

# 5. Fix Manage Packages Edit Icon (replace text-cyan-400 hover:bg-black text-white/20 with text-gray-700 hover:bg-gray-300)
content = content.replace(
    "className=\"p-2 rounded-lg bg-gray-200 text-cyan-400 hover:bg-black text-white/20 transition-colors\"",
    "className=\"p-2 rounded-lg bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors\""
)

# 6. Fix ID colors (text-cyan-400 -> text-gray-900)
content = content.replace("text-cyan-400 font-bold", "text-black font-bold")

# 7. Redo Staff Add Handler for phone/pay_day
content = content.replace(
    "await createStaff({ name: newStaffForm.name, role: newStaffForm.role, base_salary: parseFloat(newStaffForm.base_salary) });",
    "await createStaff({ name: newStaffForm.name, phone: newStaffForm.phone || null, role: newStaffForm.role, base_salary: parseFloat(newStaffForm.base_salary), pay_day: parseInt(newStaffForm.pay_day) });"
)
content = content.replace(
    "setNewStaffForm({ name: '', role: '', base_salary: '' });",
    "setNewStaffForm({ name: '', phone: '', role: '', base_salary: '', pay_day: 1 });"
)
content = content.replace(
    "if (!newStaffForm.name || !newStaffForm.role || !newStaffForm.base_salary)",
    "if (!newStaffForm.name || !newStaffForm.role || !newStaffForm.base_salary || !newStaffForm.pay_day)"
)

# 8. Separate the Finances and Staff UI
finances_and_staff_ui = """
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

          {/* Date Filter */}
          <div className="glass-panel p-6 flex flex-wrap items-end gap-4">
            <div>
              <label className="block text-sm text-gray-500 mb-1">Start Date</label>
              <input type="date" value={financeStart} onChange={e=>setFinanceStart(e.target.value)} className="bg-gray-50 border border-gray-200 rounded-lg px-4 py-2 text-sm text-black" />
            </div>
            <div>
              <label className="block text-sm text-gray-500 mb-1">End Date</label>
              <input type="date" value={financeEnd} onChange={e=>setFinanceEnd(e.target.value)} className="bg-gray-50 border border-gray-200 rounded-lg px-4 py-2 text-sm text-black" />
            </div>
            <button onClick={handleCalculateFinances} className="px-6 py-2 bg-black text-white rounded-lg font-semibold hover:bg-gray-800 transition-colors text-sm h-[38px]">
              Calculate
            </button>
            {filteredFinances && (
              <button onClick={() => { setFilteredFinances(null); setFinanceStart(''); setFinanceEnd(''); }} className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 transition-colors text-sm h-[38px]">
                Clear Filter
              </button>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="glass-panel p-6 border-emerald-500/20 border-2">
              <div className="text-sm font-medium text-gray-500 mb-1 flex items-center gap-2"><TrendingUp className="w-4 h-4 text-emerald-500"/> Net Revenue</div>
              <div className="text-3xl font-bold text-black">${(filteredFinances ? filteredFinances.net_revenue : data.net_revenue)?.toFixed(2) || '0.00'}</div>
            </div>
            <div className="glass-panel p-6">
              <div className="text-sm font-medium text-gray-500 mb-1 flex items-center gap-2"><Briefcase className="w-4 h-4 text-rose-500"/> Salaries</div>
              <div className="text-3xl font-bold text-black">${(filteredFinances ? filteredFinances.total_salaries : data.total_salaries)?.toFixed(2) || '0.00'}</div>
            </div>
            <div className="glass-panel p-6">
              <div className="text-sm font-medium text-gray-500 mb-1 flex items-center gap-2"><Settings className="w-4 h-4 text-amber-500"/> Repairs & Maintenance</div>
              <div className="text-3xl font-bold text-black">${(filteredFinances ? filteredFinances.total_maintenance : data.total_maintenance)?.toFixed(2) || '0.00'}</div>
            </div>
            <div className="glass-panel p-6">
              <div className="text-sm font-medium text-gray-500 mb-1 flex items-center gap-2"><Receipt className="w-4 h-4 text-cyan-500"/> Bills</div>
              <div className="text-3xl font-bold text-black">${(filteredFinances ? filteredFinances.total_bills : data.total_bills)?.toFixed(2) || '0.00'}</div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
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
              <button onClick={() => setPkgError('')} className="ml-auto hover:text-rose-300"><X className="w-4 h-4" /></button>
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
              <h3 className="font-semibold text-black flex items-center gap-2"><Briefcase className="w-5 h-5"/> Staff Members</h3>
              <button onClick={() => setShowAddStaff(!showAddStaff)} className="px-4 py-2 bg-black text-white hover:bg-gray-800 font-semibold rounded-lg transition-colors flex items-center gap-2 text-sm"><Plus className="w-4 h-4"/> Add Staff</button>
            </div>
            {showAddStaff && (
              <div className="bg-white rounded-xl p-5 border border-black/20 space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
                  <input type="text" placeholder="Name" value={newStaffForm.name} onChange={e=>setNewStaffForm({...newStaffForm, name: e.target.value})} className="w-full bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm"/>
                  <input type="text" placeholder="Phone" value={newStaffForm.phone} onChange={e=>setNewStaffForm({...newStaffForm, phone: e.target.value})} className="w-full bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm"/>
                  <input type="text" placeholder="Role (e.g. Trainer)" value={newStaffForm.role} onChange={e=>setNewStaffForm({...newStaffForm, role: e.target.value})} className="w-full bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm"/>
                  <input type="number" placeholder="Salary/mo" value={newStaffForm.base_salary} onChange={e=>setNewStaffForm({...newStaffForm, base_salary: e.target.value})} className="w-full bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm"/>
                  <div className="flex items-center gap-2">
                    <label className="text-xs text-gray-500">Pay Day</label>
                    <input type="number" min="1" max="31" placeholder="Day (1-31)" value={newStaffForm.pay_day} onChange={e=>setNewStaffForm({...newStaffForm, pay_day: e.target.value})} className="w-full bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm"/>
                  </div>
                </div>
                <div className="flex gap-3">
                  <button onClick={handleAddStaff} className="px-5 py-2.5 bg-black text-white font-semibold rounded-lg hover:bg-gray-800 transition-colors text-sm">Add Staff Member</button>
                  <button onClick={() => setShowAddStaff(false)} className="px-5 py-2.5 bg-gray-200 text-gray-700 font-semibold rounded-lg hover:bg-gray-300 transition-colors text-sm">Cancel</button>
                </div>
              </div>
            )}
            
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 mt-4">
              {staffList.map(staff => (
                <div key={staff.id} className="glass-panel p-5 space-y-4 relative group">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="text-2xl font-bold text-black">{staff.name}</div>
                      <div className="text-sm font-medium text-violet-600 mb-1">{staff.role}</div>
                      <div className="text-xs text-gray-500">{staff.phone ? `Phone: ${staff.phone}` : 'No phone listed'}</div>
                      <div className="text-xs text-gray-500">Pays on the {staff.pay_day} of every month</div>
                    </div>
                    <div className="text-right">
                      <div className="text-xl font-bold text-black">${staff.base_salary}</div>
                      <div className="text-xs text-gray-400">/ month</div>
                    </div>
                  </div>
                  
                  <div className="bg-gray-50 rounded-lg p-3 border border-gray-200 space-y-2">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-gray-500">Last Paid:</span>
                      <span className="font-semibold text-black">{format(new Date(staff.last_paid_date), 'MMM d, yyyy')}</span>
                    </div>
                    <div className="flex gap-2">
                      <div className="flex-1 bg-emerald-100 rounded px-2 py-1 text-xs">
                        <span className="text-emerald-700 font-semibold">Bonus:</span> <span className="font-bold text-emerald-800">${staff.pending_bonus}</span>
                      </div>
                      <div className="flex-1 bg-rose-100 rounded px-2 py-1 text-xs">
                        <span className="text-rose-700 font-semibold">Deduct:</span> <span className="font-bold text-rose-800">${staff.pending_deduction}</span>
                      </div>
                    </div>
                    
                    <div className="flex gap-2 pt-2 border-t border-gray-200 mt-2">
                      <input type="number" id={`bonus-${staff.id}`} placeholder="+ Bonus" className="w-1/3 bg-white border border-gray-300 rounded px-2 py-1.5 text-xs focus:outline-none focus:border-black" defaultValue={staff.pending_bonus}/>
                      <input type="number" id={`deduct-${staff.id}`} placeholder="- Deduct" className="w-1/3 bg-white border border-gray-300 rounded px-2 py-1.5 text-xs focus:outline-none focus:border-black" defaultValue={staff.pending_deduction}/>
                      <button onClick={() => handleUpdatePending(staff.id, document.getElementById(`bonus-${staff.id}`).value, document.getElementById(`deduct-${staff.id}`).value)} className="w-1/3 bg-black text-white rounded text-xs font-semibold hover:bg-gray-800 transition-colors">Apply</button>
                    </div>
                  </div>
                  
                  <button onClick={() => deleteStaff(staff.id).then(fetchStaff)} className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity p-2 bg-rose-500/10 text-rose-500 hover:bg-rose-500 hover:text-white rounded-lg">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
"""
content = re.sub(r"\{\/\* ═══ FINANCES TAB ═══ \*\/\}[\s\S]*?(?=\{\/\* ═══ RECEPTIONISTS TAB ═══ \*\/|\z)", finances_and_staff_ui, content)

# Check active tab effect logic (the tab 'staff' needs fetchStaff)
content = content.replace(
    "} else if (activeTab === 'finances') {",
    "} else if (activeTab === 'finances') {\n      fetchDashboard();\n    } else if (activeTab === 'staff') {"
)


with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("update_dashboard_2 success")
