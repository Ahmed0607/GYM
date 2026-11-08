import codecs

with codecs.open('api.js', 'r', 'utf-8', errors='ignore') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "e x p o r t" in line or "consumeAddon" in line.replace(" ", ""):
        continue
    new_lines.append(line)

new_lines.append("export const consumeAddon = async (memberId, addonName) => {\n")
new_lines.append("  const response = await api.post(`/members/${memberId}/addons/consume`, { addon_name: addonName });\n")
new_lines.append("  return response.data;\n")
new_lines.append("};\n")

with codecs.open('api.js', 'w', 'utf-8') as f:
    f.writelines(new_lines)
