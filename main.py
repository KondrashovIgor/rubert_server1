from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response
import pandas as pd
import io

# Создаем экземпляр приложения FastAPI
app = FastAPI(title="Cat and Dog Classifier API")

# Списки ключевых слов, как в вашем примере
cats = ['siamese', 'birman', 'abyssinian', 'russian blue', 'koshka', 'cat']
dogs = ['chihuahua', 'stafford', 'labrador', 'spaniel', 'german ovcharka', 'caucasian ovcharka', 'dalmatin', 'borzaya', 'dog']

@app.post("/predict", summary="Классифицировать тексты в CSV")
async def predict_csv(file: UploadFile = File(...)):
    """
    Принимает CSV-файл с колонкой 'text', классифицирует записи на 'cat', 'dog' или 'O'
    и возвращает обработанный CSV-файл с новой колонкой 'labels'.
    """

    # 1. Проверяем, что загруженный файл - CSV
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Ошибка: Файл должен быть в формате .csv")

    # 2. Читаем и проверяем содержимое файла
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка чтения CSV файла: {str(e)}")

    # 3. Проверяем наличие обязательной колонки 'text'
    if 'text' not in df.columns:
        raise HTTPException(status_code=400, detail="Ошибка: В CSV файле отсутствует колонка 'text'")

    # 4. ВАША ЛОГИКА МОДЕЛИ: Классифицируем тексты
    labels = []
    for item in df['text']:
        # Приводим элемент к строке на случай, если это число или None
        item_str = str(item).strip().lower()
        if item_str in cats:
            labels.append('cat')
        elif item_str in dogs:
            labels.append('dog')
        else:
            labels.append('O')
    df['labels'] = labels

    # 5. Подготавливаем CSV для отправки пользователю
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)  # Перемещаем указатель в начало "файла" в памяти

    # 6. Возвращаем файл как ответ
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=classified_{file.filename}"}
    )

# Простой endpoint для проверки, что сервер "живой"
@app.get("/")
def read_root():
    return {"message": "Сервер классификации кошек и собак работает!"}