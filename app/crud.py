import json

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import Optional, List

from models import Device, DeviceStat, User


def create_user(db: Session, username: str) -> User:
    """Создает нового пользователя в базе данных."""
    db_user = User(username=username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int) -> User:
    """Получает пользователя из базы данных по его идентификатору."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> User:
    """Получает пользователя из базы данных по его имени пользователя."""
    return db.query(User).filter(User.username == username).first()


def update_user(db: Session, user_id: int, username: str) -> User:
    """Обновляет данные пользователя в базе данных."""
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db_user.username = username
        db.commit()
        db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> User:
    """Удаляет пользователя из базы данных."""
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user


def get_all_users(db: Session) -> List[User]:
    """Получает всех пользователей из базы данных."""
    return db.query(User).all()


def create_device(db: Session, device_name: str, user_id: int) -> Device:
    """Создает новое устройство в базе данных."""
    db_device = Device(name=device_name, user_id=user_id)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


def get_device(db: Session, device_id: int) -> Device:
    """Получает устройство из базы данных по его идентификатору."""
    return db.query(Device).filter(Device.id == device_id).first()


def update_device(db: Session, device_id: int, device_name: str) -> Device:
    """Обновляет данные устройства в базе данных."""
    db_device = db.query(Device).filter(Device.id == device_id).first()
    if db_device:
        db_device.name = device_name
        db.commit()
        db.refresh(db_device)
    return db_device


def delete_device(db: Session, device_id: int) -> Device:
    """Удаляет устройство из базы данных."""
    db_device = db.query(Device).filter(Device.id == device_id).first()
    if db_device:
        db.delete(db_device)
        db.commit()
    return db_device


def get_all_devices(db: Session) -> List[Device]:
    """Получает все устройства из базы данных."""
    return db.query(Device).all()


def create_device_stat(db: Session, device_id: int, stat_data: dict):
    """Создает статистику устройства в базе данных."""
    db_stat = DeviceStat(device_id=device_id, **stat_data)
    db.add(db_stat)
    db.commit()
    db.refresh(db_stat)
    return db_stat


def get_device_stats(db: Session, device_id: int) -> List[DeviceStat]:
    """Получает статистику устройства из базы данных по его идентификатору."""
    return db.query(DeviceStat).filter(DeviceStat.device_id == device_id).all()


def delete_device_stats(db: Session, device_id: int) -> List[DeviceStat]:
    """Удаляет статистику устройства из базы данных по его идентификатору."""
    db_stats = db.query(DeviceStat).filter(DeviceStat.device_id == device_id).all()
    for stat in db_stats:
        db.delete(stat)
    db.commit()
    return db_stats


def analyze_user_stats(db: Session, user_id: int) -> dict:
    """Анализирует статистику для одного пользователя за все время."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    user_stats = []
    for device in user.devices:
        device_stats = analyze_device_stats(db, device.id)
        user_stats.append({
            "device_id": device.id,
            "device_name": device.name,
            "analysis_results": device_stats
        })

    return user_stats


def analyze_device_stats(db: Session, device_id: int, start_time: datetime = None, end_time: datetime = None) -> dict:
    """Анализирует статистику устройства за указанный временной период."""
    query = db.query(DeviceStat).filter(DeviceStat.device_id == device_id)
    if start_time:
        query = query.filter(DeviceStat.timestamp >= start_time)
    if end_time:
        query = query.filter(DeviceStat.timestamp <= end_time)
    
    stats = query.all()

    min_value = float('inf')
    max_value = float('-inf')
    total_count = len(stats)
    total_sum = 0
    values = []

    for stat in stats:
        x, y, z = stat.x, stat.y, stat.z
        min_value = min(min_value, x, y, z)
        max_value = max(max_value, x, y, z)
        total_sum += x + y + z
        values.extend([x, y, z])

    values.sort()
    n = len(values)
    median = values[n // 2] if n % 2 != 0 else (values[n // 2 - 1] + values[n // 2]) / 2

    analysis_results = {
        "min_value": min_value,
        "max_value": max_value,
        "total_count": total_count,
        "total_sum": total_sum,
        "median": median
    }

    return analysis_results


def analyze_all_devices_stats(db: Session) -> List[dict]:
    """Анализирует статистику всех устройств за все время."""
    devices = db.query(Device).all()
    analysis_results = []

    for device in devices:
        device_analysis = analyze_device_stats(db, device.id)
        analysis_results.append({
            "device_id": device.id,
            "device_name": device.name,
            "analysis_results": device_analysis
        })

    return analysis_results


def analyze_device_stats_for_user(db: Session, user_id: int, device_id: int) -> dict:
    """Анализирует статистику устройства пользователя за все время."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    device = db.query(Device).filter(Device.id == device_id, Device.user_id == user_id).first()
    if not device:
        return None
    
    return analyze_device_stats(db, device_id)


def add_data_from_json(db: Session):
    
    if db.query(func.count(User.id)).scalar() > 0:
        print("База данных уже содержит данные. Добавление данных не требуется.")
        return
    
    if db.query(func.count(Device.id)).scalar() > 0:
        print("База данных уже содержит данные устройств. Добавление данных не требуется.")
        return
    
    if db.query(func.count(DeviceStat.id)).scalar() > 0:
        print("База данных уже содержит статистику устройств. Добавление данных не требуется.")
        return

    with open('test_data.json', 'r') as file:
        data = json.load(file)
        for user_data in data['users']:
            user = create_user(db=db, username=user_data['username'])
            for device_data in user_data['devices']:
                device = create_device(db=db, device_name=device_data['name'], user_id=user.id)
                for stat_data in device_data['stats']:
                    create_device_stat(db=db, device_id=device.id, stat_data=stat_data)
