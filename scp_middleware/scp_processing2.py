import numpy as np
import cv2
import requests
from matplotlib import pyplot as plt
import os
from scp_gui import UI
import string
from scp_parser import SCP_Parser 

green_color = (0,255,255)
red_color = (0,255,0)
blue_color = (255,0,0)

aspect_ratio = 1.8
rough_range_width = 60000
rough_range_height = 6000


def process_plate(data,ip):
    #path_pic = "lisi.jpg"
    #Cargamos la foto enviada por el raspberry pi
    #image = cv2.imread(path_pic,1)
    #show_img(cv2,image,'original')
    #preprocessed_image = image
    image = cv2.imdecode(data, 1)
    preprocessed_image = cv2.imdecode(data, 1)
   # cv2.imwrite('pa.jpg',image)

    #se detecta la region donde se encuentra la placa en la imagen
    #convertimos la imagen a escala de grices
    escala_grices = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    show_img('gris',escala_grices)

    #Se remueve un poco el ruido de la imagen(osea los ejes verticales)
    blur = cv2.GaussianBlur(escala_grices,(5,5),0)
    show_img('ruido',blur)

    #Buscamos el gradiente
    grad = cv2.Sobel(blur, cv2.CV_8U, 1, 0, ksize=3)
    show_img('gradiente',grad)

    #se aplica un filtro para combertir la imagen a una imagen binaria(0 y 1)
    _,umbral = cv2.threshold(grad, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    show_img('threshold',umbral)

    #Operacion Morfologica para quitar los espacios en blanco entre cada linea de borde vertical
    Estructura = cv2.getStructuringElement(cv2.MORPH_RECT,(23,4))
    morfo = cv2.morphologyEx(umbral, cv2.MORPH_CLOSE, Estructura)
    show_img('Morfologica',morfo)
    #se obtuviero las posibles regiones donde se encuetra la placa


    contours,_ = cv2.findContours(morfo, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    draw_contours(image, contours)
    show_img("candidatas",image)

    try:
        list_verified_plates = verify_plate(preprocessed_image, image, contours)
    except:
        print "Not plate found"
        return False

    show_img('no pro',preprocessed_image)
    show_img('verified',image)
    #cv2.imwrite('verificada.jpg',image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    get_plate = ""
    index = 0
    
    for plate in list_verified_plates:
        #tess = os.popen('tesseract placabien'+str(index)+'.jpg output'+str(index),"r").read()
        tess = os.popen('tesseract image_processed0.jpg cheooo').read
        #cat = os.popen('cat output'+str(index)+'.txt',"r").read()
        cat = os.popen('cat cheooo.txt',"r").read()
        print cat
        get_plate = cat.strip();
        index+=1
    if len(get_plate) > 1:
        plate = get_plate
    else:
        plate = ""
    
    #tess = os.popen('tesseract image_processed0.jpg cheooo').read()
    #cat = os.popen('cat cheooo.txt',"r").read()
    #print cat
    #plat = cat.replace("-","")
    #print plat
    print ip
    #plate = plat.strip();
    #plate = "L8989"
    plate = cat.strip();
    parsed_plate = SCP_Parser(plate).parse_plate()

    #cam = 1
    print "request = Placa: " + parsed_plate + " Ip : " + str(ip)
    request = requests.get("http://scpweb.herokuapp.com/api/authorize_plate?plate="+parsed_plate+"&cam=192.168.0.41")
    print request.json()
    response = request.json()
    #f = open('output.txt', 'r+')
    #f.truncate()
    tess = None 
    cat = None
    
    #ui = UI("pa.jpg", "verificada.jpg", "image_processed.jpg","192.168.0.40")


    #return (response['message'] !=  "Vehicle not found" and response['message'] != "Cam not found" and response['message'] != "Visitor not found" and response['message'])
    return (response['message'] == "Vehicle Found")
#visualizar las regiones que ha encontrado como candidatas 
def draw_contours(image, contours):
    for cnt in contours:
        rectangle = cv2.minAreaRect(cnt)
        points = cv2.cv.BoxPoints(rectangle)
        points = np.int0(points)  
        cv2.drawContours(image, [points], 0, green_color, 2)

#validate a contour. We validate by estimating a rough area and aspect ratio check.
def verified_contour(contour):
    rectangle = cv2.minAreaRect(contour)
    box = cv2.cv.BoxPoints(rectangle)
    box = np.int0(box)  
    output = False
    width = (rectangle[1][0])
    height = (rectangle[1][1])
    if ((width != 0) & (height != 0)):
        if (((height / width > aspect_ratio) & (height > width)) | ((width / height> aspect_ratio) & (width > height))):
            if((height * width < rough_range_width) & (height * width > rough_range_height)):
                output=True
    return output

def save_verified_plate(plate_image, width, height,id):
    #show_img("Verified Plate",cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY) )
    #cv2.imwrite("image_processed.jpg", cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY) )
    show_img("Verified Plate",plate_image)
    cv2.imwrite("image_processed"+str(id)+".jpg",plate_image)	
    show_img("fondo blanco",verified_plate_bg_white(plate_image))

def verified_plate_bg_white(plate_image):
    plate_image[np.where((plate_image==[0,0,255]).all(axis=2))] = [255,255,255]

def is_perfect_rectangle(width,height):
    div = round(width/height,1)
    return (div == 2 or div == (2.1) or (div-1) == (2.1) )

def change_bg_plate(plate_image,id):
    n = 2    # Number of levels of quantization
    indices = np.arange(0,256)   # List of all colors 
    divider = np.linspace(0,255,n+1)[1] # we get a divider
    quantiz = np.int0(np.linspace(0,255,n)) # we get quantization colors
    color_levels = np.clip(np.int0(indices/divider),0,n-1) # color levels 0,1,2..
    palette = quantiz[color_levels] # Creating the palette
    im2 = palette[plate_image]  # Applying palette on image
    im2 = cv2.convertScaleAbs(im2) # Converting image back to uint8
    #RGB
    #im2[np.where((im2 == [0,0,255]).all(axis = 2))] = [255,255,255]#Blue
    #im2[np.where((im2 == [0,255,0]).all(axis = 2))] = [255,255,255]#Green
    #im2[np.where((im2 == [255,0,0]).all(axis = 2))] = [255,255,255]#Red
    #im2[np.where((im2 == [0,255,255]).all(axis = 2))] = [255,255,255]#Light Blue
    #im2[np.where((im2 == [255,255,0]).all(axis = 2))] = [255,255,255]#Yellow
    #im2[np.where((im2 == [255,0,255]).all(axis = 2))] = [255,255,255]#Yellow
    #show_img("Placa bien",im2)
    cv2.imwrite("placabien"+str(id)+".jpg",im2)  



def verify_plate(image, image_processed, contours):
    verified_plates = []
    for contour in contours:
        if verified_contour(contour):
            rectangle = cv2.minAreaRect(contour)
            box = cv2.cv.BoxPoints(rectangle)
            box = np.int0(box)
            x           =   int(rectangle[0][0])
            y           =   int(rectangle[0][1])+8
            width       =   int(rectangle[1][0])
            height      =   int(rectangle[1][1])
            centre      =   (x,y)
            cv2.drawContours(image_processed, [box], 0, red_color,2)
            cro = image[(y-((height/4))):y+((height/4)+10), (x-((width/2))+10):x+((width/2)+5)]
            print   "[X: " + str(x) + "] " + "[Y: " + str(y) + "] " + "[W: " + str(width) + "] " + "[H: " + str(height) + "]\n "
            if is_perfect_rectangle(width,height):
                #cropped_image = cv2.getRectSubPix(image_processed, (width, height), centre)
                verified_plates.append(cro)
    index = 0
    for plate in verified_plates:
        save_verified_plate(cro, width, height, index)
        #change_bg_plate(cro,index)
        index+=1
    return verified_plates

def show_with_plt(img):
    plt.imshow(img)
    plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
    plt.show()

def show_img(title, img):
    cv2.imshow(title,img)
