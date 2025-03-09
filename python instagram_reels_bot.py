from instagrapi import Client
import pandas as pd
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from crewai import Agent, Task, Crew

# Configuração do Instagram
def login_instagram(username, password):
    """Realiza login no Instagram e retorna o cliente autenticado."""
    cl = Client()
    cl.login(username, password)
    return cl

# Função para postar um Reels
def post_reel(username, password, video_path, caption, hashtags, cover_image, tags):
    """Posta um vídeo Reels no Instagram com capa, hashtags e tags para nicho."""
    try:
        cl = login_instagram(username, password)

        full_caption = f"{caption}\n\n{hashtags}"  # Adiciona hashtags à legenda
        extra_data = {"usertags": tags.split(",")} if tags else {}  # Converte tags para lista

        cl.clip_upload(
            video_path, 
            caption=full_caption, 
            thumbnail=cover_image if cover_image else None, 
            extra_data=extra_data
        )
        
        print(f"✅ Reels postado com sucesso: {video_path}")
    
    except Exception as e:
        print(f"❌ Erro ao postar {video_path}: {str(e)}")

# Classe do Agente de Postagem
class InstagramAgent:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.client = login_instagram(username, password)

    def post_video(self, video_path, caption, hashtags, cover_image, tags):
        post_reel(self.username, self.password, video_path, caption, hashtags, cover_image, tags)

# Função para carregar posts do CSV
def carregar_posts(csv_file):
    """Carrega posts do CSV e formata os dados corretamente."""
    df = pd.read_csv(csv_file)
    posts = []
    for _, row in df.iterrows():
        posts.append({
            "username": row["username"],
            "password": row["password"],
            "video_path": row["video_path"],
            "caption": row["caption"],
            "hashtags": row["hashtags"],
            "cover_image": row["cover_image"] if "cover_image" in row else None,
            "tags": row["tags"] if "tags" in row else "",
            "post_time": datetime.strptime(row["post_time"], "%Y-%m-%d %H:%M:%S")
        })
    return posts

# Agendamento dos posts
def agendar_posts(posts):
    """Agenda os posts para serem publicados na hora certa."""
    scheduler = BackgroundScheduler()
    
    for post in posts:
        scheduler.add_job(
            post_reel, 
            "date", 
            run_date=post["post_time"],
            args=[post["username"], post["password"], post["video_path"], post["caption"], post["hashtags"], post["cover_image"], post["tags"]]
        )
    
    scheduler.start()

# Criar CrewAI
def iniciar_crew(posts):
    """Cria agentes do CrewAI para gerenciar as postagens."""
    agentes = []
    for post in posts:
        agente = Agent(
            role="Instagram Manager",
            goal="Publicar Reels no Instagram no horário programado",
            backstory="Um agente especializado em gerenciar posts no Instagram.",
            allow_delegation=False,
            verbose=True
        )
        agentes.append(agente)
    
    tarefas = [Task(description="Postar o vídeo no Instagram", agent=agente) for agente in agentes]
    
    crew = Crew(agents=agentes, tasks=tarefas)
    crew.kickoff()
    print("👥 CrewAI iniciado!")

# Executar o script
if __name__ == "__main__":
    posts = carregar_posts("reels_posts.csv")
    iniciar_crew(posts)
    agendar_posts(posts)
