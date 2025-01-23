import tkinter as tk
from tkinter import ttk, messagebox
import csv
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from fpdf import FPDF
from arabic_reshaper import reshape
from bidi.algorithm import get_display
import customtkinter as ctk
from PIL import Image  # برای کار با تصاویر
from PIL.Image import Resampling  # برای رفع هشدار ANTIALIAS

# تنظیم تم برنامه
ctk.set_appearance_mode("System")  # حالت سیستم (تاریک یا روشن)
ctk.set_default_color_theme("blue")  # تم آبی

class PersonalFinanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("مدیریت مالی شخصی")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')

        # لیست تراکنش‌ها
        self.transactions = []

        # بارگیری تراکنش‌های ذخیره‌شده از فایل CSV
        self._load_from_csv()

        # ایجاد ویجت‌ها
        self.create_widgets()

    def create_widgets(self):
        # لوگوی برنامه
        self.load_logo()

        # عنوان برنامه
        self.label_title = ctk.CTkLabel(self.root, text="مدیریت مالی شخصی", font=('Arial', 24, 'bold'))
        self.label_title.pack(pady=10)

        # فرم ثبت تراکنش
        self.frame_form = ctk.CTkFrame(self.root)
        self.frame_form.pack(pady=10, padx=20, fill="x")

        self.label_type = ctk.CTkLabel(self.frame_form, text="نوع تراکنش:")
        self.label_type.grid(row=0, column=0, padx=5, pady=5)
        self.combo_type = ctk.CTkComboBox(self.frame_form, values=["درآمد", "هزینه"])
        self.combo_type.grid(row=0, column=1, padx=5, pady=5)

        self.label_category = ctk.CTkLabel(self.frame_form, text="دسته‌بندی:")
        self.label_category.grid(row=1, column=0, padx=5, pady=5)
        self.entry_category = ctk.CTkEntry(self.frame_form)
        self.entry_category.grid(row=1, column=1, padx=5, pady=5)

        self.label_amount = ctk.CTkLabel(self.frame_form, text="مبلغ:")
        self.label_amount.grid(row=2, column=0, padx=5, pady=5)
        self.entry_amount = ctk.CTkEntry(self.frame_form)
        self.entry_amount.grid(row=2, column=1, padx=5, pady=5)

        self.button_add = ctk.CTkButton(self.frame_form, text="ثبت تراکنش", command=self.add_transaction)
        self.button_add.grid(row=3, column=0, columnspan=2, pady=10)

        # فیلد جستجو
        self.frame_search = ctk.CTkFrame(self.root)
        self.frame_search.pack(pady=10, padx=20, fill="x")

        self.label_search = ctk.CTkLabel(self.frame_search, text="جستجو:")
        self.label_search.pack(side="left", padx=5)

        self.entry_search = ctk.CTkEntry(self.frame_search)
        self.entry_search.pack(side="left", padx=5, fill="x", expand=True)

        self.button_search = ctk.CTkButton(self.frame_search, text="جستجو", command=self.search_transactions)
        self.button_search.pack(side="left", padx=5)

        # فیلتر تراکنش‌ها
        self.frame_filter = ctk.CTkFrame(self.root)
        self.frame_filter.pack(pady=10, padx=20, fill="x")

        self.label_filter = ctk.CTkLabel(self.frame_filter, text="فیلتر بر اساس نوع:")
        self.label_filter.pack(side="left", padx=5)

        self.combo_filter = ctk.CTkComboBox(self.frame_filter, values=["همه", "درآمد", "هزینه"])
        self.combo_filter.pack(side="left", padx=5)
        self.combo_filter.set("همه")

        self.button_filter = ctk.CTkButton(self.frame_filter, text="اعمال فیلتر", command=self.filter_transactions)
        self.button_filter.pack(side="left", padx=5)

        # نمایش تراکنش‌ها
        self.frame_transactions = ctk.CTkFrame(self.root)
        self.frame_transactions.pack(pady=10, padx=20, fill="both", expand=True)

        self.tree = ttk.Treeview(self.frame_transactions, columns=("type", "category", "amount", "date"), show="headings")
        self.tree.heading("type", text="نوع")
        self.tree.heading("category", text="دسته‌بندی")
        self.tree.heading("amount", text="مبلغ")
        self.tree.heading("date", text="تاریخ")
        self.tree.pack(fill="both", expand=True)

        # دکمه‌های مدیریت
        self.frame_buttons = ctk.CTkFrame(self.root)
        self.frame_buttons.pack(pady=10)

        self.button_balance = ctk.CTkButton(self.frame_buttons, text="محاسبه موجودی", command=self.show_balance)
        self.button_balance.pack(side="left", padx=5)

        self.button_chart = ctk.CTkButton(self.frame_buttons, text="نمایش نمودار", command=self.plot_financial_chart)
        self.button_chart.pack(side="left", padx=5)

        self.button_export = ctk.CTkButton(self.frame_buttons, text="صادرات گزارش", command=self.export_to_excel)
        self.button_export.pack(side="left", padx=5)

        self.button_pdf = ctk.CTkButton(self.frame_buttons, text="دریافت PDF", command=self.export_to_pdf)
        self.button_pdf.pack(side="left", padx=5)

        self.button_reset = ctk.CTkButton(self.frame_buttons, text="ریست داده‌ها", command=self.reset_data)
        self.button_reset.pack(side="left", padx=5)

        # دکمه‌های ویرایش و حذف
        self.frame_actions = ctk.CTkFrame(self.root)
        self.frame_actions.pack(pady=10)

        self.button_edit = ctk.CTkButton(self.frame_actions, text="ویرایش", command=self.edit_transaction)
        self.button_edit.pack(side="left", padx=5)

        self.button_delete = ctk.CTkButton(self.frame_actions, text="حذف", command=self.delete_transaction)
        self.button_delete.pack(side="left", padx=5)

        # دکمه خروج
        self.button_exit = ctk.CTkButton(self.frame_actions, text="خروج", command=self.exit_app)
        self.button_exit.pack(side="left", padx=5)

        # امضای کار
        self.label_signature = ctk.CTkLabel(self.root, text="Written by the group: Nexora", font=('Arial', 12))
        self.label_signature.pack(side="bottom", pady=10)

        # بارگیری تراکنش‌ها در Treeview
        self.update_transactions_view()

    def load_logo(self):
        # بارگذاری تصویر لوگو
        try:
            logo_image = Image.open("logo.png")  # مسیر فایل لوگو
            logo_image = logo_image.resize((100, 100), Resampling.LANCZOS)  # تغییر اندازه لوگو
            self.logo = ctk.CTkImage(light_image=logo_image, size=(100, 100))  # استفاده از CTkImage

            # نمایش لوگو در برنامه
            self.logo_label = ctk.CTkLabel(self.root, image=self.logo, text="")
            self.logo_label.pack(pady=10)
        except FileNotFoundError:
            messagebox.showwarning("خطا", "فایل لوگو یافت نشد!")

    def add_transaction(self):
        type = self.combo_type.get()
        category = self.entry_category.get()
        amount = self.entry_amount.get()

        if not type or not category or not amount:
            messagebox.showwarning("خطا", "لطفاً همه فیلدها را پر کنید.")
            return

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showwarning("خطا", "مبلغ باید یک عدد باشد.")
            return

        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.transactions.append({
            'type': type,
            'category': category,
            'amount': amount,
            'date': date
        })

        self._save_to_csv()
        self.update_transactions_view()
        messagebox.showinfo("موفق", "تراکنش با موفقیت ثبت شد.")

    def update_transactions_view(self, transactions=None):
        if transactions is None:
            transactions = self.transactions
        # پاک کردن Treeview
        for row in self.tree.get_children():
            self.tree.delete(row)
        # افزودن تراکنش‌ها به Treeview
        for transaction in transactions:
            self.tree.insert("", "end", values=(
                transaction['type'],
                transaction['category'],
                transaction['amount'],
                transaction['date']
            ))

    def show_balance(self):
        income = sum(t['amount'] for t in self.transactions if t['type'] == "درآمد")
        expense = sum(t['amount'] for t in self.transactions if t['type'] == "هزینه")
        balance = income - expense
        messagebox.showinfo("موجودی", f"موجودی فعلی: {balance:.2f}")

    def plot_financial_chart(self):
        categories = {}
        for transaction in self.transactions:
            if transaction['type'] == "هزینه":
                category = transaction['category']
                amount = transaction['amount']
                if category in categories:
                    categories[category] += amount
                else:
                    categories[category] = amount

        if not categories:
            messagebox.showwarning("خطا", "هیچ هزینه‌ای برای نمایش وجود ندارد.")
            return

        labels = [get_display(reshape(cat)) for cat in categories.keys()]
        sizes = list(categories.values())

        fig, ax = plt.subplots()
        ax.bar(labels, sizes)
        ax.set_title(get_display(reshape("نمودار هزینه‌ها")))
        ax.set_ylabel(get_display(reshape("مبلغ")))
        ax.set_xlabel(get_display(reshape("دسته‌بندی")))

        # نمایش نمودار در پنجره جدید
        chart_window = tk.Toplevel(self.root)
        chart_window.title("نمودار هزینه‌ها")
        canvas = FigureCanvasTkAgg(fig, master=chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def reset_data(self):
        confirm = messagebox.askyesno("تأیید", "آیا مطمئن هستید که می‌خواهید همه داده‌ها را پاک کنید؟")
        if confirm:
            self.transactions = []
            self._save_to_csv()
            self.update_transactions_view()
            messagebox.showinfo("موفق", "همه داده‌ها پاک شدند.")

    def search_transactions(self):
        query = self.entry_search.get().lower()
        filtered_transactions = []
        for transaction in self.transactions:
            if (query in transaction['type'].lower() or
                query in transaction['category'].lower() or
                query in transaction['date'].lower()):
                filtered_transactions.append(transaction)
        self.update_transactions_view(filtered_transactions)

    def filter_transactions(self):
        filter_type = self.combo_filter.get()
        if filter_type == "همه":
            self.update_transactions_view()
        else:
            filtered_transactions = [t for t in self.transactions if t['type'] == filter_type]
            self.update_transactions_view(filtered_transactions)

    def edit_transaction(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("خطا", "لطفاً یک تراکنش را انتخاب کنید.")
            return

        # دریافت داده‌های تراکنش انتخاب‌شده
        item = self.tree.item(selected_item)
        values = item['values']

        # باز کردن پنجره ویرایش
        self.edit_window = tk.Toplevel(self.root)
        self.edit_window.title("ویرایش تراکنش")

        ttk.Label(self.edit_window, text="نوع تراکنش:").grid(row=0, column=0, padx=5, pady=5)
        self.edit_type = ttk.Combobox(self.edit_window, values=["درآمد", "هزینه"], state="readonly")
        self.edit_type.grid(row=0, column=1, padx=5, pady=5)
        self.edit_type.set(values[0])

        ttk.Label(self.edit_window, text="دسته‌بندی:").grid(row=1, column=0, padx=5, pady=5)
        self.edit_category = ttk.Entry(self.edit_window)
        self.edit_category.grid(row=1, column=1, padx=5, pady=5)
        self.edit_category.insert(0, values[1])

        ttk.Label(self.edit_window, text="مبلغ:").grid(row=2, column=0, padx=5, pady=5)
        self.edit_amount = ttk.Entry(self.edit_window)
        self.edit_amount.grid(row=2, column=1, padx=5, pady=5)
        self.edit_amount.insert(0, values[2])

        ttk.Button(self.edit_window, text="ذخیره", command=lambda: self.save_edited_transaction(selected_item)).grid(row=3, column=0, columnspan=2, pady=10)

    def save_edited_transaction(self, selected_item):
        type = self.edit_type.get()
        category = self.edit_category.get()
        amount = self.edit_amount.get()

        if not type or not category or not amount:
            messagebox.showwarning("خطا", "لطفاً همه فیلدها را پر کنید.")
            return

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showwarning("خطا", "مبلغ باید یک عدد باشد.")
            return

        # به‌روزرسانی تراکنش
        for transaction in self.transactions:
            if (transaction['type'] == self.tree.item(selected_item)['values'][0] and
                transaction['category'] == self.tree.item(selected_item)['values'][1] and
                transaction['amount'] == float(self.tree.item(selected_item)['values'][2]) and
                transaction['date'] == self.tree.item(selected_item)['values'][3]):
                transaction['type'] = type
                transaction['category'] = category
                transaction['amount'] = amount
                break

        self._save_to_csv()
        self.update_transactions_view()
        self.edit_window.destroy()
        messagebox.showinfo("موفق", "تراکنش با موفقیت ویرایش شد.")

    def delete_transaction(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("خطا", "لطفاً یک تراکنش را انتخاب کنید.")
            return

        confirm = messagebox.askyesno("تأیید", "آیا مطمئن هستید که می‌خواهید این تراکنش را حذف کنید؟")
        if confirm:
            # حذف تراکنش
            for transaction in self.transactions:
                if (transaction['type'] == self.tree.item(selected_item)['values'][0] and
                    transaction['category'] == self.tree.item(selected_item)['values'][1] and
                    transaction['amount'] == float(self.tree.item(selected_item)['values'][2]) and
                    transaction['date'] == self.tree.item(selected_item)['values'][3]):
                    self.transactions.remove(transaction)
                    break

            self._save_to_csv()
            self.update_transactions_view()
            messagebox.showinfo("موفق", "تراکنش با موفقیت حذف شد.")

    def export_to_excel(self):
        df = pd.DataFrame(self.transactions)
        df.to_excel("transactions_report.xlsx", index=False)
        messagebox.showinfo("موفق", "گزارش با موفقیت به فایل Excel صادر شد.")

    def export_to_pdf(self):
        pdf = FPDF()
        pdf.add_page()
        
        # اضافه کردن فونت فارسی (مثال: فونت BNazanin)
        pdf.add_font('BNazanin', '', 'BNazanin.ttf', uni=True)
        pdf.set_font('BNazanin', '', 14)

        # عنوان گزارش
        title = "گزارش تراکنش‌ها"
        pdf.cell(200, 10, txt=get_display(reshape(title)), ln=True, align='C')

        # اضافه کردن تراکنش‌ها به PDF
        for transaction in self.transactions:
            line = f"نوع: {transaction['type']}, دسته‌بندی: {transaction['category']}, مبلغ: {transaction['amount']}, تاریخ: {transaction['date']}"
            pdf.cell(200, 10, txt=get_display(reshape(line)), ln=True)

        # ذخیره فایل PDF
        pdf.output("transactions_report.pdf")
        messagebox.showinfo("موفق", "گزارش با موفقیت به فایل PDF صادر شد.")

    def exit_app(self):
        confirm = messagebox.askyesno("خروج", "آیا مطمئن هستید که می‌خواهید از برنامه خارج شوید؟")
        if confirm:
            self.root.destroy()

    def _save_to_csv(self):
        with open('transactions.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['type', 'category', 'amount', 'date'])
            writer.writeheader()
            writer.writerows(self.transactions)

    def _load_from_csv(self):
        try:
            with open('transactions.csv', mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                self.transactions = []
                for row in reader:
                    # بررسی وجود کلیدهای مورد نیاز
                    if all(key in row for key in ['type', 'category', 'amount', 'date']):
                        self.transactions.append({
                            'type': row['type'],
                            'category': row['category'],
                            'amount': float(row['amount']),  # تبدیل مقدار به عدد
                            'date': row['date']
                        })
        except FileNotFoundError:
            self.transactions = []

if __name__ == "__main__":
    root = ctk.CTk()  # استفاده از CustomTkinter به جای Tkinter
    app = PersonalFinanceApp(root)
    root.mainloop()