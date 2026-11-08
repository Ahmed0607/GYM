import re

filepath = 'C:/Users/DELL/Desktop/GYM/frontend/src/Onboarding.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update imports
import_pattern = r'import \{ createMember, listPackages, verifyPin \} from \'./api\';'
new_imports = "import { createMember, listPackages, verifyPin, checkinMember } from './api';"
content = content.replace('import { createMember, listPackages, verifyPin } from \'./api\';', new_imports)

# 2. Add state for newMember
state_pattern = r'const \[success, setSuccess\] = useState\(false\);'
new_state = """const [success, setSuccess] = useState(false);
  const [newMember, setNewMember] = useState(null);
  const [checkinLoading, setCheckinLoading] = useState(false);"""
content = re.sub(state_pattern, new_state, content)

# 3. Update handleSubmit success handling
submit_pattern = r'await createMember\(payload\);\n      setSuccess\(true\);\n      setFormData\(\{ name: \'\', phone: \'\', amountPaid: \'\', discount: \'\', gender: \'Man\', startDate: new Date\(\)\.toISOString\(\)\.split\(\'T\'\)\[0\] \}\);\n      setSelectedPackages\(new Set\(\)\);\n      setTimeout\(\(\) => setSuccess\(false\), 3000\);'
new_submit = """const res = await createMember(payload);
      setSuccess(true);
      setNewMember(res);
      setFormData({ name: '', phone: '', amountPaid: '', discount: '', gender: 'Man', startDate: new Date().toISOString().split('T')[0] });
      setSelectedPackages(new Set());
      setTimeout(() => setSuccess(false), 5000);"""
content = re.sub(submit_pattern, new_submit, content)

# 4. Add Checkin function
checkin_func = """
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
"""
content = re.sub(r'const handleSubmit = async \(e\) => \{', checkin_func + '\n  const handleSubmit = async (e) => {', content)

# 5. Add success panel
success_panel_pattern = r'\{success && \(\n        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center gap-3">\n          <Check className="w-5 h-5" />\n          Member successfully created!\n        </div>\n      \)\}'
new_success_panel = """{success && newMember && (
        <div className="p-6 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="bg-emerald-500/20 p-3 rounded-full text-emerald-500">
              <Check className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-emerald-500 font-bold text-lg">Member successfully created!</h3>
              <p className="text-emerald-600/80">Assigned ID: <span className="font-mono text-black font-bold text-lg bg-white px-2 py-1 rounded">{newMember.id}</span> for <strong>{newMember.name}</strong></p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button onClick={() => window.open(`/?memberId=${newMember.id}`, '_blank')} className="px-4 py-2 bg-white text-black font-medium rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
              View Info
            </button>
            <button 
              onClick={handleCheckin} 
              disabled={checkinLoading}
              className="px-4 py-2 bg-emerald-500 text-white font-medium rounded-lg hover:bg-emerald-600 transition-colors disabled:opacity-50"
            >
              {checkinLoading ? 'Recording...' : 'Start First Session'}
            </button>
          </div>
        </div>
      )}"""
content = re.sub(success_panel_pattern, new_success_panel, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated Onboarding.jsx successfully")
