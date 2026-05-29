import os
import random
import string
import threading
from pathlib import Path
import requests
from django.conf import settings
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from .models import Album

BASE_DIR = Path(__file__).resolve().parent.parent
path_env = BASE_DIR / 'core' / '.env'
load_dotenv(dotenv_path=path_env)


class SpotifyService:
    def __init__(self):
        self.client_id = getattr(settings, 'SPOTIFYAPI_CLIENT_ID', os.getenv('SPOTIFYAPI_CLIENT_ID'))
        self.client_secret = getattr(settings, 'SPOTIFYAPI_CLIENT_SECRET', os.getenv('SPOTIFYAPI_CLIENT_SECRET'))
        self.sp = None

    def buscar_albuns(self, termo_busca, limite=30):
        try:
            url_token = "https://accounts.spotify.com/api/token"
            resposta_teste = requests.post(url_token, data={'grant_type': 'client_credentials'},
                                           auth=(self.client_id, self.client_secret), timeout=2)
            if resposta_teste.status_code == 429:
                raise PermissionError()
        except:
            raise PermissionError()

        try:
            if not self.sp:
                auth_manager = SpotifyClientCredentials(client_id=self.client_id, client_secret=self.client_secret)
                self.sp = spotipy.Spotify(auth_manager=auth_manager)
            dados = self.sp.search(q=termo_busca, type='album', limit=limite)
            if not dados or "albums" not in dados: return []

            return [{
                "id_spotify": item["id"],
                "nome": item["name"],
                "artista": item["artists"][0]['name'],
                "url_capa": item["images"][0]['url'] if item["images"] else None
            } for item in dados["albums"]["items"]]
        except:
            return []


class LastFMService:
    def __init__(self):
        self.api_key = os.getenv('LASTFMAPI_API_KEY')
        self.base_url = "http://ws.audioscrobbler.com/2.0/"

    def buscar_albuns(self, termo_busca, limite=30):
        if not self.api_key: return []
        termo_limpo = termo_busca.replace('genre:', '').replace('year:', '').replace('"', '').replace('%', '')
        try:
            resposta = requests.get(self.base_url,
                                    params={'method': 'album.search', 'album': termo_limpo, 'api_key': self.api_key,
                                            'format': 'json', 'limit': limite}, timeout=3)
            if resposta.status_code == 200:
                lista_albuns = resposta.json().get('results', {}).get('albummatches', {}).get('album', [])
                resultados = []
                for album in lista_albuns:
                    imagens = album.get('image', [])
                    url_capa = next((img.get('#text') for img in reversed(imagens) if img.get('#text')), "")
                    if not url_capa: continue
                    artista = album.get('artist', 'Artista Desconhecido')
                    titulo = album.get('name', 'Álbum Desconhecido')
                    resultados.append({
                        'id_spotify': f"lastfm_{artista}_{titulo}".replace(" ", "_").lower(),
                        'nome': titulo,
                        'artista': artista,
                        'url_capa': url_capa
                    })
                return resultados
            return []
        except:
            return []


