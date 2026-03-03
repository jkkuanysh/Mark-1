import re
import json

# Читаем файл чека
with open(r"C:\Users\ПК\Desktop\Python\Practice5\raw.txt", "r", encoding="utf-8") as f:
    text = f.read()

# 1. ИЗВЛЕКАЕМ ВСЕ ЦЕНЫ

# Цены в формате: 308,00 или 1 200,00 (с пробелом внутри числа)
prices = re.findall(r"\d[\d ]*,\d{2}", text)
# Убираем дубликаты "Стоимость" — берём только строки с "x" (цена за штуку)
unit_prices = re.findall(r"[\d ]+,\d{2}(?=\nСтоимость)", text)


# 2. ИЗВЛЕКАЕМ ТОВАРЫ

# Товар идёт после номера (1., 2., ...) и до строки с количеством
products = re.findall(r"^\d+\.\n(.+?)(?:\n.+?)?\n[\d ,]+x", text, re.MULTILINE)


# 3. ИТОГОВАЯ СУММА

total_match = re.search(r"ИТОГО:\n([\d ]+,\d{2})", text)
total = total_match.group(1) if total_match else "Не найдено"


# 4. ДАТА И ВРЕМЯ

datetime_match = re.search(r"Время:\s*(\d{2}\.\d{2}\.\d{4})\s+(\d{2}:\d{2}:\d{2})", text)
date = datetime_match.group(1) if datetime_match else "Не найдено"
time = datetime_match.group(2) if datetime_match else "Не найдено"


# 5. СПОСОБ ОПЛАТЫ

payment_match = re.search(r"(Банковская карта|Наличные):\n([\d ]+,\d{2})", text)
payment_method = payment_match.group(1) if payment_match else "Не найдено"
payment_amount = payment_match.group(2) if payment_match else "Не найдено"


# 6. СТРУКТУРИРОВАННЫЙ ВЫВОД

result = {
    "дата": date,
    "время": time,
    "способ_оплаты": payment_method,
    "сумма_оплаты": payment_amount,
    "итого": total,
    "количество_товаров": len(products),
    "товары": products
}

print("=" * 50)
print("РЕЗУЛЬТАТ ПАРСИНГА ЧЕКА")
print("=" * 50)
print(f"Дата:           {date}")
print(f"Время:          {time}")
print(f"Способ оплаты:  {payment_method}")
print(f"ИТОГО:          {total} тг")
print()
print(f"Товаров найдено: {len(products)}")
print("-" * 50)
for i, product in enumerate(products, 1):
    print(f"{i}. {product}")
print("-" * 50)
print()
print("JSON формат:")
print(json.dumps(result, ensure_ascii=False, indent=2))