### TODO:
## - Še nekaj komentarjev
## - Omejiti vrstice na 80 znakov
## - Narediti gumbke z ikonicami
## - Ko izberemo color picker, se mora barva nastaviti iz trenutne barve
## - Več sporočil v statusni vrstici (Label spodaj)
## - Premikanje označenih objektov z Drag&Drop
## - Odpraviti še kak hrošček :)
##  I WAS HERE
from tkinter import *
from tkinter.colorchooser import *
import math

# Stanja
NEVTRALNO = 0
OVAL_ZAC = 1
OVAL_RISEM = 2
CRTA_ZAC = 3
CRTA_RISEM = 4
PRAV_ZAC = 5
PRAV_RISEM = 6
OZNACENO = 7

# toleranca za klik pri označevanju
eps = 0.5

class Slikar():
    def __init__(self, master):

        self.stanje = NEVTRALNO  # evidenca stanja aplikacije
        self.tocka = None        # začetna točka pri risanju
        self.trenutni = None     # id številka objekta na platnu
        self.prejsnji_width = None  # prejšnja širina črte pred označevanjem
                                    # pri označevanju odebelimo črte
        
        # Glavni menu
        menu = Menu(master)
        master.config(menu=menu) # Dodamo menu

        # Naredimo podmenu "File"
        file_menu = Menu(menu)
        menu.add_cascade(label="File", menu=file_menu)

        # Dodamo izbire v file_menu
        file_menu.add_command(label="Odpri", command=self.odpri)
        file_menu.add_command(label="Shrani", command=self.shrani)
        file_menu.add_separator() # To doda separator v menu
        file_menu.add_command(label="Izhod", command=master.destroy)


        self.canvas = Canvas(master, width=300, height=300)
        self.canvas.grid(row=0, column=0, columnspan=3, rowspan=3)

        self.canvas.bind("<Button-1>", self.pritisk_levi)
        self.canvas.bind("<B1-Motion>", self.premik_levi)
        self.canvas.bind("<ButtonRelease-1>", self.spusti_levi)
        master.bind("<Escape>", self.razveljavi)
               
        gumb_oval = Button(master, text="Oval",
                           command=self.narisi_oval, width=10)
        gumb_oval.grid(row=3, column=0)
        
        gumb_pravokotnik = Button(master, text="Pravokotnik",
                                  command=self.narisi_pravokotnik, width=10)
        gumb_pravokotnik.grid(row=3, column=1)

        gumb_crta = Button(master, text="Črta",
                           command=self.narisi_crto, width=10)
        gumb_crta.grid(row=3, column=2)

        gumb_barva_roba = Button(master, text="Barva roba",
                                 command=self.izberi_barvo_roba, width=12)
        gumb_barva_roba.grid(row=0, column=3, columnspan=2)

        gumb_barva_roba = Button(master, text="Barva površine",
                                 command=self.izberi_barvo_povrsine, width=12)
        gumb_barva_roba.grid(row=1, column=3, columnspan=2)

        napis_sirina = Label(master, text="Širina:")
        napis_sirina = napis_sirina.grid(row=2, column=3)
        
        self.debelina = IntVar(master)
        self.debelina.set(1)
        self.debelina.trace("w", self.izberi_debelino)

        deb = OptionMenu(master, self.debelina, 1, 2, 3, 4)
        deb.grid(row=2, column=4)
        
        self.napis_spodaj = StringVar(value="Izberi lik")
        napis = Label(master, textvariable=self.napis_spodaj)
        napis.grid(row=4, column=0, columnspan=4)

    def narisi_oval(self):
        if self.stanje == OZNACENO: # preklic označevanja pred risanjem
            self.razveljavi_oznacitev()
            self.stanje = NEVTRALNO
            
        if self.stanje == NEVTRALNO:
            self.napis_spodaj.set("Levi pritisk za 1. točko.")
            self.stanje = OVAL_ZAC
                    
    def narisi_pravokotnik(self):
        if self.stanje == OZNACENO: # preklic označevanja pred risanjem
            self.razveljavi_oznacitev()
            self.stanje = NEVTRALNO

        if self.stanje == NEVTRALNO:
            self.napis_spodaj.set("Levi pritisk za 1. točko.")
            self.stanje = PRAV_ZAC

    def narisi_crto(self):
        if self.stanje == OZNACENO: # preklic označevanja pred risanjem
            self.razveljavi_oznacitev()
            self.stanje = NEVTRALNO
            
        if self.stanje == NEVTRALNO:
            self.napis_spodaj.set("Levi pritisk za 1. točko.")
            self.stanje = CRTA_ZAC

    def razdalja(self, x1, y1, x2, y2):
        """Pomožna funkcija za izračun razdalje med točkama"""
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

    def razveljavi_oznacitev(self):
        """Pomožna funkcija za razveljavitev označitve objekta."""
        self.canvas.itemconfig(self.trenutni, width=self.prejsnji_width)

    def oznaci(self, id):
        """Pomožna funkcija za ustrezno označevanje objekta. Označitev se se
razveljavi s funkcijo razveljavi_oznacitev()."""
        self.trenutni = id
        self.prejsnji_width = float(self.canvas.itemcget(id, "width"))
        self.debelina.set(int(self.prejsnji_width))
        self.canvas.itemconfig(id, width=self.prejsnji_width + 2)
        
    # Pomožne testne funkcije za označevanje likov
    def je_na_crti(self, x, y, x1, y1, x2, y2, eps):
        return abs(self.razdalja(x1, y1, x, y) + self.razdalja(x, y, x2, y2) -
                       self.razdalja(x1, y1, x2, y2)) < eps

    def je_na_pravokotniku(self, x, y, x1, y1, x2, y2, eps):
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        return (self.je_na_crti(x, y, x1, y1, x2, y1, eps) or
                self.je_na_crti(x, y, x2, y1, x2, y2, eps) or
                self.je_na_crti(x, y, x2, y2, x1, y2, eps) or
                self.je_na_crti(x, y, x1, y2, x1, y1, eps))
              
    def je_na_ovalu(self, x, y, x1, y1, x2, y2, eps):
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        cx, cy = (x1 + x2)/2, (y1 + y2)/2
        a, b   = (x2 - x1)/2, (y2 - y1)/2
        return abs(((x - cx)/a)**2 + ((y - cy)/b)**2 - 1) < eps
        
        
    def pritisk_levi(self, event):
        print(self.stanje)
        if self.stanje == OZNACENO:
            self.razveljavi_oznacitev()
            self.stanje = NEVTRALNO
          
        if self.stanje == NEVTRALNO: # označevanje
            id = self.canvas.find_closest(event.x, event.y)
            if id != tuple():
                x1,y1,x2,y2 = self.canvas.coords(id)
                x, y = event.x, event.y
                if self.canvas.type(id) == "line":
                    if self.je_na_crti(x, y, x1, y1, x2, y2, eps):
                        self.oznaci(id)
                        self.stanje = OZNACENO
                elif self.canvas.type(id) == "rectangle":
                    if self.je_na_pravokotniku(x, y, x1, y1, x2, y2, eps):
                        self.oznaci(id)
                        self.stanje = OZNACENO
                elif self.canvas.type(id) == "oval":
                    if self.je_na_ovalu(x, y, x1, y1, x2, y2, eps/5):
                        self.oznaci(id)
                        self.stanje = OZNACENO               
        elif self.stanje == OVAL_ZAC: # risanje ovala
            self.tocka = (event.x, event.y)
            self.trenutni = self.canvas.create_oval(
                event.x, event.y,
                event.x, event.y)
            self.napis_spodaj.set("({0},{1})".format(event.x, event.y));
            self.stanje = OVAL_RISEM
        elif self.stanje == PRAV_ZAC: # risanje pravokotnika
            self.tocka = (event.x, event.y)
            self.trenutni = self.canvas.create_rectangle(
                event.x, event.y,
                event.x, event.y)
            self.napis_spodaj.set("({0},{1})".format(event.x, event.y));
            self.stanje = PRAV_RISEM
        elif self.stanje == CRTA_ZAC: # risanje črte
            self.tocka = (event.x, event.y)
            self.trenutni = self.canvas.create_line(
                event.x, event.y,
                event.x, event.y)
            self.napis_spodaj.set("({0},{1})".format(event.x, event.y));
            self.stanje = CRTA_RISEM

            
    def premik_levi(self, event):
        if self.stanje in [OVAL_RISEM, PRAV_RISEM, CRTA_RISEM]:
            self.canvas.coords(self.trenutni, self.tocka[0], self.tocka[1],
                                 event.x, event.y)
            self.napis_spodaj.set("({0},{1})".format(event.x, event.y));

    def spusti_levi(self, event):
        if self.stanje in [OVAL_RISEM, PRAV_RISEM, CRTA_RISEM]:
            self.canvas.coords(self.trenutni, self.tocka[0], self.tocka[1],
                                 event.x, event.y)
            self.napis_spodaj.set("Izberi lik.")
            self.stanje = NEVTRALNO

    def razveljavi(self, event):  # prtisk ESC
        if self.stanje in [OVAL_ZAC, CRTA_ZAC, PRAV_ZAC]:
            self.stanje = NEVTRALNO
        elif self.stanje in [OVAL_RISEM, CRTA_RISEM, PRAV_RISEM]:
            self.canvas.delete(self.trenutni)
            self.stanje = NEVTRALNO
        elif self.stanje == OZNACENO:
            self.razveljavi_oznacitev()
            self.stanje = NEVTRALNO

    def izberi_barvo_roba(self):
        if self.stanje == OZNACENO:
            barva = askcolor()[-1]   # uporabimo komponento "color picker" 
            if barva is not None: # pritisnili smo OK
                if self.canvas.type(self.trenutni) == "line":
                    self.canvas.itemconfig(self.trenutni, fill=barva)
                else:
                    self.canvas.itemconfig(self.trenutni, outline=barva)

    def izberi_barvo_povrsine(self):
        if self.stanje == OZNACENO:
            barva = askcolor()[-1]   # uporabimo komponento "color picker"
            if barva is not None:  # pritisnili smo OK
                if self.canvas.type(self.trenutni) != "line":
                    self.canvas.itemconfig(self.trenutni, fill=barva)                                               

    def izberi_debelino(self, name, index, mode):
        if self.stanje == OZNACENO:  # označenemu objektu spremenimo "prejšnjo" debelino!!!
            self.prejsnji_width=self.debelina.get()
            
