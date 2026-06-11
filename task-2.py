"""
============================================================
  EXPENSE TRACKER — Python Console Application
  Demonstrates: Accumulators, Lists, Dicts, File I/O, OOP
  Author  : dhillip
  Version : 1.0.0
============================================================
"""

import csv
import os
from datetime import datetime
from collections import defaultdict

# ──────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────
CSV_FILE = "expenses.csv"

CATEGORIES = [
    "Food",
    "Travel",
    "Shopping",
    "Education",
    "Entertainment",
    "Other",
]

# CSV column headers
CSV_HEADERS = ["ID", "Amount", "Category", "Description", "Date", "Time"]


# ──────────────────────────────────────────────
# DISPLAY HELPERS
# ──────────────────────────────────────────────

def print_line(char="─", width=58):
    """Print a horizontal divider line."""
    print(char * width)


def print_header(title: str):
    """Print a section header with surrounding borders."""
    print_line("═")
    print(f"  {title.upper()}")
    print_line("═")


def format_inr(amount: float) -> str:
    """Return a ₹-prefixed, comma-formatted currency string."""
    return f"₹{amount:,.2f}"


def print_table(rows: list[dict], columns: list[str]):
    """
    Render a list of dicts as a fixed-width ASCII table.

    Parameters
    ----------
    rows    : list of expense dicts
    columns : ordered list of keys to display
    """
    if not rows:
        print("  (no records to display)")
        return

    # Determine column widths
    widths = {col: len(col) for col in columns}
    for row in rows:
        for col in columns:
            widths[col] = max(widths[col], len(str(row.get(col, ""))))

    sep = "+" + "+".join("-" * (widths[col] + 2) for col in columns) + "+"
    header = "|" + "|".join(f" {col:<{widths[col]}} " for col in columns) + "|"

    print(sep)
    print(header)
    print(sep)
    for row in rows:
        line = "|" + "|".join(f" {str(row.get(col, '')):<{widths[col]}} " for col in columns) + "|"
        print(line)
    print(sep)


# ──────────────────────────────────────────────
# DATA STORE  (in-memory list of expense dicts)
# ──────────────────────────────────────────────
#
# Each expense is a dict with keys:
#   id, amount, category, description, date, time
#
expenses: list[dict] = []
_next_id: int = 1          # auto-incrementing transaction ID
total_spent: float = 0.0   # ACCUMULATOR  ← key concept


# ──────────────────────────────────────────────
# CORE FUNCTIONS
# ──────────────────────────────────────────────

def add_expense():
    """
    Prompt the user for an expense amount, category, and optional
    description.  Uses the accumulator pattern:

        total_spent = total_spent + new_expense

    Validates all inputs and rejects negative values.
    """
    global total_spent, _next_id

    print_header("Add Expense")

    # ── Amount ──────────────────────────────
    while True:
        raw = input("  Enter amount (₹): ").strip()
        if not raw:
            print("  ⚠  Amount cannot be empty. Try again.\n")
            continue
        try:
            amount = float(raw)
        except ValueError:
            print("  ⚠  Invalid amount. Please enter a number.\n")
            continue
        if amount < 0:
            print("  ⚠  Negative expenses are not allowed.\n")
            continue
        if amount == 0:
            print("  ⚠  Amount must be greater than zero.\n")
            continue
        break

    # ── Category ────────────────────────────
    print("\n  Categories:")
    for i, cat in enumerate(CATEGORIES, 1):
        print(f"    {i}. {cat}")

    while True:
        raw_cat = input(f"  Choose category [1-{len(CATEGORIES)}]: ").strip()
        try:
            cat_idx = int(raw_cat) - 1
            if 0 <= cat_idx < len(CATEGORIES):
                category = CATEGORIES[cat_idx]
                break
            else:
                print(f"  ⚠  Enter a number between 1 and {len(CATEGORIES)}.\n")
        except ValueError:
            print("  ⚠  Please enter a valid number.\n")

    # ── Description (optional) ───────────────
    description = input("  Description (optional): ").strip() or "—"

    # ── Timestamp ───────────────────────────
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    # ── Build record ────────────────────────
    expense = {
        "id":          _next_id,
        "amount":      amount,
        "category":    category,
        "description": description,
        "date":        date_str,
        "time":        time_str,
    }

    expenses.append(expense)

    # ── ACCUMULATOR PATTERN ─────────────────
    total_spent = total_spent + amount   # ← explicit accumulation

    _next_id += 1

    print(f"\n  ✅  Expense of {format_inr(amount)} ({category}) added successfully!")
    print(f"      Running total: {format_inr(total_spent)}")
    save_data(silent=True)              # auto-save after each addition


