from .getAccount import TOOL as getAccountTool
from .getAccount import get_account_details

from .getTransaction import TOOL as getTransactionTool
from .getTransaction import get_transaction_history

from .depositMoney import TOOL as depositMoneyTool
from .depositMoney import deposit_money

from .withdrawMoney import TOOL as withdrawMoneyTool
from .withdrawMoney import withdraw_money

from .transferMoney import TOOL as transMoneyTool
from .transferMoney import transfer_money

TOOL_MAP = {
    "get_account_details": get_account_details,
    "get_transaction_history": get_transaction_history,
    "deposit_money": deposit_money,
    "withdraw_money": withdraw_money,
    "transfer_money": transfer_money
}

TOOLS = [getAccountTool, getTransactionTool, depositMoneyTool, withdrawMoneyTool, transMoneyTool]
ReadAndWriteTools = ["deposit_money", "withdraw_money", "transfer_money"]
ReadOnlyTools = ["get_account_details", "get_trasaction_history"]

