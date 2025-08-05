import pygame
import random
import math
import time
import sys
from pygame import gfxdraw
import numpy as np

# Inicializar Pygame
pygame.init()

# Configurações da janela - Fullscreen
info = pygame.display.Info()
LARGURA = info.current_w
ALTURA = info.current_h
janela = pygame.display.set_mode((LARGURA, ALTURA), pygame.FULLSCREEN)
pygame.display.set_caption("Jogo da Forca - A Experiencia Visual Definitiva")

# Variável global para controlar o modo de exibição
modo_fullscreen = True

# Cores e gradientes
class CoresMagicas:
    def __init__(self):
        self.roxo_profundo = (25, 25, 50)
        self.azul_celestial = (100, 150, 255)
        self.rosa_neon = (255, 100, 200)
        self.verde_esmeralda = (50, 255, 150)
        self.amarelo_sol = (255, 255, 100)
        self.laranja_fogo = (255, 150, 50)
        self.branco_puro = (255, 255, 255)
        self.preto_veludo = (0, 0, 0)

# Sistema de partículas
class Particula:
    def __init__(self, x, y, cor, velocidade=3):
        self.x = x
        self.y = y
        self.vx = random.uniform(-velocidade, velocidade)
        self.vy = random.uniform(-velocidade, velocidade)
        self.cor = cor
        self.vida = 255
        self.tamanho = random.randint(2, 6)
        self.gravidade = 0.1
        
    def atualizar(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravidade
        self.vida -= 3
        self.tamanho = max(0, self.tamanho - 0.1)
        
    def desenhar(self, superficie):
        if self.vida > 0:
            alpha = int(self.vida)
            cor_com_alpha = (*self.cor, alpha)
            surf = pygame.Surface((self.tamanho * 2, self.tamanho * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, cor_com_alpha, (self.tamanho, self.tamanho), self.tamanho)
            superficie.blit(surf, (self.x - self.tamanho, self.y - self.tamanho))

class SistemaParticulas:
    def __init__(self):
        self.particulas = []
        
    def adicionar_explosao(self, x, y, cor, quantidade=20):
        for _ in range(quantidade):
            self.particulas.append(Particula(x, y, cor))
            
    def atualizar(self):
        self.particulas = [p for p in self.particulas if p.vida > 0]
        for p in self.particulas:
            p.atualizar()
            
    def desenhar(self, superficie):
        for p in self.particulas:
            p.desenhar(superficie)

# Efeitos visuais
class EfeitosVisuais:
    def __init__(self):
        self.ondas = []
        self.estrelas = []
        self.gerar_estrelas()
        
    def gerar_estrelas(self):
        for _ in range(100):
            self.estrelas.append({
                'x': random.randint(0, LARGURA),
                'y': random.randint(0, ALTURA),
                'brilho': random.uniform(0.5, 1.5),
                'velocidade': random.uniform(0.1, 0.5)
            })
    
    def adicionar_onda(self, x, y, cor):
        self.ondas.append({
            'x': x, 'y': y, 'raio': 0, 'cor': cor, 'vida': 255
        })
    
    def atualizar_ondas(self):
        for onda in self.ondas[:]:
            onda['raio'] += 2
            onda['vida'] -= 5
            if onda['vida'] <= 0:
                self.ondas.remove(onda)
    
    def desenhar_estrelas(self, superficie):
        for estrela in self.estrelas:
            brilho = int(255 * estrela['brilho'] * (0.5 + 0.5 * math.sin(time.time() * estrela['velocidade'])))
            brilho = max(0, min(255, brilho))  # Garantir que está entre 0 e 255
            cor = (brilho, brilho, brilho)
            pygame.draw.circle(superficie, cor, (estrela['x'], estrela['y']), 1)
    
    def desenhar_ondas(self, superficie):
        for onda in self.ondas:
            if onda['vida'] > 0:
                alpha = int(onda['vida'])
                cor_com_alpha = (*onda['cor'], alpha)
                surf = pygame.Surface((onda['raio'] * 2, onda['raio'] * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, cor_com_alpha, (onda['raio'], onda['raio']), onda['raio'], 3)
                superficie.blit(surf, (onda['x'] - onda['raio'], onda['y'] - onda['raio']))

# Jogo da Forca
class JogoForca:
    def __init__(self):
        self.cores = CoresMagicas()
        self.particulas = SistemaParticulas()
        self.efeitos = EfeitosVisuais()
        self.fonte_grande = pygame.font.Font(None, 48)
        self.fonte_media = pygame.font.Font(None, 36)
        self.fonte_pequena = pygame.font.Font(None, 24)
        
        self.palavra = ""
        self.palavra_oculta = ""
        self.letras_adivinhadas = set()
        self.vidas = 8  # Vidas fixas: 7 partes do boneco + 1
        self.vidas_iniciais = 8
        self.estado = "menu"  # menu, jogo, vitoria, derrota
        self.tempo_animacao = 0
        self.angulo_rotacao = 0
        
    def desenhar_gradiente_fundo(self, superficie):
        for y in range(ALTURA):
            intensidade = y / ALTURA
            r = max(0, min(255, int(25 + (100 - 25) * intensidade)))
            g = max(0, min(255, int(25 + (150 - 25) * intensidade)))
            b = max(0, min(255, int(50 + (255 - 50) * intensidade)))
            pygame.draw.line(superficie, (r, g, b), (0, y), (LARGURA, y))
    
    def desenhar_texto_brilhante(self, superficie, texto, posicao, tamanho, cor):
        # Sombra
        sombra = self.fonte_grande.render(texto, True, (0, 0, 0))
        superficie.blit(sombra, (posicao[0] + 3, posicao[1] + 3))
        
        # Texto principal
        texto_surf = self.fonte_grande.render(texto, True, cor)
        superficie.blit(texto_surf, posicao)
        
        # Brilho
        brilho_intensidade = int(255 * (0.7 + 0.3 * math.sin(time.time() * 2)))
        brilho_intensidade = max(0, min(255, brilho_intensidade))  # Garantir que está entre 0 e 255
        brilho_cor = (max(0, min(255, cor[0] + brilho_intensidade)), 
                     max(0, min(255, cor[1] + brilho_intensidade)), 
                     max(0, min(255, cor[2] + brilho_intensidade)))
        texto_brilho = self.fonte_grande.render(texto, True, brilho_cor)
        superficie.blit(texto_brilho, (posicao[0] - 1, posicao[1] - 1))
    
    def desenhar_botao_magico(self, superficie, texto, rect, cor_base):
        # Gradiente do botão
        for i in range(rect.height):
            intensidade = i / rect.height
            r = max(0, min(255, int(cor_base[0] * (0.7 + 0.3 * intensidade))))
            g = max(0, min(255, int(cor_base[1] * (0.7 + 0.3 * intensidade))))
            b = max(0, min(255, int(cor_base[2] * (0.7 + 0.3 * intensidade))))
            pygame.draw.line(superficie, (r, g, b), 
                           (rect.x, rect.y + i), (rect.x + rect.width, rect.y + i))
        
        # Borda brilhante
        pygame.draw.rect(superficie, self.cores.branco_puro, rect, 3)
        
        # Texto
        texto_surf = self.fonte_media.render(texto, True, self.cores.branco_puro)
        texto_rect = texto_surf.get_rect(center=rect.center)
        superficie.blit(texto_surf, texto_rect)
    
    def desenhar_forca_animada(self, superficie, vidas_perdidas):
        # Base da forca
        base_x, base_y = LARGURA // 2, ALTURA - 100
        
        # Desenhar base com gradiente
        for i in range(20):
            cor = (max(0, min(255, 100 + i * 5)), max(0, min(255, 100 + i * 5)), max(0, min(255, 100 + i * 5)))
            pygame.draw.rect(superficie, cor, (base_x - 10 + i, base_y, 20 - i * 2, 10))
        
        # Poste vertical
        if vidas_perdidas >= 1:
            for i in range(200):
                cor = (max(0, min(255, 80 + i * 2)), max(0, min(255, 80 + i * 2)), max(0, min(255, 80 + i * 2)))
                pygame.draw.line(superficie, cor, (base_x, base_y - i), (base_x, base_y - i + 1))
        
        # Topo horizontal
        if vidas_perdidas >= 2:
            for i in range(150):
                cor = (max(0, min(255, 80 + i * 2)), max(0, min(255, 80 + i * 2)), max(0, min(255, 80 + i * 2)))
                pygame.draw.line(superficie, cor, (base_x + i, base_y - 200), (base_x + i + 1, base_y - 200))
        
        # Corda
        if vidas_perdidas >= 3:
            corda_x = base_x + 150
            corda_y = base_y - 200
            for i in range(50):
                cor = (139, 69, 19)
                pygame.draw.line(superficie, cor, (corda_x, corda_y + i), (corda_x, corda_y + i + 1))
        
        # Cabeça
        if vidas_perdidas >= 4:
            cabeca_x = base_x + 150
            cabeca_y = base_y - 150
            # Cabeça com gradiente
            for raio in range(30, 0, -1):
                intensidade = raio / 30
                cor = (max(0, min(255, int(255 * intensidade))), 
                      max(0, min(255, int(200 * intensidade))), 
                      max(0, min(255, int(150 * intensidade))))
                pygame.draw.circle(superficie, cor, (cabeca_x, cabeca_y), raio)
        
        # Corpo
        if vidas_perdidas >= 5:
            corpo_x = base_x + 150
            corpo_y = base_y - 120
            # Corpo com gradiente
            for i in range(60):
                intensidade = i / 60
                cor = (max(0, min(255, int(100 * intensidade))), 
                      max(0, min(255, int(150 * intensidade))), 
                      max(0, min(255, int(255 * intensidade))))
                pygame.draw.line(superficie, cor, (corpo_x, corpo_y + i), (corpo_x, corpo_y + i + 1))
        
        # Braços
        if vidas_perdidas >= 6:
            # Braço esquerdo
            for i in range(40):
                intensidade = i / 40
                cor = (max(0, min(255, int(100 * intensidade))), 
                      max(0, min(255, int(150 * intensidade))), 
                      max(0, min(255, int(255 * intensidade))))
                pygame.draw.line(superficie, cor, (corpo_x - i, corpo_y + 20 + i), (corpo_x - i - 1, corpo_y + 20 + i + 1))
            
            # Braço direito
            for i in range(40):
                intensidade = i / 40
                cor = (max(0, min(255, int(100 * intensidade))), 
                      max(0, min(255, int(150 * intensidade))), 
                      max(0, min(255, int(255 * intensidade))))
                pygame.draw.line(superficie, cor, (corpo_x + i, corpo_y + 20 + i), (corpo_x + i + 1, corpo_y + 20 + i + 1))
        
        # Pernas
        if vidas_perdidas >= 7:
            # Perna esquerda
            for i in range(50):
                intensidade = i / 50
                cor = (max(0, min(255, int(50 * intensidade))), 
                      max(0, min(255, int(100 * intensidade))), 
                      max(0, min(255, int(200 * intensidade))))
                pygame.draw.line(superficie, cor, (corpo_x - 10 - i, corpo_y + 60 + i), (corpo_x - 10 - i - 1, corpo_y + 60 + i + 1))
            
            # Perna direita
            for i in range(50):
                intensidade = i / 50
                cor = (max(0, min(255, int(50 * intensidade))), 
                      max(0, min(255, int(100 * intensidade))), 
                      max(0, min(255, int(200 * intensidade))))
                pygame.draw.line(superficie, cor, (corpo_x + 10 + i, corpo_y + 60 + i), (corpo_x + 10 + i + 1, corpo_y + 60 + i + 1))
    
    def desenhar_palavra_oculta(self, superficie):
        if not self.palavra:
            return
            
        palavra_display = ""
        for letra in self.palavra:
            if letra.lower() in self.letras_adivinhadas or letra == " ":
                palavra_display += letra
            else:
                palavra_display += "_"
        
        # Desenhar cada letra com efeito especial
        x_inicial = LARGURA // 2 - (len(palavra_display) * 30) // 2
        for i, char in enumerate(palavra_display):
            x = x_inicial + i * 30
            y = ALTURA // 2 + 50
            
            if char == "_":
                # Linha com brilho
                brilho = int(255 * (0.5 + 0.5 * math.sin(time.time() * 3 + i)))
                brilho = max(0, min(255, brilho))  # Garantir que está entre 0 e 255
                cor_linha = (brilho, brilho, brilho)
                pygame.draw.line(superficie, cor_linha, (x, y), (x + 20, y), 3)
            else:
                # Letra com efeito especial
                cor_letra = self.cores.verde_esmeralda if char.lower() in self.letras_adivinhadas else self.cores.rosa_neon
                self.desenhar_texto_brilhante(superficie, char, (x, y - 30), 36, cor_letra)
    
    def desenhar_menu(self, superficie):
        self.desenhar_gradiente_fundo(superficie)
        self.efeitos.desenhar_estrelas(superficie)
        
        # Título principal com efeito especial
        titulo = "Jogo da Forca"
        self.desenhar_texto_brilhante(superficie, titulo, 
                                    (LARGURA // 2 - 200, 100), 48, self.cores.rosa_neon)
        
        # Subtítulo
        subtitulo = "A Experiencia Visual Definitiva"
        self.desenhar_texto_brilhante(superficie, subtitulo, 
                                    (LARGURA // 2 - 150, 160), 36, self.cores.azul_celestial)
        
        # Instruções
        instrucoes = [
            "Digite a palavra a adivinhar",
            "Vidas: 8 (automaticas)",
            "Prepare-se para a magia!",
            "",
            "Pressione ENTER para começar...",
            "F11: Fullscreen/Janela | ESC: Sair"
        ]
        
        for i, texto in enumerate(instrucoes):
            cor = self.cores.branco_puro if i < 3 else self.cores.amarelo_sol
            y = 250 + i * 40
            self.desenhar_texto_brilhante(superficie, texto, 
                                        (LARGURA // 2 - 200, y), 24, cor)
        
        # Efeitos de partículas
        if random.random() < 0.1:
            x = random.randint(0, LARGURA)
            y = random.randint(0, ALTURA)
            cor = random.choice([self.cores.rosa_neon, self.cores.azul_celestial, 
                               self.cores.verde_esmeralda, self.cores.amarelo_sol])
            self.particulas.adicionar_explosao(x, y, cor, 5)
    
    def desenhar_jogo(self, superficie):
        self.desenhar_gradiente_fundo(superficie)
        self.efeitos.desenhar_estrelas(superficie)
        self.efeitos.desenhar_ondas(superficie)
        
        # Título do jogo
        titulo = f"Vidas: {'*' * self.vidas}"
        self.desenhar_texto_brilhante(superficie, titulo, 
                                    (50, 50), 36, self.cores.rosa_neon)
        
        # Desenhar forca
        vidas_perdidas = self.vidas_iniciais - self.vidas
        self.desenhar_forca_animada(superficie, vidas_perdidas)
        
        # Desenhar palavra oculta
        self.desenhar_palavra_oculta(superficie)
        
        # Letras já tentadas
        letras_tentadas = "Letras tentadas: " + ", ".join(sorted(self.letras_adivinhadas))
        self.desenhar_texto_brilhante(superficie, letras_tentadas, 
                                    (50, ALTURA - 100), 24, self.cores.azul_celestial)
        
        # Instruções
        instrucao = "Digite uma letra e pressione ENTER..."
        self.desenhar_texto_brilhante(superficie, instrucao, 
                                    (LARGURA // 2 - 150, ALTURA - 50), 24, self.cores.branco_puro)
    
    def desenhar_vitoria(self, superficie):
        self.desenhar_gradiente_fundo(superficie)
        self.efeitos.desenhar_estrelas(superficie)
        
        # Efeito de vitória
        for _ in range(10):
            x = random.randint(0, LARGURA)
            y = random.randint(0, ALTURA)
            cor = self.cores.verde_esmeralda
            self.particulas.adicionar_explosao(x, y, cor, 3)
        
        # Mensagem de vitória
        titulo = "PARABENS!"
        self.desenhar_texto_brilhante(superficie, titulo, 
                                    (LARGURA // 2 - 150, ALTURA // 2 - 100), 48, self.cores.verde_esmeralda)
        
        subtitulo = f"Você adivinhou: {self.palavra}"
        self.desenhar_texto_brilhante(superficie, subtitulo, 
                                    (LARGURA // 2 - 150, ALTURA // 2 - 50), 36, self.cores.amarelo_sol)
        
        instrucao = "Pressione ESPACO para jogar novamente ou ESC para sair"
        self.desenhar_texto_brilhante(superficie, instrucao, 
                                    (LARGURA // 2 - 200, ALTURA // 2 + 50), 24, self.cores.branco_puro)
    
    def desenhar_derrota(self, superficie):
        self.desenhar_gradiente_fundo(superficie)
        self.efeitos.desenhar_estrelas(superficie)
        
        # Efeito de derrota
        for _ in range(5):
            x = random.randint(0, LARGURA)
            y = random.randint(0, ALTURA)
            cor = self.cores.laranja_fogo
            self.particulas.adicionar_explosao(x, y, cor, 5)
        
        # Mensagem de derrota
        titulo = "GAME OVER"
        self.desenhar_texto_brilhante(superficie, titulo, 
                                    (LARGURA // 2 - 150, ALTURA // 2 - 100), 48, self.cores.laranja_fogo)
        
        subtitulo = f"A palavra era: {self.palavra}"
        self.desenhar_texto_brilhante(superficie, subtitulo, 
                                    (LARGURA // 2 - 150, ALTURA // 2 - 50), 36, self.cores.rosa_neon)
        
        instrucao = "Pressione ESPACO para jogar novamente ou ESC para sair"
        self.desenhar_texto_brilhante(superficie, instrucao, 
                                    (LARGURA // 2 - 200, ALTURA // 2 + 50), 24, self.cores.branco_puro)
    
    def executar(self):
        global janela
        relogio = pygame.time.Clock()
        texto_atual = ""
        modo_entrada = "palavra"  # palavra, jogo
        
        while True:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    
                    elif evento.key == pygame.K_F11:
                        # Alternar entre fullscreen e janela
                        global modo_fullscreen
                        if modo_fullscreen:
                            janela = pygame.display.set_mode((1200, 800))
                        else:
                            janela = pygame.display.set_mode((LARGURA, ALTURA), pygame.FULLSCREEN)
                        modo_fullscreen = not modo_fullscreen
                    
                    elif evento.key == pygame.K_RETURN:
                        if modo_entrada == "palavra" and texto_atual:
                            self.palavra = texto_atual.upper()
                            texto_atual = ""
                            modo_entrada = "jogo"
                            self.estado = "jogo"
                        elif modo_entrada == "jogo" and texto_atual:
                            letra = texto_atual.lower()
                            if letra.isalpha() and len(letra) == 1 and letra not in self.letras_adivinhadas:
                                self.letras_adivinhadas.add(letra)
                                if letra not in self.palavra.lower():
                                    self.vidas -= 1
                                    # Efeito de erro
                                    self.particulas.adicionar_explosao(LARGURA // 2, ALTURA // 2, self.cores.laranja_fogo, 15)
                                    self.efeitos.adicionar_onda(LARGURA // 2, ALTURA // 2, self.cores.laranja_fogo)
                                else:
                                    # Efeito de acerto
                                    self.particulas.adicionar_explosao(LARGURA // 2, ALTURA // 2, self.cores.verde_esmeralda, 20)
                                    self.efeitos.adicionar_onda(LARGURA // 2, ALTURA // 2, self.cores.verde_esmeralda)
                            texto_atual = ""
                    
                    elif evento.key == pygame.K_SPACE and self.estado in ["vitoria", "derrota"]:
                        self.__init__()
                        modo_entrada = "palavra"
                    
                    elif evento.key == pygame.K_BACKSPACE:
                        if modo_entrada == "palavra":
                            texto_atual = texto_atual[:-1]
                        elif modo_entrada == "jogo":
                            texto_atual = texto_atual[:-1]
                    
                    else:
                        if evento.unicode.isprintable():
                            if modo_entrada == "palavra":
                                texto_atual += evento.unicode
                            elif modo_entrada == "jogo":
                                if evento.unicode.isalpha() and len(texto_atual) == 0:
                                    texto_atual += evento.unicode.lower()
            
            # Atualizar lógica do jogo
            if self.estado == "jogo":
                # Verificar vitória
                if all(letra.lower() in self.letras_adivinhadas or letra == " " for letra in self.palavra):
                    self.estado = "vitoria"
                    # Efeito de vitória
                    for _ in range(50):
                        x = random.randint(0, LARGURA)
                        y = random.randint(0, ALTURA)
                        cor = random.choice([self.cores.verde_esmeralda, self.cores.amarelo_sol, self.cores.azul_celestial])
                        self.particulas.adicionar_explosao(x, y, cor, 10)
                
                # Verificar derrota
                elif self.vidas <= 0:
                    self.estado = "derrota"
                    # Efeito de derrota
                    for _ in range(30):
                        x = random.randint(0, LARGURA)
                        y = random.randint(0, ALTURA)
                        cor = self.cores.laranja_fogo
                        self.particulas.adicionar_explosao(x, y, cor, 8)
            
            # Atualizar efeitos
            self.particulas.atualizar()
            self.efeitos.atualizar_ondas()
            self.tempo_animacao += 1
            
            # Desenhar
            if self.estado == "menu":
                self.desenhar_menu(janela)
                
                # Mostrar entrada de palavra
                if modo_entrada == "palavra":
                    prompt = f"Digite a palavra: {texto_atual}"
                    self.desenhar_texto_brilhante(janela, prompt, 
                                                (LARGURA // 2 - 200, ALTURA // 2 + 100), 24, self.cores.branco_puro)
            
            elif self.estado == "jogo":
                self.desenhar_jogo(janela)
                
                # Mostrar entrada de letra
                prompt = f"Digite uma letra: {texto_atual}"
                self.desenhar_texto_brilhante(janela, prompt, 
                                            (LARGURA // 2 - 150, ALTURA - 30), 24, self.cores.branco_puro)
            
            elif self.estado == "vitoria":
                self.desenhar_vitoria(janela)
            
            elif self.estado == "derrota":
                self.desenhar_derrota(janela)
            
            # Desenhar partículas por cima de tudo
            self.particulas.desenhar(janela)
            
            pygame.display.flip()
            relogio.tick(60)

if __name__ == "__main__":
    jogo = JogoForca()
    jogo.executar()