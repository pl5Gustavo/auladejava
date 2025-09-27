# pangolesgames.py
# Sistema Pangoles Games - Admin (MySQL / XAMPP)
import os
from tkinter import filedialog
from PIL import Image, ImageTk

import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import ttk
from datetime import datetime
import mysql.connector
from mysql.connector import Error
from PIL import Image, ImageTk
import os

# ---------------- Tema / Cores ----------------
THEMES = {
    "pangoles": {"bg": "#ADD8E6", "accent": "#FFFFFF", "fg": "#000000", "btn_fg": "#000000"},  # azul clarinho
    "claro":   {"bg": "#FFFFFF", "accent": "#E0E0E0", "fg": "#000000", "btn_fg": "#000000"},
    "escuro":  {"bg": "#0F0F0F", "accent": "#444444", "fg": "#FFFFFF", "btn_fg": "#FFFFFF"},
}

# ---------------- Aplicação Principal ----------------
class LojaGamerApp(tk.Tk):
    # --- CLIENTES ---
    def get_clientes(self):
        try:
            cur = self._dict_cursor()
            cur.execute("SELECT * FROM clientes ORDER BY id")
            rows = cur.fetchall()
            cur.close()
            return rows
        except Error as e:
            messagebox.showerror("Erro BD", f"Erro ao buscar clientes: {e}")
            return []

    def adicionar_cliente(self, nome, email, telefone, endereco):
        try:
            cur = self.conn.cursor()
            cur.execute("INSERT INTO clientes (nome, email, telefone, endereco) VALUES (%s,%s,%s,%s)",
                        (nome, email, telefone, endereco))
            self.conn.commit()
            lastid = cur.lastrowid
            cur.close()
            return lastid
        except Error as e:
            messagebox.showerror("Erro BD", f"Erro ao inserir cliente: {e}")
            return None

    def atualizar_cliente(self, cliente_id, nome, email, telefone, endereco):
        try:
            cur = self.conn.cursor()
            cur.execute("UPDATE clientes SET nome=%s, email=%s, telefone=%s, endereco=%s WHERE id=%s",
                        (nome, email, telefone, endereco, cliente_id))
            self.conn.commit()
            cur.close()
            return True
        except Error as e:
            messagebox.showerror("Erro BD", f"Erro ao atualizar cliente: {e}")
            return False

    def deletar_cliente(self, cliente_id):
        try:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM clientes WHERE id=%s", (cliente_id,))
            self.conn.commit()
            cur.close()
            return True
        except Error as e:
            messagebox.showerror("Erro BD", f"Erro ao deletar cliente: {e}")
            return False

    def __init__(self):
        super().__init__()
        self.title("Pangoles Games - Sistema Admin")

        # --- iniciar em tela cheia (maximizado) ---
        try:
            self.state("zoomed")  # usa maximizado no Windows
        except Exception:
            pass
        # self.attributes("-fullscreen", True)  # alternativa: tela cheia sem barra de tarefas

        self.resizable(True, True)

        # --- configuração do tema atual ---
        self.theme_name = "pangoles"
        self.theme = THEMES[self.theme_name]

        # --- Configuração MySQL (ajuste user/password se necessário) ---
        self.db_config = {
            "host": "localhost",
            "user": "root",
            "password": "",   # coloque a senha do seu MySQL se tiver
            "database": "pangolesgames"
        }
        self.conn = None
        self.conectar_bd()

        # Senha admin padrão (pode ser alterada em Configurações)
        self.admin_user = "admin"
        self.admin_senha = "123"

        # carregar logo (se existir) - tenta vários caminhos/nomes para evitar problemas
        self.logo_image = None
        possible_paths = [
            "pangoles_logo.png",
            "pangoles_logo.png.png",
            "assets/pangoles_logo.png",
            "assets/pangoles_logo.png.png",
            os.path.join(os.getcwd(), "pangoles_logo.png"),
            os.path.join(os.getcwd(), "pangoles_logo.png.png"),
        ]
        for p in possible_paths:
            if os.path.exists(p):
                try:
                    img = Image.open(p)
                    # tamanho razoável para cabeçalhos; pode ajustar depois
                    img = img.resize((140, 140), Image.LANCZOS)
                    self.logo_image = ImageTk.PhotoImage(img)
                except Exception:
                    self.logo_image = None
                break

        # area de frames
        self.frames = {}
        for F in (TelaBoasVindas, TelaLogin, TelaMenu,
                  TelaCadastroProduto, TelaListarProduto, TelaEstoque,
                  TelaHistoricoVendas, TelaRelatorios, TelaDashboard,
                  TelaConfiguracoes, TelaLogout):
            page_name = F.__name__
            frame = F(parent=self, controller=self)
            self.frames[page_name] = frame
            # uso place para cobrir toda a janela
            frame.place(x=0, y=0, relwidth=1, relheight=1)

        # mostrar primeira tela
        self.show_frame("TelaBoasVindas")

    # --- conexão BD ---
    def conectar_bd(self):
        try:
            self.conn = mysql.connector.connect(**self.db_config)
            if self.conn.is_connected():
                print("Conectado ao MySQL com sucesso!")
        except Error as e:
            messagebox.showerror("Erro BD", f"Erro ao conectar ao MySQL: {e}")
            self.conn = None

    # --- utilitários DB ---
    def _dict_cursor(self):
        if not self.conn:
            raise Error("Sem conexão com o banco")
        return self.conn.cursor(dictionary=True)

    def get_produtos(self):
        try:
            cur = self._dict_cursor()
            cur.execute("SELECT * FROM produtos ORDER BY id")
            rows = cur.fetchall()
            cur.close()
            return rows
        except Error as e:
            messagebox.showerror("Erro BD", f"Erro ao buscar produtos: {e}")
            return []

    def adicionar_produto(self, nome, preco, estoque):
        try:
            cur = self.conn.cursor()
            cur.execute("INSERT INTO produtos (nome, preco, estoque) VALUES (%s,%s,%s)",
                        (nome, float(preco), int(estoque)))
            self.conn.commit()
            lastid = cur.lastrowid
            cur.close()
            return lastid
        except Error as e:
            messagebox.showerror("Erro BD", f"Erro ao inserir produto: {e}")
            return None

    def atualizar_produto(self, produto_id, nome, preco, estoque):
        try:
            cur = self.conn.cursor()
            cur.execute("UPDATE produtos SET nome=%s, preco=%s, estoque=%s WHERE id=%s",
                        (nome, float(preco), int(estoque), int(produto_id)))
            self.conn.commit()
            cur.close()
            return True
        except Error as e:
            messagebox.showerror("Erro BD", f"Erro ao atualizar produto: {e}")
            return False

    def deletar_produto(self, produto_id):
        try:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM produtos WHERE id=%s", (int(produto_id),))
            self.conn.commit()
            cur.close()
            return True
        except Error as e:
            messagebox.showerror("Erro BD", f"Erro ao deletar produto: {e}")
            return False

    def registrar_venda(self, produto_id, quantidade):
        try:
            cur = self._dict_cursor()
            cur.execute("SELECT * FROM produtos WHERE id=%s", (produto_id,))
            prod = cur.fetchone()
            if not prod:
                return None, "Produto não encontrado"
            if prod["estoque"] < quantidade:
                return None, "Estoque insuficiente"

            novo_estoque = prod["estoque"] - quantidade
            valor_total = float(prod["preco"]) * quantidade

            cur2 = self.conn.cursor()
            cur2.execute("UPDATE produtos SET estoque=%s WHERE id=%s", (novo_estoque, produto_id))
            cur2.execute("INSERT INTO vendas (produto_id, quantidade, valor_total, data) VALUES (%s,%s,%s,NOW())",
                         (produto_id, quantidade, valor_total))
            self.conn.commit()
            lastid = cur2.lastrowid
            cur.close(); cur2.close()
            return lastid, None
        except Error as e:
            return None, str(e)

    def get_vendas(self):
        try:
            cur = self._dict_cursor()
            cur.execute("SELECT v.id, v.data, v.quantidade, v.valor_total, p.nome AS produto_nome "
                        "FROM vendas v JOIN produtos p ON v.produto_id = p.id ORDER BY v.id DESC")
            rows = cur.fetchall()
            cur.close()
            return rows
        except Error as e:
            messagebox.showerror("Erro BD", f"Erro ao buscar vendas: {e}")
            return []

    def produtos_com_estoque_baixo(self, limite=3):
        try:
            cur = self._dict_cursor()
            cur.execute("SELECT * FROM produtos WHERE estoque <= %s ORDER BY estoque ASC", (limite,))
            rows = cur.fetchall()
            cur.close()
            return rows
        except Error as e:
            messagebox.showerror("Erro BD", f"Erro ao verificar estoque: {e}")
            return []

    def rel_total_vendas(self):
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT SUM(valor_total) FROM vendas")
            total = cur.fetchone()[0] or 0
            cur.close()
            return float(total)
        except Error as e:
            messagebox.showerror("Erro BD", f"Erro rel total vendas: {e}")
            return 0.0

    def rel_produtos_mais_vendidos(self):
        try:
            cur = self._dict_cursor()
            cur.execute("SELECT p.nome, SUM(v.quantidade) as total FROM vendas v "
                        "JOIN produtos p ON v.produto_id=p.id GROUP BY p.id ORDER BY total DESC")
            rows = cur.fetchall()
            cur.close()
            return rows
        except Error as e:
            messagebox.showerror("Erro BD", f"Erro rel produtos vendidos: {e}")
            return []

    def resetar_banco(self):
        try:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM vendas")
            cur.execute("DELETE FROM produtos")
            try:
                cur.execute("DELETE FROM clientes")
            except Exception:
                pass
            self.conn.commit()
            cur.close()
            return True
        except Error as e:
            messagebox.showerror("Erro BD", f"Erro ao resetar banco: {e}")
            return False

    # --- tema dinamico: aplica tema aos frames quando troca ---
    def set_theme(self, theme_name):
        if theme_name not in THEMES:
            return
        self.theme_name = theme_name
        self.theme = THEMES[theme_name]
        for frame in self.frames.values():
            if hasattr(frame, "apply_theme"):
                frame.apply_theme()

    # --- exibir tela ---
    def show_frame(self, name):
        frame = self.frames.get(name)
        if not frame:
            return
        frame.tkraise()
        if hasattr(frame, "apply_theme"):
            frame.apply_theme()
        if hasattr(frame, "on_show"):
            frame.on_show()

