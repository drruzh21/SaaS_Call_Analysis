# Text length constraints
MAX_API_NAME_LENGTH = 100
MAX_COMMENT_LENGTH = 500
MAX_MANAGER_NAME_LENGTH = 100
MAX_CALL_TEXT_LENGTH = 5000
MAX_ANALYSIS_REASON_LENGTH = 200
MAX_RECOMMENDATIONS_LENGTH = 1000
MAX_OVERALL_ANALYSIS_LENGTH = 1000
MAX_LEAD_URL_LENGTH = 200
MAX_FULL_NAME_LENGTH = 100
MAX_EMAIL_LENGTH = 255
MAX_GPT_FILTER_PROMPT_LENGTH = 1000

# Metric constraints
METRIC_MIN_VALUE = 0.0
METRIC_MAX_VALUE = 1.0
METRIC_DEFAULT_VALUE = 0.0
METRIC_PRECISION = 10
METRIC_DECIMAL_SCALE = 5

# Security constraints
MAX_API_KEY_GENERATION_ATTEMPTS = 10
MAX_TOKEN_LENGTH = 32
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 64

# Validation patterns
EMAIL_REGEX = r"[^@]+@[^@]+\.[^@]+"
SQL_PATTERNS = [
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
