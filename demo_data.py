from database_setup import User, Business, Category, Account, Transaction, AccountUser, session, empty_database 
from lib_common import add_user, add_business, add_category, add_account

# Start with an empty database
empty_database()

# Create users
add_user("demo", "demo")
add_user("normal", "normal")


# Create businesses
add_business("Acme", "demo")
add_business("Wonka", "demo")
add_business("ABC Corp", "demo")
add_business("Bupa", "demo")
add_business("Coles", "demo")
add_business("Galojix", "demo")
add_business("Lowes", "demo")
add_business("Caltex", "demo")
add_business("Unknown", "demo")

add_business("BigCorp", "normal")
add_business("Tip Top", "normal")
add_business("Nine Corp", "normal")
add_business("Medibank", "normal")
add_business("Woolworths", "normal")
add_business("Telstra", "normal")
add_business("Best and Less", "normal")
add_business("Shell", "normal")
add_business("Unknown", "normal")

# Create categories
add_category("Food", "Expense", "demo")
add_category("Entertainment", "Expense", "demo")
add_category("Insurance", "Expense", "demo")
add_category("Salary", "Income", "demo")
add_category("Wages", "Income", "demo")
add_category("Rent", "Expense", "demo")
add_category("Fuel", "Expense", "demo")
add_category("Clothing", "Expense", "demo")
add_category("Unspecified Expense", "Expense", "demo")
add_category("Unspecified Income", "Income", "demo")
add_category("Entertainment", "Expense", "demo")

add_category("Food", "Expense", "normal")
add_category("Entertainment", "Expense", "normal")
add_category("Insurance", "Expense", "normal")
add_category("Salary", "Income", "normal")
add_category("Wages", "Income", "normal")
add_category("Rent", "Expense", "normal")
add_category("Fuel", "Expense", "normal")
add_category("Clothing", "Expense", "normal")
add_category("Unspecified Expense", "Expense", "normal")
add_category("Unspecified Income", "Income", "normal")
add_category("Entertainment", "Expense", "normal")

# Create accounts
add_account("NAB", 50000, "demo")
add_account("ANZ", 20000, "demo")
add_account("Suncorp", 10000, "demo")
add_account("Unknown", 0, "demo")

add_account("Westpac", 20000, "normal")
add_account("Commonwealth", 30000, "normal")
add_account("Bank of Queensland", 40000, "normal")
add_account("Unknown", 0, "normal")
