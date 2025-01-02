import json
import time
import threading
import requests
from solana.rpc.api import Client
from solders.pubkey import Pubkey
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import font
# Exclude CEX wallets
cex_wallets = ['5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1']
cex_accounts = []
TOTAL_SUPPLY = 1000000000
def update_liquid_pool_addresses(token): #need to fix this tmrw!
    global cex_accounts
    client = Client("https://cold-maximum-mound.solana-mainnet.quiknode.pro/7a1907a8e85dc53f00bbeb7623f9f9ac3532ba87")
    mint_address = Pubkey.from_string(token)
    token_accounts = json.loads(client.get_token_largest_accounts(mint_address).to_json())
    if not token_accounts['result']:
        print("Error fetching token accounts:", token_accounts)
        return None
    holders = token_accounts["result"]["value"]
    cex_accounts = [holder['address'] for holder in holders if json.loads
    (client.get_account_info_json_parsed(Pubkey.from_string(holder['address'])).to_json())
    ['result']['value']['data']['parsed']['info']['owner'] in cex_wallets]
    print(cex_accounts)


def get_top_holders(token_mint_address, limit=21):
    global cex_accounts
    client = Client("https://cold-maximum-mound.solana-mainnet.quiknode.pro/7a1907a8e85dc53f00bbeb7623f9f9ac3532ba87")
    mint_address = Pubkey.from_string(token_mint_address)
    token_accounts = json.loads(client.get_token_largest_accounts(mint_address).to_json())
    if not token_accounts['result']:
        print("Error fetching token accounts:", token_accounts)
        return None
    holders = token_accounts["result"]["value"]
    # Filter out CEX wallets
    filtered_holders = [holder for holder in holders if holder['address'] not in cex_accounts]
    top_holders = sorted(filtered_holders, key=lambda x: float(x['uiAmount']), reverse=True)[:limit]
    return top_holders

