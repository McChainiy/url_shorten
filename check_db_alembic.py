# debug_metadata.py
from src.models import Base

print("Таблицы в metadata:")
for table_name in Base.metadata.tables.keys():
    print(f"  - {table_name}")
    
    # Для каждой таблицы выведем её колонки
    table = Base.metadata.tables[table_name]
    for column in table.columns:
        print(f"    * {column.name}: {column.type}")
        # Проверим внешние ключи
        for fk in column.foreign_keys:
            print(f"      → внешний ключ на {fk.column.table.name}.{fk.column.name}")