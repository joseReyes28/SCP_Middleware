from Tkinter import *
from ttk import *
from Tkinter import Tk, Text, BOTH, W, N, E, S


from PIL import Image, ImageTk


class UI:
    """docstring for UI"""
    def __init__(self, original_image_path, processed_image_path, verified_plate_image_path, ip):
        self.ip = ip
        self.root = Tk()
        self.frame = Frame(self.root)

        original_file = Image.open(original_image_path).resize((800, 500),Image.ANTIALIAS)
        self.original_image = ImageTk.PhotoImage(original_file)

        processed_img = Image.open(processed_image_path).resize((800, 500),Image.ANTIALIAS)
        self.processed_image = ImageTk.PhotoImage(processed_img)

        verified_plate_img = Image.open(verified_plate_image_path).resize((200, 100),Image.ANTIALIAS)
        self.verified_plate_image = ImageTk.PhotoImage(verified_plate_img)

        self.w = self.root.winfo_screenwidth()
        self.h = self.root.winfo_screenheight()

        self.create_frame()

        self.root.title("SCP MiddleWare GUI")
        self.root.geometry("%dx%d+0+0" % (900, self.h-100)) 
        self.root.mainloop()  


    def create_frame(self):
                
        frame1 = Frame(self.root,width=500, height=500)
        frame2 = Frame(self.root,width=800, height=576)
        frame1.pack()
        frame2.pack( fill=BOTH, expand=1)
        frame1.place(x=0,y=0)
        frame2.place(x=0,y=560)

        note = Notebook(frame1)
        frame1.style = Style()
        frame1.style.theme_use("clam")
        frame2.style = Style()
        frame2.style.theme_use("clam")

        tab1 = Frame(note)
        tab2 = Frame(note)
        tab3 = Frame(note)

        Button(tab1, text='Exit').pack(padx=self.w-120, pady=self.h-100)
        note.add(tab1, text = "Imagen Recibida",compound=TOP)
        note.add(tab2, text = "Imagen Procesada")
        note.add(tab3, text = "Placa Procesada")

        label_original_image = Label(tab1, image=self.original_image)
        label_original_image.place(x=5, y=20)   
        label_original_image = Label(frame2,foreground="blue",text="Cam: "+self.ip, font=("Times",16),width=20)
        label_original_image.pack()


        label_processed_image = Label(tab2, image=self.processed_image)
        label_processed_image.place(x=5, y=20)
        label_processed_image = Label(frame2, width=20)
        label_processed_image.pack()

        label_plate_image = Label(tab3, image=self.verified_plate_image)
        label_plate_image.place(x=350, y=200)
        label_plate_image = Label(frame2, width=20)
        label_plate_image.pack()


        cbtn = Button(frame2, text="Cerrar",width=49)
        cbtn['command'] = self.btn_close
        cbtn.pack(side=LEFT)

        obtn = Button(frame2, text="Apertura Emergencia",width=49)
        obtn['command'] = self.btn_open_signal
        obtn.pack(side=LEFT)
        note.pack()
        
    
    def btn_close(self):
        self.root.quit()

    def btn_open_signal(self):
        print True
        return True

 
img = cv2.imread("pa.jpg",1)
img2 = cv2.imread("verificada.png",1)
img3 = cv2.imread("recorte.png",1)


ui = UI("pa.jpg", "verificada.png", "recorte.png","192.168.0.40")
