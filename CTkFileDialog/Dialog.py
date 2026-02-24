#!/usr/bin/env python
import os, re, cv2, time
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from pathlib import Path
from PIL import Image 
import tkinter as tk
from CTkToolTip import *
from typing import Any, Literal, Optional, TextIO, List
from _tkinter import TclError
from tkinter import ttk
import _tkinter 
from ._system import find_owner

class _CustomToolTip(CTkToolTip):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _show(self) -> None:
        if not self.widget.winfo_exists():
            self.hide()
            self.destroy()

        if self.status == "inside" and time.time() - self.last_moved >= self.delay:
            self.status = "visible"
            try: 
                self.deiconify()
            except _tkinter.TclError: 
                pass


class _System():
    
    def __init__(self) -> None:
        pass

    @staticmethod
    def GetPath(path=None) -> str:
        if path is None:
            path = os.getcwd()
        return f"{path}" if path == os.getenv('HOME') else path
    
    @staticmethod
    def parse_path(path):
        
        return os.path.abspath(os.path.expanduser(os.path.expandvars(path)))

class _DrawApp():

    def __init__(self, 
                 method : str,
                 filetypes: Optional[List[str]] = None, 
                 bufering: int = 1,
                 encoding: str = 'utf-8',
                 current_path : str = '.',
                 hidden: bool = False, 
                 preview_img: bool = False,
                 autocomplete: bool = False,
                 video_preview: bool = False,
                 tool_tip: bool = False,
                 title: str = 'CTkFileDialog',
                 geometry: str = '1320x720') -> None:
        
        self.current_path = current_path

        if not self.current_path: 
            self.current_path = os.getcwd()
        else:
            self.current_path = _System.parse_path(path=self.current_path)
        self.autocomplete = autocomplete
        
        self.preview_img = preview_img
        self.bufering = bufering
        self.encoding = encoding
        self.hidden = hidden
        self.video_preview = video_preview
        self.suggest = []
        self.tool_tip = tool_tip
        self._all_buttons = []
        self.filetypes = filetypes
        self.tab_index = -1
        self._BASE_DIR = Path(__file__).parent
        self.method = method 
        self.current_theme = ctk.get_appearance_mode()
        self.app = ctk.CTkToplevel()
        self.app.title(string=title)
        self.app.geometry(geometry)
        self.selected_file = '' 
        self.selected_objects : list = [] 
        self._load_icons()
        self._temp_item = None 
        self.app.protocol("WM_DELETE_WINDOW", self.protocol_windows)
        self._temp_items =  [] 
        
        # Sorting state
        self.sort_by = 'name' # name, type, created, modified
        self.sort_reverse = False

        self.TopSide(master=self.app)
        self.LeftSide(master=self.app)
        self.CenterSide(master=self.app)
        self.app.bind("<Alt-Left>", lambda _: self.btn_retrocess(master=self.app))
        try: 
            self.app.grab_set()
        except _tkinter.TclError:
            pass

    def protocol_windows(self):

        try:
            self.app.destroy()

            self.app.unbind_all("<MouseWheel>")
        except  Exception:
            pass

    @staticmethod
    def _is_image(image : str) -> bool :
        try:

            with Image.open(image) as img:

                img.verify()

            return True
        except:
            return False
    def _load_icons(self):
        icon_path = self._BASE_DIR / "icons"  

        self.iconos = {
            "folder": ctk.CTkImage(Image.open(icon_path / "folder.png"), size=(40, 40)),
            "bash": ctk.CTkImage(Image.open(icon_path / "bash.png"), size=(40, 40)),
            "image": ctk.CTkImage(Image.open(icon_path / "image.png"), size=(40, 40)),
            "python": ctk.CTkImage(Image.open(icon_path / "python.png"), size=(40, 40)),
            "text": ctk.CTkImage(Image.open(icon_path / "text.png"), size=(40, 40)),
            "markdown": ctk.CTkImage(Image.open(icon_path / "markdown.png"), size=(40, 40)),
            "javascript": ctk.CTkImage(Image.open(icon_path / "javascript.png"), size=(40, 40)),
            "php": ctk.CTkImage(Image.open(icon_path / "php.png"), size=(40, 40)),
            "html": ctk.CTkImage(Image.open(icon_path / "html.png"), size=(40, 40)),
            "css": ctk.CTkImage(Image.open(icon_path / "css.png"), size=(40, 40)),
            "ini": ctk.CTkImage(Image.open(icon_path / "ini.png"), size=(40, 40)),
            "conf": ctk.CTkImage(Image.open(icon_path / "conf.png"), size=(40, 40)),
            "exe": ctk.CTkImage(Image.open(icon_path / "exe.png"), size=(40, 40)),
            "odt": ctk.CTkImage(Image.open(icon_path / "odt.png"), size=(40, 40)),
            "pdf": ctk.CTkImage(Image.open(icon_path / "pdf.png"), size=(40, 40)),
            "json": ctk.CTkImage(Image.open(icon_path / "json.png"), size=(40, 40)),
            "gz": ctk.CTkImage(Image.open(icon_path / "gz.png"), size=(40, 40)),
            "video": ctk.CTkImage(Image.open(icon_path / "video.png"), size=(40, 40)),
            "awk": ctk.CTkImage(Image.open(icon_path / "bash.png"), size=(40, 40)),
            'webp': ctk.CTkImage(Image.open(icon_path / 'image.png'), size=(40, 40)),
            "default": ctk.CTkImage(Image.open(icon_path / "text.png"), size=(40, 40)),  # ícono por defecto
        }

        self.extensiones_iconos = {
            ".webp": "webp",   
            ".awk": "bash",
            ".mp4": "video",
            ".mvk": "video",
            ".sh": "bash",
            ".zsh": "bash",
            ".py": "python",
            ".png": "image",
            ".jpg": "image",
            ".jpeg": "image",
            ".txt": "text",
            ".js": "javascript",
            ".md": "markdown",
            ".php": "php",
            ".html": "html",
            ".css": "css",
            ".ini": "ini",
            ".conf": "conf",
            ".json": "json", 
            ".odt": "odt",
            ".pdf": "pdf",
            ".exe": "exe",
            ".gz": "gz",
        }
    
    def update_entry(self, ruta) -> None:
        self.PathEntry.configure(state='normal')
        self.PathEntry.delete(0, 'end')
        self.PathEntry.insert(0, ruta)

    def fix_name(self, nombre : str,
                 max_len : int = 18) -> str:

        if len(nombre) > max_len:

            return nombre[:max_len - 3]
        return nombre
    
    def btn_retrocess(self, master: ctk.CTkToplevel):
        if self.current_path != os.path.dirname(self.current_path):
            self.current_path = os.path.dirname(self.current_path)
            self.update_entry(ruta=self.current_path)
            self._list_files(master)


    def navigate_to(self, ruta: str, master):
        try:
            ruta = os.path.abspath(os.path.expanduser(os.path.expandvars(ruta)))
            
            # Si es un directorio
            if os.path.isdir(ruta):
                if self.method == 'askdirectory':
                    self._temp_item = ruta
                self.current_path = Path(ruta)
                self.update_entry(ruta=self.current_path)
                self._list_files(master)
                return

            # Si es un archivo y estamos en modo guardar como archivo
            if self.method in ['asksaveasfile', 'asksaveasfilename']:
                if os.path.isfile(ruta):
                    msg = CTkMessagebox(
                        message='Este archivo existe. ¿Deseas sobrees؟',
                        icon='warning',
                        title='Advertencia',
                        option_1='Yes',
                        option_2='No'
                    )
                    if msg.get() == 'No':
                        return
                self._temp_item = ruta
                self.close_app()
                return

            if self.method == 'askopenfile':
                if not os.path.isfile(ruta):
                    
                    CTkMessagebox(message='File not found haha!', title='Error', icon='cancel')
                    self.PathEntry.delete(0, ctk.END)
                    self.PathEntry.insert(0, self.current_path)
                    return 

                self._temp_item = ruta
                self.update_entry(self._temp_item)
                return

            if os.path.isfile(ruta):
                self._temp_item = ruta
                self.update_entry(self._temp_item)
                return

            self.PathEntry.delete(0, 'end')
            self.PathEntry.insert(0, str(self.current_path))
            self.PathEntry.configure(state='normal')
            
            CTkMessagebox(message='No such file or directory!', title='Error', icon='cancel')
            return

        except PermissionError:
            
            CTkMessagebox(message='Permiso denegado!', title='Error', icon='cancel')
        except FileNotFoundError: 
            
            CTkMessagebox(message='File Not Found!', title='Error', icon='cancel')

    def close_app(self):
        if self.method == 'asksaveasfilename':
            if not os.path.isdir(self.PathEntry.get()): self.selected_file = self.PathEntry.get()

        if self._temp_item:
            self.protocol_windows() 
            self.app.destroy()
            if self.method == 'asksaveasfile':
                self.selected_file = self._temp_item
                return 
            elif self.method == 'askopenfile':
                self.selected_file = self._temp_item
            else:
                self.selected_file = self._temp_item
                return

        if len(self._temp_items) >= 1:
            self.protocol_windows()
            self.app.destroy()
            if self.method == "askopenfilenames" or self.method ==  "askopenfiles":
                seen = set()
                self.selected_objects = [
                    f for f in self._temp_items
                    if not os.path.isdir(f) and f not in seen and not seen.add(f)
                ]
                
                return
            
    
    @staticmethod
    def _is_video(video: str):

        video_extensions = ('.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv')
        return video.lower().endswith(video_extensions)

    def _autocomplete(self, event) -> str:

        if not hasattr(self, "entire_paths"):
            return "break"

        if not self.entire_paths:

            return "break"

        if not self.archivos:
            return "break"


        max_index = len(self.archivos)

        if event.keysym == 'Up':
            self.tab_index = (self.tab_index - 1) % max_index
        else:
            self.tab_index = (self.tab_index + 1) % max_index

        path = self.entire_paths[self.tab_index]
        self.PathEntry.delete(0, ctk.END)
        self.PathEntry.insert(0, path)
        
        self._temp_item = path 

        return "break"

    def _set_sort(self, by, master):
        if self.sort_by == by:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_by = by
            self.sort_reverse = False
        self._list_files(master)

    def TopSide(self, master: ctk.CTkToplevel) -> None:
        TopBar = ctk.CTkFrame(master=master, height=80, fg_color="transparent")
        TopBar.pack(side='top', fill='x')
        
        # Row 1: Actions and Path
        Row1 = ctk.CTkFrame(master=TopBar, fg_color="transparent")
        Row1.pack(side='top', fill='x', padx=5, pady=5)

        def btn_exit():
            msg = CTkMessagebox(message='¿Deseas salir?', title='Salir', option_1='Yes', option_2='No', icon='warning')
            if msg.get() == 'Yes':
                self.protocol_windows()

                self.selected_file = None 
                self.selected_objects = []
                self._temp_item = None 
                self._temp_items = []
                master.destroy()
                return 

        # Botón Salir
        ButtonExit = ctk.CTkButton(master=Row1, text='Exit', font=('Hack Nerd Font', 15), width=70, command=btn_exit, hover_color='red')
        ButtonExit.pack(side='left', padx=5)

         # Campo Path
        self.PathEntry = ctk.CTkEntry(master=Row1, width=600, corner_radius=0, insertwidth=0)
        self.PathEntry.insert(index=0, string=_System.GetPath(str(self.current_path)))
        self.PathEntry.pack(side='left', fill='y', padx=5)
        self.PathEntry.bind('<Return>', command = lambda _: self.navigate_to(ruta=self.PathEntry.get(), master=master))

        # Campo de Búsqueda
        self.SearchEntry = ctk.CTkEntry(master=Row1, width=250, placeholder_text="Search...")
        self.SearchEntry.pack(side='right', fill='y', padx=5)
        self.SearchEntry.bind('<KeyRelease>', command=lambda _: self._on_search_change(master))
      
        # Botón Retroceso
        ButtonRetroces = ctk.CTkButton(master=Row1, text='', font=('Hack Nerd Font', 15), width=70, command = lambda path=self.PathEntry.get(): self.btn_retrocess(master=master))
        ButtonRetroces.pack(side='left', padx=5)

        # Boton de Ok 
        ButtonOk = ctk.CTkButton(master=Row1, text='Ok', font=('Hack Nerd Font', 15), width=70, command = lambda: self.close_app())
        ButtonOk.pack(side='left', padx=5)

        # Row 2: Sorting
        Row2 = ctk.CTkFrame(master=TopBar, fg_color="transparent")
        Row2.pack(side='top', fill='x', padx=5, pady=2)
        
        ctk.CTkLabel(master=Row2, text="Sort by:", font=('Arial', 12, 'bold')).pack(side='left', padx=10)
        
        sort_options = [
            ("Name", "name"),
            ("Type", "type"),
            ("Created", "created"),
            ("Modified", "modified")
        ]
        
        for text, val in sort_options:
            btn = ctk.CTkButton(master=Row2, text=text, width=80, height=25, 
                               command=lambda v=val: self._set_sort(v, master))
            btn.pack(side='left', padx=5)

        if self.autocomplete:
            
            self.PathEntry.bind('<Down>', lambda event: self._autocomplete(event))
            self.PathEntry.bind('<Up>', lambda event: self._autocomplete(event))
            self.PathEntry.bind('<Tab>', lambda event: self._autocomplete(event))
    
    def _get_video_frame(self, path: str, frame_number: int = 1) -> Image.Image | None:
        if not self._is_video(path):
            return None

        try:
            cap = cv2.VideoCapture(path)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = cap.read()
            cap.release()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                return Image.fromarray(frame)
        except:
            return None
    
         
    def LeftSide(self, master) -> None:

        # Frame principal
        LeftSideFrame = ctk.CTkFrame(master=master, width=200)
        LeftSideFrame.pack(side='left', fill='y', padx=10, pady=10)
        LeftSideFrame.pack_propagate(False)

        # Primero el HOME del usuario
        home = os.path.expanduser("~")
        carpetas = {f"{str(os.getenv('HOME')).replace('/home/', '')}": home}

        # Cargar el archivo user-dirs.dirs
        dir_file = os.path.join(home, ".config/user-dirs.dirs")
        pattern = re.compile(r'XDG_\w+_DIR="(.+?)"')
        
        import platform
        if platform.system() == 'Linux':
            if not os.path.exists(path=dir_file):
                # raise FileNotFoundError(f"El archivo {dir_file} es importante para la ejecución del programa!")
                pass
            else:
                with open(dir_file, 'r') as f:
                    for line in f:
                        if not line.startswith('#') and line.strip():
                            match = pattern.search(line)
                            if match:
                                ruta = os.path.expandvars(match.group(1))
                                nombre = os.path.basename(os.path.normpath(ruta))
                                if nombre != f"{os.getenv('USER')}":  # Evitar duplicado
                                    carpetas[nombre] = ruta

        elif platform.system() == 'Windows':
            home = Path.home()
            win_carpetas = {
                home.name: str(home),  
                "Desktop": home / "Desktop",
                "Documents": home / "Documents",
                "Downloads": home / "Downloads",
                "Pictures": home / "Pictures",
                "Music": home / "Music",
                "Videos": home / "Videos",
            }

            carpetas = {}
            carpetas = {k: v  for k, v in win_carpetas.items()}

        # Título
        LabelSide = ctk.CTkLabel(master=LeftSideFrame, text='Lugares', font=('Hack Nerd Font', 15))
        LabelSide.pack(side=ctk.TOP, padx=5, pady=5)

        iconos = {
            os.getenv("USER"): "",  # HOME del usuario
            "Desktop": "", "Escritorio": "",
            "Downloads": "", "Descargas": "",
            "Documents": "", "Documentos": "",
            "Pictures": "", "Imágenes": "",
            "Music": "", "Música": "",
            "Videos": "", "Vídeos": "",
            "Templates": "", "Plantillas": "",
            "Public": "", "Público": "",
        }

        for nombre, ruta in carpetas.items():
            icono = iconos.get(nombre, "")  
            texto_boton = f"    {icono}  {nombre}"  
            DirectorySide = ctk.CTkButton(
                master=LeftSideFrame,
                text=texto_boton,
                font=("Hack Nerd Font", 14),
                anchor="w",
                fg_color="transparent",
                hover_color="#8da3ae",
                text_color="#000000" if self.current_theme.lower() == 'light' else '#cccccc',
                corner_radius=2,
                border_width=0,
                command=lambda r=ruta, n=nombre: self.navigate_to(ruta=r, master=master)
            )
            DirectorySide.pack(fill="x", pady=4)


    def event_scroll(self):
        
        canvas = self.CenterSideFrame._parent_canvas

        def _on_mousewheel(event):

            x_root, y_root = event.x_root, event.y_root

            # Coordenadas y tamaño del scrollable frame
            x1 = self.CenterSideFrame.winfo_rootx()
            y1 = self.CenterSideFrame.winfo_rooty()
            x2 = x1 + self.CenterSideFrame.winfo_width()
            y2 = y1 + self.CenterSideFrame.winfo_height()
            if x1 <= x_root <= x2 and y1 <= y_root <= y2:


                if event.num == 4: 
                    canvas.yview_scroll(-1, "units")
                elif event.num == 5:  
                    canvas.yview_scroll(1, "units")
                else:  

                    canvas.yview_scroll(-int(event.delta / 120), "units")
                self._verificar_scroll(self.app)
                return "break"   

        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind("<Button-4>", _on_mousewheel)
        canvas.bind("<Button-5>", _on_mousewheel)

        # Vincular a todos los widgets hijos
        for widget in canvas.winfo_children():
            widget.bind("<MouseWheel>", _on_mousewheel)
            widget.bind("<Button-4>", _on_mousewheel)
            widget.bind("<Button-5>", _on_mousewheel)


    def CenterSide(self, master: ctk.CTkToplevel) -> None:
        self.CenterSideFrame = ctk.CTkScrollableFrame(master=master)
        self.CenterSideFrame.pack(expand=True, side='top', fill='both', padx=10, pady=10)
        
        
        self.event_scroll()

        self.content_frame = ctk.CTkFrame(master=self.CenterSideFrame)
        self.content_frame.pack(side='top', fill='both', expand=True, padx=20, pady=10)

        self._list_files(master=master)

    def __clear__(self):

        for widget in self.content_frame.winfo_children():
            try: 
                widget.destroy()
            except (_tkinter.TclError, Exception):
                pass

    def _handle_click(self, event, r, master, boton, tool_tip=None):
        if not event.state & 0x0004: 
            self._temp_items.clear()
            self.selected_objects.clear()

        if event.state & 0x0004:

            if self.method in  ['askopenfilenames', 'askopenfiles']:
                if r not in self._temp_items: 
                    self._temp_items.append(r)
                boton.configure(fg_color="blue")
                return 

            if boton not in self._all_buttons: 
                self._all_buttons.append(boton)


        else:
            self._temp_items.clear()
            if self.method in ['askopenfilenames', 'askopenfiles']:
                self._temp_items.append(r)

            for btn in self._all_buttons:
                if btn.winfo_exists():
                    btn.configure(fg_color="transparent",
                    hover_color="#8da3ae",
                    text_color="#000000" if self.current_theme.lower() == 'light' else '#cccccc',
        )
            if os.path.isdir(r): 
                self.navigate_to(ruta=r, master=master)
            else:
                self._temp_items.append(r)

    @staticmethod
    def _get_info(ruta: str) -> str:
        try:
            st = os.stat(ruta)

            # Usuario propietario
            owner = find_owner(ruta)

            # Permisos (ej: -rw-r--r--)
            #permisos = get_permissions(ruta)
    
            # Fecha legible
            fecha = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.st_ctime))
    
            return f"""File: {os.path.basename(ruta)}
    creation: {fecha}
    owner: {owner}
    path: {ruta}
                    """
        except Exception as e:
            return f"Error al obtener info: {e}"

    
    def _cargar_archivos(self, master: Any, cantidad: int): 
        columnas = 5
        row = self.LOADED // columnas
        col = self.LOADED % columnas
        ruta = self.current_path

        while self.LOADED < len(self.archivos) and cantidad > 0:
            
            archivo = self.archivos[self.LOADED]
            ruta_completa = os.path.join(ruta, archivo)

            if self.method == 'askdirectory' and os.path.isfile(ruta_completa):
                self.LOADED += 1
                continue

            # Obtener ícono según tipo de archivo
            if os.path.isdir(ruta_completa):
                icono = self.iconos["folder"]
            else:
                if self.preview_img and self._is_image(ruta_completa):
                    try:
                        img = Image.open(ruta_completa)
                        img.thumbnail((32, 32))
                        icono = ctk.CTkImage(light_image=img, dark_image=img, size=(32, 32))
                    except:
                        icono = self.iconos.get("image", self.iconos["default"])
                elif self.video_preview and self._is_video(ruta_completa):
                    frame = self._get_video_frame(ruta_completa, frame_number=10)
                    if frame:
                        frame.thumbnail((32, 32))
                        icono = ctk.CTkImage(light_image=frame, dark_image=frame, size=(32, 32))
                    else:
                        icono = self.iconos.get("video", self.iconos["default"])
                else:
                    ext = os.path.splitext(archivo)[1].lower()
                    icon_key = self.extensiones_iconos.get(ext, "default")
                    icono = self.iconos.get(icon_key, self.iconos["default"])

            archivo_fixeado = self.fix_name(nombre=archivo)

            command = None
            if self.method not in ['askopenfilenames']:
                command = lambda r=ruta_completa: self.navigate_to(ruta=r, master=master)
        
            boton = ctk.CTkButton(
                master=self.content_frame,
                text=archivo_fixeado,
                image=icono,
                compound="left",
                width=180,
                height=60,
                anchor="w",
                fg_color="transparent",
                hover_color="#8da3ae",
                text_color="#000000" if self.current_theme.lower() == 'light' else '#cccccc',
                command=command
            )

            if self.tool_tip:
                _CustomToolTip(widget=boton, message=self._get_info(ruta_completa))

            if self.method in ['askopenfilenames', 'askopenfiles']:
                boton.bind('<Button-1>', lambda event, r=ruta_completa, b=boton: self._handle_click(event, r, master, b))

            boton.grid(row=row, column=col, padx=10, pady=10)
            col += 1
            if col >= columnas:
                col = 0
                row += 1

            self.LOADED += 1
            cantidad -= 1

    def _verificar_scroll(self, master):
        try: 
            canvas = self.CenterSideFrame._parent_canvas
            yview = canvas.yview()
            if yview[1] > 0.98 and self.LOADED < len(self.archivos):
                self._cargar_archivos(master, cantidad=5)
        except _tkinter.TclError:
             pass


    def _on_search_change(self, master):
        self._list_files(master)

    def _list_files(self, master: ctk.CTkToplevel) -> None:
        self.LOADED = 0
        self.BATCH = 50  
        self.selected_objects.clear()
        self._all_buttons.clear()
        
        self.CenterSideFrame._parent_canvas.yview_moveto(0)
        self.__clear__()

        ruta_path = self.current_path
        search_query = self.SearchEntry.get().lower() if hasattr(self, 'SearchEntry') else ""
        
        # Get all entries and their stats for sorting
        entries = []
        for f in os.scandir(ruta_path):
            if (f.is_dir() or (self.method != 'askdirectory' and f.is_file())) and \
               (self.hidden or not f.name.startswith('.')) and \
               (f.is_dir() or not self.filetypes or any(f.name.endswith(ext) for ext in self.filetypes)) and \
               (not search_query or search_query in f.name.lower()):
                
                stat = f.stat()
                entries.append({
                    'name': f.name,
                    'is_dir': f.is_dir(),
                    'type': os.path.splitext(f.name)[1].lower() if not f.is_dir() else '',
                    'created': stat.st_ctime,
                    'modified': stat.st_mtime,
                    'path': f.path
                })

        # Sorting logic
        if self.sort_by == 'name':
            entries.sort(key=lambda x: x['name'].lower(), reverse=self.sort_reverse)
        elif self.sort_by == 'type':
            entries.sort(key=lambda x: (x['type'], x['name'].lower()), reverse=self.sort_reverse)
        elif self.sort_by == 'created':
            entries.sort(key=lambda x: x['created'], reverse=self.sort_reverse)
        elif self.sort_by == 'modified':
            entries.sort(key=lambda x: x['modified'], reverse=self.sort_reverse)

        # Always keep directories on top unless explicitly reversed
        if not self.sort_reverse:
            entries.sort(key=lambda x: not x['is_dir'])

        self.archivos = [e['name'] for e in entries]

        if not self.archivos:
            return
        
        if self.autocomplete:
            self.entire_paths = [e['path'] for e in entries]
            if not self.entire_paths: 
                self.entire_paths = None

        self._cargar_archivos(master, cantidad=self.BATCH)


