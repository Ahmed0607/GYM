import re

filepath = 'C:/Users/DELL/Desktop/GYM/frontend/src/Reception.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Layout in Reception.jsx
ui_pattern = r'<div className="grid grid-cols-1 md:grid-cols-2 gap-8 z-50">[\s\S]*?{/\* Right: Walk-in Single Session \*/}[\s\S]*?<\/div>\n      <\/div>'

new_ui = """<div className="glass-panel p-6 sm:p-8 z-50">
        <div className="flex flex-col md:flex-row gap-6">
          {/* Left: Standard Check-in (75%) */}
          <div className="w-full md:w-3/4 relative">
            <h2 className="text-xl font-bold text-black mb-4">Member Check-in</h2>
            <form onSubmit={handleSearch} className="relative group w-full">
              <div className="absolute inset-y-0 left-0 pl-6 flex items-center pointer-events-none text-black group-focus-within:text-black transition-colors">
                <Search className="h-6 w-6" />
              </div>
              <input
                ref={searchInputRef}
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onFocus={() => {
                  if (query.trim() && !/^\\d+$/.test(query.trim()) && suggestions.length > 0) setShowSuggestions(true);
                }}
                onBlur={() => {
                  setTimeout(() => setShowSuggestions(false), 200);
                }}
                placeholder="Enter ID or Name..."
                className="w-full pl-16 pr-6 py-5 bg-white border-2 border-gray-200 rounded-2xl text-xl text-black placeholder:text-gray-500 focus:outline-none focus:border-black/50 focus:ring-4 focus:ring-gray-500/10 transition-all shadow-xl"
                disabled={loading}
              />
              {loading && (
                <div className="absolute right-6 top-1/2 -translate-y-1/2">
                  <div className="animate-spin rounded-full h-6 w-6 border-2 border-black border-t-transparent"></div>
                </div>
              )}
              
              {showSuggestions && suggestions.length > 0 && (
                <div className="absolute top-full left-0 right-0 mt-2 bg-white border border-gray-200 rounded-xl shadow-2xl overflow-hidden max-h-80 overflow-y-auto custom-scrollbar z-50">
                  {suggestions.map((sug) => (
                    <div 
                      key={sug.id} 
                      onClick={() => handleSelectMember(sug)}
                      className="flex items-center justify-between p-4 hover:bg-gray-100/80 cursor-pointer border-b border-gray-200/50 last:border-0 transition-colors"
                    >
                      <div>
                        <div className="font-bold text-black">{sug.name}</div>
                        <div className="text-sm text-gray-500">ID: {sug.id}</div>
                      </div>
                      <div className="text-right flex flex-col items-end">
                        <div className={`text-xs px-2 py-1 rounded-md mb-1 ${getStatusColor(sug.status)}`}>
                          {sug.status}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </form>
          </div>

          {/* Right: Walk-in Single Session (25%) */}
          <div className="w-full md:w-1/4 flex flex-col justify-end relative">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-black">Guest</h2>
              <span className="text-emerald-600 font-bold bg-emerald-100 px-3 py-1 rounded-full text-sm">
                ${ssPrice.toFixed(2)}
              </span>
            </div>
            <form onSubmit={handleSingleSession} className="flex gap-2 relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                <UserCheck className="h-5 w-5" />
              </div>
              <input
                type="text"
                value={ssName}
                onChange={(e) => setSsName(e.target.value)}
                className="flex-1 w-full pl-10 pr-2 py-5 bg-white border-2 border-gray-200 rounded-2xl text-lg text-black placeholder:text-gray-400 focus:outline-none focus:border-emerald-500/50 focus:ring-4 focus:ring-emerald-500/10 transition-all shadow-xl"
                placeholder="Name..."
                required
              />
              <button 
                type="submit" 
                disabled={ssLoading || !ssName.trim()}
                className="px-4 bg-black text-white rounded-2xl font-bold hover:bg-gray-800 transition-colors disabled:opacity-50 shadow-lg"
              >
                {ssLoading ? '...' : '+'}
              </button>
            </form>
          </div>
        </div>
      </div>"""

content = re.sub(ui_pattern, new_ui, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated Reception.jsx layout")
