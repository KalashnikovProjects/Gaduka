import compiler

code = ["повтор 7 раз:",
        "    разделить строку: строка='1 2 3 4 5', переменная=але",
        "    добавить текст: текст=але, текст1=номер_повтора"]
a = compiler.compile_code(code=code)
print("----Гадюка код----")
print("\n".join(code))
print("\n" * 2)

print("----Питон код----")
print("\n".join(a))
print("\n" * 2)

print("----Результат----")
exec("\n".join(a))