class _MiniDialog():

    def __init__(self, 
                 method: str,
                 hidden: bool = False,
                 filetypes: Optional[List[str]] = None,
                 autocomplete: bool = False,
                 initial_dir: str = '.',
                 _extra_method: str = '',
                 geometry: str = '500x400',
                 title: str = 'CTkFileDialog'):
        
        self.master = ctk.CTkToplevel()
        self.master.geometry(geometry_string=geometry)
        self.master.title(title)
        self._extra_method = _extra_method
        self.tab_index = -1 
        self.method = method 
        self.hidden = hidden 
        self.filetypes = filetypes
        self.autocomplete = autocomplete
        self.initial_dir = initial_dir

        if not self.initial_dir: 
            self.initial_dir = os.getcwd()
        else: 
            self.initial_dir = _System().GetPath(path=self.initial_dir)

        self.selected_path = ''
        self.selected_paths = []
        self.selected_items = []
        self.selected_item = ''
        
        # Sorting state
        self.sort_by = 'name'
        self.sort_reverse = False

        # Load images 
        self._PATH = os.path.dirname(os.path.realpath(__file__))

        self.folder_image = self._load_image(image=os.path.join(self._PATH, 'icons/_IconsMini/folder.png'))
    
        self.file_image = self._load_image(image=os.path.join(self._PATH, "icons/_IconsMini/file.png"))
        
        self._TopSide()

        self._CenterSide()
        
        self.list_files()
        self.master.bind("<Alt-Left>", lambda _: self._up() )

        self.master.wait_visibility()
        self.master.grab_set()
        self.master.wait_window()

    
    def _get_path(self):

        return os.path.abspath(os.path.expandvars(os.path.expanduser(self.initial_dir)))

    def _set_sort(self, by):
        if self.sort_by == by:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_by = by
            self.sort_reverse = False
        self.list_files()

    def _TopSide(self):

        self.frame = ctk.CTkFrame(self.master)
        self.frame.pack(fill=ctk.BOTH, expand=True)

        self.path_frame = ctk.CTkFrame(self.frame)
        self.path_frame.pack(fill=ctk.X, padx=10, pady=5)

        self.path_entry = ctk.CTkEntry(self.path_frame, )
        self.path_entry.pack(expand=True, fill=ctk.X, side=ctk.LEFT, padx=10, pady=10)
        self.path_entry.bind('<Return>', lambda _: self._on_enter_path())
        self.path_entry.insert(0, self._get_path())

        if self.autocomplete: 
            for bind in ['<Tab>', '<Down>', '<Up>']:
                self.path_entry.bind(bind, self._autocomplete)

        self.up_btn = ctk.CTkButton(
            self.path_frame, text="↑", width=30, command=self._up
        )
        self.up_btn.pack(side=ctk.LEFT, padx=10, pady=10)

        # Search Bar for Mini Dialog
        self.search_entry = ctk.CTkEntry(self.path_frame, placeholder_text="Search...", width=120)
        self.search_entry.pack(side=ctk.RIGHT, padx=10, pady=10)
        self.search_entry.bind('<KeyRelease>', lambda _: self._on_search_change_mini())

        # Sort Frame for Mini Dialog
        self.sort_frame = ctk.CTkFrame(self.frame, fg_color='transparent', height=30)
        self.sort_frame.pack(fill=ctk.X, padx=10, pady=2)
        
        sort_options = [("Name", "name"), ("Type", "type"), ("Date", "modified")]
        for text, val in sort_options:
            ctk.CTkButton(self.sort_frame, text=text, width=60, height=20, font=('Arial', 10),
                         command=lambda v=val: self._set_sort(v)).pack(side=ctk.LEFT, padx=5)

        btn_frame = ctk.CTkFrame(self.frame, fg_color='transparent')
        btn_frame.pack(side=ctk.BOTTOM, fill=ctk.X, padx=10, pady=10)

        ok_btn = ctk.CTkButton(btn_frame, text="OK", command=self._on_select)
        ok_btn.pack(side=ctk.RIGHT)

        ctk.CTkButton(btn_frame, text="Cancel", command=self._on_cancel).pack(
            side=ctk.RIGHT, padx=10
        )

    def _on_search_change_mini(self):
        self.list_files()

    def list_files(self):
        ruta_path = os.path.abspath(os.path.expanduser(os.path.expandvars(self.path_entry.get())))
        if os.path.isfile(ruta_path):
            return 
        try:

            try: 
                for item in self.tree.get_children():
                        self.tree.delete(item)
            except TclError:
                return 

            self.archivos = {'name': [], 'path': []}
            search_query = self.search_entry.get().lower() if hasattr(self, 'search_entry') else ""
            
            entries = []
            for f in os.scandir(ruta_path):
                if (f.is_dir() or (self.method != 'askdirectory' and f.is_file())) and \
                   (self.hidden or not f.name.startswith('.')) and \
                   (f.is_dir() or not self.filetypes or any(f.name.endswith(ext) for ext in self.filetypes)) and \
                   (not search_query or search_query in f.name.lower()):
                    
                    stat = f.stat()
                    entries.append({
                        'name': f.name,
                        'is_dir': f.is_dir(),
                        'type': os.path.splitext(f.name)[1].lower() if not f.is_dir() else '',
                        'modified': stat.st_mtime,
                        'path': f.path
                    })

            # Sorting logic
            if self.sort_by == 'name':
                entries.sort(key=lambda x: x['name'].lower(), reverse=self.sort_reverse)
            elif self.sort_by == 'type':
                entries.sort(key=lambda x: (x['type'], x['name'].lower()), reverse=self.sort_reverse)
            elif self.sort_by == 'modified':
                entries.sort(key=lambda x: x['modified'], reverse=self.sort_reverse)

            if not self.sort_reverse:
                entries.sort(key=lambda x: not x['is_dir'])

            self.update_entry(path=ruta_path)

            for e in entries:
                icon = self.folder_image if e['is_dir'] else self.file_image
                self.tree.insert("", tk.END, text=e['name'], image=icon)
                self.archivos['name'].append(e['name'])
                self.archivos['path'].append(e['path'])
            
            if self.autocomplete:
                self.absolute_paths = [e['path'] for e in entries]

        except PermissionError:
            CTkMessagebox(message='Permision Denied!', title='Error', icon='cancel')
            self._on_cancel(destroy=False)
        else: 
            if self.autocomplete:
                self.max_index = len(self.archivos['name'])


    def update_entry(self, path):
            self.path_entry.configure(state='normal')
            self.path_entry.delete(0, ctk.END)
            self.path_entry.insert(0, path)

    def _CenterSide(self):

        self.tree_frame = ctk.CTkFrame(self.frame)
        self.tree_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

        # Configurar estilo para el Treeview
        style = ttk.Style()
        style.theme_use("default")
        
        # Colores para el Treeview
        bg_color = self.master._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
        fg_color = self.master._apply_appearance_mode(ctk.ThemeManager.theme["CTkLabel"]["text_color"])
        selected_color = self.master._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["fg_color"])

        style.configure("Treeview",
                        background=bg_color,
                        foreground=fg_color,
                        fieldbackground=bg_color,
                        borderwidth=0,
                        font=("Arial", 11))
        
        style.map("Treeview", background=[('selected', selected_color)])

        self.tree = ttk.Treeview(self.tree_frame, show="tree", selectmode="extended" if self.method in ['askopenfilenames', 'askopenfiles'] else "browse")
        self.tree.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

        scrollbar = ctk.CTkScrollbar(self.tree_frame, command=self.tree.yview)
        scrollbar.pack(side=ctk.RIGHT, fill=ctk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.bind("<Double-1>", self._on_click)
        self.tree.bind("<<TreeviewSelect>>", self._on_select_item)

    def _load_image(self, image: str):
        return tk.PhotoImage(file=image).subsample(2, 2)

    def _on_enter_path(self):
        self.initial_dir = self.path_entry.get()
        self.list_files()

    def _autocomplete(self, event):
        if not hasattr(self, "absolute_paths") or not self.absolute_paths:
            return "break"

        max_index = len(self.absolute_paths)
        if event.keysym == 'Up':
            self.tab_index = (self.tab_index - 1) % max_index
        else:
            self.tab_index = (self.tab_index + 1) % max_index

        path = self.absolute_paths[self.tab_index]
        self.path_entry.delete(0, ctk.END)
        self.path_entry.insert(0, path)
        return "break"

    def _on_cancel(self, destroy=True):
        self.selected_path = None
        self.selected_paths = []
        if destroy:
            self.master.destroy()

    def _on_select_item(self, event):
        selected_item = self.tree.focus()
        if not selected_item:
            return
        
        items = self.tree.get_children()
        idx = items.index(selected_item)
        self.selected_item = self.absolute_paths[idx]

    def _on_select(self):
        if self.method == 'asksaveasfilename':
            path = self.path_entry.get()
            if not path:
                return
            
            if os.path.exists(path):
                msg = CTkMessagebox(message="File exists. Overwrite?", icon="warning", option_1="Yes", option_2="No")
                if msg.get() == "No":
                    return
            
            self.selected_path = path
            self.master.destroy()
            return

        elif self.method in ['askopenfiles', 'askopenfilenames']:
            selected_items = self.tree.selection()
            selected_paths = [
                self.absolute_paths[self.tree.index(item)]
                for item in selected_items
                if os.path.isfile(self.absolute_paths[self.tree.index(item)])
            ]

            if selected_paths:
                self.selected_paths = selected_paths
                self.master.destroy()
            return

        elif self.method in ['askopenfilename', 'askopenfile', 'askdirectory']:
            if not self.selected_item:
                return

            if self.method == 'askdirectory' and os.path.isdir(self.selected_item):
                self.selected_path = self.selected_item
                self.master.destroy()
                return

            elif self.method in ['askopenfilename', 'askopenfile'] and os.path.isfile(self.selected_item):
                self.selected_path = self.selected_item
                self.master.destroy()
                return

    def _on_click(self, event=None):
        selected_item = self.tree.focus()
        items = self.tree.get_children()

        if not selected_item:
            return 

        idx = items.index(selected_item)
        self.selected_item = self.absolute_paths[idx]

        if os.path.isdir(self.selected_item):
            self.initial_dir = self.selected_item 
            self.path_entry.delete(0, ctk.END)
            self.path_entry.insert(0, self.selected_item)
            self.list_files()
            return  

        # Si es archivo:
        self.path_entry.delete(0, ctk.END)
        self.path_entry.insert(0, self.selected_item)


    def _up(self):
        current_path = os.path.abspath(os.path.expandvars(os.path.expanduser(self.initial_dir)))

        self.initial_dir = os.path.dirname(current_path)

        self.path_entry.delete(0, ctk.END)
        self.path_entry.insert(0, self.initial_dir)

        self.list_files()
