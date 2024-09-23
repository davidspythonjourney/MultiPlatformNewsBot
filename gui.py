import tkinter as tk 
from tkinter import filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES
import customtkinter as ctk


from bot import sendMessageToGroup


class Buttons(ctk.CTkFrame):
    def __init__(self, master, message_frame):
        super().__init__(master)
        self.message_frame = message_frame
        button_names = ["Send News Message", "Send Coffee Message", "Send Telegram Boost Message"]
        button_commands = [self.sendNewMessage, self.sendTipMessage, self.sendBoostMessage]
        for index, (btn_name, cmd) in enumerate(zip(button_names, button_commands)):
            button = ctk.CTkButton(self, text=btn_name, command=cmd)
            button.grid(row=index, column=0, padx=20, pady=10, sticky="ew")
            
    def sendNewMessage(self):
        self.pack_forget() 
        self.message_frame.pack(fill="both", expand=True)  

    def sendTipMessage(self):
        sendMessageToGroup("Testing", "coffee")

    def sendBoostMessage(self):
        sendMessageToGroup("Testing", "boost")



class MessageFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.text_input = ctk.CTkTextbox(self)
        self.text_input.pack(padx=20, pady=10, fill="both", expand=True)
        self.file_listbox = tk.Listbox(self)  
        self.file_listbox.pack(padx=10, pady=10, fill="both", expand=True)
        self.text_input.drop_target_register(DND_FILES)
        self.text_input.dnd_bind('<<Drop>>', self.dragDropMedia)
        self.media_files = [] 
        
        
        return_button = ctk.CTkButton(self, text='Go Back', command=self.returnAction)
        copy_button = ctk.CTkButton(self, text='Copy', command=self.copyAction)
        pasteButton = ctk.CTkButton(self, text='Paste', command=self.pasteAction)
        delete_button = ctk.CTkButton(self, text='Delete', command=self.deleteAction)
        send_message_button = ctk.CTkButton(self, text='Send Message', command=self.sendAction)
        upload_media = ctk.CTkButton(self, text='Select Media', command=self.uploadMedia)
        
        copy_button.pack(side=tk.LEFT, padx=5, pady=5)
        pasteButton.pack(side=tk.LEFT, padx=5, pady=5)
        delete_button.pack(side=tk.LEFT, padx=5, pady=5)
        return_button.pack(side=tk.LEFT, padx=5, pady=5)
        send_message_button.pack(side=tk.LEFT, padx=5, pady=5)
        upload_media.pack(side=tk.LEFT, padx=5, pady=5)
        
        
    def copyAction(self):
        self.master.clipboard_clear() 
        self.master.clipboard_append(self.text_input.get("1.0", tk.END))
        
    def deleteAction(self):
        self.text_input.delete("1.0", tk.END)
        
    def returnAction(self):
        self.pack_forget()
        self.master.mainbutton.pack(fill="both", expand=True)

    def pasteAction(self):
        text = self.master.clipboard_get()  
        self.text_input.insert("end", text) 
        
    def sendAction(self):
        text_content = self.text_input.get("1.0", ctk.END)
        if text_content:
            if self.media_files:
                sendMessageToGroup("Test", text_content, self.media_files)
            else:
                sendMessageToGroup("Test", text_content)
        self.media_files.clear()
        self.text_input.delete("1.0", ctk.END)
        self.file_listbox.delete(0, tk.END)
                
    def uploadMedia(self):
        new_files = filedialog.askopenfilenames()
        if new_files:
            self.media_files.extend(new_files)
            self.file_listbox.insert(tk.END, *new_files)
            
    def dragDropMedia(self, event):
        files = event.data
        if files:
            files = self.master.tk.splitlist(files)
            self.file_listbox.insert(tk.END, *files)




class App(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)
        self.title("Israel Real Time")
        self.geometry("1100x700")
        icon = tk.PhotoImage(file="/Users/davidmarks/Desktop/Flag_of_Israel.svg.png")
        self.iconphoto(True, icon)
        self.message_frame = MessageFrame(self)
        self.mainbutton = Buttons(self, self.message_frame)
        self.mainbutton.pack(fill="both", expand=True)

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark") 
    ctk.set_default_color_theme("dark-blue") 
    app = App()
    app.mainloop()
