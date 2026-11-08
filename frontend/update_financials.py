import re

filepath = 'C:/Users/DELL/Desktop/GYM/frontend/src/MemberDetail.jsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Financials block
fin_pattern = r'<div className=\{`bg-gray-200/30 p-4 rounded-xl border \$\{latestSub\.amount_owed > 0 \? \'border-rose-500/20\' : \'border-gray-200/50\'\}`\}>\s*<p className="text-sm text-gray-500 mb-1">Financials</p>\s*<div className="font-semibold text-sm space-y-1">\s*<div className="text-gray-700">Total: \$\{latestSub\.total_price\.toFixed\(2\)\} \| Paid: \$\{latestSub\.amount_paid\.toFixed\(2\)\}</div>\s*<div className=\{latestSub\.amount_owed > 0 \? \'text-rose-400\' : \'text-emerald-400\'\}>\s*Owed: \$\{latestSub\.amount_owed\.toFixed\(2\)\}\s*</div>\s*</div>\s*</div>'

fin_repl = r"""<div className={`bg-gray-200/30 p-4 rounded-xl border ${latestSub.amount_owed > 0 ? 'border-rose-500/20' : 'border-gray-200/50'}`}>
                <p className="text-sm text-gray-500 mb-1">Financials</p>
                <div className="font-semibold text-sm space-y-1">
                  <div className="text-gray-700">Original Total: ${latestSub.total_price.toFixed(2)}</div>
                  {latestSub.discount > 0 && (
                    <div className="text-violet-600">Discount: -${latestSub.discount.toFixed(2)}</div>
                  )}
                  <div className="text-gray-700">Final Price: ${(latestSub.total_price - (latestSub.discount || 0)).toFixed(2)} | Paid: ${latestSub.amount_paid.toFixed(2)}</div>
                  <div className={latestSub.amount_owed > 0 ? 'text-rose-400' : 'text-emerald-400'}>
                    Owed: ${latestSub.amount_owed.toFixed(2)}
                  </div>
                </div>
              </div>"""

content = re.sub(fin_pattern, fin_repl, content)

# 2. Update Subscription history right side
hist_right_pattern = r'<div className="text-right">\s*<div className="text-gray-500 line-through text-xs">\$\{sub\.total_price\.toFixed\(2\)\}</div>\s*<div className="font-semibold text-gray-700">Paid: \$\{sub\.amount_paid\.toFixed\(2\)\}</div>\s*</div>'
hist_right_repl = r"""<div className="text-right flex flex-col items-end">
                      {sub.discount > 0 ? (
                        <>
                          <div className="text-gray-500 line-through text-xs">${sub.total_price.toFixed(2)}</div>
                          <div className="text-gray-800 font-bold">Price: ${(sub.total_price - sub.discount).toFixed(2)}</div>
                        </>
                      ) : (
                        <div className="text-gray-800 font-bold">Price: ${sub.total_price.toFixed(2)}</div>
                      )}
                      <div className="font-semibold text-gray-500 text-xs mt-1">Paid: ${sub.amount_paid.toFixed(2)}</div>
                    </div>"""
content = re.sub(hist_right_pattern, hist_right_repl, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated MemberDetail.jsx for financials and history")
