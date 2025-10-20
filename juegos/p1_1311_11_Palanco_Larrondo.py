import numpy as np

from typing import Tuple, Set, Sequence
from game import (
    TwoPlayerGameState,
)
from tournament import (
    StudentHeuristic,
)

# Pares de direcciones opuestas a comprobar (N-S, W-E, NW-SE, NE-SW)
direction_pairs = [((-1, 0), (1, 0)), ((0, -1), (0, 1)), ((-1, -1), (1, 1)), ((-1, 1), (1, -1))]

def _line_all_same_or_stable(board, start: Tuple[int, int], dx: int, dy: int,
    player_label: str, stable_set: Set[Tuple[int, int]],
    width: int, height: int) -> bool:
        """
        Recorre desde la casilla *start* en la dirección (dx,dy).
        - Si encuentra una casilla vacía o del adversario devuelve False.
        - Si alcanza una casilla estable del mismo color devuelve True.
        - Si llega al borde (salir del tablero) habiendo encontrado solo fichas
        del mismo color devuelve True (cadena sólida hasta el borde).
        """
        x, y = start
        x += dx
        y += dy
        while 1 <= x <= width and 1 <= y <= height:
            val = board.get((x, y))
            if val is None:
                return False
            if val != player_label:
                return False
            if (x, y) in stable_set:
                return True
            x += dx
            y += dy
        # Si salimos del while, hemos recorrido hasta el borde sin interrupciones del color
        return True

def stability_component(state, perspective_label: str = None) -> float:
    """
    Calcula fichas estables y devuelve stability_norm.
    - `stability_norm` en rango [-1, 1], análogo a otras componentes.
    """
    board = state.board
    width = state.game.width
    height = state.game.height


    p1_label = state.game.player1.label
    p2_label = state.game.player2.label
    if perspective_label is None:
        perspective_label = p1_label
    other_label = p2_label if perspective_label == p1_label else p1_label


    def compute_stable_for_label(label: str) -> Set[Tuple[int, int]]:
        stable: Set[Tuple[int, int]] = set()
        # Empezamos por las esquinas propias
        corners = [(1, 1), (1, height), (width, 1), (width, height)]
        for c in corners:
            if board.get(c) == label:
                stable.add(c)


        changed = True
        # Iteramos hasta que no cambie el conjunto de estables
        while changed:
            changed = False
            # Recorremos todo el tablero
            # Nota: podrías optimizar iterando solo sobre piezas del color `label`.
            for coord, val in board.items():
                if val != label or coord in stable:
                    continue
                # Para cada par de direcciones (opuestas) comprobamos la condición
                pair_ok = True
                for (d1, d2) in direction_pairs:
                    ok1 = _line_all_same_or_stable(board, coord, d1[0], d1[1], label, stable, width, height)
                    ok2 = _line_all_same_or_stable(board, coord, d2[0], d2[1], label, stable, width, height)
                    if not (ok1 or ok2):
                        pair_ok = False
                        break
                    if pair_ok:
                        stable.add(coord)
                        changed = True
        return stable


    stable_persp = compute_stable_for_label(perspective_label)
    stable_other = compute_stable_for_label(other_label)


    stable_count_persp = len(stable_persp)
    stable_count_other = len(stable_other)
    total = stable_count_persp + stable_count_other
    
    if total == 0:
        stability_norm = 0.0
    else:
        stability_norm = (stable_count_persp - stable_count_other) / total

    return stability_norm


class Solution1(StudentHeuristic):
    def get_name(self) -> str:
        return "JA1"

    def evaluation_function(self, state: TwoPlayerGameState) -> float:
        # Determinar quién es MAX (optimización: evitar múltiples llamadas)
        p1_max = state.is_player_max(state.player1)

        # let's use a global function
        board = state.board
        height, width = state.game.height, state.game.width
        corners = [(1, 1), (1, height), (width, 1), (width, height)]

        # Contar esquinas eficientemente
        p1_corners = 0
        p2_corners = 0
        for corner in corners:
            piece = board.get(corner)
            if piece == state.game.player1.label:
                p1_corners += 1
            elif piece == state.game.player2.label:
                p2_corners += 1

        # Calcular esquinas normalizadas de [0-100]
        if p1_corners + p2_corners == 0:
            corners_diff = 0
        else:
            corners_diff = 1000*((p1_corners - p2_corners) / 
                            (p1_corners + p2_corners))
        
        # Obtener movimientos válidos (una sola llamada por jugador)
        valid_moves_p1 = len(state.game._get_valid_moves(board, state.game.player1.label))
        valid_moves_p2 = len(state.game._get_valid_moves(board, state.game.player2.label))
        
        # Calcular movilidad normalizada de [0-100]
        if valid_moves_p1 + valid_moves_p2 == 0:
            mobility = 0
        else:
            mobility = 1000*((valid_moves_p1 - valid_moves_p2) / 
                        (valid_moves_p1 + valid_moves_p2))
        
        # Calcular la estabilidad normalizada de [0-100]
        stab_norm = 1000*stability_component(state, perspective_label=state.game.player1.label)


        evaluation = corners_diff + mobility + stab_norm
        
        return evaluation if p1_max else -evaluation