def view_expenses():
    """
    Display all recorded expenses in a formatted table, along with a
    live running total recalculated from the list (demonstrates the
    accumulator concept iteratively).
    """
    print_header("All Expenses")

    if not expenses:
        print("  No expenses recorded yet.")
        return

    # Build display rows
    rows = []
    running = 0.0   # local accumulator for display
    for exp in expenses:
        running = running + exp["amount"]   # accumulator in loop
        rows.append({
            "#":           exp["id"],
            "Date":        exp["date"],
            "Category":    exp["category"],
            "Description": exp["description"][:20],
            "Amount":      format_inr(exp["amount"]),
            "Running ₹":   format_inr(running),
        })

    print_table(rows, ["#", "Date", "Category", "Description", "Amount", "Running ₹"])
    print(f"\n  Total transactions : {len(expenses)}")
    print(f"  Grand total        : {format_inr(total_spent)}")


def show_statistics():
    """
    Compute and display key statistics:
        - Total transactions
        - Total spent        (accumulator)
        - Average expense
        - Highest expense
        - Lowest expense
    """
    print_header("Statistics")

    if not expenses:
        print("  No data available yet.")
        return

    amounts = [exp["amount"] for exp in expenses]

    count   = len(amounts)
    total   = total_spent                  # from the accumulator
    average = total / count
    highest = max(amounts)
    lowest  = min(amounts)

    print_line()
    print(f"  {'Total Transactions':<22}: {count}")
    print(f"  {'Total Spent':<22}: {format_inr(total)}")
    print(f"  {'Average Expense':<22}: {format_inr(average)}")
    print(f"  {'Highest Expense':<22}: {format_inr(highest)}")
    print(f"  {'Lowest Expense':<22}: {format_inr(lowest)}")
    print_line()


def category_summary():
    """
    Group expenses by category and display:
        - Total per category
        - Percentage contribution of each category
    Uses a dict as an accumulator per category.
    """
    print_header("Category Summary")

    if not expenses:
        print("  No expenses to summarise.")
        return

    # Dict accumulator: category → running total
    cat_totals: dict[str, float] = defaultdict(float)
    for exp in expenses:
        cat_totals[exp["category"]] = cat_totals[exp["category"]] + exp["amount"]

    grand = total_spent if total_spent > 0 else 1   # avoid ZeroDivisionError

    rows = []
    for cat, amt in sorted(cat_totals.items(), key=lambda x: x[1], reverse=True):
        pct = (amt / grand) * 100
        rows.append({
            "Category":   cat,
            "Total":      format_inr(amt),
            "% of Total": f"{pct:.1f}%",
        })

    print_table(rows, ["Category", "Total", "% of Total"])


def search_by_category():
    """
    Filter and display expenses matching a user-chosen category.
    """
    print_header("Search by Category")

    print("  Categories:")
    for i, cat in enumerate(CATEGORIES, 1):
        print(f"    {i}. {cat}")

    while True:
        raw = input(f"  Choose category [1-{len(CATEGORIES)}]: ").strip()
        try:
            cat_idx = int(raw) - 1
            if 0 <= cat_idx < len(CATEGORIES):
                chosen = CATEGORIES[cat_idx]
                break
            else:
                print(f"  ⚠  Enter a number between 1 and {len(CATEGORIES)}.\n")
        except ValueError:
            print("  ⚠  Invalid input.\n")

    results = [exp for exp in expenses if exp["category"] == chosen]

    if not results:
        print(f"\n  No expenses found under '{chosen}'.")
        return

    rows = [
        {
            "#":      exp["id"],
            "Date":   exp["date"],
            "Desc":   exp["description"][:20],
            "Amount": format_inr(exp["amount"]),
        }
        for exp in results
    ]
    print_table(rows, ["#", "Date", "Desc", "Amount"])

    cat_total = sum(exp["amount"] for exp in results)
    print(f"\n  '{chosen}' total : {format_inr(cat_total)}  ({len(results)} transactions)")


