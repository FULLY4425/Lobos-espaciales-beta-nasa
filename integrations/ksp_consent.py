"""Session-only upload consent. Closing/unavailable dialogs always deny."""
import sys
import threading
from datetime import datetime,timezone

CONSENT_VERSION='ksp-upload-consent-v1'

class UploadConsent:
    def __init__(self,project,include_history=False):
        self.project=project;self.include_history=include_history;self.allowed=False;self.decided_at=None;self.reason='not-requested';self.lock=threading.Lock()

    def decide(self,allowed,reason='user-choice'):
        with self.lock:
            self.allowed=allowed is True;self.reason=reason;self.decided_at=datetime.now(timezone.utc).isoformat()
        return self.allowed

    def permits(self,project):
        with self.lock:return self.allowed and self.project==project

    def status(self):
        with self.lock:return dict(version=CONSENT_VERSION,allowed=self.allowed,project=self.project,includeHistory=self.include_history,decidedAt=self.decided_at,reason=self.reason)

    def request(self,ask=None):
        history='También se incluirán sesiones anteriores de este usuario porque se activó --cloud-include-history.' if self.include_history else 'Solo esta sesión y reintentos de sesiones anteriores autorizadas del mismo usuario/proyecto.'
        text=(f'¿Permites enviar los datos de esta prueba a Lobos Espaciales?\n\nDestino: {self.project}\n\n'
              'Se compartirán datos de vuelo/órbita, CPU, RAM, disco, rendimiento de KSP, rutas, errores y registros del conector. '
              'KSP.log y Player.log solo si elegiste sus rutas; pueden contener texto personal. No se recopilan capturas, teclas, contraseñas ni archivos personales.\n\n'
              f'{history}\n\nSi no permites, el mapa sigue funcionando y los registros quedan únicamente en tu PC. '
              'Puedes retirar el permiso desde el mapa. Lo ya enviado no se borra y una transferencia iniciada podría terminar.\n\n'
              'También necesitas iniciar sesión con un usuario autorizado; este aviso no concede acceso al servidor.')
        try:
            answer=(ask or ask_desktop)(text)
            return self.decide(answer is True,'dialog-unavailable' if answer is None else 'user-choice')
        except Exception:return self.decide(False,'dialog-unavailable')


def ask_desktop(text):
    """A regular desktop window, not UAC and not a KSP mod."""
    root=None
    try:
        import tkinter as tk
        from tkinter import ttk
        root=tk.Tk();root.title('Lobos Espaciales · Permiso para compartir');root.resizable(False,False)
        answer={'allowed':False}
        def finish(allowed=False):answer['allowed']=allowed;root.destroy()
        root.protocol('WM_DELETE_WINDOW',finish)
        frame=ttk.Frame(root,padding=22);frame.pack(fill='both',expand=True)
        ttk.Label(frame,text=text,wraplength=590,justify='left').pack(fill='x')
        buttons=ttk.Frame(frame);buttons.pack(fill='x',pady=(20,0))
        ttk.Button(buttons,text='Permitir esta sesión',command=lambda:finish(True)).pack(side='left',padx=(0,15))
        deny=ttk.Button(buttons,text='No permitir',command=finish);deny.pack(side='right');deny.focus_set()
        root.bind('<Escape>',lambda e:finish());root.bind('<Return>',lambda e:finish())
        root.update_idletasks();root.attributes('-topmost',True);root.after(1500,lambda:root.attributes('-topmost',False));root.mainloop()
        return answer['allowed']
    except Exception:
        if root is not None:
            try:root.destroy()
            except Exception:pass
        if not sys.stdin.isatty():return None
        print(text)
        return input('\nEscribe PERMITIR para compartir esta sesión; Enter = no permitir: ').strip()=='PERMITIR'
