# HomeoVault User Guide 📘

Welcome to HomeoVault! This guide will help you manage your homeopathic inventory effectively.

## 🏠 Dashboard Overview

The dashboard is your command center.

- **Stock Indicators**: At the top, you'll see counters for "Safe Stock", "Low Stock", and "Expired Items".
- **Search Bar**: Quickly find medicines by name or batch number.
- **Inventory Table**: A list of all your medicines with details like potency, form, quantity, and expiry date.

## 📦 Managing Inventory

### Adding New Medicine

1. Click the **"Add Medicine"** button in the top right.
2. Fill in the required details:
   - **Name**: e.g., "Arnica Montana"
   - **Potency**: e.g., "30C", "200C"
   - **Form**: "Dilution" or "Globules"
   - **Batch #**: Unique identifier from the bottle.
   - **Expiry Date**: Important for safety checks.
   - **Quantity**: Current stock count.
3. Click **"Save Medicine"**.

> **Note**: You cannot add a duplicate medicine with the same Name, Potency, Form, Manufacturer, and Batch Number.

### Updating Stock (Transactions)

To add or remove stock for an existing item:

1. Locate the medicine in the list.
2. Click the **"Action"** button (Update Stock).
3. **Add Stock**: Enter a positive number (e.g., `10`) to add to inventory.
4. **Sell/Remove**: Enter a negative number (e.g., `-5`) to remove from inventory.
5. Add a **Note** (optional) to explain the adjustment (e.g., "Sold to Patient X").

### Deleting Medicine

1. Locate the medicine.
2. Click the **Delete** (Trash icon) button.
3. Confirm the deletion.

> **Warning**: Deletion is permanent and removes the item from the active inventory list.

## ⚠️ Expiry Management

HomeoVault proactively helps you manage expired goods.

- **Visual Cues**: Expired items are highlighted in **Red** in the inventory list.
- **Sales Protection**: The system will prevent you from selling an expired item.
- **Override**: In special cases, you can override the sales block by adding the word `OVERRIDE` in the transaction note.

## 📊 Reports & Exports

### Viewing Reports

Click the **"Reports"** button to see a summary of:

- All currently expired items.
- Items running low on stock (below threshold).

### Exporting Data

Click **"Export CSV"** to download your entire inventory database as a `.csv` file. This can be opened in Excel or Google Sheets for further analysis or accounting.

## 💾 Backups & Data Safety

- **Automatic Backups**: Every time you restart the application, a backup of your data is saved to the `backups/` folder.
- **Restoring**: To restore a backup, close the application, rename your desired backup file to `inventory.db` and place it in the `database/` folder.
