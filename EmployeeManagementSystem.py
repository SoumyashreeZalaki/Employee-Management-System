import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import requests
import json
import sqlite3
import matplotlib.pyplot as plt

def validate_email(email):
	if "@" in email and "." in email:
		return True
	else:
		return False
	

def validate_name(name):
	if not name or not (2 <= len(name) <= 100):
		return False
	if any(char.isdigit() for char in name):
		return False
	if any(char in ('!', '@', '#', '$', '%', '&', '*', '(', ')', '_', '+', '=', '{', '}', '[', ']', '|', '\\', ':', '"', "'", '<', '>', '.', '?', '/') for char in name):
		return False
	if ' ' in name:
		return False
	return True

def validate_salary(salary):
	if salary.isdigit():
		return True
	if salary <= 0 or salary > 1000000:
		return False
	return True

class EmployeeManagementSystem:
	def __init__(self, root):
		self.root = root
		self.root.title("Employee Management System")
		self.root.geometry("600x400")
		root.configure(bg="#008080")
		f=("Century")
		tk.Label(root, text="Employee Management System", font=(f, 20, "bold")).pack(pady=5)
		
		self.current_location = tk.StringVar()
		self.current_temperature = tk.StringVar()

		self.fetch_location_and_temperature()
		self.main_window()

		self.email = tk.StringVar()
		self.name = tk.StringVar()
		self.salary = tk.StringVar()

	def main_window(self):
		self.add_button = tk.Button(self.root, text="Add Employee", font=("Century", 12, "bold"), command=self.add_employee_window)
		self.add_button.pack(pady=5)

		self.view_button = tk.Button(self.root, text="View Employee", font=("Century", 12, "bold"), command=self.view_employee_window)
		self.view_button.pack(pady=5)

		self.update_button = tk.Button(self.root, text="Update Employee", font=("Century", 12, "bold"), command=self.update_employee_window)
		self.update_button.pack(pady=5)

		self.delete_button = tk.Button(self.root, text="Delete Employee", font=("Century", 12, "bold"), command=self.delete_employee_window)
		self.delete_button.pack(pady=5)

		self.charts_button = tk.Button(self.root, text="Charts", font=("Century", 12, "bold"), command=self.show_charts)
		self.charts_button.pack(pady=5)

		self.location_label = tk.Label(self.root, text="Current location:", font=("Arial", 10), bg="#008080", fg="white")
		self.location_label.pack()
	
		self.location_label = tk.Label(self.root, text="Location", font=("Century", 12, "bold"), textvariable=self.current_location)
		self.location_label.pack(pady=5)

		self.temperature_label = tk.Label(self.root, text="Current temperature:", font=("Arial", 10), bg="#008080", fg="white")
		self.temperature_label.pack()

		self.temperature_label = tk.Label(self.root, text="Temperature", font=("Century", 12, "bold"), textvariable=self.current_temperature)
		self.temperature_label.pack()

	def fetch_location_and_temperature(self):
		try:
			api_url = "https://ipinfo.io/json"
			response = requests.get(api_url)
			if response.status_code != 200:
				raise Exception(f"Error fetching location data from ipinfo.io: {response.status_code} {response.reason}")
			data = response.json()
			city_name = data.get('city', None)
			if not city_name:
				raise Exception("Error fetching city name from ipinfo.io")
			self.current_location.set(data['city'])
			api_url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid=4cf09bc2c34281486622a3d56c2a24c7&units=metric"
			response = requests.get(api_url)
			if response.status_code != 200:
				raise Exception(f"Error fetching temperature data from OpenWeather.io: {response.status_code} {response.reason}")
			data = response.json()
			temp = data['main']['temp']
			self.current_temperature.set(f"{temp}°C")
		except Exception as e:
			print(f"Error fetching location or temperature: {e}")

	def add_employee_window(self):
		self.add_window = tk.Toplevel(self.root)
		self.add_window.title("Add Employee")
		self.add_window.geometry("300x200")
		self.add_window.config(bg='#E6E6FA')
		f = ("Century", 10)

		tk.Label(self.add_window, text="Enter Email ID:", font=f).pack()
		self.email_entry = tk.Entry(self.add_window, textvariable=self.email)
		self.email_entry.pack(pady=2)

		tk.Label(self.add_window, text="Enter Name:", font=f).pack()
		self.name_entry = tk.Entry(self.add_window, textvariable=self.name)
		self.name_entry.pack(pady=2)

		tk.Label(self.add_window, text="Enter Salary:", font=f).pack()
		self.salary_entry = tk.Entry(self.add_window, textvariable=self.salary)
		self.salary_entry.pack(pady=2)

		tk.Button(self.add_window, text="Save", font=f, command=self.save_employee).pack()
		tk.Button(self.add_window, text="Cancel", font=f, command=self.add_window.destroy).pack()

	def save_employee(self):
		email = self.email.get()
		name = self.name.get()
		salary = self.salary.get()
		if not email or not name or not salary :
			messagebox.showerror("Error", "Please fill in all fields.")
			return
		if not validate_email(email):
			messagebox.showerror("Error", "Invalid email format.")
			return
		if not validate_name(name):
			messagebox.showerror("Error", "Invalid name format. Name cannot contain digits, special characters, or spaces. Name should contain letters between 2 to 100")
			return
		if not validate_salary(salary):
			messagebox.showerror("Error", "Invalid name format. Salary must be between 0 to 10000000. Salary cannot be alphabets, special characters, or spaces.")
			return
		try:
			conn = sqlite3.connect("employees.db")
			cursor = conn.cursor()
			cursor.execute('''CREATE TABLE IF NOT EXISTS employees (email TEXT PRIMARY KEY, name TEXT, salary REAL)''')
			cursor.execute("INSERT INTO employees VALUES (?, ?, ?)", (email, name, salary))
			conn.commit()
			conn.close()
			messagebox.showinfo("Success", "Employee added successfully")
			self.add_window.destroy()
		except sqlite3.Error as e:
			messagebox.showerror("Error", f"Failed to add employee: {e}")

	def view_employee_window(self):
		self.view_window = tk.Toplevel(self.root)
		self.view_window.title("View Employees")
		self.view_window.geometry("400x300")
		self.view_window.config(bg='#98FB98')

		self.tree = ttk.Treeview(self.view_window, columns=("Email ID", "Name", "Salary"))
		self.tree.heading('#0', text='Email ID')
		self.tree.heading('#1', text='Name')
		self.tree.heading('#2', text='Salary')
		self.tree.pack()

		conn = sqlite3.connect("employees.db")
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM employees")
		rows = cursor.fetchall()
		for row in rows:
			self.tree.insert("", "end",text=row[0], values=(row[0], row[1], row[2]))
		conn.close()

		self.back_button = tk.Button(self.view_window, text="Back", command=self.view_window.destroy)
		self.back_button.pack()

	def update_employee_window(self):
		self.update_window = tk.Toplevel(self.root)
		self.update_window.title("Update Employee")
		self.update_window.geometry("300x200")
		self.update_window.config(bg='#FFFFE0')
		f = ("Century", 10)

		tk.Label(self.update_window, text="Enter New ID:", font = f).pack()
		self.new_email_entry = tk.Entry(self.update_window)
		self.new_email_entry.pack(pady=2)

		tk.Label(self.update_window, text="Enter New Name:", font = f).pack()
		self.new_name_entry = tk.Entry(self.update_window)
		self.new_name_entry.pack(pady=2)

		tk.Label(self.update_window, text="Enter New Salary:", font = f).pack()
		self.new_salary_entry = tk.Entry(self.update_window)
		self.new_salary_entry.pack(pady=2)

		tk.Button(self.update_window, text="Update", font = f, command=self.update_employee).pack(pady=2)
		tk.Button(self.update_window, text="Cancel", font = f, command=self.update_window.destroy).pack(pady=2)

	def update_employee(self):
		new_email = self.new_email_entry.get()
		new_name = self.new_name_entry.get()
		new_salary = self.new_salary_entry.get()

		if not new_email or not new_name or not new_salary :
			messagebox.showerror("Error", "Please fill in all fields.")
			return
		if not validate_email(new_email):
			messagebox.showerror("Error", "Invalid email format.")
			return
		if not validate_name(new_name):
			messagebox.showerror("Error", "Invalid name format. Name cannot contain digits, special characters, or spaces.")
			return
		if not validate_salary(new_salary):
			messagebox.showerror("Error", "Invalid name format. Salary must be between 0 to 10000000. Salary cannot be alphabets, special characters, or spaces.")
			return
		try:
			conn = sqlite3.connect("employees.db")
			cursor = conn.cursor()
			cursor.execute("UPDATE employees SET name=?, salary=? WHERE email=?", (new_name, new_salary, new_email))
			conn.commit()
			conn.close()
			messagebox.showinfo("Success", "Employee updated successfully")
			self.update_window.destroy()
		except sqlite3.Error as e:
			messagebox.showerror("Error", f"Failed to update employee: {e}")

	def delete_employee_window(self):
		self.delete_window = tk.Toplevel(self.root)
		self.delete_window.title("Delete Employee")
		self.delete_window.geometry("300x100")
		self.delete_window.config(bg='#F5F5DC')
		f = ("Century", 10)

		tk.Label(self.delete_window, text="Enter Email ID:", font = f).pack()
		self.email_entry = tk.Entry(self.delete_window)
		self.email_entry.pack(pady=2)

		tk.Button(self.delete_window, text="Delete", font = f, command=self.delete_employee).pack(pady=2)
		tk.Button(self.delete_window, text="Cancel", font = f, command=self.delete_window.destroy).pack()

	def delete_employee(self):
		email = self.email_entry.get()

		try:
			conn = sqlite3.connect("employees.db")
			cursor = conn.cursor()
			cursor.execute("DELETE FROM employees WHERE email=?", (email,))
			conn.commit()
			conn.close()
			messagebox.showinfo("Success", "Employee deleted successfully")
			self.delete_window.destroy()
		except sqlite3.Error as e:
			messagebox.showerror("Error", f"Failed to delete employee: {e}")

	def show_charts(self):
		conn = sqlite3.connect("employees.db")
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM employees ORDER BY salary DESC LIMIT 5")
		rows = cursor.fetchall()
		conn.close()

		names = [row[1] for row in rows]
		salaries = [row[2] for row in rows]
	
		plt.bar(names, salaries)
		plt.xlabel('Employee Names')
		plt.ylabel('Salaries')
		plt.title('Top 5 Highest Earning Employees')
		plt.xticks(rotation=45)
		plt.show()

if __name__ == "__main__":
	root = tk.Tk()
	app = EmployeeManagementSystem(root)
	root.mainloop()