def delete_expense():
    """
    Remove a single expense by its transaction ID.
    Adjusts the accumulator total accordingly.
    """
    global total_spent

    print_header("Delete Expense")

    if not expenses:
        print("  No expenses to delete.")
        return

    view_expenses()

    while True:
        raw = input("\n  Enter transaction # to delete (or 0 to cancel): ").strip()
        try:
            txn_id = int(raw)
        except ValueError:
            print("  ⚠  Please enter a valid number.")
            continue

        if txn_id == 0:
            print("  Cancelled.")
            return

        # Find expense with matching id
        target = next((exp for exp in expenses if exp["id"] == txn_id), None)
        if target is None:
            print(f"  ⚠  No transaction with # {txn_id}.")
            continue

        confirm = input(
            f"  Delete {format_inr(target['amount'])} ({target['category']}) on {target['date']}? [y/N]: "
        ).strip().lower()

        if confirm == "y":
            expenses.remove(target)
            total_spent = total_spent - target["amount"]   # reverse-accumulate
            print(f"  ✅  Transaction #{txn_id} deleted. New total: {format_inr(total_spent)}")
            save_data(silent=True)
        else:
            print("  Deletion cancelled.")
        return


def clear_all_expenses():
    """
    Wipe the entire expense list and reset the accumulator to zero.
    Asks for confirmation before proceeding.
    """
    global total_spent, _next_id

    print_header("Clear All Expenses")

    if not expenses:
        print("  Nothing to clear.")
        return

    confirm = input(
        f"  This will delete ALL {len(expenses)} expense(s). Type 'YES' to confirm: "
    ).strip()

    if confirm == "YES":
        expenses.clear()
        total_spent = 0.0   # reset accumulator
        _next_id = 1
        save_data(silent=True)
        print("  ✅  All expenses cleared.")
    else:
        print("  Clear operation cancelled.")


# ──────────────────────────────────────────────
# FILE I/O
# ──────────────────────────────────────────────

def save_data(silent: bool = False):
    """
    Persist the current expense list to a CSV file.

    Parameters
    ----------
    silent : if True, suppress confirmation messages (used for auto-save).
    """
    try:
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
            for exp in expenses:
                writer.writerow({
                    "ID":          exp["id"],
                    "Amount":      exp["amount"],
                    "Category":    exp["category"],
                    "Description": exp["description"],
                    "Date":        exp["date"],
                    "Time":        exp["time"],
                })
        if not silent:
            print(f"  ✅  Data saved to '{CSV_FILE}' ({len(expenses)} records).")
    except IOError as e:
        print(f"  ❌  Save failed: {e}")


def load_data():
    """
    Read expenses from the CSV file and rebuild the in-memory list
    and accumulator total.  Called automatically on startup and
    optionally from the menu.
    """
    global total_spent, _next_id

    if not os.path.exists(CSV_FILE):
        return   # nothing to load on first run

    try:
        loaded = []
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                loaded.append({
                    "id":          int(row["ID"]),
                    "amount":      float(row["Amount"]),
                    "category":    row["Category"],
                    "description": row["Description"],
                    "date":        row["Date"],
                    "time":        row["Time"],
                })

        expenses.clear()
        expenses.extend(loaded)

        # Rebuild accumulator from loaded data
        total_spent = 0.0
        for exp in expenses:
            total_spent = total_spent + exp["amount"]

        # Restore auto-increment counter
        _next_id = max((exp["id"] for exp in expenses), default=0) + 1

        print(f"  ✅  Loaded {len(expenses)} record(s) from '{CSV_FILE}'.")
    except (IOError, KeyError, ValueError) as e:
        print(f"  ⚠  Could not load data: {e}")


# ──────────────────────────────────────────────
# REPORTS
# ──────────────────────────────────────────────

