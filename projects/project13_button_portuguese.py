# Projeto 13: Construindo uma Classe de Botão (Versão do Estudante)
#
# OBJETIVO:
# No Projeto 12, você USOU uma classe (Pet).
# No Projeto 13, você vai CONSTRUIR uma classe (Button/Botão).
#
# Esta classe resolve um problema específico do robô: "Bouncing" (Rebote).
# Queremos detectar um único "clique" mesmo se o botão for mantido pressionado.
#
# Criado com a ajuda do Gemini Pro - V03

from arduino_alvik import ArduinoAlvik
import time
from nhs_robotics import NanoLED 

# ---------------------------------------------------------------------
# PARTE 1: A CLASSE BUTTON (A PLANTA BAIXA)
# ---------------------------------------------------------------------

class Button:
    """
    Uma classe para gerenciar o estado de um botão e detectar um único 
    "pressionamento" (uma "borda de subida" ou rising edge).
    """
    # 1. CONSTANTES DE CLASSE
    # Usamos estes nomes em vez de números (1 ou 2) para tornar o código legível.
    STATE_UP = 1
    STATE_PRESSED = 2
    
    def __init__(self, get_touch_function):
        """
        O Construtor: Configura o botão quando o criamos.
        
        Argumentos:
        get_touch_function -- A função do Alvik (como alvik.get_touch_ok) 
                              que este botão usará para verificar o hardware.
        """
        # --- TODO: SEÇÃO DE TRABALHO 1 ---
        # Precisamos salvar a 'get_touch_function' em uma variável "self"
        # para que possamos usá-la mais tarde em outros métodos.
        self.get_hardware_state = get_touch_function
        
        # Defina o estado inicial do botão para STATE_UP (não pressionado)
        # DICA: Olhe para as constantes acima!
        self.current_state = None # <--- SUBSTITUA 'None' PELO SEU CÓDIGO

    def get_touch(self):
        """
        Verifica o estado do botão.
        Retorna True APENAS no exato momento em que o botão é pressionado.
        """
        return_value = False
        
        # --- TODO: SEÇÃO DE TRABALHO 2 ---
        # 1. Pergunte ao hardware se ele está sendo tocado atualmente.
        # Chame a função que salvamos em __init__ (self.get_hardware_state)
        # Armazene o resultado em uma variável chamada 'is_pressed'
        
        # <--- ESCREVA O CÓDIGO AQUI
        

        # --- TODO: SEÇÃO DE TRABALHO 3 (A Lógica) ---
        # Precisamos verificar nossa "Máquina de Estados".
        # Traduza estas frases para comandos 'if' em Python.
        
        # CENÁRIO A: O botão estava UP (solto), mas agora está pressionado.
        # SE (IF) self.current_state é igual a self.STATE_UP:
            # SE (IF) is_pressed for True:
                # Encontramos um novo pressionamento!
                # 1. Defina return_value como True
                # 2. Mude self.current_state para self.STATE_PRESSED
        
        
        
        # CENÁRIO B: O botão estava PRESSED (pressionado), mas agora foi solto.
        # ELIF self.current_state é igual a self.STATE_PRESSED:
            # SE (IF) is_pressed for False:
                # O botão foi solto.
                # 1. Mude self.current_state de volta para self.STATE_UP
                
        
        
        
        # Retorna o resultado (True apenas no quadro exato do pressionamento)
        return return_value


# ---------------------------------------------------------------------
# PARTE 2: O PROGRAMA PRINCIPAL (O Trocador de LED)
# ---------------------------------------------------------------------

print("Iniciando Projeto 13: Classe Botão...")

# 1. Configuração do Robô
alvik = ArduinoAlvik()
alvik.begin()

# --- TODO: SEÇÃO DE TRABALHO 4 (Criar Objetos) ---
# Crie dois objetos Button. 
# NOTA: Passe o NOME da função (ex: alvik.get_touch_ok), 
# NÃO coloque () depois dele! Estamos passando a ferramenta, não o resultado.

center_button = Button(alvik.get_touch_ok) 
# Crie o cancel_button abaixo usando 'alvik.get_touch_cancel'
cancel_button = None # <--- SUBSTITUA 'None' PELO SEU CÓDIGO

# 2. Configuração de Variáveis
left_led_is_red = True
alvik.left_led.set_color(1, 0, 0)  # Inicia Vermelho
alvik.right_led.set_color(0, 1, 0) # Inicia Verde

try:
    # Loop até que o botão Cancelar seja pressionado
    # Note como usamos nosso novo método do objeto: .get_touch()
    while not cancel_button.get_touch():
        
        # --- TODO: SEÇÃO DE TRABALHO 5 (Usar Objetos) ---
        # Verifique se o center_button (botão central) foi tocado.
        # SE (IF) center_button.get_touch() for True:
        #    Alterne a variável 'left_led_is_red' ( use: var = not var )
        #    Imprima "Troca!" no console
        
        # <--- ESCREVA O CÓDIGO AQUI
        
        
        # --- Atualiza LEDs com base na variável (Feito para você) ---
        if left_led_is_red:
            alvik.left_led.set_color(1, 0, 0)
            alvik.right_led.set_color(0, 1, 0)
        else:
            alvik.left_led.set_color(0, 1, 0)
            alvik.right_led.set_color(1, 0, 0)

        # Pequena pausa para deixar o robô pensar
        time.sleep(0.01)

except Exception as e:
    print(f"Erro: {e}")
    
finally:
    alvik.left_led.off()
    alvik.right_led.off()
    alvik.stop()
