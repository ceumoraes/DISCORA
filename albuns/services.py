import os
import random
import string
import threading
from pathlib import Path
import requests
from django.conf import settings
from django.db import connections, transaction
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from .models import Album

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / 'core' / '.env')

class SpotifyService:
    def __init__(self):
        self.client_id = getattr(settings, 'SPOTIFYAPI_CLIENT_ID', os.getenv('SPOTIFYAPI_CLIENT_ID'))
        self.client_secret = getattr(settings, 'SPOTIFYAPI_CLIENT_SECRET', os.getenv('SPOTIFYAPI_CLIENT_SECRET'))
        self.sp = None

    def _conectar(self):
        if not self.sp:
            auth_manager = SpotifyClientCredentials(client_id=self.client_id, client_secret=self.client_secret)
            self.sp = spotipy.Spotify(auth_manager=auth_manager)
        return self.sp

    def buscar_albuns(self, termo_busca, limite=30):
        try:
            sp = self._conectar()

            dados = sp.search(str(termo_busca), int(limite), 0, 'album')

            if not dados or "albums" not in dados:
                return []

            return [{
                "id_spotify": item["id"],
                "nome": item["name"],
                "artista": item["artists"][0]['name'] if item["artists"] else 'Artista Desconhecido',
                "url_capa": item["images"][0]['url'] if item["images"] else None,
                "ano_lancamento": int(item["release_date"].split("-")[0]) if item.get("release_date") and
                                                                             item["release_date"].split("-")[
                                                                                 0].isdigit() else None
            } for item in dados["albums"]["items"]]
        except Exception as e:
            print(f"[SpotifyService] Erro na busca: {e}")
            return []


class LastFMService:
    def __init__(self):
        self.api_key = os.getenv('LASTFMAPI_API_KEY')
        self.base_url = "http://ws.audioscrobbler.com/2.0/"

    def buscar_albuns(self, termo_busca, limite=30):
        if not self.api_key:
            return []
        termo_limpo = termo_busca.replace('genre:', '').replace('year:', '').replace('"', '').replace('%', '')
        try:
            resposta = requests.get(
                self.base_url,
                params={'method': 'album.search', 'album': termo_limpo, 'api_key': self.api_key, 'format': 'json',
                        'limit': limite},
                timeout=3
            )
            if resposta.status_code == 200:
                lista_albuns = resposta.json().get('results', {}).get('albummatches', {}).get('album', [])
                resultados = []
                for album in lista_albuns:
                    imagens = album.get('image', [])
                    url_capa = next((img.get('#text') for img in reversed(imagens) if img.get('#text')), "")
                    if not url_capa:
                        continue

                    resultados.append({
                        'id_spotify': f"lastfm_{album.get('artist')}_{album.get('name')}".replace(" ", "_").lower(),
                        'nome': album.get('name', 'Álbum Desconhecido'),
                        'artista': album.get('artist', 'Artista Desconhecido'),
                        'url_capa': url_capa,
                        'ano_lancamento': None
                    })
                return resultados
            return []
        except Exception as e:
            print(f"[LastFMService] Erro na busca: {e}")
            return []


class OrquestradorAlbunsService:
    """Garantir estoque de dados."""

    @staticmethod
    def verificar_e_reabastecer_estoque():
        estrategias = ['genero', 'ano', 'curinga']
        escolha = random.choice(estrategias)

        if escolha == 'genero':
            lista = ['rock', 'jazz', 'blues', 'pop', 'indie', 'metal', 'rap', 'mpb', 'samba']
            termo_sorteado = random.choice(lista)
            filtro_banco = Album.objects.filter(termo_busca=termo_sorteado)
            query_api = f'genre:"{termo_sorteado}"'
        elif escolha == 'ano':
            lista = ['1970-1979', '1980-1989', '1990-1999', '2000-2009', '2010-2019', '2020-2026']
            termo_sorteado = random.choice(lista)
            filtro_banco = Album.objects.filter(termo_busca=termo_sorteado)
            query_api = f'year:{termo_sorteado}'
        else:
            letra = random.choice(string.ascii_lowercase)
            termo_sorteado = f'curinga_{letra}'
            filtro_banco = Album.objects.filter(titulo__icontains=letra)
            query_api = f"{letra}*"

        if filtro_banco.count() < 25:
            print(
                f"[Background Thread] Estoque baixo para '{termo_sorteado}' ({filtro_banco.count()}). Alimentando o banco...")

            connections.close_all()

            threading.Thread(
                target=OrquestradorAlbunsService.garantir_abastecimento_online,
                args=(query_api, termo_sorteado),
                daemon=True
            ).start()

    @staticmethod
    def garantir_abastecimento_online(query_api, termo_busca):
        origem = 'spotify'
        spotify = SpotifyService()

        resultados = spotify.buscar_albuns(query_api, 30)

        if not resultados:
            print("[Contingência Ativa] Spotify falhou ou limitou acesso. Acionando Last.fm...")
            try:
                lastfm = LastFMService()
                resultados = lastfm.buscar_albuns(termo_busca=query_api, limite=30)
                origem = 'lastfm'
            except Exception as lf_err:
                print(f"[Contingência] Erro crítico ao chamar Last.fm: {lf_err}")
                return

        if not resultados:
            print("[Abastecimento] Nenhuma das APIs retornou dados para o termo.")
            return

        novos_salvos = 0
        try:
            with transaction.atomic():
                for item in resultados:
                    id_chave = item.get('id_spotify')
                    url_img = item.get('url_capa')
                    if not id_chave or not url_img:
                        continue

                    ano_salvar = item.get('ano_lancamento')
                    if not ano_salvar and '-' in termo_busca:
                        ano_inicio = termo_busca.split('-')[0]
                        if ano_inicio.isdigit():
                            ano_salvar = int(ano_inicio)

                    campos_db = {
                        'titulo': item['nome'],
                        'artista': item['artista'],
                        'url_capa': url_img,
                        'termo_busca': termo_busca,
                        'ano_lancamento': ano_salvar
                    }

                    if origem == 'spotify':
                        campos_db['id_lastfm'] = None
                        _, created = Album.objects.get_or_create(id_spotify=id_chave, defaults=campos_db)
                    else:
                        campos_db['id_spotify'] = None
                        _, created = Album.objects.get_or_create(id_lastfm=id_chave, defaults=campos_db)

                    if created:
                        novos_salvos += 1

            if novos_salvos > 0:
                print(f"[Abastecimento] Sucesso! +{novos_salvos} álbuns salvos vindos do {origem.upper()}.")
        except Exception as db_err:
            print(f"[Abastecimento] Falha de concorrência ao gravar no banco: {db_err}")
        finally:
            connections.close_all()


class VitrineService:
    """RESPONSABILIDADE UNICA: Gerar a randomização pura dos discos para a interface."""


    @staticmethod
    def obter_lote_aleatorio_home():
        OrquestradorAlbunsService.verificar_e_reabastecer_estoque()

        albuns_sorteados = Album.objects.all().order_by('?')[:20]

        return [{
            'id_spotify': a.id_spotify if a.id_spotify else a.id_lastfm,
            'titulo': a.titulo,
            'nome': a.titulo,
            'artista': a.artista,
            'url_capa': a.url_capa
        } for a in albuns_sorteados]