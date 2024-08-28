from tkinter import Toplevel, StringVar, Label, Entry, Button, CENTER, TOP
from tkinter import messagebox as msg
import os
import cv2
from matplotlib import pyplot as plt
from mtcnn import MTCNN
import database as db

# CONFIG
path = "C:/Users/Dilan/Desktop/Trabajo/Usuarios"
detector = MTCNN()

# GENERAL
def print_and_show(screen, text, success):
    ''' Prints and shows text '''
    color = color_success if success else color_error
    print(f"{color}{text}{color_normal}")
    if success:
        screen.destroy()
        msg.showinfo(message=text, title="¡Éxito!")
    else:
        Label(screen, text=text, fg="red", bg=color_background, font=(font_label, 12)).pack()

def configure_screen(screen, text):
    ''' Configure global styles '''
    screen.title(text)
    screen.geometry(size_screen)
    screen.configure(bg=color_background)
    Label(screen, text=f"¡{text}!", fg=color_white, bg=color_black, font=(font_label, 18), width="500", height="2").pack()

def setup_credentials(screen, var, capture_command):
    ''' Configuration of user input '''
    Label(screen, text="Usuario:", fg=color_white, bg=color_background, font=(font_label, 12)).pack()
    entry = Entry(screen, textvariable=var, justify=CENTER, font=(font_label, 12))
    entry.focus_force()
    entry.pack(side=TOP, ipadx=30, ipady=6)
    Button(screen, text="Capturar rostro", fg=color_white, bg=color_black_btn, activebackground=color_background, borderwidth=0, font=(font_label, 14), height="2", width="40", command=capture_command).pack()
    return entry

def process_and_save_face(img_path, faces):
    ''' Process and save detected face '''
    img_data = plt.imread(img_path)
    for face in faces:
        x1, y1, ancho, alto = face["box"]
        cropped_face = cv2.resize(img_data[y1:y1+alto, x1:x1+ancho], (150, 200), interpolation=cv2.INTER_CUBIC)
        cv2.imwrite(img_path, cropped_face)

# REGISTER #
def register_user_in_db(img):
    ''' Register the user in the database '''
    username = os.path.splitext(img)[0]
    res_bd = db.registerUser(username, os.path.join(path, img))
    print_and_show(screen1, "¡Éxito! Se ha registrado correctamente" if res_bd["affected"] else "¡Error! No se ha registrado correctamente", res_bd["affected"])
    os.remove(img)

def capture_and_register():
    ''' Capture image and register face '''
    img = capture_image(user1.get())
    process_and_save_face(img, detector.detect_faces(plt.imread(img)))
    register_user_in_db(img)
    user_entry1.delete(0, END)

def register():
    ''' Initialize registration screen '''
    global user1, user_entry1, screen1
    screen1 = Toplevel(root)
    user1 = StringVar()
    configure_screen(screen1, txt_register)
    user_entry1 = setup_credentials(screen1, user1, capture_and_register)

# LOGIN #
def compare_faces(img1, img2):
    ''' Compare two faces and return similarity score '''
    orb = cv2.ORB_create()
    kp1, desc1 = orb.detectAndCompute(img1, None)
    kp2, desc2 = orb.detectAndCompute(img2, None)
    if desc1 is None or desc2 is None:
        return 0
    matches = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(desc1, desc2)
    return len([m for m in matches if m.distance < 70]) / len(matches) if matches else 0

def capture_and_login():
    ''' Capture image and attempt login '''
    img = capture_image(f"{user2.get()}_login")
    process_and_save_face(img, detector.detect_faces(plt.imread(img)))

    user_img_path = os.path.join(path, f"{user2.get()}.jpg")
    if db.getUser(user2.get(), user_img_path)["affected"] and os.path.exists(user_img_path):
        comp = compare_faces(cv2.imread(user_img_path, 0), cv2.imread(img, 0))
        login_success = comp >= 0.94
        print_and_show(screen2, f"Bienvenido, {user2.get()}" if login_success else "¡Error! Incompatibilidad de datos", login_success)
        os.remove(user_img_path)
    else:
        print_and_show(screen2, "¡Error! Usuario no encontrado", 0)
    os.remove(img)
    user_entry2.delete(0, END)

def login():
    ''' Initialize login screen '''
    global screen2, user2, user_entry2
    screen2 = Toplevel(root)
    user2 = StringVar()
    configure_screen(screen2, txt_login)
    user_entry2 = setup_credentials(screen2, user2, capture_and_login)

def capture_image(filename):
    ''' Capture an image using the webcam '''
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    img_path = f"{filename}.jpg"
    cv2.imwrite(img_path, frame)
    cap.release()
    cv2.destroyAllWindows()
    return img_path
