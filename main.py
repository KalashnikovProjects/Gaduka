import starter

if __name__ == "__main__":
    code = ["повтор 7 раз:",
            "    разделить строку: строка='1 2 3 4 5', переменная=але",
            "    если номер_повтора:",
            "        добавить текст: текст=але, текст1=номер_повтора",
            "        сжать изображение: изображение=изображения[1], коэффициент=2",
            "        добавить изображение: изображение=изображения[1]"]
    starter.run_from_console(code=code, images=("test1.jpeg", "test2.png", "test3.png"))
