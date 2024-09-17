from bot import *
if __name__ == '__main__':
    while True:
        try:
            value = int(input("Enter 1 to start the bot,\nEnter 2 to send a coffee message,\nEnter 3 for boost message: "))
            if value == 1:
                main()
                break
            elif value == 2:
                group_name = "your_group_name_here"  # Replace with actual group name
                asyncio.run(sendMessageToGroup(group_name, COFFEE_MESSAGE_FILE))
                break
            elif value == 3:
                group_name = "your_group_name_here"  # Replace with actual group name
                asyncio.run(sendMessageToGroup(group_name, BOOST_MESSAGE_FILE))
                break
            else:
                print("Invalid input. Please enter either 1, 2, or 3.")
        except ValueError:
            print("Please enter a valid number (1, 2, or 3).")
