import tkinter as tk
from tkinter import messagebox
import pandas as pd

# Constants for maximum capacities and refill threshold
MAX_CAPACITY = 10  # Assuming each pan can hold up to 10 units
REFILL_THRESHOLD = 1  # Refill the pan when it drops to 2 or fewer units

# Path to the Excel file
inventory_file = 'inventory.xlsx'

# Load and save functions for inventory outside of the class
def load_inventory():
    try:
        # Adjust this according to your Excel file's structure
        df = pd.read_excel(inventory_file, index_col=[0, 1])
        # Ensure that 'Freezer' column is of type string
        df.index = pd.MultiIndex.from_arrays([df.index.get_level_values(0).astype(str), df.index.get_level_values(1)])
    except FileNotFoundError:
        df = pd.DataFrame(columns=['Freezer', 'Flavor', 'Quantity'])
        df.set_index(['Freezer', 'Flavor'], inplace=True)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while loading the inventory: {e}")
    return df


def save_inventory(inventory_df):
    inventory_df.to_excel(inventory_file)

# GUI Application
class InventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Gelato Inventory Management')
        self.geometry('600x400')  # Set the window size
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
        try:
            quantity = int(self.quantity_var.get())
            self.add_gelato(freezer, flavor, quantity)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid integer for quantity.")

    def use_gelato_cmd(self):
        freezer = self.freezer_var.get().strip()
        flavor = self.flavor_var.get().strip()
        try:
            quantity = int(self.quantity_var.get())
            self.use_gelato(freezer, flavor, quantity)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid integer for quantity.")

    def refill_suggestions_cmd(self):
         suggestions = self.refill_suggestions()
         suggestions_text = '\n'.join([f'{freezer}: {", ".join(map(str, flavors))}' for freezer, flavors in suggestions.items() if flavors])
         messagebox.showinfo("Refill Suggestions", suggestions_text or "No refills needed at the moment.")

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
           inventory_df = inventory_df.append(pd.DataFrame({'Quantity': [quantity]}, index=pd.MultiIndex.from_tuples([key], names=['Freezer', 'Flavor'])))

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
        suggestions = (inventory_df[inventory_df['Quantity'] <= REFILL_THRESHOLD]
                       .reset_index()
                       .groupby('Freezer')['Flavor']
                       .apply(list)
                       .to_dict())
        return suggestions
    
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