# ---------------- Telas utilitarias / helpers ----------------
def styled_button(parent, text, command, width=22):
    # helper para botões com estilo do tema atual
    btn = tk.Button(parent, text=text, command=command,
                    font=("Arial", 11, "bold"), relief="flat", bd=0)
    # será estilizado pelo apply_theme das telas
    return btn

class TelaBase(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

    def apply_theme(self):
        # configuração base: cor de fundo
        t = self.controller.theme
        self.configure(bg=t["bg"])
        # cada tela implementa seus próprios ajustes

class TelaBoasVindas(TelaBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.container = tk.Frame(self)
        self.container.place(relx=0.5, rely=0.5, anchor="center")

        # logo (se existir)
        if controller.logo_image:
            self.lbl_logo = tk.Label(self.container, image=controller.logo_image, bg=controller.theme["bg"])
            self.lbl_logo.pack(pady=(0, 12))
        else:
            self.lbl_logo = tk.Label(self.container, text="Pangoles Games",
                                     font=("Arial Black", 30), bg=controller.theme["bg"])
            self.lbl_logo.pack(pady=(0, 12))

        self.lbl_title = tk.Label(self.container, text="Sistema Administrativo",
                                  font=("Arial", 18, "bold"), bg=controller.theme["bg"])
        self.lbl_title.pack(pady=(0,12))

        self.btn_login = styled_button(self.container, "Login Admin", lambda: controller.show_frame("TelaLogin"))
        self.btn_login.pack(pady=6)

        self.btn_sair = styled_button(self.container, "Sair", controller.destroy)
        self.btn_sair.pack(pady=6)

        self.apply_theme()

    def apply_theme(self):
        t = self.controller.theme
        self.configure(bg=t["bg"])
        self.container.configure(bg=t["bg"])
        if hasattr(self, "lbl_logo"):
            try:
                self.lbl_logo.configure(bg=t["bg"])
            except:
                pass
        self.lbl_title.configure(bg=t["bg"], fg=t["fg"])
        self.btn_login.configure(bg=t["accent"], fg=t["btn_fg"], width=25)
        self.btn_sair.configure(bg="#D23A3A", fg=t["fg"], width=25)

class TelaLogin(TelaBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        wrap = tk.Frame(self)
        wrap.place(relx=0.5, rely=0.5, anchor="center")

        # exibir logo pequeno no topo da tela de login (se houver)
        if controller.logo_image:
            self.lbl_logo = tk.Label(wrap, image=controller.logo_image, bg=controller.theme["bg"])
            self.lbl_logo.pack(pady=(0, 12))

        tk.Label(wrap, text="Login Administrativo", font=("Arial", 20, "bold"), bg=controller.theme["bg"]).pack(pady=(0,12))

        tk.Label(wrap, text="Usuário:", bg=controller.theme["bg"]).pack(anchor="w")
        self.entry_user = tk.Entry(wrap, width=30)
        self.entry_user.pack()

        tk.Label(wrap, text="Senha:", bg=controller.theme["bg"]).pack(anchor="w", pady=(8,0))
        self.entry_pass = tk.Entry(wrap, show="*", width=30)
        self.entry_pass.pack()

        self.btn_enter = styled_button(wrap, "Entrar", lambda: self.login(), width=30)
        self.btn_enter.pack(pady=12)

        self.btn_back = styled_button(wrap, "Voltar", lambda: controller.show_frame("TelaBoasVindas"), width=30)
        self.btn_back.pack()

        self.apply_theme()

    def login(self):
        user = self.entry_user.get().strip()
        passwd = self.entry_pass.get().strip()
        if user == self.controller.admin_user and passwd == self.controller.admin_senha:
            self.entry_pass.delete(0, tk.END)
            self.entry_user.delete(0, tk.END)
            self.controller.show_frame("TelaMenu")
        else:
            messagebox.showerror("Login", "Usuário ou senha inválidos.")

    def apply_theme(self):
        t = self.controller.theme
        self.configure(bg=t["bg"])
        for w in self.winfo_children():
            try:
                w.configure(bg=t["bg"], fg=t["fg"])
            except Exception:
                pass
        self.btn_enter.configure(bg=t["accent"], fg=t["btn_fg"])
        self.btn_back.configure(bg="gray", fg=t["fg"])

class TelaMenu(TelaBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        header = tk.Frame(self)
        header.pack(fill="x", pady=12)

        # exibir logo no header (se houver)
        if controller.logo_image:
            self.logo_label = tk.Label(header, image=controller.logo_image, bg=controller.theme["bg"])
            self.logo_label.pack(side="left", padx=12)
        tk.Label(header, text="Menu Principal (Admin)", font=("Arial", 18, "bold"), bg=controller.theme["bg"]).pack(pady=6)

        menu_frame = tk.Frame(self)
        menu_frame.pack(pady=10)

        buttons = [
            ("Cadastro de Produto", "TelaCadastroProduto"),
            ("Listar Produtos", "TelaListarProduto"),
            ("Controle de Estoque", "TelaEstoque"),
            ("Histórico de Vendas", "TelaHistoricoVendas"),
            ("Relatórios", "TelaRelatorios"),
            ("Dashboard", "TelaDashboard"),
            ("Configurações", "TelaConfiguracoes"),
            ("Logout", "TelaLogout"),
        ]

        for idx, (txt, page) in enumerate(buttons):
            b = styled_button(menu_frame, txt, lambda p=page: controller.show_frame(p), width=30)
            b.grid(row=idx // 2, column=idx % 2, padx=12, pady=8)

        self.apply_theme()

    def apply_theme(self):
        t = self.controller.theme
        self.configure(bg=t["bg"])
        for w in self.winfo_children():
            try:
                w.configure(bg=t["bg"])
            except:
                pass
        # estilizar botões
        for child in self.winfo_children():
            for widget in child.winfo_children():
                if isinstance(widget, tk.Button):
                    widget.configure(bg=t["accent"], fg=t["btn_fg"])

# ---------------- Cadastro Produto ----------------
class TelaCadastroProduto(TelaBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        frame = tk.Frame(self)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        # logo pequeno no topo da tela
        if controller.logo_image:
            self.lbl_logo = tk.Label(frame, image=controller.logo_image, bg=controller.theme["bg"])
            self.lbl_logo.pack(pady=(0,8))

        tk.Label(frame, text="Cadastro de Produto", font=("Arial", 18, "bold"), bg=controller.theme["bg"]).pack(pady=6)

        tk.Label(frame, text="Nome:", bg=controller.theme["bg"]).pack(anchor="w")
        self.entry_nome = tk.Entry(frame, width=50)
        self.entry_nome.pack()

        tk.Label(frame, text="Preço (ex: 199.90):", bg=controller.theme["bg"]).pack(anchor="w", pady=(8,0))
        self.entry_preco = tk.Entry(frame, width=25)
        self.entry_preco.pack()

        tk.Label(frame, text="Estoque (inteiro):", bg=controller.theme["bg"]).pack(anchor="w", pady=(8,0))
        self.entry_estoque = tk.Entry(frame, width=25)
        self.entry_estoque.pack()

        self.lbl_feedback = tk.Label(frame, text="", font=("Arial", 10), bg=controller.theme["bg"])
        self.lbl_feedback.pack(pady=6)

        bframe = tk.Frame(frame, bg=controller.theme["bg"])
        bframe.pack(pady=8)
        self.btn_salvar = styled_button(bframe, "Salvar Produto", lambda: self.salvar(), width=25)
        self.btn_salvar.grid(row=0, column=0, padx=6)
        self.btn_voltar = styled_button(bframe, "Voltar", lambda: controller.show_frame("TelaMenu"), width=25)
        self.btn_voltar.grid(row=0, column=1, padx=6)

        self.apply_theme()

    def salvar(self):
        nome = self.entry_nome.get().strip()
        preco = self.entry_preco.get().strip()
        estoque = self.entry_estoque.get().strip()
        if not (nome and preco and estoque):
            self.lbl_feedback.configure(text="Preencha todos os campos!", fg="red")
            return
        try:
            preco_f = float(preco)
            estoque_i = int(estoque)
        except:
            self.lbl_feedback.configure(text="Preço ou estoque inválido!", fg="red")
            return
        pid = self.controller.adicionar_produto(nome, preco_f, estoque_i)
        if pid:
            self.lbl_feedback.configure(text=f"Produto cadastrado (ID {pid})", fg="green")
            self.entry_nome.delete(0, tk.END)
            self.entry_preco.delete(0, tk.END)
            self.entry_estoque.delete(0, tk.END)
        else:
            self.lbl_feedback.configure(text="Erro ao cadastrar produto.", fg="red")

    def apply_theme(self):
        t = self.controller.theme
        self.configure(bg=t["bg"])
        for w in self.winfo_children():
            try:
                w.configure(bg=t["bg"])
            except:
                pass
        # botões
        for child in self.winfo_children():
            for widget in child.winfo_children():
                if isinstance(widget, tk.Button):
                    widget.configure(bg=t["accent"], fg=t["btn_fg"])

# ---------------- Listar Produtos ----------------
class TelaListarProduto(TelaBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        header = tk.Frame(self)
        header.pack(fill="x", pady=6)

        # logo no header
        if controller.logo_image:
            lbl = tk.Label(header, image=controller.logo_image, bg=controller.theme["bg"])
            lbl.pack(side="left", padx=12)
        tk.Label(header, text="Produtos Cadastrados", font=("Arial", 16, "bold"), bg=controller.theme["bg"]).pack(pady=6)

        # Treeview para listar produtos
        cols = ("id", "nome", "preco", "estoque")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=15)
        self.tree.heading("id", text="ID")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("preco", text="Preço")
        self.tree.heading("estoque", text="Estoque")
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("nome", width=500)
        self.tree.column("preco", width=100, anchor="e")
        self.tree.column("estoque", width=100, anchor="center")
        self.tree.pack(pady=10)

        btns = tk.Frame(self)
        btns.pack(pady=6)
        self.btn_atualizar = styled_button(btns, "Atualizar", lambda: self.atualizar())
        self.btn_atualizar.grid(row=0, column=0, padx=6)
        self.btn_editar = styled_button(btns, "Editar Selecionado", lambda: self.editar_selecionado())
        self.btn_editar.grid(row=0, column=1, padx=6)
        self.btn_deletar = styled_button(btns, "Deletar Selecionado", lambda: self.deletar_selecionado())
        self.btn_deletar.grid(row=0, column=2, padx=6)
        self.btn_voltar = styled_button(btns, "Voltar", lambda: controller.show_frame("TelaMenu"))
        self.btn_voltar.grid(row=0, column=3, padx=6)

        self.apply_theme()

    def on_show(self):
        self.atualizar()

    def atualizar(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        produtos = self.controller.get_produtos()
        for p in produtos:
            try:
                preco_text = f"{float(p['preco']):.2f}"
            except:
                preco_text = str(p.get('preco', '0.00'))
            self.tree.insert("", "end", values=(p["id"], p["nome"], preco_text, p["estoque"]))

    def editar_selecionado(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Editar", "Selecione um produto.")
            return
        item = self.tree.item(sel[0])["values"]
        pid, nome, preco, estoque = item[0], item[1], item[2], item[3]

        popup = tk.Toplevel(self)
        popup.title("Editar Produto")
        popup.geometry("420x250")
        popup.transient(self)
        popup.grab_set()

        tk.Label(popup, text="Nome:").pack(anchor="w", padx=12, pady=(12,0))
        e_nome = tk.Entry(popup, width=50)
        e_nome.pack(padx=12)
        e_nome.insert(0, nome)

        tk.Label(popup, text="Preço:").pack(anchor="w", padx=12, pady=(8,0))
        e_preco = tk.Entry(popup, width=20)
        e_preco.pack(padx=12)
        e_preco.insert(0, preco)

        tk.Label(popup, text="Estoque:").pack(anchor="w", padx=12, pady=(8,0))
        e_estoque = tk.Entry(popup, width=20)
        e_estoque.pack(padx=12)
        e_estoque.insert(0, estoque)

        def salvar_edit():
            try:
                novo_nome = e_nome.get().strip()
                novo_preco = float(e_preco.get().strip())
                novo_estoque = int(e_estoque.get().strip())
            except:
                messagebox.showerror("Erro", "Valores inválidos.")
                return
            ok = self.controller.atualizar_produto(pid, novo_nome, novo_preco, novo_estoque)
            if ok:
                messagebox.showinfo("Sucesso", "Produto atualizado.")
                popup.destroy()
                self.atualizar()
            else:
                messagebox.showerror("Erro", "Erro ao atualizar.")

        tk.Button(popup, text="Salvar", command=salvar_edit, bg=self.controller.theme["accent"], fg=self.controller.theme["btn_fg"]).pack(pady=12)

    def deletar_selecionado(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Deletar", "Selecione um produto.")
            return
        item = self.tree.item(sel[0])["values"]
        pid = item[0]
        if messagebox.askyesno("Confirmar", f"Deletar produto ID {pid}?"):
            ok = self.controller.deletar_produto(pid)
            if ok:
                messagebox.showinfo("Sucesso", "Produto deletado.")
                self.atualizar()

# ---------------- Estoque ----------------
class TelaEstoque(TelaBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # header com logo
        header = tk.Frame(self)
        header.pack(fill="x", pady=6)
        if controller.logo_image:
            tk.Label(header, image=controller.logo_image, bg=controller.theme["bg"]).pack(side="left", padx=12)
        tk.Label(header, text="Controle de Estoque", font=("Arial", 16, "bold"), bg=controller.theme["bg"]).pack(pady=6)

        self.lista = tk.Listbox(self, width=100, height=18)
        self.lista.pack(pady=8)

        btns = tk.Frame(self)
        btns.pack(pady=6)
        self.btn_atualizar = styled_button(btns, "Atualizar Estoque", lambda: self.atualizar())
        self.btn_atualizar.grid(row=0, column=0, padx=6)
        self.btn_voltar = styled_button(btns, "Voltar", lambda: controller.show_frame("TelaMenu"))
        self.btn_voltar.grid(row=0, column=1, padx=6)

        self.alert = tk.Label(self, text="", font=("Arial", 10), bg=controller.theme["bg"])
        self.alert.pack(pady=6)

        self.apply_theme()

    def on_show(self):
        self.atualizar()

    def atualizar(self):
        self.lista.delete(0, tk.END)
        produtos = self.controller.get_produtos()
        for p in produtos:
            self.lista.insert(tk.END, f"ID:{p['id']} | {p['nome']} - Estoque: {p['estoque']}")
        baixos = self.controller.produtos_com_estoque_baixo()
        if baixos:
            nomes = ", ".join([f"{b['nome']}({b['estoque']})" for b in baixos])
            self.alert.configure(text=f"Estoque baixo: {nomes}", fg="yellow")
            # aviso modal pode ser irritante se disparar sempre; você já avisou via alert, mas deixei como antes
            messagebox.showwarning("Atenção", f"Estoque baixo para: {nomes}")
        else:
            self.alert.configure(text="Nenhum estoque baixo.", fg=self.controller.theme["fg"])

    def apply_theme(self):
        t = self.controller.theme
        self.configure(bg=t["bg"])
        self.lista.configure(bg="#FFFFFF", fg="#000000")  # listbox mais legível
        self.btn_atualizar.configure(bg=t["accent"], fg=t["btn_fg"])
        self.btn_voltar.configure(bg="gray", fg=t["fg"])

# ---------------- Histórico de Vendas ----------------
# ---------------- Histórico de Vendas ----------------
class TelaHistoricoVendas(TelaBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        header = tk.Frame(self)
        header.pack(fill="x", pady=6)
        if controller.logo_image:
            tk.Label(header, image=controller.logo_image, bg=controller.theme["bg"]).pack(side="left", padx=12)
        tk.Label(header, text="Histórico de Vendas", font=("Arial", 16, "bold"), bg=controller.theme["bg"]).pack(pady=6)

        self.tree = ttk.Treeview(self, columns=("id", "data", "produto", "qtd", "total"), show="headings", height=14)
        self.tree.heading("id", text="ID")
        self.tree.heading("data", text="Data")
        self.tree.heading("produto", text="Produto")
        self.tree.heading("qtd", text="Qtd")
        self.tree.heading("total", text="Total (R$)")
        self.tree.column("id", width=50)
        self.tree.column("data", width=180)
        self.tree.column("produto", width=400)
        self.tree.column("qtd", width=60, anchor="center")
        self.tree.column("total", width=100, anchor="e")
        self.tree.pack(pady=8)

        btns = tk.Frame(self)
        btns.pack(pady=6)
        self.btn_atualizar = styled_button(btns, "Atualizar Vendas", lambda: self.atualizar())
        self.btn_atualizar.grid(row=0, column=0, padx=6)
        self.btn_registrar = styled_button(btns, "Registrar Venda", lambda: self.popup_registrar())
        self.btn_registrar.grid(row=0, column=1, padx=6)
        self.btn_voltar = styled_button(btns, "Voltar", lambda: controller.show_frame("TelaMenu"))
        self.btn_voltar.grid(row=0, column=2, padx=6)

        self.apply_theme()

    def on_show(self):
        self.atualizar()

    def atualizar(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        vendas = self.controller.get_vendas()
        for v in vendas:
            data = v["data"].strftime("%Y-%m-%d %H:%M:%S") if isinstance(v["data"], datetime) else str(v["data"])
            self.tree.insert("", "end", values=(v["id"], data, v["produto_nome"], v["quantidade"], f"{float(v['valor_total']):.2f}"))

    def popup_registrar(self):
        pop = tk.Toplevel(self)
        pop.title("Registrar Venda")
        pop.geometry("520x460")
        pop.transient(self)
        pop.grab_set()
        pop.configure(bg=self.controller.theme["bg"])

        # Logo no topo do popup (se existir)
        if self.controller.logo_image:
            tk.Label(pop, image=self.controller.logo_image, bg=self.controller.theme["bg"]).pack(pady=6)

        # Instrução
        tk.Label(pop, text="Selecione Produto:", font=("Arial", 12), bg=self.controller.theme["bg"]).pack(pady=6)

        # Lista de produtos
        prod_list = tk.Listbox(pop, width=70, height=8)
        prod_list.pack(pady=6)
        prods = self.controller.get_produtos()
        for p in prods:
            try:
                text = f"ID:{p['id']} | {p['nome']} - R${float(p['preco']):.2f} - Estoque:{p['estoque']}"
            except Exception:
                text = f"ID:{p.get('id')} | {p.get('nome')} - R${p.get('preco')} - Estoque:{p.get('estoque')}"
            prod_list.insert(tk.END, text)

        # Quantidade
        frm_qty = tk.Frame(pop, bg=self.controller.theme["bg"])
        frm_qty.pack(pady=(8,0))
        tk.Label(frm_qty, text="Quantidade:", bg=self.controller.theme["bg"]).grid(row=0, column=0, padx=6)
        qty_entry = tk.Entry(frm_qty, width=12)
        qty_entry.grid(row=0, column=1)
        qty_entry.focus_set()

        # Feedback
        feedback = tk.Label(pop, text="", fg="red", bg=self.controller.theme["bg"])
        feedback.pack(pady=6)

        # Função de confirmação (registrar a venda)
        def confirmar(event=None):
            sel = prod_list.curselection()
            if not sel:
                messagebox.showerror("Erro", "Selecione um produto.")
                return
            linha = prod_list.get(sel[0])
            try:
                pid = int(linha.split("|")[0].replace("ID:", "").strip())
            except Exception:
                messagebox.showerror("Erro", "Erro ao ler ID do produto.")
                return
            try:
                q = int(qty_entry.get())
                if q <= 0:
                    raise ValueError
            except Exception:
                messagebox.showerror("Erro", "Quantidade inválida. Digite um número inteiro maior que 0.")
                return

            venda_id, err = self.controller.registrar_venda(pid, q)
            if err:
                messagebox.showerror("Erro na venda", err)
                return
            messagebox.showinfo("Sucesso", f"Venda registrada! ID:{venda_id}")
            pop.destroy()
            # atualizar a lista desta tela e estoque
            self.atualizar()
            est_frame = self.controller.frames.get("TelaEstoque")
            if est_frame:
                est_frame.atualizar()

        # Botões (lado a lado)
        btns2 = tk.Frame(pop, bg=self.controller.theme["bg"])
        btns2.pack(pady=12)

        btn_confirm = tk.Button(
            btns2,
            text="Confirmar Venda",
            command=confirmar,
            bg=self.controller.theme["accent"],
            fg=self.controller.theme["btn_fg"],
            width=18
        )
        btn_confirm.grid(row=0, column=0, padx=8)

        btn_cancel = tk.Button(
            btns2,
            text="Cancelar",
            command=pop.destroy,
            bg="gray",
            fg="white",
            width=12
        )
        btn_cancel.grid(row=0, column=1, padx=8)

        # Atalho Enter confirma
        pop.bind("<Return>", confirmar)

    def apply_theme(self):
        t = self.controller.theme
        self.configure(bg=t["bg"])
        for w in [self.btn_atualizar, self.btn_registrar, self.btn_voltar]:
            w.configure(bg=t["accent"], fg=t["btn_fg"])


# ---------------- Relatórios ----------------
class TelaRelatorios(TelaBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        header = tk.Frame(self)
        header.pack(fill="x", pady=6)
        if controller.logo_image:
            tk.Label(header, image=controller.logo_image, bg=controller.theme["bg"]).pack(side="left", padx=12)
        tk.Label(header, text="Relatórios (simples)", font=("Arial", 16, "bold"), bg=controller.theme["bg"]).pack(pady=6)

        btns = tk.Frame(self)
        btns.pack(pady=10)
        b1 = styled_button(btns, "Total de Vendas (R$)", lambda: self.total_vendas())
        b1.grid(row=0, column=0, padx=8)
        b2 = styled_button(btns, "Produtos mais vendidos", lambda: self.produtos_mais_vendidos())
        b2.grid(row=0, column=1, padx=8)
        b3 = styled_button(btns, "Voltar", lambda: controller.show_frame("TelaMenu"))
        b3.grid(row=0, column=2, padx=8)

        self.apply_theme()

    def total_vendas(self):
        total = self.controller.rel_total_vendas()
        messagebox.showinfo("Total Vendas", f"Total de vendas: R${total:.2f}")

    def produtos_mais_vendidos(self):
        rows = self.controller.rel_produtos_mais_vendidos()
        if not rows:
            messagebox.showinfo("Produtos mais vendidos", "Nenhuma venda registrada.")
            return
        texto = "\n".join([f"{r['nome']}: {r['total']}" for r in rows])
        messagebox.showinfo("Produtos mais vendidos", texto)

    def apply_theme(self):
        t = self.controller.theme
        self.configure(bg=t["bg"])
        for child in self.winfo_children():
            if isinstance(child, tk.Frame):
                for w in child.winfo_children():
                    if isinstance(w, tk.Button):
                        w.configure(bg=t["accent"], fg=t["btn_fg"])

# ---------------- Dashboard ----------------
class TelaDashboard(TelaBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        header = tk.Frame(self)
        header.pack(fill="x", pady=6)
        if controller.logo_image:
            tk.Label(header, image=controller.logo_image, bg=controller.theme["bg"]).pack(side="left", padx=12)
        tk.Label(header, text="Dashboard (Resumo Rápido)", font=("Arial", 16, "bold"), bg=controller.theme["bg"]).pack(pady=6)

        self.lbl_info = tk.Label(self, text="", font=("Arial", 12), justify="left", bg=controller.theme["bg"])
        self.lbl_info.pack(pady=12)
        btns = tk.Frame(self)
        btns.pack(pady=6)
        tk.Button(btns, text="Atualizar Resumo", command=self.resumo).grid(row=0, column=0, padx=8)
        tk.Button(btns, text="Voltar", command=lambda: controller.show_frame("TelaMenu")).grid(row=0, column=1, padx=8)
        self.apply_theme()

    def on_show(self):
        self.resumo()

    def resumo(self):
        total_vendas = self.controller.rel_total_vendas()
        produtos = self.controller.get_produtos()
        qtd_produtos = len(produtos)
        # contar estoque baixo
        estoque_baixo = len(self.controller.produtos_com_estoque_baixo())
        texto = (f"Total vendas (R$): {total_vendas:.2f}\n"
                 f"Produtos cadastrados: {qtd_produtos}\n"
                 f"Produtos com estoque baixo: {estoque_baixo}")
        self.lbl_info.configure(text=texto)

    def apply_theme(self):
        t = self.controller.theme
        self.configure(bg=t["bg"])
        self.lbl_info.configure(bg=t["bg"], fg=t["fg"])

# ---------------- Configurações ----------------
class TelaConfiguracoes(TelaBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        header = tk.Frame(self)
        header.pack(fill="x", pady=6)
        if controller.logo_image:
            tk.Label(header, image=controller.logo_image, bg=controller.theme["bg"]).pack(side="left", padx=12)
        tk.Label(self, text="Configurações do Sistema", font=("Arial", 16, "bold"), bg=controller.theme["bg"]).pack(pady=8)

        # Tema
        tk.Label(self, text="Tema do Sistema:", font=("Arial", 12), bg=controller.theme["bg"]).pack(anchor="w", padx=12)
        btns = tk.Frame(self)
        btns.pack(pady=6, padx=12, anchor="w")
        tk.Button(btns, text="Padrão (Pangoles)", command=lambda: controller.set_theme("pangoles")).grid(row=0, column=0, padx=6)
        tk.Button(btns, text="Claro", command=lambda: controller.set_theme("claro")).grid(row=0, column=1, padx=6)
        tk.Button(btns, text="Escuro", command=lambda: controller.set_theme("escuro")).grid(row=0, column=2, padx=6)

        # alterar senha
        sep = tk.Frame(self, height=2, bd=0, bg=controller.theme["bg"])
        sep.pack(fill="x", pady=10)
        tk.Label(self, text="Alterar senha do admin:", font=("Arial", 12), bg=controller.theme["bg"]).pack(anchor="w", padx=12)
        self.entry_nova_senha = tk.Entry(self, show="*", width=30)
        self.entry_nova_senha.pack(padx=12, pady=6, anchor="w")
        tk.Button(self, text="Salvar nova senha", command=self.alterar_senha).pack(padx=12, anchor="w", pady=6)

        # resetar banco
        sep2 = tk.Frame(self, height=2, bd=0, bg=controller.theme["bg"])
        sep2.pack(fill="x", pady=10)
        tk.Label(self, text="Manutenção:", font=("Arial", 12), bg=controller.theme["bg"]).pack(anchor="w", padx=12)
        tk.Button(self, text="Resetar banco (apaga produtos e vendas)", fg="#FFFFFF", bg="#D23A3A",
                  command=self.resetar_banco).pack(padx=12, pady=6, anchor="w")

        tk.Button(self, text="Voltar", command=lambda: controller.show_frame("TelaMenu")).pack(pady=8)

        self.apply_theme()

    def alterar_senha(self):
        nova = self.entry_nova_senha.get().strip()
        if not nova:
            messagebox.showerror("Erro", "Digite uma senha válida.")
            return
        self.controller.admin_senha = nova
        self.entry_nova_senha.delete(0, tk.END)
        messagebox.showinfo("Sucesso", "Senha do admin alterada (em memória).")

    def resetar_banco(self):
        if messagebox.askyesno("Atenção", "Deseja apagar TODAS as vendas e produtos?"):
            ok = self.controller.resetar_banco()
            if ok:
                messagebox.showinfo("Reset", "Banco limpo com sucesso.")
            else:
                messagebox.showerror("Erro", "Falha ao resetar banco.")

    def apply_theme(self):
        t = self.controller.theme
        self.configure(bg=t["bg"])
        # atualizar botões da tela (procura botões diretos)
        for widget in self.winfo_children():
            if isinstance(widget, tk.Button):
                # botões importantes recebem accent
                widget.configure(bg=t["accent"], fg=t["btn_fg"])

# ---------------- Logout ----------------
class TelaLogout(TelaBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        # header com logo
        header = tk.Frame(self)
        header.pack(fill="x", pady=6)
        if controller.logo_image:
            tk.Label(header, image=controller.logo_image, bg=controller.theme["bg"]).pack(side="left", padx=12)
        tk.Label(self, text="Logout", font=("Arial", 16, "bold"), bg=controller.theme["bg"]).pack(pady=10)
        tk.Label(self, text="Deseja encerrar a sessão e voltar para a tela inicial?", bg=controller.theme["bg"]).pack(pady=6)
        bframe = tk.Frame(self, bg=controller.theme["bg"])
        bframe.pack(pady=8)
        tk.Button(bframe, text="Sim", command=lambda: controller.show_frame("TelaBoasVindas")).grid(row=0, column=0, padx=8)
        tk.Button(bframe, text="Não", command=lambda: controller.show_frame("TelaMenu")).grid(row=0, column=1, padx=8)
        self.apply_theme()

    def apply_theme(self):
        t = self.controller.theme
        self.configure(bg=t["bg"])
        for widget in self.winfo_children():
            try:
                widget.configure(bg=t["bg"], fg=t["fg"])
            except:
                pass

# ---------------- Execução ----------------
if __name__ == "__main__":
    app = LojaGamerApp()
    app.mainloop()
