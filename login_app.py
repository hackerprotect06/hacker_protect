"""نافذة تسجيل الدخول وإنشاء حساب باستعمال Tkinter فقط.

شغّل الملف هكذا: python3 login_app.py
يمكن وضع logo.jpeg بجانب هذا الملف لإظهار الشعار. Pillow اختياري لدعم JPEG.
"""

import re
import tkinter as tk
from pathlib import Path
from tkinter import messagebox


BG = "#f2f3fb"
CARD = "#ffffff"
PRIMARY = "#5658d9"
PRIMARY_HOVER = "#4446bf"
TEXT = "#20223a"
MUTED = "#777b91"
BORDER = "#e1e3ee"


class LoginApp:
    def _init_(self, root: tk.Tk):
        self.root = root
        self.mode = "login"
        self.show_password = False
        self.logo_image = None

        root.title("تسجيل الدخول")
        root.geometry("440x650")
        root.minsize(360, 560)
        root.configure(bg=BG)

        # البطاقة الرئيسية
        self.card = tk.Frame(root, bg=CARD, padx=34, pady=28,
                             highlightthickness=1, highlightbackground="#e7e8f0")
        self.card.pack(expand=True, padx=24, pady=24, fill="both")

        self._load_logo()

        self.heading = tk.Label(self.card, text="مرحبا بعودتك", bg=CARD,
                                fg=TEXT, font=("Arial", 21, "bold"))
        self.heading.pack(anchor="e", pady=(14, 4))

        self.subtitle = tk.Label(
            self.card, text="دخل المعلومات ديالك باش تسجل الدخول للحساب.",
            bg=CARD, fg=MUTED, font=("Arial", 10), anchor="e", justify="right"
        )
        self.subtitle.pack(fill="x", anchor="e", pady=(0, 18))

        # اختيار الدخول أو إنشاء حساب
        tabs = tk.Frame(self.card, bg="#f1f2f8", padx=4, pady=4)
        tabs.pack(fill="x", pady=(0, 18))
        self.login_tab = tk.Button(tabs, text="تسجيل الدخول", command=lambda: self.set_mode("login"),
                                   relief="flat", bd=0, font=("Arial", 10, "bold"), cursor="hand2")
        self.signup_tab = tk.Button(tabs, text="إنشاء حساب", command=lambda: self.set_mode("signup"),
                                    relief="flat", bd=0, font=("Arial", 10, "bold"), cursor="hand2")
        self.login_tab.pack(side="right", expand=True, fill="x", padx=2)
        self.signup_tab.pack(side="right", expand=True, fill="x", padx=2)

        self.name_label = self._label("الاسم الكامل")
        self.name_entry = self._entry("مثال: محمد العلوي")

        self.email_label = self._label("البريد الإلكتروني")
        self.email_entry = self._entry("name@example.com")

        self.password_label = self._label("كلمة المرور")
        password_row = tk.Frame(self.card, bg=CARD)
        password_row.pack(fill="x", pady=(0, 14))
        self.password_entry = tk.Entry(
            password_row, show="•", justify="right", font=("Arial", 11),
            relief="flat", bd=0, bg="#ffffff", fg=TEXT,
            highlightthickness=1, highlightbackground=BORDER, highlightcolor=PRIMARY
        )
        self.password_entry.pack(side="right", expand=True, fill="x", ipady=12)
        self.password_entry.insert(0, "دخل كلمة المرور")
        self.password_entry.bind("<FocusIn>", lambda _e: self._clear_placeholder(self.password_entry, "دخل كلمة المرور"))
        self.password_entry.bind("<FocusOut>", lambda _e: self._restore_password_placeholder())
        self.toggle_button = tk.Button(password_row, text="إظهار", command=self.toggle_password,
                                       bg=CARD, fg=PRIMARY, relief="flat", bd=0,
                                       font=("Arial", 9), cursor="hand2")
        self.toggle_button.pack(side="left", padx=(7, 0))

        self.confirm_label = self._label("تأكيد كلمة المرور")
        self.confirm_entry = self._entry("عاود دخل كلمة المرور")
        self.confirm_entry.config(show="•")

        self.options = tk.Frame(self.card, bg=CARD)
        self.options.pack(fill="x", pady=(0, 16))
        self.remember_var = tk.BooleanVar(value=False)
        self.remember = tk.Checkbutton(self.options, text="تذكرني", variable=self.remember_var,
                                       bg=CARD, fg=MUTED, activebackground=CARD,
                                       font=("Arial", 9), selectcolor=CARD)
        self.remember.pack(side="right")
        self.forgot = tk.Button(self.options, text="نسيت كلمة المرور؟", command=self.forgot_password,
                                bg=CARD, fg=PRIMARY, relief="flat", bd=0,
                                font=("Arial", 9), cursor="hand2")
        self.forgot.pack(side="left")

        self.submit_button = tk.Button(
            self.card, text="دخول", command=self.submit,
            bg=PRIMARY, fg="white", activebackground=PRIMARY_HOVER,
            activeforeground="white", relief="flat", bd=0,
            font=("Arial", 11, "bold"), cursor="hand2", pady=12
        )
        self.submit_button.pack(fill="x", pady=(0, 10))

        self.status = tk.Label(self.card, text="", bg=CARD, fg=MUTED,
                               font=("Arial", 9), wraplength=330, justify="center")
        self.status.pack(fill="x")

        self.terms = tk.Label(self.card,
                              text="بإنشاء حساب، كتوافق على شروط الاستخدام وسياسة الخصوصية.",
                              bg=CARD, fg=MUTED, font=("Arial", 8), wraplength=330,
                              justify="center")
        self.terms.pack(fill="x", pady=(8, 0))

        self.set_mode("login")

    def _load_logo(self):
        """يحاول عرض logo.jpeg إذا كان موجوداً وPillow منصّباً."""
        logo_path = Path(_file_).with_name("logo.jpeg")
        if not logo_path.exists():
            tk.Label(self.card, text="م", bg=PRIMARY, fg="white",
                     font=("Arial", 22, "bold"), width=3, height=1).pack(anchor="e")
            return
        try:
            from PIL import Image, ImageTk
            image = Image.open(logo_path).convert("RGB")
            image.thumbnail((72, 72))
            self.logo_image = ImageTk.PhotoImage(image)
            tk.Label(self.card, image=self.logo_image, bg=CARD).pack(anchor="e")
        except ImportError:
            tk.Label(self.card, text="م", bg=PRIMARY, fg="white",
                     font=("Arial", 22, "bold"), width=3, height=1).pack(anchor="e")
            print("ملاحظة: لتشغيل logo.jpeg ثبّت Pillow بالأمر: python3 -m pip install pillow")
        except Exception as exc:
            tk.Label(self.card, text="م", bg=PRIMARY, fg="white",
                     font=("Arial", 22, "bold"), width=3, height=1).pack(anchor="e")
            print(f"تعذر تحميل الشعار: {exc}")

    def _label(self, text: str) -> tk.Label:
        label = tk.Label(self.card, text=text, bg=CARD, fg=TEXT,
                         font=("Arial", 10, "bold"), anchor="e")
        label.pack(fill="x", pady=(0, 6))
        return label

    def _entry(self, placeholder: str) -> tk.Entry:
        entry = tk.Entry(self.card, justify="right", font=("Arial", 11),
                         relief="flat", bd=0, bg="#ffffff", fg=TEXT,
                         highlightthickness=1, highlightbackground=BORDER,
                         highlightcolor=PRIMARY)
        entry.pack(fill="x", ipady=12, pady=(0, 14))
        entry.insert(0, placeholder)
        entry.bind("<FocusIn>", lambda _e, w=entry, p=placeholder: self._clear_placeholder(w, p))
        entry.bind("<FocusOut>", lambda _e, w=entry, p=placeholder: self._restore_placeholder(w, p))
        return entry

    @staticmethod
    def _clear_placeholder(entry: tk.Entry, placeholder: str):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)

    @staticmethod
    def _restore_placeholder(entry: tk.Entry, placeholder: str):
        if not entry.get():
            entry.insert(0, placeholder)

    def _restore_password_placeholder(self):
        if not self.password_entry.get():
            self.password_entry.config(show="")
            self.password_entry.insert(0, "دخل كلمة المرور")
            self.password_entry.config(show="•")

    def toggle_password(self):
        self.show_password = not self.show_password
        self.password_entry.config(show="" if self.show_password else "•")
        self.toggle_button.config(text="إخفاء" if self.show_password else "إظهار")

    def set_mode(self, mode: str):
        self.mode = mode
        signup = mode == "signup"
        self.login_tab.config(bg=CARD if not signup else "#f1f2f8",
                              fg=PRIMARY if not signup else MUTED)
        self.signup_tab.config(bg=CARD if signup else "#f1f2f8",
                               fg=PRIMARY if signup else MUTED)
        self.heading.config(text="إنشاء حساب جديد" if signup else "مرحبا بعودتك")
        self.subtitle.config(text=("عمر المعلومات التالية باش تنشئ الحساب ديالك."
                                   if signup else "دخل المعلومات ديالك باش تسجل الدخول للحساب."))
        self.submit_button.config(text="إنشاء الحساب" if signup else "دخول")

    def set_mode(self, mode: str):
        self.mode = mode
        signup = mode == "signup"
        self.login_tab.config(bg=CARD if not signup else "#f1f2f8",
                              fg=PRIMARY if not signup else MUTED)
        self.signup_tab.config(bg=CARD if signup else "#f1f2f8",
                               fg=PRIMARY if signup else MUTED)
        self.heading.config(text="إنشاء حساب جديد" if signup else "مرحباً بعودتك")
        self.subtitle.config(text="عمر المعلومات التالية باش تنشئ الحساب ديالك." if signup else ".دخل المعلومات ديالك باش تسجل الدخول للحساب")
        self.submit_button.config(text="إنشاء الحساب" if signup else "دخول")

        self._show(self.name_label, self.name_entry, visible=signup)
        self._show(self.confirm_label, self.confirm_entry, visible=signup)
        self._show(self.options, self.remember, visible=not signup)
        self._show(self.options, self.forgot, visible=not signup)
        self._show(self.terms, visible=signup)
        self.status.config(text="", fg=MUTED)




         
