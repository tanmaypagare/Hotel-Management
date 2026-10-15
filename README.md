# QueueBite — Online Food Order Processing System

## Introduction

QueueBite is a beginner-friendly restaurant order desk built with Python and Tkinter. It demonstrates how a restaurant can accept orders, prepare them in the order they arrived, and track completion in a simple desktop dashboard.

## Objectives

- Demonstrate the queue data structure and FIFO order processing.
- Accept and validate customer and food order details.
- Track pending, preparing, completed, and cancelled orders.
- Show live order counts and completed sales.

## Features

- Automatically generated order IDs, timestamps, and order totals.
- A fixed food menu with read-only prices and a live total preview.
- A pending order queue, one current preparation, and a separate completed collection.
- Search by order ID or customer name and clear the search.
- Cancel a pending order after confirmation; other statuses cannot be cancelled.
- Dashboard statistics and visible status indicators.
- Input checks for required fields, positive whole-number quantities, positive prices, and phone numbers.

## Queue data structure and FIFO principle

The `OrderManager` stores pending orders in `collections.deque`. When an order arrives, `append()` places it at the rear. `prepare_next()` uses `popleft()` to remove the order at the front. This is FIFO: First In, First Out. The oldest pending order is therefore always prepared first. The program prevents starting another order until the current one is completed.

The `deque` is the main pending-order structure. Completed orders are retained separately for history and sales totals. Cancelling an order removes it from the pending deque while preserving the order of all remaining orders.

## Menu and price calculation

Choose a food item from the dropdown. Its price is selected from the fixed menu in `main.py` and displayed in a read-only field. Enter a positive quantity to see the total update before adding the order. The fixed prices are Pizza ₹150, Burger ₹80, Sandwich ₹60, French Fries ₹70, Pasta ₹120, Veg Biryani ₹100, Dosa ₹60, Idli ₹40, Cold Coffee ₹70, and Tea ₹20. The order record stores the selected item, fixed unit price, quantity, and calculated total.

## How orders are processed

1. Enter the customer name, phone, food item, quantity, and unit price.
2. Select **Add Order**. The new order appears with `Pending` status at the end of the queue.
3. Select **Prepare Next Order**. The oldest pending order moves to preparation and becomes `Preparing`.
4. Select **Complete Order** when preparation is finished. The order moves to completed history and contributes to completed sales.
5. Repeat to process the next order.

Search the order table to locate an order. To cancel an order, select its row and choose **Cancel selected pending**; the app asks for confirmation and only permits pending orders.

## How to run

Python 3.8 or newer with Tkinter is recommended. Tkinter is included with most standard Python installations. There are no third-party dependencies.

```bash
python main.py
```

On some Linux distributions, install the operating system's Tkinter package if `tkinter` is missing (often named `python3-tk`).

## Sample test cases

| Test | Action | Expected result |
|---|---|---|
| Add several orders | Add Asha's dosa, then Ravi's thali | Both appear as Pending; total count is 2 |
| FIFO | Prepare next order | Asha's earlier dosa becomes Preparing |
| Single preparation | Click Prepare Next again before completion | App explains that the current order must be completed first |
| Complete and continue | Complete Asha's order, then prepare next | Asha is Completed; Ravi becomes Preparing |
| Empty queue | Prepare with no pending orders | App reports that the queue has no pending orders |
| Invalid input | Leave a required field blank or enter quantity 0 | App rejects the input with a message |
| Fixed price | Select Pizza, then Burger | Read-only price displays ₹150.00, then ₹80.00 |
| Live total | Select Pizza and enter quantity 2, then 3 | Total displays ₹300.00, then ₹450.00 |
| Correct saved total | Add Pizza with quantity 2 | Order row displays unit price ₹150.00 and total ₹300.00 |
| Cancel | Select a Pending order and confirm cancellation | Order status becomes Cancelled and it leaves the pending count |
| Search | Search an order ID or part of a customer's name | Matching orders are shown; Clear search restores all orders |
| Statistics | Complete an order | Completed count and completed sales update |

## Project files

- `main.py` — order model, deque-based processing, and Tkinter dashboard.
- `requirements.txt` — documents that there are no third-party packages.
