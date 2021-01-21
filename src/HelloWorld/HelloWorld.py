def unicode_test(value):
   import unicodedata
   name = unicodedata.name(value)
   value2 = unicodedata.lookup(name)
   # 文字をUnicodeコードポイントの整数に変換
   code = ord(value)
   code_str = hex(code)
   print('value="%s", name="%s", value2="%s", code="%s"' % (value, name, value2, code_str))

print('Hello World')

language = 7
print(f'Language {language} : I am Python')
print('Language {} : I am Python'.format(language))
print('Language {0} : I am Python'.format(language))
print('Language {i} : I am Python'.format(i=language))

template = 'Language {} : I am Python'
for country in ['ja', 'en','ko']:
   print(template.format(country))

unicode_test('A')
unicode_test('$')
unicode_test('\u00a2')
unicode_test('\u20ac')

