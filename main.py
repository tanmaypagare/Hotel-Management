"""Online food order processing system demonstrating a FIFO queue."""

from collections import deque
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
import itertools
import tkinter as tk
from tkinter import messagebox, ttk


# The staff selects a menu item; its price always comes from this fixed menu.
MENU = {
    "Pizza": Decimal("150"),
    "Burger": Decimal("80"),
    "Sandwich": Decimal("60"),
    "French Fries": Decimal("70"),
    "Pasta": Decimal("120"),
    "Veg Biryani": Decimal("100"),
    "Dosa": Decimal("60"),
    "Idli": Decimal("40"),
    "Cold Coffee": Decimal("70"),
    "Tea": Decimal("20"),
}


def calculate_total(food: str, quantity: int) -> Decimal:
    """Calculate an order total using the fixed menu price."""
    if food not in MENU:
        raise ValueError("Select a food item from the menu.")
    if quantity <= 0:
        raise ValueError("Quantity must be a positive whole number.")
    return MENU[food] * quantity


def timestamp() -> str:
    """Return a readable local date and time."""
    return datetime.now().strftime("%d %b %Y, %I:%M:%S %p")


@dataclass
class Order:
    """All information recorded for one restaurant order."""

    order_id: str
    customer: str
    phone: str
    food: str
    quantity: int
    unit_price: Decimal
    placed_at: str
    status: str = "Pending"
    completed_at: str = "—"

    @property
    def total(self) -> Decimal:
        return self.unit_price * self.quantity


class OrderManager:
    """Owns orders and enforces FIFO processing with collections.deque."""

    def __init__(self):
        self.pending = deque()
        self.preparing = None
        self.completed = []
        self._all_orders = {}
        self._ids = itertools.count(1)

    @property
    def all_orders(self):
        return list(self._all_orders.values())

    def add_order(self, customer, phone, food, quantity, unit_price):
        order = Order(
            order_id=f"ORD-{next(self._ids):04d}",
            customer=customer.strip(), phone=phone.strip(), food=food.strip(),
            quantity=quantity, unit_price=unit_price, placed_at=timestamp(),
        )
        self.pending.append(order)  # New orders join the rear of the queue.
        self._all_orders[order.order_id] = order
        return order

    def prepare_next(self):
        if self.preparing is not None:
            raise ValueError("Complete the current order before preparing another.")
        if not self.pending:
            raise ValueError("There are no pending orders in the queue.")
        self.preparing = self.pending.popleft()  # FIFO: remove the oldest order.
        self.preparing.status = "Preparing"
        return self.preparing

    def complete_current(self):
        if self.preparing is None:
            raise ValueError("There is no order currently being prepared.")
        order = self.preparing
        order.status = "Completed"
        order.completed_at = timestamp()
        self.completed.append(order)
        self.preparing = None
        return order

    def cancel_pending(self, order_id):
        """Remove a pending order while preserving the relative queue order."""
        for order in self.pending:
            if order.order_id == order_id:
                self.pending.remove(order)
                order.status = "Cancelled"
                return order
        raise ValueError("Only pending orders can be cancelled.")

    def search(self, query):
        query = query.strip().casefold()
        if not query:
            return self.all_orders
        return [order for order in self._all_orders.values()
                if query in order.order_id.casefold() or query in order.customer.casefold()]

    @property
    def total_sales(self):
        return sum((order.total for order in self.completed), Decimal("0.00"))


