import tkinter as tk
from tkinter import messagebox
import pandas as pd

# Constants for maximum capacities and refill threshold
MAX_CAPACITY = 10  # Each pan can hold
REFILL_THRESHOLD = 1  # Refill the pan when it drops to 1 or fewer units

# Path to the Excel file
inventory_file = 'data\Inventory.xlsx' 

# Load and save functions for inventory outside of the class
def load_inventory():
    try:
        # Adjust this according to your Excel file's structure
        df = pd.read_excel(inventory_file, index_col=[0, 1])
        df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0).astype(float)
        # make sure nan is not showed
        nan_rows = df[df['Quantity'].isna()]
        if not nan_rows.empty:
            print("NaN values found on load:", nan_rows)
        df = df.fillna({'Quantity': 0})
        # Ensure that 'Freezer' column is of type string
        df.index = pd.MultiIndex.from_arrays([df.index.get_level_values(0).astype(str), df.index.get_level_values(1)])
    except FileNotFoundError:
        df = pd.DataFrame(columns=['Freezer', 'Flavor', 'Quantity'])
        df.set_index(['Freezer', 'Flavor'], inplace=True)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while loading the inventory: {e}")
    return df


def save_inventory(inventory_df):
    nan_rows = inventory_df[inventory_df['Quantity'].isna()]
    if not nan_rows.empty:
        print("NaN values found before save:", nan_rows)
    inventory_df.to_excel(inventory_file)

