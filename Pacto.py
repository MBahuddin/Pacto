import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image, ImageDraw
import datetime
import os
import sys
from functools import partial

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path= os.path.abspath(".")
    return os.path.join(base_path, relative_path)



def insertion_sort(data, key=lambda x: x):
    for i in range(1, len(data)):
        key_item = data[i]
        j = i - 1
        while j >= 0 and key(data[j]) > key(key_item):
            data[j + 1] = data[j]
            j -= 1
        data[j + 1] = key_item
    return data

def selection_sort(data, key=lambda x: x):
    for i in range(len(data)):
        min_idx = i
        for j in range(i + 1, len(data)):
            if key(data[j]) < key(data[min_idx]):
                min_idx = j
        data[i], data[min_idx] = data[min_idx], data[i]
    return data

def binary_search_history(history, target_total):
    low = 0
    high = len(history) - 1
    while low <= high:
        mid = (low + high) // 2
        mid_total = history[mid]['total']
        if mid_total == target_total:
            return mid
        elif mid_total < target_total:
            low = mid + 1
        else:
            high = mid - 1
    return -1


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, width=300, fg_color="#00A86B", **kwargs)
        self.master = master
        self.expanded = True
        self.pack_propagate(False)

        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(pady=(20, 10), padx=10, anchor="nw", fill="x")

        self.logo_label = ctk.CTkLabel(
        self.header_frame,
        text="☰",
        font=ctk.CTkFont(size=30),
        text_color="#EAF8F4"
        )

        self.logo_label.pack(side="left")

        self.title_label = ctk.CTkLabel(self.header_frame, text="PACTO", font=ctk.CTkFont(size=30, weight="bold"),text_color="#EAF8F4")
        self.title_label.pack(side="left", padx=(10, 0))

        self.toggle_btn = ctk.CTkButton(self, text="", width=0, height=0, command=self.toggle_sidebar)
        self.toggle_btn.pack_forget()  # hidden, functionality handled by logo_label

        self.logo_label.bind("<Button-1>", lambda e: self.toggle_sidebar())
        self.toggle_btn.pack(pady=(10, 0), padx=10, anchor="nw")

        

        button_font = ctk.CTkFont(size=25, weight="bold")
        self.buttons = []

        menu_items = [
            ("Dashboard", "📊", lambda: master.master.show_frame("product")),
            ("Settings", "⚙️", lambda: master.master.show_frame("settings")),
            ("Checkout", "🧾", lambda: master.master.show_frame("cart")),
            ("History", "🕘", lambda: master.master.show_frame("history")),
        ]

        for text, icon, command in menu_items:
            btn = ctk.CTkButton(
                self,
                text=text if self.expanded else "",
                anchor="w",
                width=160,
                fg_color="#00A86B",
                text_color="#EAF8F4",
                hover_color="#FFBC53",
                font=button_font,
                command=command,
                height=50,
                image=None
            )
            btn._text_label.configure(compound="left")
            btn.configure(text=f"{icon} {text}" if self.expanded else f"{icon}")
            btn.pack(pady=5, padx=10, fill="both")
            self.buttons.append(btn)

        self.logout_btn = ctk.CTkButton(
            self,
            text="🔓 Log Out" if self.expanded else "🔓",
            anchor="w",
            width=160,
            fg_color="#00A86B",
            text_color="#EAF8F4",
            hover_color="#FFBC53",
            font=button_font,
            command=self.logout
        )
        self.logout_btn.pack(side="bottom", pady=10, padx=10, fill="both")

    def toggle_sidebar(self):
        labels = ["Dashboard", "Settings", "Checkout", "History"]
        icons = ["📊", "⚙️", "🧾", "🕘"]

        if self.expanded:
            self.configure(width=60)
            self.title_label.pack_forget()
            for btn, icon in zip(self.buttons, icons):
                btn.configure(text=icon)
            self.logout_btn.configure(text="🔓")
        else:
            self.configure(width=300)
            self.title_label.pack(pady=(10, 30))
            for btn, label, icon in zip(self.buttons, labels, icons):
                btn.configure(text=f"{icon} {label}")
            self.logout_btn.configure(text="🔓 Log Out")
        self.expanded = not self.expanded

    def logout(self):
        self.master.master.user_logged_in = False
        self.master.master.cart.clear()
        self.master.master.show_frame("signin")


class GroceryApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.profile_image_path = None  # agar bisa diakses semua halaman

        self.purchase_history = []

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")
        self.configure(fg_color="white")

        self.geometry("1200x800")
        self.minsize(800, 600)
        self.title("Marketplace")

        self.cart = []
        self.user_logged_in = False

        self.frames = {}
        self.init_frames()

        self.show_frame("beranda")

    def show_frame(self, name):
        frame = self.frames[name]
        if name == "cart":
            frame.render_cart()
        elif name == "cart":
            frame.render_history()
        frame.tkraise()

    def init_frames(self):
        for F in (BerandaPage, SignInPage, SignUpPage, ProductPage, CartPage, HistoryPage, SettingsPage):
            frame = F(self)
            self.frames[F.__name__.replace("Page", "").lower()] = frame
            frame.place(relwidth=1, relheight=1)


    def login_success(self):
        self.user_logged_in = True
        self.show_frame("product")

    def add_to_cart(self, product_name):
        self.cart.append(product_name)
        self.frames["product"].update_basket()

    def remove_from_cart(self, item):
        self.cart.remove(item)
        self.frames["cart"].render_cart()
        self.frames["product"].update_basket()

class BerandaPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master,fg_color="#00A86B")

        
        container = ctk.CTkFrame(self, width=400, height=500, fg_color="white", corner_radius=10,border_color="black",border_width=2)
        container.place(relx=0.5, rely=0.5, anchor="center")
        container.pack_propagate(False)

        ctk.CTkLabel(container, text="Welcome to", font=ctk.CTkFont(family="Poppins", size=20)).pack(pady=(30, 10))

        logo = ctk.CTkImage(light_image=Image.open(resource_path("assets\\images\\logo pacto.png")).resize((250, 180)), size=(250, 180))

        ctk.CTkLabel(container, image=logo, text="").pack(pady=(0, 20))

        ctk.CTkButton(container,fg_color="#FFBC53",hover_color="#FF7125", text="Sign In", width=200,height=40, command=lambda: master.show_frame("signin")).pack(pady=10)
        ctk.CTkButton(container, fg_color="#FFBC53",hover_color="#FF7125",text="Sign Up", width=200,height=40,command=lambda: master.show_frame("signup")).pack(pady=10)

class SignInPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master,fg_color="#00A86B")

        
        # Frame putih tengah
        container = ctk.CTkFrame(self, width=400, height=500, fg_color="white", corner_radius=10,border_color="black",border_width=2)
        container.place(relx=0.5, rely=0.5, anchor="center")
        container.pack_propagate(False)

        # Gambar kepala
        user_icon = ctk.CTkImage(light_image=Image.open(resource_path("assets\\login\\user_icon.png")).resize((150, 140)), size=(150, 140))
        ctk.CTkLabel(container, image=user_icon, text="").pack(pady=(25, 10))

        
        ctk.CTkLabel(container, text="Sign In", font=ctk.CTkFont(family="Times New Roman", size=24)).pack(pady=(0, 10))

        self.username = ctk.CTkEntry(container, placeholder_text="Username", width=200, height=30)
        self.username.pack(pady=5)

        self.password = ctk.CTkEntry(container, placeholder_text="Password", show="*", width=200)
        self.password.pack(pady=5)

        ctk.CTkButton(container,fg_color="#FFBC53",hover_color="#FF7125", width=200,height=40, text="Sign In", command=self.login).pack(pady=20)
        ctk.CTkButton(container, fg_color="#FFBC53",hover_color="#FF7125", width=150,height=40,text="Back", command=lambda: master.show_frame("beranda")).pack()

    def login(self):
        if not self.username.get() or not self.password.get():
            messagebox.showwarning("Input Kosong", "Username dan password harus diisi!")
            return
        self.master.login_success()

class SignUpPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master,fg_color="#00A86B")

       
        # Frame putih tengah
        container = ctk.CTkFrame(self, width=400, height=500, fg_color="white", corner_radius=10,border_color="black", border_width=2)
        container.place(relx=0.5, rely=0.5, anchor="center")
        container.pack_propagate(False)

        # Gambar kepala user
        user_icon = ctk.CTkImage(light_image=Image.open(resource_path("assets\\login\\user_icon.png")).resize((150, 140)), size=(150, 140))

        ctk.CTkLabel(container, image=user_icon, text="").pack(pady=(25, 10))

        ctk.CTkLabel(container, text="Sign Up", font=ctk.CTkFont(family="Times New Roman", size=24)).pack(pady=5)

        self.username = ctk.CTkEntry(container, placeholder_text="Username", width=200)
        self.username.pack(pady=5)

        self.phone = ctk.CTkEntry(container, placeholder_text="No. Handphone", width=200)
        self.phone.pack(pady=5)

        self.password = ctk.CTkEntry(container, placeholder_text="Password", show="*", width=200)
        self.password.pack(pady=5)

        ctk.CTkButton(container, text="Register", fg_color="#FFBC53",hover_color="#FF7125", width=200,height=40, command=self.register).pack(pady=20)
        ctk.CTkButton(container, text="Back",fg_color="#FFBC53",hover_color="#FF7125", width=150,height=40,command=lambda: master.show_frame("beranda")).pack()

    def register(self):
        if not self.username.get() or not self.phone.get() or not self.password.get():
            messagebox.showwarning("Input Kosong", "Semua data harus diisi!")
            return
        self.master.login_success()

class ProductPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="white")
        self.configure(fg_color="white")
        self.master = master
        self.sort_ascending = True


        self.sidebar = Sidebar(self)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        self.content = ctk.CTkFrame(self,fg_color="white")
        self.content.grid(row=0, column=1, sticky="nsew")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(4, weight=1)

        # === HEADER ===
        self.header = ctk.CTkFrame(self.content,fg_color="white")
        self.header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        self.header.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            self.header,
            placeholder_text="🔍Search item .....",
            width=1600,
            height=30,
            corner_radius=10
            ,
            fg_color="white",
            text_color="black",
            border_color="#CCCCCC",
            border_width=2,
    )
        self.search_entry.grid(row=0, column=0, sticky="w")
        self.search_entry.bind("<Return>", self.on_search_enter)
        self.sort_button = ctk.CTkButton(
            self.header,
            text="↕️sort",
            width=30,
            height=40,
            corner_radius=10,
            fg_color="#00A86B",
            text_color="white",

            hover_color="#DDDDDD",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.toggle_price_sort
        )
        self.sort_button.grid(row=0, column=1, padx=(10, 0), sticky="e")

        self.account_btn = ctk.CTkButton(
            self.header,
            text="👤",
            width=20,
            height=20,
            command=lambda: self.master.show_frame("settings"),
            corner_radius=40,
            text_color="black",
            fg_color="white",
            hover_color="#DDDDDD",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.account_btn.grid(row=0, column=3, sticky="e", padx=(5, 0))

        self.basket_btn = ctk.CTkButton(
            self.header,
            text=f"🛒 ({len(self.master.cart)})",
            text_color="white",
            width=40,
            height=40,
            command=self.show_cart,
            corner_radius=10,
            fg_color="#FFBC53",
            hover_color="#FF7125",
            font=ctk.CTkFont(size=14, weight="bold")
            
        )
        self.basket_btn.grid(row=0, column=2, sticky="e", padx=(5, 0))

        # === BANNER SLIDER ===
        self.banner_index = 0
        self.banner_colors = [(255, 200, 200), (200, 255, 200), (200, 200, 255)]
        self.banner_ctk_images = []
        self.update_banner_images(self.winfo_width())

        self.coupon_codes = ["HEMAT10", "DISKON20", "HEMAT30"]
        self.after(1000, self.auto_rotate_banner)  # wait 1 second before starting



        self.banner_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self.banner_frame.grid(row=1, column=0, padx=0, pady=(5, 5), sticky="nsew")
        self.banner_frame.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(1, weight=0)
        self.banner_label = ctk.CTkLabel(self.banner_frame, image=self.banner_ctk_images[0], text="")
        self.banner_label.place(relwidth=1, relheight=1)  # covers entire banner frame
        
        # === CATEGORY ===
        self.allcat_label = ctk.CTkLabel(self.content, text="All Categories", font=ctk.CTkFont(size=22, weight="bold"))
        self.allcat_label.grid(row=2, column=0, sticky="w", padx=20, pady=(10, 0))

        self.category_frame = ctk.CTkFrame(self.content, fg_color="white")
        self.category_frame.grid(row=3, column=0, pady=(10, 10))
        self.category_frame.grid_columnconfigure(0, weight=1)
        self.update_account_button_image()


        self.kategori_produk = {
            "Semua": [
                ("Wortel 1.5 Kg", "wortel.png"),
                ("Timun 500 g", "timun.png"),
                ("Baby Corn 80 g", "baby_corn.png"),
                ("Tomat 1.4 kg", "tomat.png"),
                ("Anggur Merah 500 g", "anggur merah.png"),
                ("Anggur Hijau 500 g", "anggur hijau.png"),
                ("Strawberry 250 g", "strawberry.png"),
                ("Blueberry 250 g", "blueberry.png"),
                ("Raspberry 2.5 kg", "raspberry.png"),
                ("Lemon 150 g", "lemon.png"),
                ("Paha Ayam 450 g", "ayam.png"),
                ("Chicken Wing 300 g", "sayap ayam.png"),
                ("Dada Ayam Fillet 500 g", "dada ayam fillet.png"),
                ("Salmon Fillet 200 g", "salmon.png"),
                ("Premium Beef 500 g", "slice beef.png"),
                ("Teh Botol 350 ml", "tehbotol.png"),
                ("Susu UHT Cokelat 1L", "susu_uht.png"),
                ("Air Mineral 600 ml", "air_mineral.png"),
                ("Kopi Hitam Instan", "kopi.png"),
                ("Keripik Kentang 180g", "keripik.png"),
                ("Biskuit Cokelat 150g", "biskuit.png"),
                ("Coklat Batangan 100g", "coklat.png"),
                ("Permen Mint 50g", "permen.png"),
                ("Roti Tawar 250g", "roti.png"),
                ("Donat Cokelat 2 pcs", "donat.png"),
                ("Kue Brownies Slice", "brownies.png"),
                ("Croissant Butter", "croissant.png"),
                ("Timun 500 g", "timun.png"),
                ("Daun Bawang 110 g", "daun bawang.png"),
                ("Sawi Putih 100 g", "sawi putih.png"),
                ("Jagung Manis 500 g", "jagung.png"),
                ("Bawang Putih 250 g", "bawang_putih.png"),
                ("Bawang Merah 250 g", "bawang_merah.png"),
                ("Cabe Merah 200 g", "cabe_merah.png"),
                ("Cabe Rawit 150 g", "cabe_rawit.png"),
                ("Lengkuas 100 g", "lengkuas.png"),
                ("Jahe 100 g", "jahe.png"),
                ("Keju Cheddar 170g", "keju_cheddar.png"),
                ("Yogurt Strawberry 200 ml", "yogurt_strawberry.png"),
                ("Susu Kental Manis 490g", "susu_kental.png"),
                ("Butter Unsalted 200g", "butter.png"),
                ("Nugget Ayam 500 g", "nugget.png"),
                ("Sosis Sapi 300 g", "sosis.png"),
                ("Bakso Ikan 400 g", "bakso_ikan.png"),
            
            ],
            "Buah": [
                ("Anggur Merah 500 g", "anggur merah.png"),
                ("Anggur Hijau 500 g", "anggur hijau.png"),
                ("Strawberry 250 g", "strawberry.png"),
                ("Blueberry 250 g", "blueberry.png"),
                ("Raspberry 2.5 kg", "raspberry.png"),
                ("Lemon 150 g", "lemon.png")
            ],
            "Sayur": [
                ("Wortel 1.5 Kg", "wortel.png"),
                ("Timun 500 g", "timun.png"),
                ("Baby Corn 80 g", "baby_corn.png"),
                ("Daun Bawang 110 g", "daun bawang.png"),
                ("Sawi Putih 100 g", "sawi putih.png"),
                ("Jagung Manis 500 g", "jagung.png"),
                ("Tomat 1.4 kg", "tomat.png"),
                ("Bawang Putih 250 g", "bawang_putih.png"),
                ("Bawang Merah 250 g", "bawang_merah.png"),
                ("Cabe Merah 200 g", "cabe_merah.png"),
                ("Cabe Rawit 150 g", "cabe_rawit.png"),
                ("Lengkuas 100 g", "lengkuas.png"),
                ("Jahe 100 g", "jahe.png"),
            ],
            "Daging": [
                ("Paha Ayam 450 g", "ayam.png"),
                ("Chicken Wing 300 g", "sayap ayam.png"),
                ("Dada Ayam Fillet 500 g", "dada ayam fillet.png"),
                ("Salmon Fillet 200 g", "salmon.png"),
                ("Premium Beef 500 g", "slice beef.png")
            ],
            
            "Minuman": [
                ("Teh Botol 350 ml", "tehbotol.png"),
                ("Susu UHT Cokelat 1L", "susu_uht.png"),
                ("Air Mineral 600 ml", "air_mineral.png"),
                ("Kopi Hitam Instan", "kopi.png")
            ],
            "Snack": [
                ("Keripik Kentang 180g", "keripik.png"),
                ("Biskuit Cokelat 150g", "biskuit.png"),
                ("Coklat Batangan 100g", "coklat.png"),
                ("Permen Mint 50g", "permen.png")
            ],
            "Roti & Kue": [
                ("Roti Tawar 250g", "roti.png"),
                ("Donat Cokelat 2 pcs", "donat.png"),
                ("Kue Brownies Slice", "brownies.png"),
                ("Croissant Butter", "croissant.png")
            ],
           
            "Produk Susu": [
                ("Keju Cheddar 170g", "keju_cheddar.png"),
                ("Yogurt Strawberry 200 ml", "yogurt_strawberry.png"),
                ("Susu Kental Manis 490g", "susu_kental.png"),
                ("Butter Unsalted 200g", "butter.png")
            ],
            "Makanan Beku": [
                ("Nugget Ayam 500 g", "nugget.png"),
                ("Sosis Sapi 300 g", "sosis.png"),
                ("Bakso Ikan 400 g", "bakso_ikan.png"),
                ("Kentang Goreng Beku 1 kg", "kentang_beku.png")
            ]
           
        }
        self.active_category = "Semua"

        icon_map = {
            "Semua": "🗂️",
            "Sayur": "🥕",
            "Buah": "🍎",
            "Daging": "🍖",
            "Minuman": "🥤",
            "Snack": "🍪",
            "Roti & Kue": "🍞",
            "Produk Susu": "🧀",
            "Makanan Beku": "🧊",
        }
        for category in self.kategori_produk.keys():
            icon = icon_map.get(category, "📦")
            btn = ctk.CTkButton(
                self.category_frame,
                text=f"{icon}\n{category}",
                font=ctk.CTkFont(size=15),
                width=80,
                height=60,
                corner_radius=10,
                text_color="black",
                fg_color="#FFBC53",
                hover_color="#FF7125",
                border_color="black",
                border_width=2,
                command=lambda c=category: self.set_category(c)
            )
            btn.pack(side="left", padx=8, pady=5)
        # === PRODUCT GRID ==
      
        self.popular_label = ctk.CTkLabel(self.content, text="Products", font=ctk.CTkFont(size=22, weight="bold"))
        self.popular_label.grid(row=5, column=0, sticky="w", padx=20, pady=(0, 5))


        self.main_body = ctk.CTkFrame(self.content, fg_color="white")
        self.main_body.grid(row=6, column=0, sticky="nsew", padx=10, pady=10)
        self.main_body.grid_columnconfigure(0, weight=1)
        self.main_body.grid_rowconfigure(0, weight=1)

        self.grid_scroll = ctk.CTkScrollableFrame(self.main_body, width= 950, height=600,fg_color="white")
        self.grid_scroll.grid(row=0, column=0, sticky="nsew")
        self.grid_scroll.configure(width=900, height= 600)

        self.populate_products(self.kategori_produk[self.active_category])
        self.bind("<Configure>", self.on_resize)

    def claim_discount(self):
        messagebox.showinfo("Diskon", "🎉 Diskon HEMAT10 berhasil diklaim! Gunakan saat checkout.")

    def next_banner(self):
        self.banner_index = (self.banner_index + 1) % len(self.banner_ctk_images)
        self.banner_label.configure(image=self.banner_ctk_images[self.banner_index])

    def auto_rotate_banner(self):
        self.next_banner()
        self.after(5000, self.auto_rotate_banner)
    def update_coupon_button(self):
        code = self.coupon_codes[self.banner_index]
        self.coupon_button.configure(text=f"🎁 Klaim Kupon: {code}")
    def on_resize(self, event):
        if event.widget == self:
            self.update_banner_images(event.width)

    def update_banner_images(self, new_width):
        banner_paths = [
            resource_path("assets\\banners\\banner1.png"),
            resource_path("assets\\banners\\banner2.png"),
            resource_path("assets\\banners\\banner3.png")
        ]
        new_width = max(self.content.winfo_width(), 1760)
        new_height = int(190)

        self.banner_ctk_images = []
        for path in banner_paths:
            try:
                img = Image.open(path).resize((new_width, new_height)).convert("RGBA")
            except Exception as e:
                print(f"Failed to load {path}: {e}")
                img = Image.new("RGB", (new_width, new_height), color=(200, 200, 200))
            self.banner_ctk_images.append(ctk.CTkImage(light_image=img, size=(new_width, new_height)))

        if hasattr(self, "banner_label"):
            self.banner_label.configure(image=self.banner_ctk_images[self.banner_index])
        if hasattr(self, "left_arrow") and hasattr(self, "right_arrow"):
            show_arrows = len(self.banner_ctk_images) > 1
            if show_arrows:
                self.left_arrow.place(relx=0.01, rely=0.5, anchor="center")
                self.right_arrow.place(relx=0.99, rely=0.5, anchor="center")
            else:
                self.left_arrow.place_forget()
                self.right_arrow.place_forget()


    def on_search_enter(self, event):
        self.search_products()

    def search_products(self):
        query = self.search_entry.get().lower()
        produk_list = sorted(self.kategori_produk[self.active_category], key=lambda x: x[0].lower())  # sort by name

        # Binary Search
        def binary_search(data, target):
            low = 0
            high = len(data) - 1
            while low <= high:
                mid = (low + high) // 2
                nama = data[mid][0].lower()
                if nama == target:
                    return [data[mid]]
                elif nama < target:
                    low = mid + 1
                else:
                    high = mid - 1
            return []

        result = binary_search(produk_list, query)
        self.populate_products(result if result else [])
    def toggle_price_sort(self):
        produk_list = self.kategori_produk[self.active_category]
        # Gunakan insertion_sort yang sudah ada di file
        sorted_list = insertion_sort(
            produk_list.copy(),
            key=lambda item: self.get_price(item[0])
        )

        if not self.sort_ascending:
            sorted_list.reverse()

        self.sort_ascending = not self.sort_ascending
        self.sort_button.configure(
            text="⬇️" if not self.sort_ascending else "⬆️"
        )

        self.populate_products(sorted_list)

    def set_category(self, category):
        self.active_category = category
        self.populate_products(self.kategori_produk[category])
    def update_account_button_image(self):
        size = (28, 28)
        path = self.master.profile_image_path
        if path and os.path.exists(path):
            img = Image.open(path).resize(size).convert("RGBA")
        else:
            img = Image.new("RGBA", size, (200, 200, 200, 255))
            draw = ImageDraw.Draw(img)
            draw.text((4, 10), "A", fill=(255, 255, 255))  # placeholder

        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size[0], size[1]), fill=255)
        img.putalpha(mask)

        self.account_img = ctk.CTkImage(light_image=img, size=size)
        self.account_btn.configure(image=self.account_img, text="")  # hapus teks agar hanya gambar


    def populate_products(self, produk_list):
        for widget in self.grid_scroll.winfo_children():
            widget.destroy()

        max_columns = 5
        card_width = 180
        card_height = 220

        wrapper = ctk.CTkFrame(self.grid_scroll, fg_color="white")
        wrapper.pack(padx=10, pady=10)

        price_map = {
            "Wortel 1.5 Kg": 20000,
            "Timun 500 g": 8000,
            "Baby Corn 80 g": 10000,
            "Daun Bawang 110 g": 6000,
            "Sawi Putih 100 g": 7000,
            "Jagung Manis 500 g": 9000,
            "Tomat 1.4 kg": 15000,
            "Anggur Merah 500 g": 25000,
            "Anggur Hijau 500 g": 26000,
            "Strawberry 250 g": 22000,
            "Blueberry 250 g": 23000,
            "Raspberry 2.5 kg": 60000,
            "Lemon 150 g": 12000,
            "Paha Ayam 450 g": 27000,
            "Chicken Wing 300 g": 24000,
            "Dada Ayam Fillet 500 g": 30000,
            "Salmon Fillet 200 g": 40000,
            "Premium Beef 500 g": 50000,
            "Teh Botol 350 ml": 5000,
            "Susu UHT Cokelat 1L": 12000,
            "Air Mineral 600 ml": 3000,
            "Kopi Hitam Instan": 7000,
            "Keripik Kentang 180g": 15000,
            "Biskuit Cokelat 150g": 10000,
            "Coklat Batangan 100g": 12000,
            "Permen Mint 50g": 6000,
            "Roti Tawar 250g": 8000,
            "Donat Cokelat 2 pcs": 10000,
            "Kue Brownies Slice": 12000,
            "Croissant Butter": 11000,
            "Bawang Putih 250 g": 9000,
            "Bawang Merah 250 g": 10000,
            "Cabe Merah 200 g": 12000,
            "Cabe Rawit 150 g": 11000,
            "Lengkuas 100 g": 5000,
            "Jahe 100 g": 6000,
            "Keju Cheddar 170g": 14000,
            "Yogurt Strawberry 200 ml": 8000,
            "Susu Kental Manis 490g": 12000,
            "Butter Unsalted 200g": 25000,
            "Nugget Ayam 500 g": 28000,
            "Sosis Sapi 300 g": 23000,
            "Bakso Ikan 400 g": 24000,
            "Kentang Goreng Beku 1 kg": 27000

           
            # tambahkan harga lainnya jika diperlukan
        }

        for row in range((len(produk_list) + max_columns - 1) // max_columns):
            for col in range(max_columns):
                idx = row * max_columns + col
                if idx >= len(produk_list):
                    break

                nama, file = produk_list[idx]
                price = price_map.get(nama, 10000)
                qty_var = ctk.IntVar(value=1)


                # === Outer Shadow Frame ===
                outer_frame = ctk.CTkFrame(wrapper, fg_color="transparent", corner_radius=20)
                outer_frame.grid(row=row, column=col, padx=10, pady=10)

                # === Card Frame ===
                card = ctk.CTkFrame(outer_frame, width=card_width, height=card_height,
                                    corner_radius=12, fg_color="white", border_color="black", border_width=2)
                card.pack()
                card.grid_propagate(False)

                # === Hover effect ===
                def on_enter(e, frame=card):
                    frame.configure(fg_color="#DDDDDD")  # warna hover mirip tombol kategori

                def on_leave(e, frame=card):
                    frame.configure(fg_color="white")

                def bind_hover_recursive(widget):
                    widget.bind("<Enter>", on_enter)
                    widget.bind("<Leave>", on_leave)
                    for child in widget.winfo_children():
                        bind_hover_recursive(child)

                
                bind_hover_recursive(card)
                # === Product Image ===
                image_path = os.path.join("assets", "images", file)
                try:
                    img_obj = Image.open(image_path).resize((160, 90), Image.LANCZOS).convert("RGBA")
                except:
                    img_obj = Image.new("RGBA", (160, 90), (230, 230, 230, 255))
                img = ctk.CTkImage(light_image=img_obj, size=(160, 90))
                image_label = ctk.CTkLabel(card, image=img, text="")
                image_label.pack(pady=(15, 8), padx=10)

                # === Product Detail ===
                detail = ctk.CTkFrame(card, fg_color="transparent")
                detail.pack(padx=10, anchor="w")

                ctk.CTkLabel(detail, text=nama, font=ctk.CTkFont(size=11)).pack(anchor="w")
                ctk.CTkLabel(detail, text=f"Rp{price:,}", text_color="#00A86B",
                             font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w", pady=(2, 0))

                # === Qty + Add Cart ===
                bottom = ctk.CTkFrame(card, fg_color="transparent")
                bottom.pack(fill="x", expand=True, padx=10, pady=(10, 5))

                def increase(qv=qty_var):
                    qv.set(qv.get() + 1)

                def decrease(qv=qty_var):
                    if qv.get() > 1:
                        qv.set(qv.get() - 1)

                qty_frame = ctk.CTkFrame(bottom, fg_color="transparent")
                qty_frame.pack(side="left")

                ctk.CTkButton(qty_frame,fg_color="#E4281D",hover_color="#AF0E05", text="–", width=20, height=22, command=decrease).pack(side="left", padx=2)
                ctk.CTkLabel(qty_frame, textvariable=qty_var, width=10).pack(side="left", padx=2)
                ctk.CTkButton(qty_frame,fg_color="#00A86B", text="+", width=20, height=22, command=increase).pack(side="left", padx=2)

                ctk.CTkButton(
                    bottom, text="🛒", width=28, height=28, corner_radius=10,
                    fg_color="#FFBC53",hover_color="#FF7125", text_color="white",
                    font=ctk.CTkFont(size=12),
                    command=lambda n=nama, q=qty_var: self.add_to_cart_multiple(n, q.get())
                ).pack(side="right")

                # === Click to show popup ===
                def show_popup(event, n=nama, i=img):
                    self.show_product_popup(n, i)

                card.bind("<Button-1>", show_popup)
                for child in card.winfo_children():
                    child.bind("<Button-1>", show_popup)

    def show_product_popup(self, name, image):
        popup = ctk.CTkToplevel(self, fg_color="white")
        popup.title(name)
        popup.geometry("400x550")
        popup.transient(self.master)
        popup.attributes("-topmost", True)

        qty_var = ctk.IntVar(value=1)

        price = self.get_price(name)
        stock = {
            "Wortel 1.5 Kg": 20,
            "Timun 500 g": 80,
            "Baby Corn 80 g": 10,
            "Daun Bawang 110 g": 60,
            "Sawi Putih 100 g": 70,
            "Jagung Manis 500 g": 90,
            "Tomat 1.4 kg": 15,
            "Anggur Merah 500 g": 25,
            "Anggur Hijau 500 g": 26,
            "Strawberry 250 g": 22,
            "Blueberry 250 g": 23,
            "Raspberry 2.5 kg": 60,
            "Lemon 150 g": 12,
            "Paha Ayam 450 g": 27,
            "Chicken Wing 300 g": 24,
            "Dada Ayam Fillet 500 g": 30,
            "Salmon Fillet 200 g": 40,
            "Premium Beef 500 g": 50,
            "Teh Botol 350 ml": 50,
            "Susu UHT Cokelat 1L": 12,
            "Air Mineral 600 ml": 30,
            "Kopi Hitam Instan": 70,
            "Keripik Kentang 180g": 15,
            "Biskuit Cokelat 150g": 10,
            "Coklat Batangan 100g": 12,
            "Permen Mint 50g": 60,
            "Roti Tawar 250g": 80,
            "Donat Cokelat 2 pcs": 10,
            "Kue Brownies Slice": 12,
            "Croissant Butter": 11,
            "Bawang Putih 250 g": 90,
            "Bawang Merah 250 g": 10,
            "Cabe Merah 200 g": 12,
            "Cabe Rawit 150 g": 11,
            "Lengkuas 100 g": 50,
            "Jahe 100 g": 60,
            "Keju Cheddar 170g": 14,
            "Yogurt Strawberry 200 ml": 80,
            "Susu Kental Manis 490g": 12,
            "Butter Unsalted 200g": 25,
            "Nugget Ayam 500 g": 28,
            "Sosis Sapi 300 g": 23,
            "Bakso Ikan 400 g": 24,
            "Kentang Goreng Beku 1 kg": 27
        }.get(name, 50)

        # Gambar produk
        large_image = image._light_image.resize((300, 200))
        popup_image = ctk.CTkImage(light_image=large_image, size=(300, 200))
        ctk.CTkLabel(popup, image=popup_image, text="").pack(pady=(0, 10))

        # Nama produk
        ctk.CTkLabel(popup, text=name, font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)

        # Harga
        ctk.CTkLabel(popup, text=f"Harga: Rp{price:,}", text_color="#00A86B", font=ctk.CTkFont(size=14)).pack()

        # Stok
        ctk.CTkLabel(popup, text=f"Stok tersedia: {stock}").pack(pady=(0, 10))

        # Deskripsi
        desc = self.get_description(name)
        ctk.CTkLabel(popup, text=desc, wraplength=300, justify="left").pack(padx=10, pady=10)

        # === Kontrol Qty ===
        qty_frame = ctk.CTkFrame(popup, fg_color="white")
        qty_frame.pack(pady=10)

        def increase():
            if qty_var.get() < stock:
                qty_var.set(qty_var.get() + 1)

        def decrease():
            if qty_var.get() > 1:
                qty_var.set(qty_var.get() - 1)

        ctk.CTkButton(qty_frame, text="–", width=30, fg_color="#E4281D", hover_color="#AF0E05", command=decrease).pack(side="left", padx=5)
        ctk.CTkLabel(qty_frame, textvariable=qty_var, width=30).pack(side="left", padx=5)
        ctk.CTkButton(qty_frame, text="+", width=30, fg_color="#00A86B", command=increase).pack(side="left", padx=5)

        # Tombol Tambah ke keranjang
        ctk.CTkButton(
            popup,
            text="🛒 Tambahkan ke Keranjang",
            font=ctk.CTkFont(size=15, weight="bold"),
            width=50,
            height=50,
            corner_radius=10,
            text_color="white",
            fg_color="#FFBC53",
            hover_color="#FF7125",
            command=lambda: [
                self.add_to_cart_multiple(name, qty_var.get()),
                popup.destroy()
            ]
        ).pack(pady=20, padx=10)

    def update_basket(self):
        self.basket_btn.configure(text=f"🛒 ({len(self.master.cart)})")
    def add_to_cart_multiple(self, product_name, quantity):
        for _ in range(quantity):
            self.master.add_to_cart(product_name)

    def show_cart(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Keranjang Belanja")
        popup.geometry("400x400")
        popup.transient(self.master)

        ctk.CTkLabel(popup, text="Keranjang Belanja", font=ctk.CTkFont(size=18)).pack(pady=10)
        scroll_frame = ctk.CTkScrollableFrame(popup, width=360, height=280,fg_color="white")
        scroll_frame.pack(pady=10)

        if not self.master.cart:
            ctk.CTkLabel(scroll_frame, text="Keranjang kosong").pack(pady=10)
        else:
            for item in self.master.cart:
                frame = ctk.CTkFrame(scroll_frame,fg_color="white")
                frame.pack(fill="x", pady=5, padx=10)
                ctk.CTkLabel(frame, text=item).pack(side="left", padx=10)
                ctk.CTkButton(frame,fg_color="#E4281D",hover_color="#AF0E05", text="❌", width=30, command=lambda i=item: [self.master.remove_from_cart(i), popup.destroy()]).pack(side="right", padx=10)

        btn_frame = ctk.CTkFrame(popup,fg_color="white")
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame,fg_color="#FFBC53", text="Checkout",hover_color="#FF7125",width=50, height=40, command=lambda: [popup.destroy(), self.master.show_frame("cart")]).pack(side="right", padx=10)
        ctk.CTkButton(btn_frame,fg_color="#E4281D",hover_color="#AF0E05",width=50, height=40, text="Tutup", command=popup.destroy).pack(side="left", padx=10)

    def get_price(self, name):
        return {
            "Wortel 1.5 Kg": 20000,
            "Timun 500 g": 8000,
            "Baby Corn 80 g": 10000,
            "Daun Bawang 110 g": 6000,
            "Sawi Putih 100 g": 7000,
            "Jagung Manis 500 g": 9000,
            "Tomat 1.4 kg": 15000,
            "Anggur Merah 500 g": 25000,
            "Anggur Hijau 500 g": 26000,
            "Strawberry 250 g": 22000,
            "Blueberry 250 g": 23000,
            "Raspberry 2.5 kg": 60000,
            "Lemon 150 g": 12000,
            "Paha Ayam 450 g": 27000,
            "Chicken Wing 300 g": 24000,
            "Dada Ayam Fillet 500 g": 30000,
            "Salmon Fillet 200 g": 40000,
            "Premium Beef 500 g": 50000,
            "Teh Botol 350 ml": 5000,
            "Susu UHT Cokelat 1L": 12000,
            "Air Mineral 600 ml": 3000,
            "Kopi Hitam Instan": 7000,
            "Keripik Kentang 180g": 15000,
            "Biskuit Cokelat 150g": 10000,
            "Coklat Batangan 100g": 12000,
            "Permen Mint 50g": 6000,
            "Roti Tawar 250g": 8000,
            "Donat Cokelat 2 pcs": 10000,
            "Kue Brownies Slice": 12000,
            "Croissant Butter": 11000,
            "Bawang Putih 250 g": 9000,
            "Bawang Merah 250 g": 10000,
            "Cabe Merah 200 g": 12000,
            "Cabe Rawit 150 g": 11000,
            "Lengkuas 100 g": 5000,
            "Jahe 100 g": 6000,
            "Keju Cheddar 170g": 14000,
            "Yogurt Strawberry 200 ml": 8000,
            "Susu Kental Manis 490g": 12000,
            "Butter Unsalted 200g": 25000,
            "Nugget Ayam 500 g": 28000,
            "Sosis Sapi 300 g": 23000,
            "Bakso Ikan 400 g": 24000,
            "Kentang Goreng Beku 1 kg": 27000
        }.get(name, 0)

    def get_description(self, name):
        return {
            "Wortel 1.5 Kg": "Wortel segar dengan kualitas terbaik, kaya vitamin A, cocok untuk sop dan jus.",
            "Timun 500 g": "Timun hijau segar yang renyah, sempurna untuk lalapan atau infused water.",
            "Baby Corn 80 g": "Jagung muda yang manis dan lembut, cocok untuk tumisan dan salad.",
            "Daun Bawang 110 g": "Daun bawang segar untuk tambahan rasa pada mie, sup, dan gorengan.",
            "Sawi Putih 100 g": "Sawi putih berkualitas, renyah dan enak untuk sup dan tumisan.",
            "Jagung Manis 500 g": "Jagung manis siap masak, bisa direbus, dibakar, atau dijadikan sup.",
            "Tomat 1.4 kg": "Tomat merah segar, sumber vitamin C dan antioksidan, cocok untuk sambal atau jus.",
            "Anggur Merah 500 g": "Anggur merah manis, juicy dan segar, baik untuk camilan sehat.",
            "Anggur Hijau 500 g": "Anggur hijau segar, rasa manis dan asam seimbang, cocok disantap langsung.",
            "Strawberry 250 g": "Strawberry merah segar, kaya vitamin C, nikmat untuk smoothie atau topping.",
            "Blueberry 250 g": "Blueberry segar dengan rasa khas dan kaya antioksidan.",
            "Raspberry 2.5 kg": "Raspberry premium, lembut dan manis, cocok untuk kue atau jus sehat.",
            "Lemon 150 g": "Lemon segar dan harum, ideal untuk minuman segar atau penambah rasa.",
            "Paha Ayam 450 g": "Potongan paha ayam segar, cocok untuk digoreng atau dibakar.",
            "Chicken Wing 300 g": "Sayap ayam pilihan untuk hidangan BBQ, goreng, atau saus pedas manis.",
            "Dada Ayam Fillet 500 g": "Dada ayam tanpa tulang, rendah lemak, cocok untuk diet dan meal prep.",
            "Salmon Fillet 200 g": "Fillet salmon segar dari laut, tinggi omega-3, baik untuk kesehatan jantung.",
            "Premium Beef 500 g": "Daging sapi premium, cocok untuk steak, yakiniku, atau tumisan.",
            "Telur Ayam Negeri 1 kg": "Telur ayam negeri segar dengan cangkang bersih dan kuning cerah.",
            "Beras Premium 5 kg": "Beras pulen, harum, dan tidak mudah hancur, cocok untuk nasi harian keluarga",
            "Jahe 100 g": "Jahe segar untuk minuman hangat dan bumbu dapur.",
            "Keju Cheddar 170g": "Keju cheddar lezat untuk roti, pasta, atau camilan.",
            "Yogurt Strawberry 200 ml": "Yogurt rasa stroberi segar dengan probiotik alami.",
            "Susu Kental Manis 490g": "Susu manis kental serbaguna untuk kopi atau kue.",
            "Butter Unsalted 200g": "Butter tanpa garam untuk masak dan baking.",
            "Nugget Ayam 500 g": "Nugget ayam renyah, tinggal goreng siap santap.",
            "Sosis Sapi 300 g": "Sosis sapi dengan rasa gurih dan tekstur kenyal.",
            "Bakso Ikan 400 g": "Bakso ikan lezat cocok untuk kuah atau goreng.",
            "Kentang Goreng Beku 1 kg": "Kentang beku siap goreng ala restoran.",
            "Teh Botol 350 ml": "Minuman teh manis khas Indonesia, segar diminum dingin.",
            "Susu UHT Cokelat 1L": "Susu UHT rasa cokelat dengan nutrisi tinggi.",
            "Air Mineral 600 ml": "Air mineral murni yang menyegarkan dan sehat.",
            "Kopi Hitam Instan": "Kopi instan hitam pekat dengan aroma khas.",
            "Keripik Kentang 180g": "Keripik kentang renyah dengan rasa gurih.",
            "Biskuit Cokelat 150g": "Biskuit isi cokelat, cocok untuk teman ngopi.",
            "Coklat Batangan 100g": "Coklat manis untuk camilan atau hadiah.",
            "Permen Mint 50g": "Permen rasa mint menyegarkan napas.",
            "Roti Tawar 250g": "Roti tawar lembut, cocok untuk sarapan.",
            "Donat Cokelat 2 pcs": "Donat lembut dengan topping cokelat lezat.",
            "Kue Brownies Slice": "Brownies cokelat moist siap santap.",
            "Croissant Butter": "Croissant renyah berlapis mentega harum.",

        }.get(name, "Deskripsi belum tersedia.")
     
class CartPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master,fg_color="white")

        self.sidebar = Sidebar(self)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_content = ctk.CTkFrame(self, fg_color="white")
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_content.grid_columnconfigure((0, 1), weight=1, uniform="column")

        # === ORDER SUMMARY (LEFT COLUMN) ===
        self.order_frame = ctk.CTkFrame(self.main_content, fg_color="white", corner_radius=10)
        self.order_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        self.order_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.order_frame, text="🛒 Order Summary", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(10, 5))

        self.cart_list_frame = ctk.CTkScrollableFrame(self.order_frame, width=400, height=300, fg_color="white")
        self.cart_list_frame.pack(pady=(0, 10), padx=10, fill="both", expand=True)

        self.promo_entry = ctk.CTkEntry(self.order_frame, placeholder_text="Promo Code", width=200)
        self.promo_entry.pack(pady=(5, 2))
        self.apply_coupon_btn = ctk.CTkButton(self.order_frame, fg_color="#00A86B", text="Apply Coupon", width=150, command=self.update_total)
        self.apply_coupon_btn.pack(pady=(0, 10))

        # === PAYMENT SUMMARY (RIGHT COLUMN) ===
        self.payment_frame = ctk.CTkFrame(self.main_content, fg_color="white", corner_radius=10)
        self.payment_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)

        ctk.CTkLabel(self.payment_frame, text="💳 Payment", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(10, 10))

        self.subtotal_label = ctk.CTkLabel(self.payment_frame, text="Sub Total: Rp0")
        self.subtotal_label.pack(anchor="e", padx=20)
        self.tax_label = ctk.CTkLabel(self.payment_frame, text="Tax 10%: Rp0")
        self.tax_label.pack(anchor="e", padx=20)
        self.discount_label = ctk.CTkLabel(self.payment_frame, text="Discount: Rp0")
        self.discount_label.pack(anchor="e", padx=20)
        self.total_label = ctk.CTkLabel(self.payment_frame, text="Total: Rp0", font=ctk.CTkFont(size=16, weight="bold"), text_color="#FF5722")
        self.total_label.pack(anchor="e", padx=20, pady=(5, 10))

        self.checkout_btn = ctk.CTkButton(self.payment_frame, fg_color="#FFBC53",hover_color="#FF7125", text="Bayar Sekarang", width=200, height=40, command=self.finish_checkout)
        self.checkout_btn.pack(pady=10)

        ctk.CTkButton(self.payment_frame,fg_color="#E4281D",hover_color="#AF0E05", text="Kembali", command=lambda: master.show_frame("product")).pack(pady=(0, 10))

        self.valid_coupons = {
            "HEMAT10": 0.10,
            "DISKON20": 0.20,
            "HEMAT30": 0.30
        }
        self.render_cart()


    def render_cart(self):
        for widget in self.cart_list_frame.winfo_children():
            widget.destroy()

        self.quantities = {}
        self.prices = {
            "Wortel 1.5 Kg": 20000,
            "Timun 500 g": 8000,
            "Baby Corn 80 g": 10000,
            "Daun Bawang 110 g": 6000,
            "Sawi Putih 100 g": 7000,
            "Jagung Manis 500 g": 9000,
            "Tomat 1.4 kg": 15000,
            "Anggur Merah 500 g": 25000,
            "Anggur Hijau 500 g": 26000,
            "Strawberry 250 g": 22000,
            "Blueberry 250 g": 23000,
            "Raspberry 2.5 kg": 60000,
            "Lemon 150 g": 12000,
            "Paha Ayam 450 g": 27000,
            "Chicken Wing 300 g": 24000,
            "Dada Ayam Fillet 500 g": 30000,
            "Salmon Fillet 200 g": 40000,
            "Premium Beef 500 g": 50000,
            "Teh Botol 350 ml": 5000,
            "Susu UHT Cokelat 1L": 12000,
            "Air Mineral 600 ml": 3000,
            "Kopi Hitam Instan": 7000,
            "Keripik Kentang 180g": 15000,
            "Biskuit Cokelat 150g": 10000,
            "Coklat Batangan 100g": 12000,
            "Permen Mint 50g": 6000,
            "Roti Tawar 250g": 8000,
            "Donat Cokelat 2 pcs": 10000,
            "Kue Brownies Slice": 12000,
            "Croissant Butter": 11000,
            "Bawang Putih 250 g": 9000,
            "Bawang Merah 250 g": 10000,
            "Cabe Merah 200 g": 12000,
            "Cabe Rawit 150 g": 11000,
            "Lengkuas 100 g": 5000,
            "Jahe 100 g": 6000,
            "Keju Cheddar 170g": 14000,
            "Yogurt Strawberry 200 ml": 8000,
            "Susu Kental Manis 490g": 12000,
            "Butter Unsalted 200g": 25000,
            "Nugget Ayam 500 g": 28000,
            "Sosis Sapi 300 g": 23000,
            "Bakso Ikan 400 g": 24000,
            "Kentang Goreng Beku 1 kg": 27000
        }

        for item in set(self.master.cart):
            frame = ctk.CTkFrame(self.cart_list_frame, fg_color="#FFFFFF", corner_radius=8)
            frame.pack(fill="x", pady=5, padx=10)

            # Image on the left
            image_path = os.path.join("assets", "images", item.lower().split()[0] + ".png")
            try:
                img_obj = Image.open(image_path).resize((40, 40)).convert("RGBA")
                img = ctk.CTkImage(light_image=img_obj, size=(40, 40))
                ctk.CTkLabel(frame, image=img, text="").pack(side="left", padx=5)
            except:
                pass  # Fallback to no image if not found

            qty = self.master.cart.count(item)
            self.quantities[item] = ctk.IntVar(value=qty)

            name_label = ctk.CTkLabel(frame, text=item)
            name_label.pack(side="left", padx=10)

            qty_controls = ctk.CTkFrame(frame, fg_color="white")
            qty_controls.pack(side="right", padx=10)

            # – button
            ctk.CTkButton(qty_controls, fg_color="#E4281D", hover_color="#AF0E05", text="-", width=20,
                          command=lambda i=item: self.change_quantity(i, -1)).pack(side="left")

            # qty label
            ctk.CTkLabel(qty_controls, textvariable=self.quantities[item]).pack(side="left", padx=5)

            # + button
            ctk.CTkButton(qty_controls, text="+", width=20, fg_color="#00A86B",
                          command=lambda i=item: self.change_quantity(i, 1)).pack(side="left", padx=(0, 5))

            # ❌ button (moved here)
            ctk.CTkButton(qty_controls, fg_color="#E4281D", hover_color="#AF0E05", text="❌", width=32,
                          command=lambda i=item: self.remove_item(i)).pack(side="left")

        self.update_total()


    def change_quantity(self, item, delta):
        count = self.master.cart.count(item)
        if delta < 0 and count > 1:
            self.master.cart.remove(item)
        elif delta > 0:
            self.master.cart.append(item)
        self.render_cart()
        self.master.frames["product"].update_basket()

    def remove_item(self, item):
        self.master.cart = [i for i in self.master.cart if i != item]
        self.render_cart()
        self.master.frames["product"].update_basket()

    
    def update_total(self):
        subtotal = sum(self.prices.get(item, 0) * self.master.cart.count(item) for item in set(self.master.cart))
        tax = int(subtotal * 0.10)

        code = self.promo_entry.get().strip().upper()
        discount_rate = self.valid_coupons.get(code, 0.0)
        discount = int(subtotal * discount_rate)

        total = subtotal + tax - discount

        self.subtotal_label.configure(text=f"Sub Total: Rp{subtotal:,.0f}")
        self.tax_label.configure(text=f"Tax 10%: Rp{tax:,.0f}")
        self.discount_label.configure(text=f"Discount: Rp{discount:,.0f}")
        self.total_label.configure(text=f"Total: Rp{total:,.0f}")

 
    def finish_checkout(self):
        if not self.master.cart:
            messagebox.showinfo("Pembayaran", "Keranjang kosong.")
            return

        confirm = messagebox.askokcancel("Konfirmasi Pembayaran", "Apakah Anda yakin ingin membayar?")
        if not confirm:
            return

        total = sum(self.prices.get(item, 0) * self.master.cart.count(item) for item in set(self.master.cart))
        item_counts = {item: self.master.cart.count(item) for item in set(self.master.cart)}

        # Simpan ke history
        self.master.purchase_history.append({
            'timestamp': datetime.datetime.now(),
            'items': item_counts,
            'total': total
        })

        messagebox.showinfo("Pembayaran", "Pembayaran berhasil! Transaksi disimpan ke history.")
        self.master.cart.clear()
        self.render_cart()
        self.master.frames["product"].update_basket()
        self.master.frames["history"].render_history()  # <== baris ini penting!


class HistoryPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master



        self.sidebar = Sidebar(self)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        self.content = ctk.CTkFrame(self,fg_color="white")
        self.content.grid(row=0, column=1, sticky="nsew")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        ctk.CTkLabel(self.content, text="Riwayat Transaksi", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=10)

        option_frame = ctk.CTkFrame(self.content)
        option_frame.pack(pady=5)

        self.sort_option = ctk.CTkOptionMenu(option_frame, values=["Terlama", "Terbaru"], command=self.render_history)
        self.sort_option.set("Terlama")

        self.sort_option.pack(side="left", padx=5)

        self.search_entry = ctk.CTkEntry(option_frame, placeholder_text="Cari berdasarkan nama produk", width=200)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<Return>", self.search_history)

        self.history_frame = ctk.CTkScrollableFrame(self.content, width=600, height=400)
        self.history_frame.pack(pady=10, padx=20, fill="both", expand=True)

        ctk.CTkButton(self.content, fg_color="#E4281D",hover_color="#AF0E05",text="Kembali", command=lambda: master.show_frame("product")).pack(pady=10)

    def render_history(self, *_):
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        history = self.master.purchase_history.copy()
        mode = self.sort_option.get()

        if mode == "Terlama":
            history.sort(key=lambda x: x['timestamp'])  # ascending
        elif mode == "Terbaru":
            history.sort(key=lambda x: x['timestamp'], reverse=True)  # descending

        self.sorted_history = history  # untuk pencarian jika dibutuhkan

        if not history:
            ctk.CTkLabel(self.history_frame, text="Belum ada riwayat transaksi.").pack(pady=10)
            return

        header = ctk.CTkFrame(self.history_frame)
        header.pack(fill="x", pady=5)
        font_bold = ctk.CTkFont(size=16, weight="bold")
        ctk.CTkLabel(header, text="Produk", width=300, anchor="w", font=font_bold).pack(side="left")
        ctk.CTkLabel(header, text="Jumlah", width=120, anchor="center", font=font_bold).pack(side="left")
        ctk.CTkLabel(header, text="Harga Total", width=180, anchor="e", font=font_bold).pack(side="left")
        ctk.CTkLabel(header, text="Tanggal", width=200, anchor="e", font=font_bold).pack(side="left")

        for data in history:
            time_str = data['timestamp'].strftime("%d %b %Y %H:%M")
            for item, qty in data['items'].items():
                total_item = qty * ProductPage.get_price(self, item)
                row = ctk.CTkFrame(self.history_frame)
                row.pack(fill="x", pady=2)
                
                font_normal = ctk.CTkFont(size=15)
                ctk.CTkLabel(row, text=item, width=300, anchor="w", font=font_normal).pack(side="left")
                ctk.CTkLabel(row, text=str(qty), width=120, anchor="center", font=font_normal).pack(side="left")
                ctk.CTkLabel(row, text=f"Rp{total_item:,}", width=180, anchor="e", font=font_normal).pack(side="left")
                ctk.CTkLabel(row, text=time_str, width=200, anchor="e", font=font_normal).pack(side="left")

    def search_history(self, event):
        query = self.search_entry.get().strip().lower()
        if not query:
            messagebox.showwarning("Input Kosong", "Masukkan nama produk untuk mencari.")
            return

        results = []
        for record in self.master.purchase_history:
            for item in record['items']:
                if query in item.lower():
                    results.append(record)
                    break  # Stop checking this record after first match

        for widget in self.history_frame.winfo_children():
            widget.destroy()

        if not results:
            ctk.CTkLabel(self.history_frame, text="Produk tidak ditemukan.").pack(pady=10)
            return

        for data in results:
            time_str = data['timestamp'].strftime("%d %b %Y %H:%M")
            for item, qty in data['items'].items():
                if query in item.lower():  # Only show matching item rows
                    total_item = qty * ProductPage.get_price(self, item)
                    row = ctk.CTkFrame(self.history_frame)
                    row.pack(fill="x", pady=2)
                    ctk.CTkLabel(row, text=item, width=200, anchor="w").pack(side="left")
                    ctk.CTkLabel(row, text=str(qty), width=100, anchor="center").pack(side="left")
                    ctk.CTkLabel(row, text=f"Rp{total_item:,}", width=150, anchor="e").pack(side="left")
                    ctk.CTkLabel(row, text=time_str, width=150, anchor="e").pack(side="left")


class SettingsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master,fg_color="white")
        self.master = master
        self.profile_image_path = None

        # Grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = Sidebar(self)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        # Content area
        self.content = ctk.CTkFrame(self, fg_color="white")
        self.content.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.content.grid_columnconfigure((0, 1), weight=1)

        # Dummy user data
        self.user_data = {
            "first_name": "Bryan",
            "last_name": "Cranston",
            "email": "bryan.cranston@mail.com"
        }

        # === PROFILE SECTION ===
        ctk.CTkLabel(self.content, text="Account", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, columnspan=2, padx=20, pady=(10, 5), sticky="w")

        # Profile Image
        self.profile_image_label = ctk.CTkLabel(self.content, text="")
        self.load_profile_image()
        self.profile_image_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        # Upload & Delete buttons
        self.upload_btn = ctk.CTkButton(self.content,fg_color="#FFBC53",hover_color="#FF7125", text="Upload new picture", command=self.upload_picture)
        self.upload_btn.grid(row=1, column=1, sticky="e", padx=20)

        self.delete_btn = ctk.CTkButton(self.content, fg_color="#E4281D",hover_color="#AF0E05",text="Delete", command=self.delete_picture, text_color="white")
        self.delete_btn.grid(row=2, column=1, sticky="e", padx=20, pady=(0, 10))

        # === PERSONAL INFO ===
        ctk.CTkLabel(self.content, text="First name").grid(row=3, column=0, padx=20, pady=(0, 5), sticky="w")
        self.first_name = ctk.CTkEntry(self.content, placeholder_text="First name")
        self.first_name.insert(0, self.user_data["first_name"])
        self.first_name.grid(row=4, column=0, padx=20, pady=5, sticky="ew")

        ctk.CTkLabel(self.content, text="Last name").grid(row=3, column=1, padx=20, pady=(0, 5), sticky="w")
        self.last_name = ctk.CTkEntry(self.content, placeholder_text="Last name")
        self.last_name.insert(0, self.user_data["last_name"])
        self.last_name.grid(row=4, column=1, padx=20, pady=5, sticky="ew")

        ctk.CTkLabel(self.content, text="Email").grid(row=5, column=0, columnspan=2, padx=20, pady=(10, 5), sticky="w")
        self.email = ctk.CTkEntry(self.content, placeholder_text="Email")
        self.email.insert(0, self.user_data["email"])
        self.email.grid(row=6, column=0, columnspan=2, padx=20, pady=5, sticky="ew")

        # === PASSWORD ===
        ctk.CTkLabel(self.content, text="Current Password").grid(row=7, column=0, padx=20, pady=(10, 5), sticky="w")
        self.current_password = ctk.CTkEntry(self.content, placeholder_text="Current Password", show="*")
        self.current_password.grid(row=8, column=0, padx=20, pady=5, sticky="ew")

        ctk.CTkLabel(self.content, text="New Password").grid(row=7, column=1, padx=20, pady=(10, 5), sticky="w")
        self.new_password = ctk.CTkEntry(self.content, placeholder_text="New Password", show="*")
        self.new_password.grid(row=8, column=1, padx=20, pady=5, sticky="ew")

        # === SAVE BUTTON ===
        # === THEME SWITCH ===
        ctk.CTkLabel(self.content, text="Appearance Mode").grid(row=9, column=0, padx=20, pady=(10, 5), sticky="w")
        self.theme_switch = ctk.CTkSwitch(self.content, text="Dark Mode", command=self.toggle_theme)
        self.theme_switch.grid(row=10, column=0, padx=20, pady=5, sticky="w")

        # === LANGUAGE SELECTOR ===
        ctk.CTkLabel(self.content, text="Language").grid(row=9, column=1, padx=20, pady=(10, 5), sticky="w")
        self.language_option = ctk.CTkOptionMenu(self.content, values=["English", "Indonesia"], command=self.set_language)
        self.language_option.set("English")  # default
        self.language_option.grid(row=10, column=1, padx=20, pady=5, sticky="w")

        # === SAVE BUTTON ===
        ctk.CTkButton(self.content,fg_color="#00A86B" ,text="Save Changes", command=self.save_changes).grid(row=11, column=0, columnspan=2, padx=20, pady=20)

    def load_profile_image(self):
        size = (80, 80)
        if self.profile_image_path and os.path.exists(self.profile_image_path):
            img = Image.open(self.profile_image_path).resize(size).convert("RGBA")
        else:
            img = Image.new("RGBA", size, (200, 200, 200, 255))
            draw = ImageDraw.Draw(img)
            draw.text((20, 30), "IMG", fill=(255, 255, 255))

        # Circle mask
        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size[0], size[1]), fill=255)
        img.putalpha(mask)

        self.tk_image = ctk.CTkImage(light_image=img, size=size)
        self.profile_image_label.configure(image=self.tk_image)

    def upload_picture(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg")])
        if file_path:
            self.profile_image_path = file_path
            self.master.profile_image_path = file_path  # simpan ke global app
            self.load_profile_image()

            # Update tombol akun di ProductPage
            self.master.frames["product"].update_account_button_image()

    def delete_picture(self):
        self.profile_image_path = None
        self.load_profile_image()

    def save_changes(self):
        messagebox.showinfo("Saved", "Changes saved successfully!")
    def toggle_theme(self):
        if self.theme_switch.get():
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")

    def set_language(self, selected):
        if selected == "Indonesia":
            messagebox.showinfo("Bahasa", "Bahasa diatur ke Indonesia (fitur demo).")
            # You could refresh labels here
        else:
            messagebox.showinfo("Language", "Language set to English (demo only).")

if __name__ == "__main__":
    app = GroceryApp()
    app.mainloop()
