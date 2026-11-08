import re

filepath = 'C:/Users/DELL/Desktop/GYM/frontend/src/Reception.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update imports
new_imports = "import { searchMembers, checkinMember, createSingleSession, getSingleSessionPrice } from './api';"
content = content.replace("import { searchMembers, checkinMember } from './api';", new_imports)

# 2. Add state and fetch for single session
state_pattern = r'const searchInputRef = useRef\(null\);\n  const debounceRef = useRef\(null\);'
new_state = """const searchInputRef = useRef(null);
  const debounceRef = useRef(null);
  
  const [ssPrice, setSsPrice] = useState(30);
  const [ssName, setSsName] = useState('');
  const [ssLoading, setSsLoading] = useState(false);"""
content = re.sub(state_pattern, new_state, content)

fetch_pattern = r'useEffect\(\(\) => \{\n    if \(searchInputRef\.current\) \{\n      searchInputRef\.current\.focus\(\);\n    \}\n  \}, \[\]\);'
new_fetch = """useEffect(() => {
    if (searchInputRef.current) {
      searchInputRef.current.focus();
    }
    const fetchPrice = async () => {
      try {
        const price = await getSingleSessionPrice();
        setSsPrice(price);
      } catch(e) {}
    };
    fetchPrice();
  }, []);"""
content = re.sub(fetch_pattern, new_fetch, content)

# 3. Add handleSingleSession
handle_ss = """
  const handleSingleSession = async (e) => {
    e.preventDefault();
    if (!ssName.trim()) return;
    setSsLoading(true);
    try {
      await createSingleSession(ssName, ssPrice);
      setSsName('');
      alert(`Walk-in session recorded for ${ssName} ($${ssPrice})`);
    } catch (err) {
      alert("Failed to record walk-in session");
    } finally {
      setSsLoading(false);
    }
  };
"""
content = content.replace('  const handleSelectMember = async (selectedMember) => {', handle_ss + '\n  const handleSelectMember = async (selectedMember) => {')

# 4. UI for Single Session
ui_old = """<form onSubmit={handleSearch} className="relative max-w-2xl mx-auto">
          <input
            ref={searchInputRef}
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setShowSuggestions(true);
            }}
            className="w-full bg-white border border-gray-200 rounded-xl px-5 py-4 pl-12 text-black placeholder-gray-400 focus:outline-none focus:border-black/50 focus:ring-2 focus:ring-gray-500/10 transition-all text-lg shadow-sm"
            placeholder="Scan ID or search name..."
          />
          <Search className="w-6 h-6 text-gray-400 absolute left-4 top-1/2 -translate-y-1/2" />
          
          {showSuggestions && suggestions.length > 0 && !/^\\d+$/.test(query.trim()) && (
            <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-xl border border-gray-100 shadow-xl overflow-hidden z-50 max-h-64 overflow-y-auto">
              {suggestions.map((s, idx) => (
                <div 
                  key={idx}
                  onClick={() => handleSelectMember(s)}
                  className="px-4 py-3 hover:bg-gray-50 cursor-pointer border-b border-gray-50 last:border-0 flex items-center justify-between"
                >
                  <div>
                    <div className="font-semibold text-black">{s.name}</div>
                    <div className="text-sm text-gray-400">ID: {s.id}</div>
                  </div>
                  <div className="text-sm px-2 py-1 bg-gray-100 text-gray-600 rounded">Select</div>
                </div>
              ))}
            </div>
          )}
        </form>"""

new_ui = """<div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
        {/* Left: Standard Check-in */}
        <div className="glass-panel p-8">
          <h2 className="text-xl font-bold text-black mb-4">Member Check-in</h2>
          <form onSubmit={handleSearch} className="relative w-full">
            <input
              ref={searchInputRef}
              type="text"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setShowSuggestions(true);
              }}
              className="w-full bg-white border border-gray-200 rounded-xl px-5 py-4 pl-12 text-black placeholder-gray-400 focus:outline-none focus:border-black/50 focus:ring-2 focus:ring-gray-500/10 transition-all text-lg shadow-sm"
              placeholder="Scan ID or search name..."
            />
            <Search className="w-6 h-6 text-gray-400 absolute left-4 top-1/2 -translate-y-1/2" />
            
            {showSuggestions && suggestions.length > 0 && !/^\\d+$/.test(query.trim()) && (
              <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-xl border border-gray-100 shadow-xl overflow-hidden z-50 max-h-64 overflow-y-auto">
                {suggestions.map((s, idx) => (
                  <div 
                    key={idx}
                    onClick={() => handleSelectMember(s)}
                    className="px-4 py-3 hover:bg-gray-50 cursor-pointer border-b border-gray-50 last:border-0 flex items-center justify-between"
                  >
                    <div>
                      <div className="font-semibold text-black">{s.name}</div>
                      <div className="text-sm text-gray-400">ID: {s.id}</div>
                    </div>
                    <div className="text-sm px-2 py-1 bg-gray-100 text-gray-600 rounded">Select</div>
                  </div>
                ))}
              </div>
            )}
          </form>
        </div>

        {/* Right: Walk-in Single Session */}
        <div className="glass-panel p-8 bg-gradient-to-br from-white to-gray-50">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-black">Walk-in Session</h2>
            <span className="text-emerald-600 font-bold bg-emerald-100 px-3 py-1 rounded-full text-sm">
              ${ssPrice.toFixed(2)}
            </span>
          </div>
          <form onSubmit={handleSingleSession} className="flex gap-3">
            <input
              type="text"
              value={ssName}
              onChange={(e) => setSsName(e.target.value)}
              className="flex-1 bg-white border border-gray-200 rounded-xl px-5 py-4 text-black placeholder-gray-400 focus:outline-none focus:border-black/50 focus:ring-2 focus:ring-gray-500/10 transition-all text-lg shadow-sm"
              placeholder="Guest Name..."
              required
            />
            <button 
              type="submit" 
              disabled={ssLoading || !ssName.trim()}
              className="px-6 bg-black text-white rounded-xl font-bold hover:bg-gray-800 transition-colors disabled:opacity-50"
            >
              {ssLoading ? '...' : 'Record'}
            </button>
          </form>
        </div>
      </div>"""

# Replace exactly
content = content.replace(ui_old, new_ui)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated Reception.jsx successfully")