# GUI Application
class InventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Gelato Inventory Management')
        self.geometry('1000x800')  # Set the window size
        self.inventory = load_inventory()  # Initialize the inventory
        self.create_widgets()  # Build the UI components

    def create_widgets(self):
        # Freezer selection
        tk.Label(self, text='Select Freezer (-18 or -12):').grid(row=0, column=0, sticky='w')
        self.freezer_var = tk.StringVar(self)
        self.freezer_entry = tk.Entry(self, textvariable=self.freezer_var)
        self.freezer_entry.grid(row=0, column=1)

        # Flavor entry
        tk.Label(self, text='Enter Flavor:').grid(row=1, column=0, sticky='w')
        self.flavor_var = tk.StringVar(self)
        self.flavor_entry = tk.Entry(self, textvariable=self.flavor_var)
        self.flavor_entry.grid(row=1, column=1)

        # Quantity entry
        tk.Label(self, text='Enter Quantity:').grid(row=2, column=0, sticky='w')
        self.quantity_var = tk.StringVar(self)
        self.quantity_entry = tk.Entry(self, textvariable=self.quantity_var)
        self.quantity_entry.grid(row=2, column=1)

        self.freezer_content_text = tk.Text(self, height=15, width=50)
        self.freezer_content_text.grid(row=5, column=0, columnspan=4)

        # Buttons
        self.add_button = tk.Button(self, text='Add Gelato', command=self.add_gelato_cmd)
        self.add_button.grid(row=3, column=0)
        self.use_button = tk.Button(self, text='Use Gelato', command=self.use_gelato_cmd)
        self.use_button.grid(row=3, column=1)
        self.refill_button = tk.Button(self, text='Get Refill Suggestions', command=self.refill_suggestions_cmd)
        self.refill_button.grid(row=4, column=0, columnspan=2)
        self.show_neg_18_button = tk.Button(self, text='Show -18 Freezer Contents', command=lambda: self.update_freezer_display('-18'))
        self.show_neg_18_button.grid(row=6, column=0)
        self.show_neg_12_button = tk.Button(self, text='Show -12 Freezer Contents', command=lambda: self.update_freezer_display('-12'))
        self.show_neg_12_button.grid(row=6, column=1)
        self.clear_inventory_button = tk.Button(self, text='Clear Freezer Inventory', command=self.clear_inventory_cmd)
        self.clear_inventory_button.grid(row=7, column=0, columnspan=2)
        self.delete_button = tk.Button(self, text='Delete Gelato', command=self.delete_row_cmd)
        self.delete_button.grid(row=4, column=2, columnspan=2)
        self.switch_button = tk.Button(self, text='Switch Freezer', command=self.switch_freezer_cmd)
        self.switch_button.grid(row=8, column=0, columnspan=2)

    def update_freezer_display(self, freezer_temp):
        self.freezer_content_text.delete('1.0', tk.END)  # Clear the current contents
        inventory_df = load_inventory()

        try:
           display_contents = inventory_df.xs(freezer_temp, level='Freezer', drop_level=False)
           for index, row in display_contents.iterrows():
               flavor_name = index[1]
               self.freezer_content_text.insert(tk.END, f"Flavor: {flavor_name}, Quantity: {row['Quantity']}\n")
        except KeyError:
           self.freezer_content_text.insert(tk.END, f"Freezer {freezer_temp} not found.\n")

    

    def add_gelato_cmd(self):
        freezer = self.freezer_var.get().strip()
        flavor = self.flavor_var.get().strip()
        if freezer not in ['-18', '-12']:
           messagebox.showerror("Error", "Please enter a valid freezer temperature (-18 or -12).")
           return
        try:
            quantity = float(self.quantity_var.get())
            self.add_gelato(freezer, flavor, quantity)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for quantity.")

    def use_gelato_cmd(self):
        freezer = self.freezer_var.get().strip()
        flavor = self.flavor_var.get().strip()
        if freezer not in ['-18', '-12']:
           messagebox.showerror("Error", "Please enter a valid freezer temperature (-18 or -12).")
           return
        try:
            quantity = float(self.quantity_var.get())
            self.use_gelato(freezer, flavor, quantity)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for quantity.")

    def refill_suggestions_cmd(self):
         suggestions = self.refill_suggestions()
         suggestions_text = '\n'.join([f'{freezer}: {", ".join(map(str, flavors))}' for freezer, flavors in suggestions.items() if flavors])
         messagebox.showinfo("Refill Suggestions", suggestions_text or "No refills needed at the moment.")

    def clear_inventory_cmd(self):
    # Prompt the user to select a freezer to clear
        freezer_to_clear = self.freezer_var.get().strip()
        if freezer_to_clear not in ['-18', '-12']:
           messagebox.showerror("Error", "Please enter a valid freezer temperature (-18 or -12) to clear.")
           return
    # Confirmation dialog
        response = messagebox.askyesno("Confirm", f"Are you sure you want to clear the inventory for freezer {freezer_to_clear}?")
        if response:
         self.clear_inventory(freezer_to_clear)

    def switch_freezer_cmd(self):
        current_freezer = self.freezer_var.get().strip()
        flavor = self.flavor_var.get().strip()
        quantity = self.quantity_var.get().strip() # You might need this if you want to switch specific quantities
    # Determine the new freezer to switch to
        new_freezer = '-12' if current_freezer == '-18' else '-18'
    # Check if the current freezer and flavor are valid and exist in the inventory
        if (current_freezer, flavor) in self.inventory.index:
            quantity_to_switch = self.inventory.loc[(current_freezer, flavor), 'Quantity']
            self.inventory.drop((current_freezer, flavor), inplace=True)  # Remove from current freezer
        # Check if the flavor already exists in the new freezer and update the quantity accordingly
            if (new_freezer, flavor) in self.inventory.index:
               self.inventory.loc[(new_freezer, flavor), 'Quantity'] += quantity_to_switch
            else:
                new_row = pd.DataFrame({'Quantity': [quantity_to_switch]}, index=pd.MultiIndex.from_tuples([(new_freezer, flavor)], names=['Freezer', 'Flavor']))
                self.inventory = pd.concat([self.inventory, new_row])
            save_inventory(self.inventory)
            self.show_inventory()
            messagebox.showinfo("Success", f"Switched {flavor} from freezer {current_freezer} to {new_freezer}.")
        else:
           messagebox.showerror("Error", f"{flavor} Flavor not found in freezer {current_freezer}.")
    
    def delete_row_cmd(self):
        self.delete_row()

    def clear_inventory(self, freezer):
    # Load the current inventory
       inventory_df = load_inventory()

    # Identify the rows corresponding to the selected freezer and clear them
       if freezer in inventory_df.index.get_level_values(0):
          inventory_df.loc[freezer, 'Flavor'] = ''  # Clear the 'Flavor' column
          inventory_df.loc[freezer, 'Quantity'] = 0  # Set the 'Quantity' to zero

        # Save the updated inventory
          save_inventory(inventory_df)
          messagebox.showinfo("Success", f"The inventory for freezer {freezer} has been cleared.")
       else:
        messagebox.showerror("Error", f"No inventory found for freezer {freezer}.")

    def add_gelato(self, freezer, flavor, quantity):
        inventory_df = load_inventory()
    
    # Ensure the DataFrame's MultiIndex is lexically sorted
        inventory_df = inventory_df.sort_index()

        key = (freezer.strip(), flavor.strip())
        if key in inventory_df.index:
        # Update the quantity for an existing flavor in the inventory
           inventory_df.loc[key, 'Quantity'] += quantity
        else:
        # Append the new flavor and quantity to the inventory
           inventory_df = inventory_df._append(pd.DataFrame({'Quantity': [quantity]}, index=pd.MultiIndex.from_tuples([key], names=['Freezer', 'Flavor'])))

        inventory_df.sort_index(inplace=True)
    # Save the updated inventory to the Excel file
        save_inventory(inventory_df)
    
        messagebox.showinfo("Success", f"Added {quantity} units of {flavor} to freezer {freezer}.")        

    def use_gelato(self, freezer, flavor, quantity):
        inventory_df = load_inventory()
        freezer = freezer.strip()
        flavor = flavor.strip()
        key = (freezer, flavor)

        try:
            if key in inventory_df.index:
                current_quantity = inventory_df.loc[key, 'Quantity']
                if isinstance(current_quantity, pd.Series) and not current_quantity.empty:
                     current_quantity = current_quantity.iloc[0] 

                new_quantity = max(current_quantity - quantity, 0)
                inventory_df.loc[key, 'Quantity'] = new_quantity
                save_inventory(inventory_df)
                messagebox.showinfo("Success", f"Used {quantity} units of {flavor} from freezer {freezer}.")
            else:
                messagebox.showerror("Error", f"{flavor} not found in freezer {freezer}.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refill_suggestions(self):
        inventory_df = load_inventory()
        inventory_df = inventory_df.dropna(subset=['Quantity'])
        suggestions = (inventory_df[inventory_df['Quantity'] <= REFILL_THRESHOLD]
                       .reset_index()
                       .groupby('Freezer')['Flavor']
                       .apply(list)
                       .to_dict())
        
        return suggestions
    
    def delete_row(self):
        freezer_temp = self.freezer_var.get().strip()

        if not freezer_temp:
            messagebox.showerror("Error", "Please enter a freezer temperature to proceed.")
            return

    # Confirm deletion of all entries from the specified freezer
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete all entries from freezer {freezer_temp}?")
        if not confirm:
            return  # User canceled the operation.
        try:
        # Check if freezer exists in the inventory
            if freezer_temp in self.inventory.index.get_level_values(0).unique():
            # Delete all rows for the specified freezer
                self.inventory = self.inventory.drop(freezer_temp, level=0)
                save_inventory(self.inventory)  # Save the updated inventory after modification.
                self.show_inventory()  # Refresh the displayed inventory.
                self.clear_text_boxes()  # Clear the input fields, if necessary.
                messagebox.showinfo("Success", f"All entries from freezer {freezer_temp} have been successfully deleted.")
            else:
                messagebox.showerror("Error", f"No entries found for freezer {freezer_temp}.")
        except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def show_inventory(self):
       self.freezer_content_text.delete('1.0', tk.END)  # Clear the current contents
    # Check if there is any inventory to display
       if not self.inventory.empty:
           for (freezer, flavor), row in self.inventory.iterrows():
              self.freezer_content_text.insert(tk.END, f"Freezer: {freezer}, Flavor: {flavor}, Quantity: {row['Quantity']}\n")
       else:
          self.freezer_content_text.insert(tk.END, "No inventory found.")

    def switch_gelato_freezer(self):
        freezer_from = self.freezer_var.get().strip()
        flavor_to_switch = self.flavor_var.get().strip()
        if not freezer_from or not flavor_to_switch:
            messagebox.showerror("Error", "Please enter both the freezer and flavor to switch.")
            return
        if freezer_from not in ['-18', '-12']:
           messagebox.showerror("Error", "Please enter a valid freezer temperature (-18 or -12).")
           return
    # Determine the freezer to switch to
        freezer_to = '-18' if freezer_from == '-12' else '-12'
        try:
        # Ensure the item exists in the source freezer
           if (freezer_from, flavor_to_switch) in self.inventory.index:
            quantity = self.inventory.loc[(freezer_from, flavor_to_switch), 'Quantity']

            # Update or add the item in the destination freezer
            if (freezer_to, flavor_to_switch) in self.inventory.index:
                self.inventory.loc[(freezer_to, flavor_to_switch), 'Quantity'] += quantity
            else:
                # Append if not exists
                new_row = pd.DataFrame({'Quantity': [quantity]}, index=pd.MultiIndex.from_tuples([(freezer_to, flavor_to_switch)], names=['Freezer', 'Flavor']))
                self.inventory = pd.concat([self.inventory, new_row])

            # Remove the item from the source freezer
            self.inventory.drop((freezer_from, flavor_to_switch), inplace=True)

            save_inventory(self.inventory)  # Assuming this function correctly saves the inventory to Excel
            self.show_inventory()
            messagebox.showinfo("Success", f"Switched {flavor_to_switch} from freezer {freezer_from} to {freezer_to}.")
           else:
            messagebox.showerror("Error", f"{flavor_to_switch} Flavor not found in freezer {freezer_from}.")
        except Exception as e:
           messagebox.showerror("Error", str(e))

    def clear_text_boxes(self):
        self.freezer_var.set('')
        self.flavor_var.set('')
        self.quantity_var.set('')

    
    def display_freezer_contents(self, freezer_temp):
        self.freezer_contents_text.delete('1.0', tk.END)
        inventory_df = load_inventory()
        try:
        # Ensure that the key used to access the inventory matches the index type
           freezer_inventory = inventory_df.xs(freezer_temp, level='Freezer')
           for flavor, row in freezer_inventory.iterrows():
               self.freezer_contents_text.insert(tk.END, f"Flavor: {row['Flavor']}, Quantity: {row['Quantity']}\n")
        except KeyError as e:
            self.freezer_contents_text.insert(tk.END, f"Error: {e}\n")

if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()
