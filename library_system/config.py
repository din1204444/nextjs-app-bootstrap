class Config:
    # Database Configuration
    DATABASE_URL = 'sqlite:///library.db'
    
    # System Information
    LIBRARY_NAME = "SDCKL Library"  # You can change this to your preferred library name
    DOMAIN_NAME = "library.sdckl.edu"  # You can change this domain name
    
    # Business Rules
    MAX_BOOKS_PER_USER = 3
    LOAN_PERIOD_DAYS = 14
    PENALTY_RATE = 5.00  # RM per day
    MAX_PENALTY = 50.00  # RM
    
    # System Version
    VERSION = "1.0.0"
