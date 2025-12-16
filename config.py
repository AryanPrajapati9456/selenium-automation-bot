# Configuration file for the Selenium automation framework

# Target URL - Using a demo/redacted URL for safety
URL = "https://demo.example.com/login"

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY_RANGE = (1, 3)  # in seconds

# Threading configuration
THREAD_COUNT = 2

# XPath selectors
XPATH_MY_SECTION = "//uni-view[@data-cur='personcenter']"
XPATH_INPUT_NUMBER = "//input[@type='text']"
XPATH_INPUT_PASSWORD = "//input[@type='password']"
XPATH_LOGIN_BUTTON = "//uni-button[@class='btn-login bg-blue margin-tb-sm lg']"
XPATH_LOGOUT = "//uni-button[@class='btn-logout bg-grey margin-tb-sm lg']"
XPATH_LOGOUT_YES = "//uni-button[normalize-space()='YES']"

# CSS selectors
CSS_POP_CANCEL = ".cu-btn.text-gray.border"
CSS_POP_CONFIRM = ".cu-btn.text-blue"
CSS_BALANCE_CONTAINER = (
    'uni-view[class="padding-xl"] '
    "uni-view:nth-child(3) "
    "uni-text:nth-child(1) "
    "span:nth-child(1)"
)

# Delay ranges for human-like behavior (in seconds)
HUMAN_SLEEP_SHORT = (0.2, 0.6)
HUMAN_SLEEP_MEDIUM = (1.5, 2.0)
HUMAN_SLEEP_LONG = (3.0, 5.0)