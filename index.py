import sys
import os
import platform
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox, filedialog
from yt_dlp import YoutubeDL



def resource_path(relative_path):
    
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


ffmpeg_path = resource_path("assets/ffmpeg.exe")
ffprobe_path = resource_path("assets/ffprobe.exe")




def get_ffmpeg_folder():
    sistema = platform.system()

    # Caminhos embutidos (dentro do executável/pasta assets)
    ffmpeg_embutido = resource_path("assets/ffmpeg.exe" if sistema == "Windows" else "assets/ffmpeg")
    ffprobe_embutido = resource_path("assets/ffprobe.exe" if sistema == "Windows" else "assets/ffprobe")

    if os.path.isfile(ffmpeg_embutido) and os.path.isfile(ffprobe_embutido):
        return os.path.dirname(ffmpeg_embutido)

    # Windows: tenta pasta externa padrão
    if sistema == "Windows":
        pasta_externa = r"C:\ffmpeg"
        ffmpeg_externo = os.path.join(pasta_externa, "ffmpeg.exe")
        ffprobe_externo = os.path.join(pasta_externa, "ffprobe.exe")
        if os.path.isfile(ffmpeg_externo) and os.path.isfile(ffprobe_externo):
            return pasta_externa

    # Linux/macOS ou fallback: confiar no PATH
    return None


def escolher_caminho(entry_var):
    caminho = filedialog.asksaveasfilename(
        title="Escolha onde salvar o MP3",
        defaultextension=".mp3",
        filetypes=[("MP3 files", "*.mp3")]
    )
    if caminho:
        entry_var.set(caminho)



def abrir_arquivo (path) :
    try:
        if platform.system() == 'Windows':
            os.startfile(path)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.run(['open', path])
        elif platform.system() == 'Linux':
            subprocess.run(['xdg-open', path])
        else:
            raise Exception("Sistema operacional não suportado")
    except Exception as e:
        print(f"Erro ao tentar abrir o arquivo: {e}")




def baixar_audio(url, caminho_completo, status_label, limpar_campos):
    try:
        status_label.config(text="🔄 Baixando...", fg="blue")
        
        if not url or not caminho_completo:
            raise Exception("URL ou caminho de saída inválido")

        caminho_sem_ext = os.path.splitext(caminho_completo)[0]

        sistema = platform.system()

        if sistema == 'Windows':
            ffmpeg_dir = os.path.dirname(ffmpeg_path)
        else:
            ffmpeg_dir = None  # Confia nos binários do sistema

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': caminho_sem_ext + '.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': False,
            'noplaylist': True
        }

        if ffmpeg_dir:
            ydl_opts['ffmpeg_location'] = ffmpeg_dir

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        caminho_mp3 = caminho_sem_ext + '.mp3'

        status_label.config(text="✅ Download finalizado!", fg="green")

        if os.path.exists(caminho_mp3):
            abrir_arquivo(caminho_mp3)

        limpar_campos()

    except Exception as e:
        status_label.config(text=f"❌ Erro: {e}", fg="red")




def start_download(entry_url, caminho_saida, status_label):
    url = entry_url.get()
    caminho = caminho_saida.get()
    if not url or not caminho:
        status_label.config(text="❌ Preencha todos os campos", fg="red")
        return
    
    def limpar_campos():
        entry_url.delete(0, tk.END)
        caminho_saida.set("")


    threading.Thread(target=baixar_audio,  args=(url, caminho, status_label, limpar_campos)).start()





root = tk.Tk()
root.title("YouTube para MP3")
root.geometry("500x220")
root.resizable(False, False)

tk.Label(root, text="URL do vídeo:", font=("Arial", 12)).pack(pady=5)
url_entry = tk.Entry(root, width=60, font=("Arial", 11))
url_entry.pack(pady=5)

tk.Label(root, text="Salvar como:", font=("Arial", 12)).pack()
frame_caminho = tk.Frame(root)
frame_caminho.pack(pady=5)
caminho_saida = tk.StringVar()
tk.Entry(frame_caminho, textvariable=caminho_saida, width=45, font=("Arial", 10)).pack(side=tk.LEFT)
tk.Button(frame_caminho, text="Escolher", command=lambda: escolher_caminho(caminho_saida)).pack(side=tk.LEFT, padx=5)

status_label = tk.Label(root, text="", font=("Arial", 11))
status_label.pack(pady=5)

tk.Button(root, text="Baixar MP3", font=("Arial", 12, "bold"),
          command=lambda: start_download(url_entry, caminho_saida, status_label)).pack(pady=5)

root.mainloop()