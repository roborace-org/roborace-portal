def hash_code(s):
  h = 0
  for c in s:
    h = (h << 5) - h + ord(c)
  return h