def monthly_report():
    """
    Group expenses by YYYY-MM and show per-month totals and counts.
    Uses a dict accumulator: month → {"total": ..., "count": ...}
    """
    print_header("Monthly Report")

    if not expenses:
        print("  No data available.")
        return

    # Dict accumulator keyed by "YYYY-MM"
    monthly: dict[str, dict] = defaultdict(lambda: {"total": 0.0, "count": 0})
    for exp in expenses:
        month_key = exp["date"][:7]   # "YYYY-MM"
        monthly[month_key]["total"] = monthly[month_key]["total"] + exp["amount"]
        monthly[month_key]["count"] += 1

    rows = []
    for month in sorted(monthly):
        data = monthly[month]
        rows.append({
            "Month":        month,
            "Transactions": data["count"],
            "Total Spent":  format_inr(data["total"]),
            "Average":      format_inr(data["total"] / data["count"]),
        })

    print_table(rows, ["Month", "Transactions", "Total Spent", "Average"])


def summary_report():
    """
    Print a formatted summary report shown on exit.
    Mirrors the project's required output format.
    """
    print("\n")
    print_line("=")
    print("  EXPENSE TRACKER — FINAL SUMMARY")
    print_line("=")

    if not expenses:
        print("  No expenses were recorded this session.")
        print_line("=")
        return

    amounts = [exp["amount"] for exp in expenses]
    count   = len(amounts)
    average = total_spent / count
    highest = max(amounts)
    lowest  = min(amounts)

    print(f"  {'Total Transactions':<24}: {count}")
    print(f"  {'Total Spent':<24}: {format_inr(total_spent)}")
    print(f"  {'Average Expense':<24}: {format_inr(average)}")
    print(f"  {'Highest Expense':<24}: {format_inr(highest)}")
    print(f"  {'Lowest Expense':<24}: {format_inr(lowest)}")

    # Category breakdown
    cat_totals: dict[str, float] = defaultdict(float)
    for exp in expenses:
        cat_totals[exp["category"]] += exp["amount"]

    print_line()
    print("  CATEGORY BREAKDOWN")
    print_line()
    for cat, amt in sorted(cat_totals.items(), key=lambda x: x[1], reverse=True):
        pct = (amt / total_spent) * 100
        bar = "█" * int(pct / 5)   # simple ASCII bar (max 20 chars)
        print(f"  {cat:<14} {format_inr(amt):>12}  {pct:5.1f}%  {bar}")

    print_line("=")
    print(f"  Data saved to '{CSV_FILE}'")
    print_line("=")


# ──────────────────────────────────────────────
# MENU
# ──────────────────────────────────────────────

MENU_OPTIONS = {
    "1":  ("Add Expense",          add_expense),
    "2":  ("View Expenses",        view_expenses),
    "3":  ("Show Statistics",      show_statistics),
    "4":  ("Category Summary",     category_summary),
    "5":  ("Monthly Report",       monthly_report),
    "6":  ("Search by Category",   search_by_category),
    "7":  ("Delete Expense",       delete_expense),
    "8":  ("Clear All Expenses",   clear_all_expenses),
    "9":  ("Save Data",            save_data),
    "10": ("Load Data",            load_data),
    "0":  ("Exit",                 None),
}


def print_menu():
    """Render the main menu."""
    print("\n")
    print_line("═")
    print("  💰  EXPENSE TRACKER")
    if expenses:
        print(f"      {len(expenses)} record(s) | Total: {format_inr(total_spent)}")
    print_line("═")
    for key, (label, _) in MENU_OPTIONS.items():
        print(f"   {key:>2}.  {label}")
    print_line("─")


def main():
    """
    Application entry-point.
    Loads existing data, then runs the interactive menu loop.
    """
    print_line("═")
    print("  Welcome to Expense Tracker 💰")
    print("  Track your spending, understand your habits.")
    print_line("═")

    # Load previous data on startup
    load_data()

    while True:
        print_menu()
        choice = input("  Choose an option: ").strip()

        if choice == "0":
            summary_report()
            save_data(silent=True)
            print("\n  Goodbye! Stay on budget. 👋\n")
            break

        if choice not in MENU_OPTIONS:
            print("  ⚠  Invalid option. Please try again.")
            continue

        label, func = MENU_OPTIONS[choice]
        print()
        try:
            func()
        except KeyboardInterrupt:
            print("\n  (interrupted — returning to menu)")
        except Exception as e:
            print(f"  ❌  Unexpected error in '{label}': {e}")

        input("\n  Press Enter to continue…")


# ──────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────
if __name__ == "__main__":
    main()