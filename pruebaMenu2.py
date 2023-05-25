import cv2
import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from opencv.fr.search.schemas import VerificationRequest
from openCvConfig import *
import cv2
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.textinput import TextInput
from pathlib import Path
from opencv.fr.persons.schemas import PersonBase
from opencv.fr.api_error import APIError

class MenuPrincipal(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical')

        spacer = BoxLayout(size_hint_y=(1))   
        layout.add_widget(spacer)

        solicitar_acceso_button = Button(text="Solicitar acceso")
        solicitar_acceso_button.bind(on_press=self.solicitar_acceso)
        solicitar_acceso_button.size_hint = (0.5, 0.2)
        solicitar_acceso_button.pos_hint = {'center_x': 0.5, 'center_y': 0.7}
        layout.add_widget(solicitar_acceso_button)

        spacer = BoxLayout(size_hint_y=(0.1))   
        layout.add_widget(spacer)

        ingresar_usuarios_button = Button(text="Crear usuario")
        ingresar_usuarios_button.bind(on_press=self.crear_usuario)
        ingresar_usuarios_button.size_hint = (0.5, 0.2)
        ingresar_usuarios_button.pos_hint = {'center_x': 0.5, 'center_y': 0.9}
        layout.add_widget(ingresar_usuarios_button)

        spacer = BoxLayout(size=(1, 1)) 
        layout.add_widget(spacer)

        self.add_widget(layout)

    def solicitar_acceso(self, instance):
       
        self.clear_widgets()
        self.add_widget(SolicitarAccesoLayout())
    
    def crear_usuario(self, instance):
        
        self.clear_widgets()
        self.add_widget(CrearUsuario())

########################################################## CLASS SOLICITARACCESO

class SolicitarAccesoLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical')

       
        volver_button = Button(text="Volver al menú")
        volver_button.size_hint = (1, 0.1)
        volver_button.pos_hint = {'x':0, 'y':0}
        volver_button.bind(on_press=self.volver_menu_principal)
        layout.add_widget(volver_button)

        
        self.image = Image()
        layout.add_widget(self.image)

       
        self.status_label = Label(text='Estado de acceso.', size_hint=(1, 0.1), height=30, size_hint_min_y=30, size_hint_max_y=30)   
        layout.add_widget(self.status_label)
        
        button = Button(text="Tomar foto")
        button.size_hint = (1, 0.1)
        button.pos_hint = {'x':0, 'y':0}
        button.bind(on_press=self.take_photo)
        layout.add_widget(button)

        self.capture = cv2.VideoCapture(0)

        def update_camera_preview(dt):
            ret, frame = self.capture.read()

            # Convierta el frame en una textura y muéstrelo en el widget de imagen de Kivy
            if ret:
                buf1 = cv2.flip(frame, 0)
                buf = buf1.tostring()
                texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                self.image.texture = texture
        
        Clock.schedule_interval(update_camera_preview, 1.0/30.0)

        self.add_widget(layout)
    
    def take_photo(self, instance):
        ret, frame = self.capture.read()
        cv2.imwrite('foto.jpg', frame)
        print("Foto tomada!")

        personas = sdk.persons.list()
        cantidadPersonas = personas.count 
        find = False 

        for i in range(cantidadPersonas):
            
            person_id = personas.persons[i].id
            verification_request = VerificationRequest(person_id, ["foto.jpg"])
                   
            try:
                pReq = sdk.search.verify(verification_request)
            except APIError as e:
                if  e.err_code == 'ERR_NO_FACES_FOUND':
                    self.status_label.text = "No se encontraron rostros en la foto. Vuelve a intentarlo."
                    return
                else:
                    raise e
            
            if pReq.score != 0 :
                find = True
                personaEncontrada = pReq.person.name
                self.status_label.text = "Acceso permitido, bienvenido " + personaEncontrada + "."
                break

        if not find : 
            self.status_label.text = "No se encontraron coincidencias."
            
    def volver_menu_principal(self, instance):

        self.clear_widgets()
        self.add_widget(MenuPrincipal())


########################################################## CLASS CREARUSUARIO

class CrearUsuario(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical')

        self.count = 3
        self.count_text = str(self.count)
        self.status_name = Label(text='')
        self.status_password= Label()

        volver_button = Button(text="Volver al menu")
        volver_button.size_hint = (1, 0.2)
        volver_button.pos_hint = {'x': 0, 'top': 1}
        volver_button.bind(on_press=self.volver_menu_principal)
        layout.add_widget(volver_button)

        spacer = BoxLayout(size=(1, 1))      
        layout.add_widget(spacer)

        self.passinput = TextInput(hint_text='Ingrese la contraseña', password = True, multiline=False, padding=(0, 15, 0, 0))
        self.passinput.bind(on_text_validate=self.verificar_password)
        self.passinput.size_hint = (0.5, 0.2)
        self.passinput.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        self.passinput.halign = 'center'
        self.passinput.valign = 'middle' 
        layout.add_widget(self.passinput)

        self.status_password = Label( text='Cantidad de intentos : ' + self.count_text + "." ,size_hint=(1, 0.1), height=30, size_hint_min_y=30, size_hint_max_y=30)
        self.status_password.size_hint =  (0.5, 0.2)
        self.status_password.pos_hint =  {'center_x': 0.5, 'center_y': 0.5}
        layout.add_widget(self.status_password) 

        spacer = BoxLayout(size=(1, 1))     
        layout.add_widget(spacer)

        self.add_widget(layout)

    def volver_menu_principal(self, instance):

        self.clear_widgets()
        self.add_widget(MenuPrincipal())

    def verificar_password(self, instance):

        password = instance.text
        if password == "password":

            self.clear_widgets()
            layout = BoxLayout(orientation='vertical')

            volver_button = Button(text="Volver al menu")
            volver_button.size_hint = (1, 0.1)
            volver_button.pos_hint = {'x':0, 'y':0}
            volver_button.bind(on_press=self.volver_menu_principal)
            layout.add_widget(volver_button)
                
            self.image = Image()
            layout.add_widget(self.image)

            button = Button(text="Tomar foto")
            button.size_hint = (1, 0.1)
            button.pos_hint = {'x':0, 'y':0}
            button.bind(on_press=self.take_photo)
            layout.add_widget(button)

            self.status_face_found = Label(text='', size_hint=(1, 0.1), height=30, size_hint_min_y=30, size_hint_max_y=30)   
            layout.add_widget(self.status_face_found)

            self.capture = cv2.VideoCapture(0)

            def update_camera_preview(dt):
                ret, frame = self.capture.read()

                # Convierta el frame en una textura y muéstrelo en el widget de imagen de Kivy
                if ret:
                    buf1 = cv2.flip(frame, 0)
                    buf = buf1.tostring()
                    texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                    texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                    self.image.texture = texture
            
            Clock.schedule_interval(update_camera_preview, 1.0/30.0)
            self.add_widget(layout)

        else:
            self.count -= 1
            self.count_text = str(self.count)
            print(self.count)
            self.status_password.text='Cantidad de intentos : ' + self.count_text
            self.passinput.text = ''
 
            if self.count == 0:
                self.clear_widgets()
                self.add_widget(MenuPrincipal())

            
            
    def take_photo(self, instance):
        
        ret, frame = self.capture.read()
        cv2.imwrite('nuevoUsuario.jpg', frame)
        print("Foto tomada!") 
        self.capture.release()

        self.clear_widgets()
        layout = BoxLayout(orientation='vertical')

        volver_button = Button(text="Volver al menu")
        volver_button.size_hint = (1, 0.2)
        volver_button.pos_hint = {'x': 0, 'top': 1}
        volver_button.bind(on_press=self.volver_menu_principal)
        layout.add_widget(volver_button)

        spacer = BoxLayout(size=(1, 1))      
        layout.add_widget(spacer)

        textinput = TextInput(hint_text="Ingrese su nombre", multiline=False, padding=(0, 15, 0, 0))
        textinput.bind(on_text_validate=self.verificar_nombre)
        textinput.size_hint = (0.5, 0.2)
        textinput.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        textinput.halign = 'center'
        textinput.valign = 'middle' 
        layout.add_widget(textinput)

        self.status_name = Label( size_hint=(1, 0.1), height=30, size_hint_min_y=30, size_hint_max_y=30)
        self.status_name.size_hint =  (0.5, 0.2)
        self.status_name.pos_hint =  {'center_x': 0.5, 'center_y': 0.5}
        layout.add_widget(self.status_name) 

        spacer = BoxLayout(size=(1, 1))      
        layout.add_widget(spacer)

        self.add_widget(layout)

    def verificar_nombre(self, instance):
         nombre = instance.text
         if len(nombre) >= 3:

            image_base_path = Path("./")
            image_path = image_base_path / "nuevoUsuario.jpg"
            person = PersonBase([image_path], name=nombre)
            person = sdk.persons.create(person)
            print("Usuario creado!") 

            self.clear_widgets()
            layout = BoxLayout(orientation='vertical')

            volver_button = Button(text="Volver al menu")
            volver_button.size_hint = (1, 0.1)
            volver_button.pos_hint = {'x':0, 'y':0}
            volver_button.bind(on_press=self.volver_menu_principal)
            layout.add_widget(volver_button)

            self.image = Image(source='./nuevoUsuario.jpg')
            layout.add_widget(self.image)

            self.user_label = Label(text='Usuario creado con exito, bienvenido ' + nombre + ".", size_hint=(1, 0.1), height=30, size_hint_min_y=30, size_hint_max_y=30)   
            layout.add_widget(self.user_label)

            self.add_widget(layout)

         elif len(nombre) == 0:
       
            self.status_name.text = "El nombre no puede estar vacio."
            print("Nombre error")
        
         elif len(nombre) < 3:
            self.status_name.text = "El nombre debe contener al menos 3 letras."
            print("Nombre error cantidad")

########################################################## CLASS MAIN
class MainApp(App):
    def build(self):
        # Crear ScreenManager
        screen_manager = ScreenManager()

        # Crear las pantallas y agregarlas al ScreenManager
        menu_screen = Screen(name='menu')
        menu_screen.add_widget(MenuPrincipal())
        screen_manager.add_widget(menu_screen)

        # Establecer la pantalla inicial
        screen_manager.current = 'menu'

        return screen_manager

if __name__ == '__main__':
    MainApp().run()

