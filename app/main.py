from fastapi import FastAPI, Depends, HTTPException
from database import SessionLocal, engine
from models import Base, Device, DeviceStat, User
from sqlalchemy.orm import Session
from datetime import datetime
from crud import (
    create_device, get_device, update_device, delete_device,
    create_device_stat, get_all_devices, get_device_stats, delete_device_stats, analyze_all_devices_stats,
    analyze_user_stats, analyze_device_stats_for_user, analyze_device_stats,
    add_data_from_json
)

app = FastAPI()

def init_db():
    """Инициализация базы данных."""
    Base.metadata.create_all(bind=engine)
    add_data_from_json(db=SessionLocal())

init_db()

def get_db():
    """Зависимость для получения сессии базы данных."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/{user_id}/stats/")
def get_user_stats(user_id: int, db: Session = Depends(get_db)):
    """Получает всю статистику для одного пользователя за все время."""
    return analyze_user_stats(db, user_id)

@app.get("/users/{user_id}/devices/{device_id}/stats/")
def get_device_stats_for_user(user_id: int, device_id: int, db: Session = Depends(get_db)):
    """Получает статистику для устройства пользователя за все время."""
    return analyze_device_stats_for_user(db, user_id, device_id)

@app.get("/devices/{device_id}/stats/")
def get_all_device_stats(device_id: int, db: Session = Depends(get_db)):
    """Получает статистику для всех устройств за все время."""
    return analyze_device_stats(db, device_id)

@app.get("/devices/{device_id}/stats/")
def get_device_stats_for_period(device_id: int, start_time: datetime, end_time: datetime, db: Session = Depends(get_db)):
    """Получает статистику для устройства за указанный период времени."""
    return analyze_device_stats(db, device_id, start_time, end_time)

@app.post("/devices/")
def create_device(device: dict, db: Session = Depends(get_db)):
    """Создает новое устройство."""
    return create_device(db=db, device=device)

@app.get("/devices/{device_id}")
def read_device(device_id: int, db: Session = Depends(get_db)):
    """Получает информацию об устройстве по его идентификатору."""
    db_device = get_device(db=db, device_id=device_id)
    if db_device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return db_device

@app.put("/devices/{device_id}")
def update_device(device_id: int, device: dict, db: Session = Depends(get_db)):
    """Обновляет информацию об устройстве."""
    db_device = update_device(db=db, device_id=device_id, device=device)
    if db_device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return db_device

@app.delete("/devices/{device_id}")
def delete_device(device_id: int, db: Session = Depends(get_db)):
    """Удаляет устройство по его идентификатору."""
    db_device = delete_device(db=db, device_id=device_id)
    if db_device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return db_device

@app.get("/devices/")
def read_devices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получает список устройств с пагинацией."""
    devices = get_all_devices(db=db, skip=skip, limit=limit)
    return devices

@app.post("/devices/{device_id}/stats/")
def create_device_stat_for_device(device_id: int, stat: dict, db: Session = Depends(get_db)):
    """Создает новую запись статистики для устройства."""
    return create_device_stat(db=db, device_id=device_id, stat=stat)

@app.get("/devices/{device_id}/stats/")
def read_device_stats(device_id: int, db: Session = Depends(get_db)):
    """Получает статистику для устройства по его идентификатору."""
    return get_device_stats(db=db, device_id=device_id)

@app.delete("/devices/{device_id}/stats/")
def delete_device_stats(device_id: int, db: Session = Depends(get_db)):
    """Удаляет статистику для устройства по его идентификатору."""
    return delete_device_stats(db=db, device_id=device_id)
