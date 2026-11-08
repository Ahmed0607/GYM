import re

filepath = 'C:/Users/DELL/Desktop/GYM/frontend/src/api.js'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

new_api = """
// ─── Single Sessions ────────────────────────────────────────────────────────
export const createSingleSession = async (name, amount) => {
  const response = await api.post('/single-sessions', { name, amount });
  return response.data;
};

export const getSingleSessionPrice = async () => {
  const response = await api.get('/config/single-session-price');
  return response.data.price;
};

export const updateSingleSessionPrice = async (price) => {
  const response = await api.post('/config/single-session-price', { price });
  return response.data;
};
"""
content += new_api

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated api.js")
