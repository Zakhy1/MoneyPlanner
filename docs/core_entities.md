# Transaction

* occurred_at - timestamp with timezone
* kind - enum(expense, income, transfer, adjustment)
* amount - decimal(12, 2), must be positive
* account - FK(Account)
* counterparty_account - FK(Account, nullable)
* category - FK(Category, nullable)
* note - text

Rules:
* expense: `account` required, `category` required, `counterparty_account = null`
* income: `account` required, `category` required, `counterparty_account = null`
* transfer: `account` required, `counterparty_account` required, `category = null`, accounts must be different
* adjustment: `account` required, `counterparty_account = null`, `category = null`

# Account

* name - varchar(64)
* kind - enum(cash, checking, savings, credit_card, loan)
* currency_code - char(3), ISO 4217
* include_in_net_worth - bool
* opening_balance - decimal(12, 2)
* credit_limit - decimal(12, 2), nullable

Rules:
* `credit_limit` is allowed only for `credit_card`
* current balance is derived from `opening_balance` and transactions, not stored as a source of truth

# Category

* name - varchar(64)
* direction - enum(income, expense)
* parent - FK(Category, nullable)
* archived_at - timestamp with timezone, nullable

Rules:
* categories with `direction = income` can only be used by `income` transactions
* categories with `direction = expense` can only be used by `expense` transactions