class OrquestradorAlbunsService:
    """Gerencia de forma isolada o sorteio matemático e o recheio do banco via APIs."""

    @staticmethod
    def sortear_lote_do_banco():
        """
        Sorteia uma condicional e puxa os IDs direto do banco.
        Garante aleatoriedade pura e respostas ultra rápidas.
        """
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

            # Verificação de estoque local
        if filtro_banco.count() < 25:
            print(
                f"[Estoque Baixo] Apenas {filtro_banco.count()} álbuns para '{termo_sorteado}'. Disparando Orquestrador de Threads...")
            threading.Thread(
                target=OrquestradorAlbunsService.garantir_abastecimento_online,
                args=(query_api, termo_sorteado)
            ).start()

        # Resposta imediata baseada nos IDs presentes no banco
        if filtro_banco.exists():
            albuns_sorteados = list(filtro_banco.order_by('?')[:20])
        else:
            albuns_sorteados = list(Album.objects.all().order_by('?')[:20])

        lista_retorno = []
        for a in albuns_sorteados:
            id_ativo = a.id_spotify if a.id_spotify else a.id_lastfm
            lista_retorno.append({
                'id_spotify': id_ativo,
                'titulo': a.titulo,
                'nome': a.titulo,
                'artista': a.artista,
                'url_capa': a.url_capa
            })

        return lista_retorno

    @staticmethod
    def garantizar_abastecimento_online(query_api, termo_busca):
        # Alias temporário para manter compatibilidade absoluta caso alguma thread antiga chame com "z"
        return OrquestradorAlbunsService.garantir_abastecimento_online(query_api, termo_busca)

    @staticmethod
    def garantir_abastecimento_online(query_api, termo_busca):
        """
        Busca novos álbuns usando chamadas HTTP puras e isoladas.
        Se o Spotify falhar ou responder com Rate Limit (429), o Last.fm assume na mesma hora.
        """
        resultados = []
        origem = 'spotify'

        # 1. TENTATIVA SPOTIFY (HTTP Pura para evitar travamentos da biblioteca)
        try:
            print(f"[Abastecimento] Consultando disjuntor do Spotify para: {query_api}")
            spotify = SpotifyService()

            url_token = "https://accounts.spotify.com/api/token"
            res_token = requests.post(
                url_token,
                data={'grant_type': 'client_credentials'},
                auth=(spotify.client_id, spotify.client_secret),
                timeout=1.5
            )

            if res_token.status_code == 429:
                print("[Abastecimento] Instabilidade detectada no Spotify (429). Ignorando...")
            elif res_token.status_code == 200:
                access_token = res_token.json().get('access_token')

                url_busca = "https://api.spotify.com/v1/search"
                headers = {"Authorization": f"Bearer {access_token}"}
                params = {"q": query_api, "type": "album", "limit": 30}

                res_busca = requests.get(url_busca, headers=headers, params=params, timeout=1.5)

                if res_busca.status_code == 200:
                    dados = res_busca.json()
                    lista_itens = dados.get("albums", {}).get("items", [])

                    for item in lista_itens:
                        ano = None
                        if item.get("release_date"):
                            ano_str = item["release_date"].split("-")[0]
                            if ano_str.isdigit():
                                ano = int(ano_str)

                        resultados.append({
                            "id_spotify": item["id"],
                            "nome": item["name"],
                            "artista": item["artists"][0]['name'] if item["artists"] else 'Artista Desconhecido',
                            "url_capa": item["images"][0]['url'] if item["images"] else None,
                            "ano_lancamento": ano
                        })
                    print(f"[Abastecimento] Spotify respondeu com sucesso! {len(resultados)} álbuns encontrados.")
        except Exception as e:
            print(f"[Abastecimento] Conexão com Spotify falhou ou estourou o tempo limite.")

        # 2. SE O SPOTIFY TIMEOUT OU RATE LIMIT, O LAST.FM ENTRA EM AÇÃO IMEDIATAMENTE
        if not resultados:
            print("\n[Contingência Ativa] Spotify indisponível. Acionando Last.fm imediatamente...")
            try:
                lastfm = LastFMService()
                res_lf = lastfm.buscar_albuns(termo_busca=query_api, limite=30)
                if res_lf:
                    resultados = res_lf
                    origem = 'lastfm'
                    print(f"[Contingência] Last.fm retornou {len(resultados)} álbuns com sucesso.")
            except Exception as le:
                print(f"[Contingência] Falha crítica: Last.fm também está indisponível.")
                return

        if not resultados:
            print("[Abastecimento] Nenhuma das APIs retornou dados para este termo.")
            return

        # 3. GRAVAÇÃO SEGURA E CORRIGIDA NO BANCO DE DADOS
        novos_salvos = 0
        for item in resultados:
            id_chave = item.get('id_spotify')
            url_img = item.get('url_capa')
            if not id_chave or not url_img: continue

            ano_salvar = item.get('ano_lancamento')
            if not ano_salvar and '-' in termo_busca:
                ano_inicio = termo_busca.split('-')[0]
                if ano_inicio.isdigit():
                    ano_salvar = int(ano_inicio)

            # CORREÇÃO DA DIGITAÇÃO AQUI (Removido o teste quebrado 'origi')
            if origem == 'spotify':
                obj, created = Album.objects.get_or_create(
                    id_spotify=id_chave,
                    defaults={
                        'id_lastfm': None,
                        'titulo': item['nome'],
                        'artista': item['artista'],
                        'url_capa': url_img,
                        'termo_busca': termo_busca,
                        'ano_lancamento': ano_salvar
                    }
                )
                if created: novos_salvos += 1
            else:
                obj, created = Album.objects.get_or_create(
                    id_lastfm=id_chave,
                    defaults={
                        'id_spotify': None,
                        'titulo': item['nome'],
                        'artista': item['artista'],
                        'url_capa': url_img,
                        'termo_busca': termo_busca,
                        'ano_lancamento': ano_salvar
                    }
                )
                if created: novos_salvos += 1

        if novos_salvos > 0:
            print(
                f"[Abastecimento] Sucesso! Banco alimentado com +{novos_salvos} novos álbuns vindo do {origem.upper()}.\n")