class Solution2(StudentHeuristic):
    def get_name(self) -> str:
        return "JuanAbril2"

    def evaluation_function(self, state: TwoPlayerGameState) -> float:
        # Si estado final, gana la que más casillas tenga
        if state.end_of_game:
            scores = state.scores
            return scores[0] - scores[1] if state.is_player_max(state.player1) else scores[1] - scores[0]
        

        # PESOS DE CADA PARÁMETRO
        w_mobility = 1.12                # Peso para movimientos válidos
        w_corners = 3.25                 # Peso para esquinas
        w_stability = 1.11               # Peso para la estabilidad del tablero
        
        # Determinar quién es MAX (optimización: evitar múltiples llamadas)
        p1_max = state.is_player_max(state.player1)
        
        # Obtener datos del tablero una sola vez
        board = state.board
        height, width = state.game.height, state.game.width
        
        # Pre-calcular posiciones estratégicas
        corners = [(1, 1), (1, height), (width, 1), (width, height)]
        
        # Obtener movimientos válidos (una sola llamada por jugador)
        valid_moves_p1 = len(state.game._get_valid_moves(board, state.game.player1.label))
        valid_moves_p2 = len(state.game._get_valid_moves(board, state.game.player2.label))
        
        # Calcular movilidad normalizada de [0-100]
        if valid_moves_p1 + valid_moves_p2 == 0:
            mobility = 0
        else:
            mobility = (100 *
            ((valid_moves_p1 - valid_moves_p2) / 
            (valid_moves_p1 + valid_moves_p2)))
        
        # Contar esquinas eficientemente
        p1_corners = 0
        p2_corners = 0
        for corner in corners:
            piece = board.get(corner)
            if piece == state.game.player1.label:
                p1_corners += 1
            elif piece == state.game.player2.label:
                p2_corners += 1
        # Calcular esquinas normalizadas de [0-100]
        if p1_corners + p2_corners == 0:
            corners_diff = 0
        else:
            corners_diff = (100 *
            ((p1_corners - p2_corners) / 
            (p1_corners + p2_corners)))
        
        stab_norm = 100*stability_component(state, perspective_label=state.game.player1.label)
        
        # Calcular evaluación final
        evaluation = (w_mobility * mobility + 
                     w_corners * corners_diff + 
                     w_stability * stab_norm)
        
        # Aplicar perspectiva del jugador MAX
        return evaluation if p1_max else -evaluation


        
class Solution3(StudentHeuristic):
    
    def get_name(self) -> str:
        return "AbrilJuan3"

    def evaluation_function(self, state: TwoPlayerGameState) -> float:
        # Si estado final, gana la que más casillas tenga
        if state.end_of_game:
            scores = state.scores
            return scores[0] - scores[1] if state.is_player_max(state.player1) else scores[1] - scores[0]

        # PESOS DE CADA PARÁMETRO
        w_mobility = 1.0                # Peso para movimientos válidos
        w_corners = 1.0                 # Peso para esquinas
        w_stability = 1.0               # Peso para la estabilidad del tablero
        
        # Determinar quién es MAX (optimización: evitar múltiples llamadas)
        p1_max = state.is_player_max(state.player1)
        
        # Obtener datos del tablero una sola vez
        board = state.board
        height, width = state.game.height, state.game.width
        moves_made = len(board) - 4
        
        # Pre-calcular posiciones estratégicas
        corners = [(1, 1), (1, height), (width, 1), (width, height)]
        
        # Obtener movimientos válidos (una sola llamada por jugador)
        valid_moves_p1 = len(state.game._get_valid_moves(board, state.game.player1.label))
        valid_moves_p2 = len(state.game._get_valid_moves(board, state.game.player2.label))

        # Calcular movilidad normalizada de [-1, 1]
        if valid_moves_p1 + valid_moves_p2 == 0:
            mobility = 0
        else:
            mobility = ((valid_moves_p1 - valid_moves_p2) / (valid_moves_p1 + valid_moves_p2))
        
        # Contar esquinas eficientemente
        p1_corners = 0
        p2_corners = 0
        for corner in corners:
            piece = board.get(corner)
            if piece == state.game.player1.label:
                p1_corners += 1
            elif piece == state.game.player2.label:
                p2_corners += 1
        
        # Calcular esquinas normalizadas de [-1, 1]
        if p1_corners + p2_corners == 0:
            corners_diff = 0
        else:
            corners_diff = (((p1_corners - p2_corners) / (p1_corners + p2_corners)))
#                             * ((p1_corners + p2_corners) / 4))
        
        # Calcular estabilidad normalizada a [-1, 1]
        stab_norm = stability_component(state, perspective_label=state.game.player1.label)
        
        # Calcular pesos según la etapa de la partida
        max = width*height - 4
        if moves_made < max*(20/60):
#            mobility * ((p1_corners + p2_corners) / 7)
            w_mobility *= 33
            w_corners *= 52
            w_stability *= 15
        elif moves_made < max*(40/60):
#            mobility * ((p1_corners + p2_corners) / 12)
            w_mobility *= 46
            w_corners *= 31
            w_stability *= 23
        elif moves_made < max*(50/60):
#            mobility * ((p1_corners + p2_corners) / 6)
            w_mobility *= 22
            w_corners *= 29
            w_stability *= 49
        else:
#            mobility * ((p1_corners + p2_corners) / 4)
            w_mobility *= 16
            w_corners *= 23
            w_stability *= 61
        
        # Calcular evaluación final
        evaluation = (w_mobility * mobility + 
                     w_corners * corners_diff + 
                     w_stability * stab_norm)
        
        # Aplicar perspectiva del jugador MAX
        return evaluation if p1_max else -evaluation