import time
from typing import Callable, Sequence, Tuple, Set
from game import (
    TwoPlayerGameState,
)
from heuristic import (
    simple_evaluation_function,
)
from tournament import (
    StudentHeuristic,
)

def func_glob(n: int, state: TwoPlayerGameState) -> float:
    return n + simple_evaluation_function(state)


class Solution1(StudentHeuristic):
    def get_name(self) -> str:
        return "Abril"

    def evaluation_function(self, state: TwoPlayerGameState) -> float:
        # let's use a global function
        return self.movimientos_legales(state)
    
    def movimientos_legales(self, state: TwoPlayerGameState) -> float:
        if state.end_of_game:
            # Si el juego terminó, devolver la diferencia de puntuación
            scores = state.scores
            if state.is_player_max(state.next_player):
                return scores[0] - scores[1]  # MAX es player1
            else:
                return scores[1] - scores[0]  # MAX es player2

        mov_legales = state.game.generate_successors(state)
        cantidad_actual = len(mov_legales)
        
        # Verificar que hay movimientos antes de acceder al índice 0
        if cantidad_actual == 0:
            cantidad_oponente = 0
        else:
            oponente = state.game.opponent(state.next_player)
            estado_oponente = mov_legales[0]
            mov_legales_oponente = estado_oponente.game.generate_successors(estado_oponente)
            cantidad_oponente = len(mov_legales_oponente)
        
        # Determinar quién es MAX y calcular diferencia correctamente
        current_player = state.next_player
        if state.is_player_max(current_player):
            # El jugador actual es MAX
            return cantidad_actual - cantidad_oponente
        else:
            # El oponente es MAX
            return cantidad_oponente - cantidad_actual

    def dummy(self, n: int) -> int:
        return n + 1