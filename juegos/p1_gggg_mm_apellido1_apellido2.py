from dis import Positions
import numpy as np
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

dirs8 = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]
    # Pares de direcciones opuestas a comprobar (N-S, W-E, NW-SE, NE-SW)
direction_pairs = [((-1, 0), (1, 0)), ((0, -1), (0, 1)),
    ((-1, -1), (1, 1)), ((-1, 1), (1, -1))]

def _ray_all_same_or_reaches_stable(board, start: Tuple[int, int], dx: int, dy: int,
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
    """Calcula fichas estables y devuelve (normalized_diff, stable_count_perspective, stable_count_opponent).


    - `normalized_diff` en rango [-100, 100], análogo a otras componentes.
    - También devuelve los contadores crudos por si quieres ponderarlos.


    Nota: algoritmo iterativo que parte de esquinas y propaga estabilidad. No es
    100% perfecto en todos los tableros (hay definiciones teóricas muy complejas),
    pero es robusto y usado en muchas implementaciones prácticas.
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
                x, y = coord
                # Para cada par de direcciones (opuestas) comprobamos la condición
                pair_ok = True
                for (d1, d2) in direction_pairs:
                    ok1 = _ray_all_same_or_reaches_stable(board, coord, d1[0], d1[1], label, stable, width, height)
                    ok2 = _ray_all_same_or_reaches_stable(board, coord, d2[0], d2[1], label, stable, width, height)
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
        normalized = 0.0
    else:
        normalized = 100.0 * (stable_count_persp - stable_count_other) / total

    return normalized


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
        return "solution2"

    def evaluation_function(self, state: TwoPlayerGameState) -> float:
        # Si estado final, gana la que más casillas tenga
        if state.end_of_game:
            scores = state.scores
            return scores[0] - scores[1] if state.is_player_max(state.player1) else scores[1] - scores[0]
        

        # PESOS DE CADA PARÁMETRO
        w_mobility = 1.0                # Peso para movimientos válidos
        w_corners = 3.0                 # Peso para esquinas
        w_x_squares = w_corners*0.4     # Peso para las X_squares
        w_score = 0.0                   # Peso para el conteo total de piezas
        w_stability = 2                 # Peso para la estabilidad del tablero
        
        # Determinar quién es MAX (optimización: evitar múltiples llamadas)
        p1_max = state.is_player_max(state.player1)
        
        # Obtener datos del tablero una sola vez
        board = state.board
        height, width = state.game.height, state.game.width
        moves_made = len(board) - 4
        
        # Pre-calcular posiciones estratégicas
        corners = [(1, 1), (1, height), (width, 1), (width, height)]
        x_squares = [(2, 2), (2, height-1), (width-1, 2), (width-1, height-1)]
        
        # Obtener movimientos válidos (una sola llamada por jugador)
        valid_moves_p1 = state.game._get_valid_moves(board, state.game.player1.label)
        valid_moves_p2 = state.game._get_valid_moves(board, state.game.player2.label)
        
        # Calcular movilidad normalizada de [0-100]
        if valid_moves_p1 + valid_moves_p2 == 0:
            mobility = 0
        else:
            mobility = (100 *
            ((len(valid_moves_p1) - len(valid_moves_p2)) / 
            (len(valid_moves_p1) + len(valid_moves_p2))))
        
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
        
        # Contar X squares eficientemente
        p1_x_squares = 0
        p2_x_squares = 0
        for sq in x_squares:
            piece = board.get(sq)
            if piece == state.game.player1.label:
                p1_x_squares += 1
            elif piece == state.game.player2.label:
                p2_x_squares += 1
        # Calcular X squares normalizadas de [0-100]
        if p1_x_squares + p2_x_squares == 0:

            x_squares_diff = 0
        else:
            x_squares_diff = (100 *
            ((p1_x_squares - p2_x_squares) / 
            (p1_x_squares + p2_x_squares)))
        
        # Contar piezas totales eficientemente
        scores = state.scores
        # Calcular piezas totales normalizadas de [0-100]
        if scores[0] + scores[1] == 0:

            score = 0
        else:
            score = (100 *
            ((scores[0] - scores[1]) / 
            (scores[0] + scores[1])))
        
        stab_norm = stability_component(state, perspective_label=state.game.player1.label)
        
        # Calcular peso dinámico para X squares según la etapa de la partida
        if moves_made < 20:
            w_score *= 0.0
            w_mobility *= 1.0
            w_x_squares *= 1.0      # X squares muy malos al inicio
            w_stability *= 0.0
        elif moves_made < 40:
            w_score *= 0.1
            w_mobility *= 0.5
            w_x_squares *= 0.7      # X squares malos en etapa media
            w_stability *= 0.3
        elif moves_made < 50:
            w_score *= 0.5
            w_mobility *= 0.1
            w_x_squares *= 0.2      # X squares menos malos en etapa tardía
            w_stability *= 0.7
        else:
            w_score *= 1.0
            w_mobility *= 0.0
            w_x_squares *= 0.0      # X squares neutrales al final
            w_stability *= 1.0
        
        # Calcular evaluación final
        evaluation = (w_mobility * mobility + 
                     w_corners * corners_diff + 
                     w_x_squares * (-x_squares_diff) + 
                     w_score * score + 
                     w_stability * stab_norm)
        
        # Aplicar perspectiva del jugador MAX
        return evaluation if p1_max else -evaluation

class Solution3(StudentHeuristic):
    def get_name(self) -> str:
        return "solution3"

    def evaluation_function(self, state: TwoPlayerGameState) -> float:
        # let's use a global function
        return func_glob(2, state)