# Tkinter Application
class TokenTrackerApp:
    def __init__(self, root, token_mint_address):
        self.root = root
        self.token_mint_address = token_mint_address
        self.total_balances = []
        self.timestamps = []
        self.holder_history = {}
        self.start_time = time.time()
        self.tracking = False
        # Configure the root window
        self.root.title("Solana Token Tracker")
        self.root.geometry("800x800")
        # Create a Matplotlib figure and embed it in Tkinter
        self.fig = Figure(figsize=(8, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title(f"Top Holders' Total Balance for {token_mint_address}")
        self.ax.set_xlabel("Time (seconds)")
        self.ax.set_ylabel("Total Balance")
        self.line, = self.ax.plot([], [], label="Total Balance", color="blue")
        self.ax.legend()
        self.table_data = [["Interval", "Change (%)"],
                           ["1-min", "N/A"],
                           ["2-min", "N/A"],
                           ["5-min", "N/A"],
                           ["15-min", "N/A"]]
        self.table = self.ax.table(cellText=self.table_data,
                                   colWidths=[0.2, 0.2],
                                   loc='lower right',  # Set anchor to lower right
                                   cellLoc='center',
                                   bbox=[0.78, 0.04, 0.2, 0.25])  # Adjust position and size
        self.table.auto_set_font_size(False)
        self.table.set_fontsize(7)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        # Add controls
        self.controls_frame = tk.Frame(self.root)
        self.controls_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.address_label = tk.Label(self.controls_frame, text="Token Mint Address:")
        self.address_label.pack(side=tk.LEFT, padx=5)
        self.address_entry = tk.Entry(self.controls_frame, width=50)
        self.address_entry.insert(0, self.token_mint_address)
        self.address_entry.pack(side=tk.LEFT, padx=5)
        self.submit_button = tk.Button(self.controls_frame, text="Submit", command=self.update_address)
        self.submit_button.pack(side=tk.LEFT, padx=5)
        self.track_button = tk.Button(self.controls_frame, text="Start Tracking", command=self.toggle_tracking)
        self.track_button.pack(side=tk.LEFT, padx=5)
        # Add holder balance change display
        self.holder_frame = tk.Frame(self.root)
        self.holder_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.holder_list = tk.Text(self.holder_frame, height=40, wrap=tk.WORD)
        self.holder_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        small_font = font.Font(family="Arial", size=7)  # You can adjust the size
        self.holder_list.configure(font=small_font)
        self.scrollbar = tk.Scrollbar(self.holder_frame, command=self.holder_list.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.holder_list.config(yscrollcommand=self.scrollbar.set)
        # Start the plot update loop
        self.update_plot()

    def update_address(self):
        self.token_mint_address = self.address_entry.get()
        update_liquid_pool_addresses(self.address_entry.get())
        print(f"Updated token mint address to: {self.token_mint_address}")

    def toggle_tracking(self):
        self.tracking = not self.tracking
        if self.tracking:
            self.track_button.config(text="Stop Tracking")
            self.tracking_thread = threading.Thread(target=self.track_top_holders, daemon=True)
            self.tracking_thread.start()
        else:
            self.track_button.config(text="Start Tracking")

    def track_top_holders(self):
        while self.tracking:
            top_holders = get_top_holders(self.token_mint_address)
            if top_holders:
                current_time = time.time() - self.start_time
                self.timestamps.append(current_time)

                total_balance = sum(float(holder['uiAmount']) for holder in top_holders)
                self.total_balances.append(total_balance)

                for holder in top_holders:
                    address = holder['address']
                    balance = float(holder['uiAmount'])
                    if address not in self.holder_history:
                        self.holder_history[address] = []
                    self.holder_history[address].append((current_time, balance))

                self.update_holder_list(top_holders)

            time.sleep(1)  # Fetch data every 1 second

    def calculate_balance_changes(self, holder_address):
        if holder_address not in self.holder_history:
            return "N/A", "N/A", "N/A"

        history = self.holder_history[holder_address]
        current_time = time.time() - self.start_time

        def get_balance_at_time(delta):
            target_time = current_time - delta
            balances = [balance for time, balance in history if time >= target_time]
            return balances[0] if balances else None

        current_balance = history[-1][1]
        balance_1m = get_balance_at_time(60)
        balance_2m = get_balance_at_time(120)
        balance_5m = get_balance_at_time(300)
        balance_15m = get_balance_at_time(900)

        def calculate_change_and_percentage(current, previous):
            if previous is None:
                return "N/A", ""
            change = current - previous
            percentage = (change / previous) * 100 if previous != 0 else float('inf')
            return change, f"({percentage:.2f}%)"

        change_1m, percent_1m = calculate_change_and_percentage(current_balance, balance_1m)
        change_2m, percent_2m = calculate_change_and_percentage(current_balance, balance_2m)
        change_5m, percent_5m = calculate_change_and_percentage(current_balance, balance_5m)
        change_15m,percent_15m = calculate_change_and_percentage(current_balance, balance_5m) #add later
        return (change_1m, percent_1m), (change_2m, percent_2m), (change_5m, percent_5m)

    def update_holder_list(self, top_holders):
        self.holder_list.delete(1.0, tk.END)
        for holder in top_holders:
            address = holder['address']
            current_balance = float(holder['uiAmount'])
            (change_1m, percent_1m), (change_2m, percent_2m), (change_5m, percent_5m) = self.calculate_balance_changes(
                address)

            def format_change(change, percent):
                if change == "N/A" or change == 0:
                    return "N/A", "black"  # Default color if no change
                color = "blue" if change > 0 else "red"
                return f"{change:.2f} {percent} ({abs((change / TOTAL_SUPPLY) * 100):.2f})", color

            # Format balance changes with color
            change_1m_text, color_1m = format_change(change_1m, percent_1m)
            change_2m_text, color_2m = format_change(change_2m, percent_2m)
            change_5m_text, color_5m = format_change(change_5m, percent_5m)

            # Insert address and current balance
            self.holder_list.insert(tk.END,
                                    f"Address: {address} Balance: {current_balance:.2f} ({abs((current_balance / TOTAL_SUPPLY) * 100):.2f}%)\n")

            # Insert changes with coloring
            self.holder_list.insert(tk.END, f"1-min Change: ", ("1m", color_1m))
            self.holder_list.insert(tk.END, change_1m_text + "  ", ("1m", color_1m))

            self.holder_list.insert(tk.END, f"2-min Change: ", ("2m", color_2m))
            self.holder_list.insert(tk.END, change_2m_text + "  ", ("2m", color_2m))

            self.holder_list.insert(tk.END, f"5-min Change: ", ("5m", color_5m))
            self.holder_list.insert(tk.END, change_5m_text + "\n", ("5m", color_5m))

            self.holder_list.insert(tk.END, "\n")

            # Add tags for color styling
            self.holder_list.tag_configure(color_1m, foreground=color_1m)
            self.holder_list.tag_configure(color_2m, foreground=color_2m)
            self.holder_list.tag_configure(color_5m, foreground=color_5m)

    def update_plot(self):
        if len(self.timestamps) > 0 and len(self.total_balances) > 0:
            self.line.set_data(self.timestamps, self.total_balances)
            self.ax.relim()
            self.ax.autoscale_view()

            # Calculate changes for intervals
            def get_change(seconds):
                # Find the timestamp corresponding to the desired time interval
                target_time = self.timestamps[-1] - seconds

                # Find the closest timestamp in the past
                for i in range(len(self.timestamps) - 1, -1, -1):
                    if self.timestamps[i] <= target_time:
                        break
                else:
                    return "N/A"  # Not enough data for this interval

                # Calculate the percentage change
                change = self.total_balances[-1] - self.total_balances[i]
                percentage = (change / self.total_balances[i]) * 100 if self.total_balances[i] != 0 else float('inf')
                return f"{percentage:.2f}%"

            self.table_data[1][1] = get_change(60)  # 1-minute change
            self.table_data[2][1] = get_change(120)  # 2-minute change
            self.table_data[3][1] = get_change(300)  # 5-minute change
            self.table_data[4][1] = get_change(900)  # 15-minute change

            # Update table with new data
            for i, row in enumerate(self.table_data):
                for j, cell in enumerate(row):
                    self.table[i, j].get_text().set_text(cell)

            self.canvas.draw()

        self.root.after(1000, self.update_plot)  # Update plot every second


# Run the application
if __name__ == "__main__":
    TOKEN_MINT_ADDRESS = "3MPTUS9FEaVzh1vqbP3d3ezKu8UKvRsBL1rPgkRhpump"
    update_liquid_pool_addresses(TOKEN_MINT_ADDRESS)
    root = tk.Tk()
    app = TokenTrackerApp(root, TOKEN_MINT_ADDRESS)
    root.mainloop()



#a cool metric would be order wallets by holding time and get the sell and buy volume for walletas which have been holding longest
