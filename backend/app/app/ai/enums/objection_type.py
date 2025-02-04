"""Enums for call objection types."""

from enum import Enum


class ObjectionType(Enum):
    """Types of objections that can occur during a sales call."""
    
    # Price objections
    PRICE_TOO_HIGH = "Слишком дорого"
    NO_BUDGET = "Нет бюджета"
    CHEAPER_COMPETITOR = "У конкурентов дешевле"
    
    # Trust objections
    NEED_TO_THINK = "Надо подумать"
    NEED_TO_CONSULT = "Нужно посоветоваться"
    NEED_MORE_INFO = "Нужно больше информации"
    
    # Timing objections
    NOT_RIGHT_TIME = "Сейчас не время"
    NEED_LATER = "Вернемся к этому позже"
    
    # Competition objections
    ALREADY_HAVE_SOLUTION = "У нас уже есть решение"
    WORKING_WITH_OTHERS = "Мы работаем с другими"
    BETTER_COMPETITOR_OFFER = "У конкурентов предложение лучше"
    
    # Implementation objections
    COMPLEX_INTEGRATION = "Сложно внедрить"
    NEED_APPROVAL = "Нужно согласование"
    
    # Value objections
    NO_NEED = "Нам это не нужно"
    NOT_PRIORITY = "Это не приоритет"
    UNCLEAR_VALUE = "Не вижу ценности"
    
    # Past experience objections
    BAD_EXPERIENCE = "Был негативный опыт"
    FAILED_IMPLEMENTATION = "Внедрение не удалось"
