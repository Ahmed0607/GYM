import re

filepath = 'C:/Users/DELL/Desktop/GYM/frontend/src/Dashboard.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Append finance history UI to Finances tab
finances_history_ui = """
          {/* Finance History */}
          <div className="glass-panel p-6 mt-6">
            <h3 className="font-semibold text-black flex items-center gap-2 mb-4"><FileText className="w-5 h-5"/> Financial Activity Log</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="py-3 px-4 text-xs font-semibold text-gray-500 uppercase">Date</th>
                    <th className="py-3 px-4 text-xs font-semibold text-gray-500 uppercase">Type</th>
                    <th className="py-3 px-4 text-xs font-semibold text-gray-500 uppercase">Description</th>
                    <th className="py-3 px-4 text-xs font-semibold text-gray-500 uppercase text-right">Amount</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {((filteredFinances ? filteredFinances.finance_history : data.finance_history) || []).map((log, idx) => (
                    <tr key={idx} className="hover:bg-gray-50 transition-colors">
                      <td className="py-4 px-4 text-sm text-gray-500">{format(new Date(log.date), 'MMM d, yyyy h:mm a')}</td>
                      <td className="py-4 px-4 text-sm font-medium">
                        <span className={`px-2 py-1 rounded text-xs ${log.type === 'Salary' ? 'bg-violet-100 text-violet-700' : log.type === 'Bill' ? 'bg-cyan-100 text-cyan-700' : 'bg-amber-100 text-amber-700'}`}>
                          {log.type}
                        </span>
                      </td>
                      <td className="py-4 px-4 text-sm text-black">{log.description || '-'}</td>
                      <td className="py-4 px-4 text-sm font-bold text-rose-500 text-right">-${log.amount.toFixed(2)}</td>
                    </tr>
                  ))}
                  {((filteredFinances ? filteredFinances.finance_history : data.finance_history) || []).length === 0 && (
                    <tr>
                      <td colSpan="4" className="py-8 text-center text-sm text-gray-400">No financial activity found</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
"""

# Insert right after the end of the grid that holds Record Expense (which is the last element in Finances tab before Staff tab)
content = re.sub(r'(<button onClick=\{handleAddExpense\}[\s\S]*?<\/div>\n              \}\)\n            <\/div>\n          <\/div>)', r'\1' + "\n" + finances_history_ui, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated Dashboard UI successfully")
