from getAccount import TOOL as getAccountTool
from getAccount import get_account_details

from getTransaction import TOOL as getTransactionTool
from getTransaction import get_transaction_history

from depositMoney import TOOL as depositMoneyTool
from depositMoney import deposit_money

TOOL_MAP = {
    "get_account_details": get_account_details,
    "get_transaction_history": get_transaction_history,
    "deposit_money": deposit_money
}

TOOLS = [getAccountTool, getTransactionTool, depositMoneyTool]
ReadAndWriteTools = ["deposit_money"]
ReadOnlyTools = ["get_account_details", "get_trasaction_history"]

