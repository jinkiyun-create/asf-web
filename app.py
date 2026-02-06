import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os
from PIL import Image, ImageTk

EXCEL_FILE = "data.xlsx"
LOGO_FILE = "logo.png"

class ASFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ASF 데이터 분석 시스템 v2.0")
        self.root.geometry("1300x850") 
        self.root.configure(bg="#F0F2F5") # 배경을 밝은 그레이로

        # --- 상단 고해상도 헤더 ---
        header = tk.Frame(root, bg="#1A237E", height=100)
        header.pack(fill="x")
        header.pack_propagate(False)

        if os.path.exists(LOGO_FILE):
            try:
                img = Image.open(LOGO_FILE)
                img.thumbnail((200, 60), Image.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(img)
                tk.Label(header, image=self.logo_img, bg="#1A237E").pack(side="left", padx=30)
            except: pass

        tk.Label(header, text="ASF 사육돼지 발생 실시간 현황", 
                 font=("나눔스퀘어", 24, "bold"), bg="#1A237E", fg="white").pack(side="left", pady=20)

        # --- 중앙 검색 카드 영역 ---
        search_card = tk.Frame(root, bg="white", padx=25, pady=25, relief="flat")
        search_card.pack(fill="x", padx=40, pady=30)

        tk.Label(search_card, text="🔎 통합 검색", font=("맑은 고딕", 12, "bold"), bg="white", fg="#555").pack(side="left")
        
        self.search_entry = tk.Entry(search_card, font=("맑은 고딕", 15), width=40, 
                                     relief="solid", bd=1, highlightthickness=1, highlightcolor="#3F51B5")
        self.search_entry.pack(side="left", padx=20)
        self.search_entry.bind("<Return>", lambda e: self.search_data())

        btn = tk.Button(search_card, text="데이터 검색", command=self.search_data, 
                        bg="#3F51B5", fg="white", font=("맑은 고딕", 11, "bold"), 
                        padx=35, pady=8, relief="flat", cursor="hand2")
        btn.pack(side="left")

        # --- 표 디자인 커스텀 ---
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", font=("맑은 고딕", 10), rowheight=38, background="white", borderwidth=0)
        style.configure("Treeview.Heading", font=("맑은 고딕", 11, "bold"), background="#F8F9FA", foreground="#333")
        style.map("Treeview", background=[('selected', '#E8EAF6')], foreground=[('selected', '#1A237E')])

        table_container = tk.Frame(root, bg="white")
        table_container.pack(expand=True, fill='both', padx=40, pady=(0, 40))

        cols = ("no", "도", "시군", "년도", "신고일자", "확진일자", "사육규모", "발생내용")
        self.tree = ttk.Treeview(table_container, columns=cols, show='headings')
        
        # 열 너비 자동 설정
        w = {"no": 60, "도": 80, "시군": 120, "년도": 80, "신고일자": 110, "확진일자": 110, "사육규모": 120, "발생내용": 550}
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w[c], anchor="center" if c != "발생내용" else "w")

        v_scroll = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        h_scroll = ttk.Scrollbar(table_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')
        table_container.grid_columnconfigure(0, weight=1)
        table_container.grid_rowconfigure(0, weight=1)

        self.load_initial_data()

    def load_initial_data(self):
        if not os.path.exists(EXCEL_FILE): return
        try:
            self.df = pd.read_excel(EXCEL_FILE, skiprows=1)
            if len(self.df.columns) >= 8:
                self.df = self.df.iloc[:, :8]
                self.df.columns = ["no", "도", "시군", "년도", "신고일자", "확진일자", "사육규모", "발생내용"]
            self.display_data(self.df)
        except Exception as e:
            messagebox.showerror("오류", f"파일 읽기 실패: {e}")

    def display_data(self, dataframe):
        for item in self.tree.get_children(): self.tree.delete(item)
        for i, row in dataframe.iterrows():
            if pd.isna(row.values[0]): continue 
            f_row = []
            for col, val in zip(self.df.columns, row.values):
                if col == "사육규모":
                    try: val = f"{int(val):,}" # 1,000 단위 콤마
                    except: pass
                f_row.append(str(val) if pd.notna(val) else "-")
            tag = 'even' if i % 2 == 0 else 'odd'
            self.tree.insert("", "end", values=f_row, tags=(tag,))
        
        self.tree.tag_configure('odd', background='#FBFBFC')
        self.tree.tag_configure('even', background='white')

    def search_data(self):
        q = self.search_entry.get().strip().lower()
        if not q:
            self.display_data(self.df)
            return
        mask = self.df.apply(lambda r: r.astype(str).str.contains(q, case=False).any(), axis=1)
        self.display_data(self.df[mask])

if __name__ == "__main__":
    root = tk.Tk()
    app = ASFApp(root)
    root.mainloop()
