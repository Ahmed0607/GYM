import re

filepath = 'C:/Users/DELL/Desktop/GYM/frontend/src/Dashboard.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Finance History Table Row
finance_row_pattern = r'<td className="py-4 px-4 text-sm font-medium">\n\s*<span className={`px-2 py-1 rounded text-xs \$\{log\.type === \'Salary\' \? \'bg-violet-100 text-violet-700\' : log\.type === \'Bill\' \? \'bg-cyan-100 text-cyan-700\' : \'bg-amber-100 text-amber-700\'\}`}>\n\s*\{log\.type\}\n\s*<\/span>\n\s*<\/td>\n\s*<td className="py-4 px-4 text-sm text-black">\{log\.description \|\| \'-\'\}<\/td>\n\s*<td className="py-4 px-4 text-sm font-bold text-rose-500 text-right">-\$\{log\.amount\.toFixed\(2\)\}<\/td>'

new_finance_row = """<td className="py-4 px-4 text-sm font-medium">
                        <span className={`px-2 py-1 rounded text-xs ${log.type === 'Salary' ? 'bg-violet-100 text-violet-700' : log.type === 'Bill' ? 'bg-cyan-100 text-cyan-700' : log.type === 'Income' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}`}>
                          {log.type}
                        </span>
                      </td>
                      <td className="py-4 px-4 text-sm text-black">{log.description || '-'}</td>
                      <td className={`py-4 px-4 text-sm font-bold text-right ${log.type === 'Income' ? 'text-emerald-500' : 'text-rose-500'}`}>
                        {log.type === 'Income' ? '+' : '-'}${Math.abs(log.amount).toFixed(2)}
                      </td>"""

content = re.sub(finance_row_pattern, new_finance_row, content)

# 2. Add API imports in Dashboard for single session price
import_pattern = r'import \{ getDashboard, addPackage, deletePackage, recordExpense, getFinancesFiltered, getStaff, addStaff, updateStaff, deleteStaff, processSalaries \} from \'./api\';'
new_imports = "import { getDashboard, addPackage, deletePackage, recordExpense, getFinancesFiltered, getStaff, addStaff, updateStaff, deleteStaff, processSalaries, getSingleSessionPrice, updateSingleSessionPrice } from './api';"
content = content.replace("import { getDashboard, addPackage, deletePackage, recordExpense, getFinancesFiltered, getStaff, addStaff, updateStaff, deleteStaff, processSalaries } from './api';", new_imports)

# 3. State and fetch for single session price
state_pattern = r'const \[packages, setPackages\] = useState\(\[\]\);'
new_state = """const [packages, setPackages] = useState([]);
  const [singleSessionPrice, setSingleSessionPrice] = useState(30);
  const [editingSessionPrice, setEditingSessionPrice] = useState(false);"""
content = re.sub(state_pattern, new_state, content)

fetch_pattern = r'const data = await getDashboard\(\);\n      setData\(data\);\n      setPackages\(data\.packages \|\| \[\]\);'
new_fetch = """const data = await getDashboard();
      setData(data);
      setPackages(data.packages || []);
      const price = await getSingleSessionPrice();
      setSingleSessionPrice(price);"""
content = re.sub(fetch_pattern, new_fetch, content)

# 4. Handle saving single session price
handle_save_price = """
  const handleSaveSessionPrice = async () => {
    try {
      await updateSingleSessionPrice(singleSessionPrice);
      setEditingSessionPrice(false);
      alert("Single Session price updated!");
    } catch (e) {
      alert("Failed to update price");
    }
  };
"""
content = re.sub(r'const handleAddPackage = async \(\) => \{', handle_save_price + '\n  const handleAddPackage = async () => {', content)

# 5. UI for Single Session Price under Manage Packages
# Look for <div className="space-y-4"> inside Manage Packages
# We can inject it right after the title "Manage Packages"
title_pattern = r'<h3 className="font-semibold text-black flex items-center gap-2 mb-4"><Package className="w-5 h-5"/> Manage Packages<\/h3>'
new_title = """<h3 className="font-semibold text-black flex items-center gap-2 mb-4"><Package className="w-5 h-5"/> Manage Packages</h3>
            <div className="flex items-center justify-between p-4 bg-emerald-50 rounded-lg border border-emerald-100 mb-6">
              <div>
                <h4 className="font-medium text-emerald-900">Single Session (Walk-in)</h4>
                <p className="text-sm text-emerald-700">Adjust the price for a 1-day walk-in pass</p>
              </div>
              <div className="flex items-center gap-2">
                {editingSessionPrice ? (
                  <>
                    <span className="text-emerald-900 font-bold">$</span>
                    <input 
                      type="number" 
                      value={singleSessionPrice}
                      onChange={(e) => setSingleSessionPrice(parseFloat(e.target.value))}
                      className="w-20 px-2 py-1 rounded border border-emerald-300 text-black text-center"
                    />
                    <button onClick={handleSaveSessionPrice} className="px-3 py-1 bg-emerald-600 text-white rounded text-sm hover:bg-emerald-700">Save</button>
                  </>
                ) : (
                  <>
                    <span className="text-2xl font-bold text-emerald-600">${singleSessionPrice}</span>
                    <button onClick={() => setEditingSessionPrice(true)} className="p-2 text-emerald-600 hover:bg-emerald-200 rounded-full"><Edit3 className="w-4 h-4"/></button>
                  </>
                )}
              </div>
            </div>"""
content = re.sub(title_pattern, new_title, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated Dashboard.jsx")
