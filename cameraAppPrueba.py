from opencv.fr.search.schemas import VerificationRequest
from openCvConfig import *
import cv2
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.label import Label

class CameraApp(App): 

    def build(self):
        layout = BoxLayout(orientation='vertical')

        # Crear un botón para tomar una foto
        button = Button(text="Tomar foto")
        button.size_hint = (1, 0.1)
        button.pos_hint = {'x':0, 'y':0}
        button.bind(on_press=self.take_photo)
        layout.add_widget(button)

        # Cree un widget de imagen para mostrar la vista previa de la cámara
        self.image = Image()
        layout.add_widget(self.image)

        # Abrir la camara
        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update, 1.0/30.0)

        return layout

    def update(self, dt):
        ret, frame = self.capture.read()

        # Convierta el frame en una textura y muéstrelo en el widget de imagen de Kivy
        if ret:
            buf1 = cv2.flip(frame, 0)
            buf = buf1.tostring()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.image.texture = texture

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
            pReq = sdk.search.verify(verification_request)
         
            if pReq.score != 0 :
                find = True
                personaEncontrada = pReq.person.name
                break

        if find : 
            print("Acceso permitido, bienvenido", personaEncontrada)
        else :
            print("No se encontraron coincidencias")


if __name__ == '__main__':
    CameraApp().run()