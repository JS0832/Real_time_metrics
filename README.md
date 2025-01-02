Overview
This application is a Solana Token Tracker that monitors the largest token holders of a specified Solana token. The app provides a real-time dashboard with a graphical representation of changes in token balances, along with a detailed breakdown of balance changes over various time intervals.

Features
Top Holders Tracking: Displays the top holders of a specified token, excluding centralized exchange (CEX) wallets.
Real-Time Updates: Continuously fetches and displays the token balances of top holders.
Graphical Visualization: Plots the total balance of the top holders over time using Matplotlib.
Historical Analysis: Tracks balance changes over 1-minute, 2-minute, 5-minute, and 15-minute intervals.
Interactive UI:
Change the token mint address.
Start/stop tracking dynamically.
View balance data and percentage changes in an embedded table and text display.
Requirements
Python 3.7 or higher
Libraries:
requests
json
threading
tkinter
matplotlib
solana
solders
Install dependencies with:

bash
Copy code
pip install requests matplotlib solana-python-client
How to Use
Run the script:

bash
Copy code
python solana_token_tracker.py
Initial Setup:

The default token mint address is set to 3MPTUS9FEaVzh1vqbP3d3ezKu8UKvRsBL1rPgkRhpump.
Excludes wallets specified in the cex_wallets list.
Using the App:

Change Token Address: Enter a new token mint address in the input field and click "Submit."
Start/Stop Tracking: Toggle tracking using the "Start Tracking" button.
View updates in the graph and table in real time.
Code Highlights
CEX Exclusion: Filters out centralized exchange wallets (cex_wallets) to focus on decentralized holders.
Real-Time Plotting: Uses Matplotlib to display token balance trends dynamically.
Customizable Intervals: Pre-configured to track changes for 1, 2, 5, and 15-minute intervals.
Extensible Design: The update_liquid_pool_addresses function can be modified for additional filtering criteria.
Known Issues
The update_liquid_pool_addresses function needs improvement for robust error handling and efficiency.
The app fetches data every second, which might strain the RPC endpoint for high-frequency use.
Contribution
Feel free to submit issues or pull requests on GitHub to improve the application's functionality.