class RestaurantDashboard:
    """Tkinter dashboard for placing, preparing, searching and completing orders."""

    BG = "#f3f6fb"
    NAVY = "#172b4d"
    TEAL = "#087e8b"
    MUTED = "#62718a"

    def __init__(self, root):
        self.root = root
        self.manager = OrderManager()
        self.root.title("QueueBite | Restaurant Order Desk")
        self.root.geometry("1280x850")
        self.root.minsize(1050, 700)
        self.root.configure(bg=self.BG)
        self._setup_style()
        self._build_ui()
        self.refresh()

    def _setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=27, font=("Segoe UI", 9),
                        background="white", fieldbackground="white", foreground=self.NAVY)
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"),
                        background="#e8edf5", foreground=self.NAVY, padding=7)
        style.map("Treeview", background=[("selected", "#d5eef0")],
                  foreground=[("selected", self.NAVY)])
        style.configure("TCombobox", padding=5)

    def _build_ui(self):
        header = tk.Frame(self.root, bg=self.NAVY, padx=24, pady=16)
        header.pack(fill="x")
        tk.Label(header, text="QueueBite", bg=self.NAVY, fg="white",
                 font=("Segoe UI", 22, "bold")).pack(side="left")
        tk.Label(header, text="RESTAURANT ORDER PROCESSING SYSTEM  •  FIFO QUEUE",
                 bg=self.NAVY, fg="#c9d7eb", font=("Segoe UI", 10)).pack(side="left", padx=18, pady=(8, 0))

        body = tk.Frame(self.root, bg=self.BG, padx=18, pady=14)
        body.pack(fill="both", expand=True)
        stats = tk.Frame(body, bg=self.BG)
        stats.pack(fill="x", pady=(0, 12))
        self.stat_vars = {}
        for key, label in (("total", "TOTAL ORDERS"), ("pending", "PENDING"),
                           ("preparing", "PREPARING"), ("completed", "COMPLETED"),
                           ("sales", "COMPLETED SALES")):
            card = tk.Frame(stats, bg="white", padx=14, pady=10, highlightbackground="#e1e7f0", highlightthickness=1)
            card.pack(side="left", fill="x", expand=True, padx=(0, 9))
            tk.Label(card, text=label, bg="white", fg=self.MUTED, font=("Segoe UI", 8, "bold")).pack(anchor="w")
            var = tk.StringVar(value="0")
            self.stat_vars[key] = var
            tk.Label(card, textvariable=var, bg="white", fg=self.NAVY,
                     font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(3, 0))

        top = tk.Frame(body, bg=self.BG)
        top.pack(fill="x", pady=(0, 12))
        self._build_form(top)
        self._build_current(top)
        self._build_orders(body)

    def _panel(self, parent, title):
        panel = tk.Frame(parent, bg="white", padx=14, pady=11,
                         highlightbackground="#e1e7f0", highlightthickness=1)
        tk.Label(panel, text=title, bg="white", fg=self.NAVY,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 9))
        return panel

    def _build_form(self, parent):
        panel = self._panel(parent, "Place a new order")
        panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.inputs = {}
        self.food_var = tk.StringVar()
        self.quantity_var = tk.StringVar()
        self.price_var = tk.StringVar()
        self.total_var = tk.StringVar(value="Select food and quantity")
        grid = tk.Frame(panel, bg="white")
        grid.pack(fill="x")

        def add_field(index, label, key, widget_type="entry", textvariable=None, **options):
            row, col = divmod(index, 2)
            cell = tk.Frame(grid, bg="white")
            cell.grid(row=row, column=col, sticky="ew", padx=(0, 10), pady=3)
            tk.Label(cell, text=label, bg="white", fg=self.MUTED,
                     font=("Segoe UI", 8)).pack(anchor="w")
            if widget_type == "combobox":
                widget = ttk.Combobox(cell, textvariable=textvariable, state="readonly",
                                      values=tuple(MENU), font=("Segoe UI", 10), **options)
                widget.bind("<<ComboboxSelected>>", self.update_price_and_total)
            else:
                widget = ttk.Entry(cell, textvariable=textvariable, font=("Segoe UI", 10), **options)
            widget.pack(fill="x", pady=(3, 0))
            self.inputs[key] = widget

        add_field(0, "Customer name", "customer")
        add_field(1, "Phone number", "phone")
        add_field(2, "Food item", "food", "combobox", self.food_var)
        add_field(3, "Quantity", "quantity", textvariable=self.quantity_var)
        add_field(4, "Price per item", "price", textvariable=self.price_var, state="readonly")
        add_field(5, "Total amount", "total", textvariable=self.total_var, state="readonly")
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)
        self.quantity_var.trace_add("write", self.update_price_and_total)
        self._button(panel, "＋  Add Order", self.add_order, self.TEAL).pack(anchor="w", pady=(10, 0))

    def _build_current(self, parent):
        panel = self._panel(parent, "Current preparation")
        panel.pack(side="left", fill="both", expand=True)
        self.current_text = tk.StringVar(value="No order is being prepared.")
        tk.Label(panel, textvariable=self.current_text, bg="white", fg=self.NAVY,
                 justify="left", anchor="nw", font=("Segoe UI", 10), wraplength=420).pack(fill="both", expand=True)
        buttons = tk.Frame(panel, bg="white")
        buttons.pack(fill="x", pady=(10, 0))
        self._button(buttons, "▶  Prepare Next Order", self.prepare_next, self.NAVY).pack(side="left", padx=(0, 7))
        self._button(buttons, "✓  Complete Order", self.complete_order, "#27845a").pack(side="left")

    def _build_orders(self, parent):
        panel = self._panel(parent, "Order management")
        panel.pack(fill="both", expand=True)
        toolbar = tk.Frame(panel, bg="white")
        toolbar.pack(fill="x", pady=(0, 8))
        tk.Label(toolbar, text="Search by order ID or customer", bg="white", fg=self.MUTED,
                 font=("Segoe UI", 9)).pack(side="left")
        self.search_entry = ttk.Entry(toolbar, width=28)
        self.search_entry.pack(side="left", padx=8)
        self.search_entry.bind("<Return>", lambda _event: self.search_orders())
        self._button(toolbar, "Search", self.search_orders, self.NAVY).pack(side="left", padx=(0, 6))
        self._button(toolbar, "Clear search", self.clear_search, "#69788e").pack(side="left")
        self._button(toolbar, "Cancel selected pending", self.cancel_selected, "#b54b4b").pack(side="right")

        columns = ("id", "customer", "phone", "food", "qty", "price", "total", "placed", "status", "completed")
        self.tree = ttk.Treeview(panel, columns=columns, show="headings", selectmode="browse")
        headings = {"id": "Order ID", "customer": "Customer", "phone": "Phone", "food": "Food item",
                    "qty": "Qty", "price": "Unit price", "total": "Total", "placed": "Placed at",
                    "status": "Status", "completed": "Completed at"}
        widths = {"id": 82, "customer": 105, "phone": 98, "food": 115, "qty": 42,
                  "price": 78, "total": 76, "placed": 145, "status": 82, "completed": 145}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], minwidth=42, anchor="w" if col not in ("qty",) else "center")
        self.tree.tag_configure("Pending", foreground="#a26408")
        self.tree.tag_configure("Preparing", foreground=self.TEAL)
        self.tree.tag_configure("Completed", foreground="#27845a")
        self.tree.tag_configure("Cancelled", foreground="#9b4e4e")
        scrollbar = ttk.Scrollbar(panel, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.displayed_orders = []

    def _button(self, parent, text, command, color):
        return tk.Button(parent, text=text, command=command, bg=color, fg="white",
                         activebackground=color, activeforeground="white", relief="flat",
                         padx=11, pady=7, cursor="hand2", font=("Segoe UI", 9, "bold"))

    @staticmethod
    def _money(amount):
        return f"₹{amount:,.2f}"

    def add_order(self):
        values = {key: entry.get().strip() for key, entry in self.inputs.items()}
        if not values["customer"] or not values["phone"] or not values["food"] or not values["quantity"]:
            messagebox.showerror("Missing information", "Please fill in every order field.", parent=self.root)
            return
        try:
            quantity = int(values["quantity"])
            if quantity <= 0:
                raise ValueError("Quantity must be a positive whole number.")
        except ValueError:
            messagebox.showerror("Invalid quantity", "Quantity must be a positive whole number.", parent=self.root)
            return
        if values["food"] not in MENU:
            messagebox.showerror("Invalid food item", "Select a food item from the menu.", parent=self.root)
            return
        if len(values["phone"]) < 5 or not any(char.isdigit() for char in values["phone"]):
            messagebox.showerror("Invalid phone number", "Enter a phone number with at least 5 characters and a digit.", parent=self.root)
            return
        price = MENU[values["food"]]
        order = self.manager.add_order(values["customer"], values["phone"], values["food"], quantity, price)
        self.inputs["customer"].delete(0, "end")
        self.inputs["phone"].delete(0, "end")
        self.food_var.set("")
        self.quantity_var.set("")
        self.update_price_and_total()
        self.refresh()
        messagebox.showinfo("Order added", f"{order.order_id} added to the pending queue.\nTotal: {self._money(order.total)}", parent=self.root)

    def update_price_and_total(self, *_args):
        """Update the read-only price and total whenever food or quantity changes."""
        food = self.food_var.get()
        quantity_text = self.quantity_var.get().strip()
        if food in MENU:
            self.price_var.set(self._money(MENU[food]))
        else:
            self.price_var.set("")
        try:
            quantity = int(quantity_text)
            if quantity <= 0:
                raise ValueError
            self.total_var.set(self._money(calculate_total(food, quantity)))
        except (ValueError, TypeError):
            self.total_var.set("Enter a positive quantity" if quantity_text else "Select food and quantity")

    def prepare_next(self):
        try:
            order = self.manager.prepare_next()
        except ValueError as error:
            messagebox.showinfo("Cannot prepare order", str(error), parent=self.root)
            return
        self.refresh()
        messagebox.showinfo("Order started", f"Now preparing {order.order_id} for {order.customer}.", parent=self.root)

    def complete_order(self):
        try:
            order = self.manager.complete_current()
        except ValueError as error:
            messagebox.showinfo("No current order", str(error), parent=self.root)
            return
        self.refresh()
        messagebox.showinfo("Order completed", f"{order.order_id} marked Completed.", parent=self.root)

    def cancel_selected(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Select an order", "Select an order row first.", parent=self.root)
            return
        order_id = selection[0]
        order = self.manager._all_orders.get(order_id)
        if order is None or order.status != "Pending":
            messagebox.showinfo("Cannot cancel", "Only pending orders can be cancelled.", parent=self.root)
            return
        if messagebox.askyesno("Cancel pending order", f"Cancel {order_id} for {order.customer}?", parent=self.root):
            self.manager.cancel_pending(order_id)
            self.refresh()

    def search_orders(self):
        self.refresh(self.manager.search(self.search_entry.get()))

    def clear_search(self):
        self.search_entry.delete(0, "end")
        self.refresh()

    def refresh(self, orders=None):
        manager = self.manager
        self.stat_vars["total"].set(str(len(manager.all_orders)))
        self.stat_vars["pending"].set(str(len(manager.pending)))
        self.stat_vars["preparing"].set("1" if manager.preparing else "0")
        self.stat_vars["completed"].set(str(len(manager.completed)))
        self.stat_vars["sales"].set(self._money(manager.total_sales))
        if manager.preparing:
            order = manager.preparing
            self.current_text.set(
                f"{order.order_id}  •  {order.status}\n\nCustomer: {order.customer}\nPhone: {order.phone}\n"
                f"Food: {order.food}\nQuantity: {order.quantity}\nUnit price: {self._money(order.unit_price)}\n"
                f"Total: {self._money(order.total)}\nPlaced: {order.placed_at}"
            )
        else:
            self.current_text.set("No order is being prepared.\n\nSelect ‘Prepare Next Order’ to take the oldest pending order.")
        for item in self.tree.get_children():
            self.tree.delete(item)
        shown = manager.all_orders if orders is None else orders
        self.displayed_orders = shown
        for order in shown:
            self.tree.insert("", "end", iid=order.order_id, tags=(order.status,), values=(
                order.order_id, order.customer, order.phone, order.food, order.quantity,
                self._money(order.unit_price), self._money(order.total), order.placed_at,
                order.status, order.completed_at,
            ))


def main():
    root = tk.Tk()
    RestaurantDashboard(root)
    root.mainloop()


if __name__ == "__main__":
    main()
