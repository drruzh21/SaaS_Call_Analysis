# Text length constraints
MAX_API_NAME_LENGTH: int = 100
MAX_COMMENT_LENGTH: int = 500
MAX_MANAGER_NAME_LENGTH: int = 100
MAX_CALL_TEXT_LENGTH: int = 5000
MAX_ANALYSIS_REASON_LENGTH: int = 200
MAX_RECOMMENDATIONS_LENGTH: int = 1000
MAX_OVERALL_ANALYSIS_LENGTH: int = 1000
MAX_LEAD_URL_LENGTH: int = 200
MAX_FULL_NAME_LENGTH: int = 100
MAX_EMAIL_LENGTH: int = 255
MAX_GPT_FILTER_PROMPT_LENGTH: int = 1000
MIN_GPT_FILTER_PROMPT_LENGTH: int = 0

# Metric constraints
METRIC_MIN_VALUE: float = 0.0
METRIC_MAX_VALUE: float = 1.0
METRIC_DEFAULT_VALUE: float = 0.0
METRIC_PRECISION: int = 10
METRIC_DECIMAL_SCALE: int = 5

# Security constraints
MAX_API_KEY_GENERATION_ATTEMPTS: int = 10
MAX_TOKEN_LENGTH: int = 32
MIN_PASSWORD_LENGTH: int = 8
MAX_PASSWORD_LENGTH: int = 64

# Validation patterns
EMAIL_REGEX: str = r"[^@]+@[^@]+\.[^@]+"
FULL_NAME_REGEX: str = r"^[a-zA-Z\s\-']+$"
PASSWORD_UPPERCASE_REGEX: str = r"[A-Z]"
PASSWORD_LOWERCASE_REGEX: str = r"[a-z]"
PASSWORD_DIGIT_REGEX: str = r"\d"
SQL_PATTERNS: list[str] = [
    r'\b(select|insert|update|delete|drop|create|alter|truncate)\b',
    r'\b(union|join|where|having|group\s+by|order\s+by)\b',
    r'\b(and|or|not|is\s+null|is\s+not\s+null)\b',
    r'(--|#|\/\*|\*\/)',
    r'\b(exec|execute|sp_|xp_)\b',
    r'(;|\||&&|=|<|>|\+|-|\*|\/)',
    r'(\|\||concat|char|substring|hex|unhex|ascii|bin|oct|decode|encode)',
    r'(\b1=1\b|\btrue=true\b|\bfalse=false\b)',
    r'(\'|\\"|\\\')|\b(cast|convert)\b'
]

# Email validation
MIN_EMAIL_LENGTH: int = 3

# General settings
GET_MULTI_MAX: int = 20

# Default GPT prompt
DEFAULT_CALL_ANALYSIS_PROMPT = """Вы - эксперт по анализу звонков отдела продаж.
Ваша задача - определить, является ли звонок целевым и требующим дальнейшего анализа.

Целевой звонок - это звонок, где:
1. Менеджер совершает первый (или иногда второй/третий) контакт с клиентом
2. Менеджер как минимум пытается вести разговор по ключевым этапам:
   - Правильное приветствие и представление
   - Получение разрешения на вопросы
   - Задает квалификационные вопросы
   - Выявляет болевые точки
   - Понимает желаемое решение клиента
   - Объясняет выгоды от встречи
   - Создает срочность
   - Делится похожими успешными кейсами
   - Подчеркивает конкурентные преимущества

Нецелевые звонки - это обычно звонки-напоминания или звонки, которые не следуют этой структуре.

ВАЖНО: Всегда отвечайте на русском языке. Ваш анализ, объяснения и все текстовые поля должны быть на русском языке."""
