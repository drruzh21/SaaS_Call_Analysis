"""Script for generating test data for call analysis system."""
import random
from datetime import datetime, timedelta
import pytz
from sqlalchemy.orm import Session
from app.db.session import SessionLocal

from app.models import CallAnalysisResult, Objection

# Фиксированные имена менеджеров для каждой компании
COMPANY_7_MANAGERS = [
    "Иванов Петр Сергеевич",
    "Смирнова Анна Владимировна",
    "Петров Михаил Александрович",
    "Козлова Елена Дмитриевна",
    "Соколов Андрей Николаевич"
]

COMPANY_8_MANAGERS = [
    "Морозов Алексей Игоревич",
    "Волкова Мария Павловна",
    "Лебедев Дмитрий Васильевич",
    "Новикова Ольга Михайловна",
    "Федоров Сергей Андреевич"
]

# Common objections in sales
OBJECTIONS = [
    "Дорого",
    "Нужно подумать",
    "Нет денег",
    "У конкурентов дешевле",
    "Сейчас не время",
    "Нужно согласовать с руководством",
    "Мы уже работаем с другими",
    "Пришлите КП на почту",
    "Нет необходимости",
    "Не принимаем решения"
]

def get_manager_name(company_name_id: int) -> str:
    """Get a random manager name for the specified company."""
    if company_name_id == 7:
        return random.choice(COMPANY_7_MANAGERS)
    elif company_name_id == 8:
        return random.choice(COMPANY_8_MANAGERS)
    else:
        raise ValueError(f"Unexpected company_name_id: {company_name_id}")

def generate_random_date() -> datetime:
    """Generate a random date in December 2024."""
    start_date = datetime(2024, 12, 1, tzinfo=pytz.UTC)
    end_date = datetime(2024, 12, 31, 23, 59, 59, tzinfo=pytz.UTC)
    time_between_dates = end_date - start_date
    days_between = time_between_dates.days
    random_number_of_days = random.randrange(days_between)
    random_date = start_date + timedelta(days=random_number_of_days)
    # Add random hours and minutes
    random_date = random_date.replace(
        hour=random.randint(9, 17),
        minute=random.randint(0, 59)
    )
    return random_date

def generate_metric_value() -> float:
    """Generate a metric value: 0.0, 0.5, or 1.0."""
    return random.choice([0.0, 0.5, 1.0])

def generate_comment() -> str:
    """Generate a random comment."""
    comments = [
        "Менеджер хорошо справился с задачей",
        "Требуется улучшение навыков",
        "Отличная работа с возражениями",
        "Недостаточно проработан этап",
        "Успешно выявлены потребности клиента",
        "Можно лучше работать с возражениями",
        "Хорошее построение диалога",
        "Требуется больше практики",
        "Уверенное ведение разговора",
        "Есть пространство для улучшения"
    ]
    return random.choice(comments)

def create_objections(db: Session) -> list[Objection]:
    """Create objections in the database."""
    objections = []
    for obj_name in OBJECTIONS:
        objection = Objection(name=obj_name)
        db.add(objection)
        objections.append(objection)
    db.commit()
    return objections

def create_call_analysis(
    db: Session,
    company_name_id: int,
    objections: list[Objection],
    count: int = 150
) -> None:
    """Create call analysis results for a company."""
    for _ in range(count):
        # Generate metrics
        metrics = {
            'is_manager_established_contact': generate_metric_value(),
            'is_manager_holding_initiative': generate_metric_value(),
            'is_manager_using_dialog_programming': generate_metric_value(),
            'is_manager_qualifying_client': generate_metric_value(),
            'is_manager_identifying_pain': generate_metric_value(),
            'is_manager_presenting_product': generate_metric_value(),
            'is_manager_showing_expertise': generate_metric_value(),
            'is_manager_handling_objections': generate_metric_value(),
            'is_manager_setting_next_step': generate_metric_value(),
            'is_manager_using_client_framing': generate_metric_value(),
        }
        
        # Calculate final grade as average of all metrics
        final_grade = sum(metrics.values()) / len(metrics)
        
        # Create call analysis result
        call = CallAnalysisResult(
            company_name_id=company_name_id,
            date=generate_random_date(),
            manager_fio=get_manager_name(company_name_id),
            # Metrics
            **metrics,
            final_grade=final_grade,
            # Comments
            is_manager_established_contact_comment=generate_comment(),
            is_manager_holding_initiative_comment=generate_comment(),
            is_manager_using_dialog_programming_comment=generate_comment(),
            is_manager_qualifying_client_comment=generate_comment(),
            is_manager_identifying_pain_comment=generate_comment(),
            is_manager_presenting_product_comment=generate_comment(),
            is_manager_showing_expertise_comment=generate_comment(),
            is_manager_handling_objections_comment=generate_comment(),
            is_manager_setting_next_step_comment=generate_comment(),
            is_manager_using_client_framing_comment=generate_comment(),
            # Additional fields
            call_text="Текст звонка будет добавлен позже",
            analysis_reason="Плановый анализ",
            recommendations_how_to_work_with_client="Рекомендации будут добавлены позже",
            overall_analysis="Общий анализ будет добавлен позже",
            lead_url="https://example.com/lead/123"
        )
        
        # Add random objections (1-3 per call)
        num_objections = random.randint(1, 3)
        selected_objections = random.sample(objections, num_objections)
        call.objections.extend(selected_objections)
        
        db.add(call)
    
    db.commit()

def main():
    """Main function to generate test data."""
    db = SessionLocal()
    try:
        # Create objections first
        objections = create_objections(db)
        
        # Create call analysis results for company 7
        create_call_analysis(db, company_name_id=7, objections=objections)
        
        # Create call analysis results for company 8
        create_call_analysis(db, company_name_id=8, objections=objections)
        
        print("Test data generated successfully!")
    
    finally:
        db.close()

if __name__ == "__main__":
    main()
