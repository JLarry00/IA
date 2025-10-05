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
        return "solution1"

    def evaluation_function(self, state: TwoPlayerGameState) -> float:
        # let's use an auxiliary function
        aux = self.dummy(123)
        return aux

    def dummy(self, n: int) -> int:
        return n + 1


class Solution2(StudentHeuristic):
    def get_name(self) -> str:
        return "diferencia_fichas"

    def evaluation_function(self, state: TwoPlayerGameState) -> float:
        # Heurística personalizada para Reversi
        return self.diferencia_fichas(state)
    
    def diferencia_fichas(self, state: TwoPlayerGameState) -> float:
        if state.end_of_game:
            # Si el juego terminó, devolver la diferencia de puntuación
            scores = state.scores
            if state.is_player_max(state.next_player):
                return scores[0] - scores[1]  # MAX es player1
            else:
                return scores[1] - scores[0]  # MAX es player2
        
        # Si el juego no terminó, evaluar el tablero
        board = state.board
        if not board:
            return 0.0
        
        # Contar fichas de cada jugador
        fichas_max = 0
        fichas_min = 0
        
        for pos, ficha in board.items():
            if ficha == 'B':  # Asumiendo que B es MAX
                fichas_max += 1
            elif ficha == 'W':  # Asumiendo que W es MIN
                fichas_min += 1
        
        # Diferencia de fichas (favorables para MAX)
        diferencia_fichas = fichas_max - fichas_min
        
        # Bonus por esquinas (muy importantes en Reversi)
        esquinas = [(1, 1), (1, state.game.height), 
                   (state.game.width, 1), (state.game.width, state.game.height)]
        bonus_esquinas = 0
        for esquina in esquinas:
            if esquina in board:
                if board[esquina] == 'B':  # MAX
                    bonus_esquinas += 10
                else:  # MIN
                    bonus_esquinas -= 10
        
        # Penalización por bordes (pueden ser capturados fácilmente)
        penalizacion_bordes = 0
        for pos, ficha in board.items():
            x, y = pos
            if (x == 1 or x == state.game.width or 
                y == 1 or y == state.game.height):
                if ficha == 'B':  # MAX
                    penalizacion_bordes -= 2
                else:  # MIN
                    penalizacion_bordes += 2
        
        return diferencia_fichas + bonus_esquinas + penalizacion_bordes


class Solution3(StudentHeuristic):
    def get_name(self) -> str:
        return "movimientos_legales"

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



class Solution4(StudentHeuristic):
    def get_name(self) -> str:
        return "movimientos_legales"

    def evaluation_function(self, state: TwoPlayerGameState) -> float:
        return self.movimientos_legales(state)