import mysql.connector
import speech_recognition as sr
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock  # Add this import statement

# Database connection parameters
DB_NAME = "ledger"
DB_USER = "ansh"
DB_PASS = "ansh"
DB_HOST = "localhost"

# Initialize recognizer
recognizer = sr.Recognizer()

# Function to connect to the database
def connect_db():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )
        if conn.is_connected():
            print("Successfully connected to the database")
        return conn
    except mysql.connector.Error as e:
        print(f"Error: {e}")
        return None

# Function to add a new entry to the ledger
def add_record(name, amount, phone, payment):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO ledger (name, amount, phone, payment)
            VALUES (%s, %s, %s, %s)
        ''', (name, amount, phone, payment))
        conn.commit()
        cursor.close()
        conn.close()
        show_popup("Success", "Record added successfully.")
    else:
        show_popup("Error", "Failed to connect to the database. Record not added.")

# Function to display popup message
def show_popup(title, message):
    popup = Popup(title=title, content=Label(text=message), size_hint=(None, None), size=(400, 200))
    popup.open()

# Function to recognize speech and return text
def recognize_speech(prompt):
    with sr.Microphone() as source:
        print(f"{prompt}")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Listening... Please speak into the microphone.")
        audio_text = recognizer.listen(source)
        print("Recognizing speech...")

        try:
            text = recognizer.recognize_google(audio_text)
            print("You said:", text)
            return text
        except sr.UnknownValueError:
            print("Sorry, I did not understand the audio. Please try again.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}. Please try again.")
            return None

class MenuScreen(BoxLayout):
    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.input_mode = "text"  # Default input mode

        toggle_button_text = ToggleButton(text="Add Entry(Text)", group="input_mode", state="down", on_press=self.add_entry_text)
        toggle_button_text.bind(on_press=self.toggle_input_mode)
        toggle_button_voice = ToggleButton(text="Add Entry(Voice)", group="input_mode", on_press=self.add_entry_voice)
        toggle_button_voice.bind(on_press=self.toggle_input_mode)
        view_records_button = Button(text='View Records', on_press=self.view_records)
        delete_record_button = Button(text='Delete Record', on_press=self.delete_record)
        delete_all_records_button = Button(text='Delete All Records', on_press=self.delete_all_records)
        modify_record_button = Button(text='Modify Record', on_press=self.modify_record)
        exit_button = Button(text='Exit', on_press=self.exit_app)

        self.add_widget(toggle_button_text)
        self.add_widget(toggle_button_voice)
        self.add_widget(view_records_button)
        self.add_widget(delete_record_button)
        self.add_widget(delete_all_records_button)
        self.add_widget(modify_record_button)
        self.add_widget(exit_button)

    def toggle_input_mode(self, instance):
        self.input_mode = instance.text.lower()  # Update input mode

    def add_entry_text(self, instance):
        def add_record_by_data(name, amount, phone, payment):
            add_record(name, amount, phone, payment)

        content = BoxLayout(orientation="vertical")
        name_input = TextInput(hint_text="Name")
        amount_input = TextInput(hint_text="Amount")
        phone_input = TextInput(hint_text="Phone")
        payment_input = TextInput(hint_text="Payment")
        submit_button = Button(text="Submit")
        submit_button.bind(on_press=lambda x: add_record_by_data(name_input.text, amount_input.text, phone_input.text, payment_input.text))
        back_button = Button(text="Back", on_press=lambda x: self.display_menu())
        content.add_widget(name_input)
        content.add_widget(amount_input)
        content.add_widget(phone_input)
        content.add_widget(payment_input)
        content.add_widget(submit_button)
        content.add_widget(back_button)
        popup = Popup(title="Add Entry(Text)", content=content, size_hint=(None, None), size=(400, 300))
        popup.open()

    def add_entry_voice(self, instance):
        name = recognize_speech("Please say the name:")
        amount = recognize_speech("Please say the amount:")
        phone = recognize_speech("Please say the phone number:")
        payment = recognize_speech("Please say the payment:")
        if name and amount and phone and payment:
            add_record(name, amount, phone, payment)
        else:
            show_popup("Error", "Failed to recognize speech. Please try again.")
        back_button = Button(text="Back", on_press=lambda x: self.display_menu())
        content = BoxLayout(orientation="vertical")
        content.add_widget(back_button)
        popup = Popup(title="Add Entry(Voice)", content=content, size_hint=(None, None), size=(400, 300))
        popup.open()

    def view_records(self, instance):
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute
            ("""
                SELECT name, (SELECT phone FROM ledger l2 WHERE l2.name = l1.name LIMIT 1) AS phone, SUM(amount)
                FROM ledger l1
                GROUP BY name
            """)
            records = cursor.fetchall()
            cursor.close()
            conn.close()

            if records:
                content = BoxLayout(orientation="vertical")
                scroll_view = ScrollView(size_hint=(1, None), size=(400, 300))
                inner_layout = BoxLayout(orientation="vertical", size_hint_y=None)
                inner_layout.bind(minimum_height=inner_layout.setter('height'))
                for record in records:
                    inner_layout.add_widget(Label(text=f"Name: {record[0]}, Phone: {record[1]}, Total Amount: {record[2]}"))
                scroll_view.add_widget(inner_layout)
                content.add_widget(scroll_view)
                back_button = Button(text="Back", size_hint_y=None, height=50, on_press=lambda x: self.display_menu())
                content.add_widget(back_button)
                popup = Popup(title="View Records", content=content, size_hint=(None, None), size=(400, 400))
                popup.open()
            else:
                show_popup("No Records", "No records found in the database.")
        else:
            show_popup("Error", "Failed to connect to the database.")

    def delete_record(self, instance):
        def delete_record_by_name(name):
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM ledger WHERE name = %s", (name,))
                conn.commit()
                cursor.close()
                conn.close()
                show_popup("Success", f"Record for {name} deleted successfully.")
            else:
                show_popup("Error", "Failed to connect to the database.")

        content = BoxLayout(orientation="vertical")
        name_input = TextInput(hint_text="Name")
        submit_button = Button(text="Submit")
        submit_button.bind(on_press=lambda x: delete_record_by_name(name_input.text))
        back_button = Button(text="Back", on_press=lambda x: self.display_menu())
        content.add_widget(name_input)
        content.add_widget(submit_button)
        content.add_widget(back_button)
        popup = Popup(title="Delete Record", content=content, size_hint=(None, None), size=(400, 200))
        popup.open()

    def delete_all_records(self, instance):
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ledger")
            conn.commit()
            cursor.close()
            conn.close()
            show_popup("Success", "All records deleted successfully.")
        else:
            show_popup("Error", "Failed to connect to the database.")
        back_button = Button(text="Back", on_press=lambda x: self.display_menu())
        content = BoxLayout(orientation="vertical")
        content.add_widget(back_button)
        popup = Popup(title="Delete All Records", content=content, size_hint=(None, None), size=(400, 200))
        popup.open()

    def modify_record(self, instance):
        def modify_record_by_name(name, payment_received):
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT amount, payment FROM ledger WHERE name = %s", (name,))
                record = cursor.fetchone()
                if record is None:
                    show_popup("Error", f"No record found for {name}.")
                else:
                    try:
                        amount, payment = record
                        payment_received = float(payment_received)
                        if payment_received > payment:
                            show_popup("Error", "Payment received cannot be greater than total payment.")
                        else:
                            updated_payment = payment - payment_received
                            cursor.execute("UPDATE ledger SET payment = %s WHERE name = %s", (updated_payment, name))
                            conn.commit()
                            show_popup("Success", f"Payment received for {name} updated successfully.")
                            # Display the updated record
                            show_popup("Updated Record", f"Name: {name}\nAmount: {amount}\nPayment: {updated_payment}")
                    except ValueError:
                        show_popup("Error", "Payment received must be a number.")
                cursor.close()
                conn.close()
            else:
                show_popup("Error", "Failed to connect to the database.")

        content = BoxLayout(orientation="vertical")
        name_input = TextInput(hint_text="Name")
        payment_received_input = TextInput(hint_text="Payment Received")
        submit_button = Button(text="Submit")
        submit_button.bind(on_press=lambda x: modify_record_by_name(name_input.text, payment_received_input.text))
        back_button = Button(text="Back", on_press=lambda x: self.display_menu())
        content.add_widget(name_input)
        content.add_widget(payment_received_input)
        content.add_widget(submit_button)
        content.add_widget(back_button)
        popup = Popup(title="Modify Payment Received", content=content, size_hint=(None, None), size=(400, 200))
        popup.open()

    def display_menu(self):
        self.clear_widgets()
        self.__init__()

    def exit_app(self, instance):
        App.get_running_app().stop()

class LedgerApp(App):
    def build(self):
        return MenuScreen()

if __name__ == "__main__":
    LedgerApp().run()