@staticmethod
def _show(*widgets, visible: bool):
        for widget in widgets:
            if visible:
                widget.pack(fill="x", pady=(0, 6))
            else:
                widget.pack_forget()
                
                
def forgot_password(self):
        messagebox.showinfo("استرجاع كلمة المرور",
                            "ربط هاد الخيار بخدمة استرجاع كلمة المرور ديالك.")

def submit(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        placeholders = {"name@example.com", "دخل كلمة المرور"}
        if email in placeholders or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            self._set_status("دخل بريد إلكتروني صحيح.", "#c0394b")
            self.email_entry.focus_set()
            return
        if password == "دخل كلمة المرور" or len(password) < 8:
            self._set_status("كلمة المرور خاصها تكون على الأقل 8 حروف.", "#c0394b")
            self.password_entry.focus_set()
            return

        if self.mode == "signup":
            name = self.name_entry.get().strip()
            confirm = self.confirm_entry.get()
            if not name or name == "مثال: محمد العلوي":
                self._set_status("دخل الاسم الكامل.", "#c0394b")
                self.name_entry.focus_set()
                return
            if confirm != password:
                self._set_status("كلمتا المرور ما متطابقينش.", "#c0394b")
                self.confirm_entry.focus_set()
                return
            self._set_status("الواجهة خدامة. ربطها بخادم أو خدمة مصادقة لإتمام التسجيل.", "#16835d")
        else:
            self._set_status("الواجهة خدامة. ربطها بخادم أو خدمة مصادقة للتحقق من الحساب.", "#16835d")

def _set_status(self, text: str, color: str):
        self.status.config(text=text, fg=color)


if __name__ == "__main__":
    window = tk.Tk()
    app = LoginApp(window)
    window.mainloop()