# pip install kivy --pre --no-deps --index-url  https://kivy.org/downloads/simple/
# pip install "kivy[base]" --pre --extra-index-url https://kivy.org/downloads/simple/


import openai
import sys
import time
import os
from threading import Thread
from cryptography.fernet import Fernet

from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.app import App
from kivy.core.window import Window
from kivy.properties import partial
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label


def consultar_openai(prompt, pedido_viejo='', context=''):
    try:
        r = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'user', 'content': pedido_viejo},
                {'role': 'assistant', 'content': context},
                {'role': 'user', 'content': prompt}
            ], request_timeout=60
        )
        data = r["choices"][0]["message"]["content"]
    except Exception as err:
        data = str(err)
    return data


def consultar(pedido):
    global pedido_anterior
    global resp_anterior
    if 'cambio de tema' in pedido.lower():
        pedido_anterior = resp_anterior = ''
    respuesta = consultar_openai(pedido, pedido_anterior, resp_anterior)
    if respuesta.split() == '':
        msg = 'SIN RESPUESTA\n\n'
        return msg
    else:
        if 'that model is currently overloaded' not in respuesta.lower():
            resp_anterior = respuesta
        pedido_anterior = pedido
        return f'{respuesta}\n\n'


class ChatGPT(App):
    pedido = ''
    API_KEY = ''

    def __init__(self, **kwargs):
        super().__init__()
        self._keyboard = None
        self.respuesta = None
        self.label = None
        self.imagen = None
        self.button = None
        self.txt_input = None
        self.txt_response = None
        self.txtinput_apikey = None
        self.apikey_label = None

    def build(self):
        layout = BoxLayout(padding=10, orientation='vertical')

        layout_input = BoxLayout(size_hint_y=0.1)
        self.txt_input = TextInput()
        self.imagen = Image(source='walk.gif', size_hint_x=0.1)
        self.imagen.anim_delay = -1
        self.button = Button(text='->', size_hint_x=0.3)
        self.button.bind(on_release=self.button_clicked)
        layout.add_widget(layout_input)
        layout_input.add_widget(self.txt_input)
        layout_input.add_widget(self.imagen)
        layout_input.add_widget(self.button)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        self.label = Label(size_hint_y=0.05)
        self.txt_response = TextInput()
        layout.add_widget(self.label)
        layout.add_widget(self.txt_response)

        layout_footer = BoxLayout(size_hint_y=0.1)
        btn_salir = Button(text='Salir', size_hint_y=0.1)
        btn_salir.bind(on_release=self.salir)
        layout_footer.add_widget(btn_salir)
        btn_config = Button(text='Conf.', size_hint_x=0.2, size_hint_y=0.1)
        btn_config.bind(on_release=self.popup)
        layout_footer.add_widget(btn_config)
        layout.add_widget(layout_footer)

        self.respuesta = ''
        return layout

    def _keyboard_closed(self):
        print('My keyboard have been closed!')
        pass

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        print('on_key_down')
        if self.txt_input.focus and keycode[1] == 'enter':
            self.button_clicked(self.button)

    def button_clicked(self, instance):
        if self.API_KEY == '':
            self.popup(None)
        elif self.txt_input.text.strip() != '':
            self.pedido = self.txt_input.text
            self.txt_input.text = ''
            y = Thread(target=self.consulta)
            y.start()

    def consulta(self):
        x = Thread(target=self.contar)
        x.start()
        self.imagen.anim_delay = 0.01
        self.label.text = 'Conectando/Procesando...'
        self.button.disabled = True
        self.txt_input.disabled = True
        self.respuesta = ''
        self.respuesta = consultar(self.pedido)
        Clock.schedule_once(partial(self.txt_response.insert_text, '\nPedido: ' + self.pedido
                                    + '\n\nRespuesta:\n' + self.respuesta), -1)
        self.label.text = ''
        self.button.disabled = False
        self.txt_input.disabled = False
        self.imagen.anim_delay = -1
        SoundLoader.load('beep.wav').play()

    def contar(self):
        time.sleep(5)
        for cont in range(6, 121):
            time.sleep(1)
            if self.respuesta != '':
                self.label.text = ''
                break
            self.label.text = f'Conectando/Procesando...{cont}'

    @staticmethod
    def salir():
        sys.exit()

    def popup(self, instance):
        layout_popup = BoxLayout(orientation='vertical')

        popup_label = Label(text="OpenAI API-KEY")
        self.txtinput_apikey = TextInput()
        self.apikey_label = Label()
        save_button = Button(text='Guardar', size_hint_y=0.2)
        save_button.bind(on_release=self.save)
        close_button = Button(text="Atrás", size_hint_y=0.2)

        layout_popup.add_widget(popup_label)
        layout_popup.add_widget(self.txtinput_apikey)
        layout_popup.add_widget(save_button)
        layout_popup.add_widget(self.apikey_label)
        layout_popup.add_widget(close_button)

        popup = Popup(title='Configuración', content=layout_popup)
        popup.open()
        close_button.bind(on_press=popup.dismiss)

    def save(self, instance):
        self.API_KEY = self.txtinput_apikey.text.strip()
        openai.api_key = self.API_KEY

        fernets = Fernet(key)
        API_KEY_enc = fernets.encrypt(self.API_KEY.encode())
        with open('kajd', 'w') as fk:
            fk.write(str(API_KEY_enc))
        self.apikey_label.text = 'Grabada!'


# key = Fernet.generate_key() # tt
key = b'Vfj3B8_4K5bqFb6soBwUF46jkinB18m8IISBGmOWHPA='

if __name__ == '__main__':
    pedido_anterior = ''
    resp_anterior = ''

    if os.path.exists('kajd'):
        with open('kajd') as f:
            ChatGPT.API_KEY = f.readline().strip()
            ChatGPT.API_KEY = ChatGPT.API_KEY[2:len(ChatGPT.API_KEY)-1]
            fernet = Fernet(key)
            ChatGPT.API_KEY = fernet.decrypt(bytes(ChatGPT.API_KEY, 'utf-8')).decode()

    openai.api_key = ChatGPT.API_KEY

    ChatGPT().run()