##    Delo z datotekamo. Primer zapisa podatkov v datoteko:
##        
##    Oval(43,57,232,226,fill="",outline="#ff3232",width=2)
##    Pravokotnik(14,168,193,239,fill="#3bff73",outline="black",width=8)
##    Crta(127,29,137,179,fill="black",width=1)

    def dekodiraj(self, v):
        """Pomožna funkcija za branje vrstic iz datoteke."""
        try:
            pos = v.find("(")
            glava = v[:pos].strip()
            vrednosti = v[pos:].strip().strip("()").split(",")
            print(vrednosti)
            coords = [int(i) for i in vrednosti if "=" not in i]
            params = dict([[j.strip().strip('"') for j in i.split("=")] for i in vrednosti if "=" in i ])
            return glava, coords, params
        except:
            return None, None, None
        
    def odpri(self):
        ime = filedialog.askopenfilename()
        if ime == "":  # Pritisnili smo Cancel
            return
        with open(ime, encoding="utf8") as f:
            self.canvas.delete(ALL)
            for v in f:
                glava, coords, params = self.dekodiraj(v)
                print(v)
                print(glava, coords, params)
                if glava == "Crta":
                    print("Rišem črto")
                    self.canvas.create_line(*coords, **params)
                elif glava == "Oval":
                    self.canvas.create_oval(*coords, **params)
                elif glava == "Pravokotnik":
                    self.canvas.create_rectangle(*coords, **params)

    def kodiraj(self, id):
        """Pomožna funkcija za generiranje podatkov za shranjevanje v datoteko."""
        preslikava = {
            "line": "Crta",
            "oval": "Oval",
            "rectangle": "Pravokotnik"
            }
        tip = preslikava[self.canvas.type(id)]
        coords = [int(i) for i in self.canvas.coords(id)]
        lastnosti = {}
        lastnosti["fill"] = self.canvas.itemcget(id, "fill")
        lastnosti["width"] = int(float(self.canvas.itemcget(id, "width")))
        if tip != "Crta":
            lastnosti["outline"] = self.canvas.itemcget(id, "outline")
        print((tip, coords, lastnosti))
        return (tip, coords, lastnosti)
        
    def shrani(self):
        ime = filedialog.asksaveasfilename()
        if ime == "":  # Pritisnili smo Cancel
            return

        if self.stanje == OZNACENO:
            self.razveljavi_oznacitev()
            self.stanje = NEVTRALNO
            
        with open(ime, "wt", encoding="utf8") as f:
            for id in self.canvas.find_all():
                tip, coords, lastnosti = self.kodiraj(id)
                if tip == "Crta":
                    f.write(
                'Crta({0},{1},{2},{3},fill="{fill}",width={width})\n'.format(
                    *coords, **lastnosti))
                else:
                    f.write(
                '{0}({1},{2},{3},{4},fill="{fill}",outline="{outline}",width={width})\n'.format(
                    tip, *coords, **lastnosti))
                    

# Naredimo glavno okno
root = Tk()

aplikacija = Slikar(root)

# Kontrolo prepustimo glavnemu oknu. Funkcija mainloop neha
# delovati, ko okno zapremo.
root.mainloop()
