#!/usr/bin/env python3
"""
Seed Class 1 lessons with video URLs for all subjects
"""
import os
import sys
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta, date

# Create a minimal Base class
Base = declarative_base()

class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    course_id = Column(Integer)

class Lesson(Base):
    __tablename__ = "lessons"
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    title = Column(String(255))
    description = Column(Text)
    scheduled_date = Column(Date)
    order_in_subject = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

class LessonContent(Base):
    __tablename__ = "lesson_content"
    id = Column(Integer, primary_key=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    content_type = Column(String(50))  # 'video', 'notes', 'quiz'
    title = Column(String(255))
    content_url = Column(String(500))
    content_text = Column(Text)
    order_in_lesson = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

# Use SQLite database
DATABASE_URL = "sqlite:///./dev.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Lesson data by day and subject
lesson_data = [
    {
        "Day": "1",
        "Quran": "https://youtu.be/2fUmBu_bdNE",
        "Hadees": "https://youtu.be/ISKhKn83Pus",
        "Fiqh": "https://youtu.be/9I9xLJHb-ho",
        "Swarf": "https://youtu.be/0GVdanuajco",
        "Nahv": "https://youtu.be/oxuPuR4JyZk",
    },
    {
        "Day": "2",
        "Quran": "https://youtu.be/_M3CqmqsTcw",
        "Hadees": "https://youtu.be/xNjD7uhizCY",
        "Fiqh": "https://youtu.be/17BCMXQueuo",
        "Swarf": "https://youtu.be/5a2Ao-ejb-0",
        "Nahv": "https://youtu.be/5KAO3bCnS6A",
    },
    {
        "Day": "3",
        "Quran": "https://youtu.be/K_BqPOzhS6Q",
        "Hadees": "https://youtu.be/brLMYRFL9gc",
        "Fiqh": "https://youtu.be/k2rWiN_V_5s",
        "Swarf": "https://youtu.be/VaGeRNAFPfg",
        "Nahv": "https://youtu.be/uwrEX9c_Djo",
    },
    {
        "Day": "4",
        "Quran": "https://youtu.be/UQwLqECoV3w",
        "Hadees": "https://youtu.be/AqcuVJK8B0I",
        "Fiqh": "https://youtu.be/_nV4SBMH_xU",
        "Swarf": "https://youtu.be/TvFRHpCCEIQ",
        "Nahv": "https://youtu.be/HWqc7lphkOs",
    },
    {
        "Day": "5",
        "Quran": "https://youtu.be/XZ8fJDIaJ-0",
        "Hadees": "https://youtu.be/vCGL-cI4DLw",
        "Fiqh": "https://youtu.be/jYE8-Fc69mo",
        "Swarf": "https://youtu.be/SkEBA4hRT4k",
        "Nahv": "https://youtu.be/PGnyTGvJdes",
    },
    {
        "Day": "6",
        "Quran": "https://youtu.be/84mbAp1UCVk",
        "Hadees": "https://youtu.be/bLB-Whq_0yk",
        "Fiqh": "https://youtu.be/Usj7IZhSHf8",
        "Swarf": "https://youtu.be/Cec40f73AE4",
        "Nahv": "https://youtu.be/Hzcd3Vg-I4g",
    },
    {
        "Day": "7",
        "Quran": "https://youtu.be/_Bn2ShLLlVo",
        "Hadees": "https://youtu.be/dPd65bXw64s",
        "Fiqh": "https://youtu.be/n-jaJVR8t98",
        "Swarf": "https://youtu.be/pPsjXxH29AE",
        "Nahv": "https://youtu.be/oZ7v_HgiEaU",
    },
    {
        "Day": "8",
        "Quran": "https://youtu.be/bzezuWKgPL8",
        "Hadees": "https://youtu.be/GuSvfZTxHdI",
        "Fiqh": "https://youtu.be/VhHfww-iVTw",
        "Swarf": "https://youtu.be/9ZNiYIGnOW0",
        "Nahv": "https://youtu.be/DFGmrBKANpE",
    },
    {
        "Day": "9",
        "Quran": "https://youtu.be/SqOpIxx5XEM",
        "Hadees": "https://youtu.be/9e54Q43DP9I",
        "Fiqh": "https://youtu.be/afqXl5-grMQ",
        "Swarf": "https://youtu.be/Yw6AtChV7VE",
        "Nahv": "https://youtu.be/A5HgET3OkYA",
    },
    {
        "Day": "10",
        "Quran": "https://youtu.be/_OUi_xByDFU",
        "Hadees": "https://youtu.be/0UcgKgwihuE",
        "Fiqh": "https://youtu.be/1Hb6hQJRLM4",
        "Swarf": "https://youtu.be/ayciO87fmPU",
        "Nahv": "https://youtu.be/d468KtX8UuI",
    },
    {
        "Day": "11",
        "Quran": "https://youtu.be/nQqiRwQ5BxE",
        "Hadees": "https://youtu.be/8hZoL-vO028",
        "Fiqh": "https://youtu.be/kzV80BiRvDw",
        "Swarf": "https://youtu.be/PPljBh9TqdQ",
        "Nahv": "https://youtu.be/glw8n8jJdig",
    },
    {
        "Day": "12",
        "Quran": "https://youtu.be/ZCRSZH1lN-k",
        "Hadees": "https://youtu.be/thQ6aZZvvQE",
        "Fiqh": "https://youtu.be/A3z7BHxAlbU",
        "Swarf": "https://youtu.be/7UzGM2R5LT4",
        "Nahv": "https://youtu.be/9W-1s-YnGwU",
    },
    {
        "Day": "13",
        "Quran": "https://youtu.be/5FS1O3HMQv0",
        "Hadees": "https://youtu.be/8aogaIXj0N4",
        "Fiqh": "https://youtu.be/kGOzerIGnkE",
        "Swarf": "https://youtu.be/NSR7itdF4hQ",
        "Nahv": "https://youtu.be/T9wAxfB05fM",
    },
    {
        "Day": "14",
        "Quran": "https://youtu.be/5KezxEf5VoY",
        "Hadees": "https://youtu.be/BLHnQ0BcXNA",
        "Fiqh": "https://youtu.be/VVOGw91fkUY",
        "Swarf": "https://youtu.be/vavNngqStLM",
        "Nahv": "https://youtu.be/W61QLlQrDhc",
    },
    {
        "Day": "15",
        "Quran": "https://youtu.be/P-AKHcF-TMQ",
        "Hadees": "https://youtu.be/5y9s7waqaTc",
        "Fiqh": "https://youtu.be/YX4t9gCd3qI",
        "Swarf": "https://youtu.be/y9kNEdoKLL0",
        "Nahv": "https://youtu.be/BVZ2HxW1PM8",
    },
    {
        "Day": "16",
        "Quran": "https://youtu.be/0rPflFFm4xw",
        "Hadees": "https://youtu.be/BKNHKtY9qHg",
        "Fiqh": "https://youtu.be/LM3OiJJudKE",
        "Swarf": "https://youtu.be/2VmYF60237Y",
        "Nahv": "https://youtu.be/UG6KoZB8dVk",
    },
    {
        "Day": "17",
        "Quran": "https://youtu.be/8WClZjJVaNE",
        "Hadees": "https://youtu.be/Wuv9g1TUdr0",
        "Fiqh": "https://youtu.be/xsVO-sHrwQI",
        "Swarf": "https://youtu.be/29CrJHRvgJs",
        "Nahv": "https://youtu.be/CeDyFKMIZTY",
    },
    {
        "Day": "18",
        "Quran": "https://youtu.be/qw_jf_S-2w0",
        "Hadees": "https://youtu.be/FeJTeab1VJU",
        "Fiqh": "https://youtu.be/eXsG2OkxCrU",
        "Swarf": "https://youtu.be/0GpjybQOdCM",
        "Nahv": "https://youtu.be/IB9AhStRX-M",
    },
    {
        "Day": "19",
        "Quran": "https://youtu.be/RxIqnuLEOus",
        "Hadees": "https://youtu.be/VcSEAf5iqrE",
        "Fiqh": "https://youtu.be/ReLg01E4pRI",
        "Swarf": "https://youtu.be/1-c_Y7vD_1E",
        "Nahv": "https://youtu.be/hvZxYA0V3Ao",
    },
    {
        "Day": "20",
        "Quran": "https://youtu.be/2P5fvlZg_t4",
        "Hadees": "https://youtu.be/eqeC0ds-NEk",
        "Fiqh": "https://youtu.be/GgXb73M8AsI",
        "Swarf": "https://youtu.be/6UiXFoJjfts",
        "Nahv": "https://youtu.be/nty6_lnC3u0",
    },
    {
        "Day": "21",
        "Quran": "https://youtu.be/3yozSujo49M",
        "Hadees": "https://youtu.be/Sb-kGntloAU",
        "Fiqh": "https://youtu.be/Fh4k4CTsLD4",
        "Swarf": "https://youtu.be/i4jkCz4PsJw",
        "Nahv": "https://youtu.be/tlinTQKM4nw",
    },
    {
        "Day": "22",
        "Quran": "",
        "Hadees": "https://youtu.be/m8QjD0iRlnA",
        "Fiqh": "https://youtu.be/LC0a2OF2VTw",
        "Swarf": "https://youtu.be/3OniHR6MHI0",
        "Nahv": "https://youtu.be/d2QJSuH-VJA",
    },
    {
        "Day": "23",
        "Quran": "",
        "Hadees": "https://youtu.be/37A3k05jakc",
        "Fiqh": "https://youtu.be/_CvBkT8zSoo",
        "Swarf": "https://youtu.be/LScARB7kW6Q",
        "Nahv": "https://youtu.be/zbohqHMv64E",
    },
    {
        "Day": "24",
        "Quran": "",
        "Hadees": "https://youtu.be/Hqse8yO3BBw",
        "Fiqh": "https://youtu.be/R8XAKgP-svM",
        "Swarf": "https://youtu.be/ZB5gHV56F6A",
        "Nahv": "https://youtu.be/qTG8Nrf31oo",
    },
    {
        "Day": "25",
        "Quran": "",
        "Hadees": "https://youtu.be/MCZrUpghkkU",
        "Fiqh": "https://youtu.be/eVbqdKsPxz4",
        "Swarf": "https://youtu.be/MLlJjUHSVX8",
        "Nahv": "https://youtu.be/hAP0ztRBzsk",
    },
    {
        "Day": "26",
        "Quran": "",
        "Hadees": "https://youtu.be/3-Mdk0hvVO4",
        "Fiqh": "https://youtu.be/EjbpBWL1uBI",
        "Swarf": "https://youtu.be/g3nrkIHL_O0",
        "Nahv": "https://youtu.be/gaKyuEBYqgQ",
    },
    {
        "Day": "27",
        "Quran": "",
        "Hadees": "https://youtu.be/p2RU32e65PE",
        "Fiqh": "https://youtu.be/akBtDv9Aad4",
        "Swarf": "https://youtu.be/aPqcpOxN2bU",
        "Nahv": "https://youtu.be/DXDRzcdKpWY",
    },
    {
        "Day": "28",
        "Quran": "",
        "Hadees": "https://youtu.be/VA1vp39XCFs",
        "Fiqh": "https://youtu.be/20HATo4tZTw",
        "Swarf": "https://youtu.be/i4NGOjHIQIQ",
        "Nahv": "https://youtu.be/EcyWmlC_Q-I",
    },
    {
        "Day": "29",
        "Quran": "",
        "Hadees": "https://youtu.be/Kfuq9WanaIc",
        "Fiqh": "https://youtu.be/b1TWoaknU14",
        "Swarf": "https://youtu.be/jN68zI5Mzs4",
        "Nahv": "",
    },
    {
        "Day": "30",
        "Quran": "",
        "Hadees": "https://youtu.be/lQS3Bnhkb38",
        "Fiqh": "https://youtu.be/b4dkheVOBs8",
        "Swarf": "https://youtu.be/MJ8ly9MvdvE",
        "Nahv": "",
    },
]

def get_or_create_lesson(day: int, subject_name: str, video_url: str):
    """Get or create a lesson for the given day and subject and add video content"""
    if not video_url:
        return None
    
    subject = db.query(Subject).filter(Subject.name == subject_name).first()
    if not subject:
        print(f"  Subject {subject_name} not found")
        return None
    
    # Try to find existing lesson
    lesson = db.query(Lesson).filter(
        Lesson.subject_id == subject.id,
        Lesson.title == f"{subject_name} - Day {day}"
    ).first()
    
    if not lesson:
        # Schedule lessons starting from today, one per day
        scheduled_date = date.today() + timedelta(days=day-1)
        lesson = Lesson(
            title=f"{subject_name} - Day {day}",
            description=f"Lesson for Day {day}",
            subject_id=subject.id,
            course_id=subject.course_id,
            scheduled_date=scheduled_date,
            order_in_subject=day
        )
        db.add(lesson)
        db.commit()
        db.refresh(lesson)
        print(f"  Created lesson: {subject_name} - Day {day}")
    
    # Check if video content already exists
    existing_content = db.query(LessonContent).filter(
        LessonContent.lesson_id == lesson.id,
        LessonContent.content_type == "video"
    ).first()
    
    if not existing_content:
        # Create video content
        content = LessonContent(
            lesson_id=lesson.id,
            content_type="video",
            title=f"{subject_name} Video - Day {day}",
            content_url=video_url,
            order_in_lesson=1
        )
        db.add(content)
        db.commit()
        print(f"  Added video for {subject_name} - Day {day}: {video_url}")
    else:
        # Update URL if changed
        if existing_content.content_url != video_url:
            existing_content.content_url = video_url
            db.commit()
            print(f"  Updated video for {subject_name} - Day {day}")
    
    return lesson

print("Seeding Class 1 lessons from Excel data...")
print("=" * 60)

subject_mapping = {
    "Quran": "Quran",
    "Hadees": "Hadees",
    "Fiqh": "Fiqh",
    "Swarf": "Swarf",
    "Nahv": "Nahv"
}

for entry in lesson_data:
    day = int(entry["Day"])
    print(f"\nProcessing Day {day}:")
    
    for excel_subject, db_subject in subject_mapping.items():
        video_url = entry.get(excel_subject, "").strip()
        if video_url:
            get_or_create_lesson(day, db_subject, video_url)

print("\n" + "=" * 60)
print("Class 1 lessons seeding completed!")
db.close()
