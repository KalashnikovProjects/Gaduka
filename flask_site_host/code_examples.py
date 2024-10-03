from dataclasses import dataclass


@dataclass
class Example:
    id: str
    name: str
    code: str
    result: str


# Привет, Мир!, Циклы, Списки, работа с изображениями
EXAMPLES = [Example("1",
                    "Привет, Мир!", """печать("Привет, Мир!")
# Это комментарий
# Здесь можно писать что угодно, и это не будет выполняться!""", "Привет, Мир!"),

            Example("2", "Циклы",
                    """# Создаём некоторую переменную со значением 12
n = 12

повтор пока n > 1:
    печать("n =", n)
    повтор 3 раз:
        # Переменная 'номер_повтора' считает с 0, а не с 1
        печать("Цикл от 1 до 3 - ", номер_повтора)

    # Уменьшаем n в 2 раза
    n = n / 2""",
                    '''n = 12
Цикл от 1 до 3 - 0
Цикл от 1 до 3 - 1
Цикл от 1 до 3 - 2
n = 6.0
Цикл от 1 до 3 - 0
Цикл от 1 до 3 - 1
Цикл от 1 до 3 - 2
n = 3.0
Цикл от 1 до 3 - 0
Цикл от 1 до 3 - 1
Цикл от 1 до 3 - 2
n = 1.5
Цикл от 1 до 3 - 0
Цикл от 1 до 3 - 1
Цикл от 1 до 3 - 2'''),
            Example('3', "Списки",
                    """список_чисел = [23, 53, 14, 71, 2]

повтор длина(список_чисел) раз:
    текущее_число = список_чисел[номер_повтора]
    # Проходимся по всем числам из списка

    если текущее_число % 2 == 0:
        печать(текущее_число, "- чётное")
    иначе:
        печать(текущее_число, "- нечётное")

# Можем добавить другие элементы, даже других типов
добавить(список_чисел, "яблоко")  
печать(все_элементы(список_чисел))
""",
                    """23 - нечётное
53 - нечётное
14 - чётное
71 - нечётное
2 - чётное
23 53 14 71 2 яблоко
"""),
            Example(
                "4", "Работа с изображениями",
                """повтор длина(изображения) раз:
    текущая_картинка = изображения[номер_повтора]
    #Проходимся по списку изображений
    # Он создаётся автоматически из выбранных вами изображений

    изображение = эффекты(текущая_картинка, [блюр, серость])
    добавить_прямоугольник(текущая_картинка, где=левый_верхний_угол, ширина=0.9, высота=0.9)
    #Перенос строки с помощью тире в конце старой, и в начале новой строки
    печать(текущая_картинка)
""", """Код ничего не выведет в качестве текста. 
Данный код сделает все выбранные вами изображения чёрно-белыми и наложит на них блюр и рамку."""
            )]
