# ===== Utils adaptados a tu reversi.py (labels 'B'/'W', board dict 1-indexado) =====
from typing import Tuple
from tournament import StudentHeuristic
from game import TwoPlayerGameState

def _dims(state) -> Tuple[int, int]:
    return int(state.game.height), int(state.game.width)  # (h, w)

def _labels(state) -> Tuple[str, str]:
    max_label = state.player_max.label           # 'B' o 'W'
    min_label = state.game.opponent(state.player_max).label
    return max_label, min_label

def _count_label(board: dict, label: str) -> int:
    return sum(1 for v in board.values() if v == label)

def _mobility_for_label(state: TwoPlayerGameState, label: str) -> int:
    """
    Nº de jugadas del jugador con 'label' en ESTE tablero.
    Si el turno actual no es suyo, simulamos el cambio de turno
    manteniendo el mismo board.
    """
    game = state.game
    s = state if state.next_player.label == label else state.generate_successor(state.board)
    return len(game.generate_successors(s))

# ===================================================================================
# Heurística 1 — Material + Movilidad (sencilla, rápida, estable)
# ===================================================================================
class Solution1(StudentHeuristic):
    def get_name(self) -> str:
        return "sol1_material+mobility"

    def evaluation_function(self, state: TwoPlayerGameState) -> float:
        board = state.board
        maxL, minL = _labels(state)

        # Material
        my = _count_label(board, maxL)
        op = _count_label(board, minL)

        # Movilidad
        my_m = _mobility_for_label(state, maxL)
        op_m = _mobility_for_label(state, minL)

        # Ponderación: movilidad pesa un poco más al principio
        h, w = _dims(state)
        area = h * w
        filled = max(1, my + op)
        early_factor = 1.0 - min(1.0, filled / (area * 0.5))  # ~1 al inicio, ~0 hacia mitad

        return float(
            1.0 * (my - op) +
            (2.0 + 1.0 * early_factor) * (my_m - op_m)
        )

# ===================================================================================
# Heurística 2 — Posicional: Esquinas + Bordes + Centro + Movilidad
# ===================================================================================
class Solution2(StudentHeuristic):
    def get_name(self) -> str:
        return "sol2_positional"

    def evaluation_function(self, state: TwoPlayerGameState) -> float:
        board = state.board
        h, w = _dims(state)
        maxL, minL = _labels(state)

        # Esquinas
        corners = [(1,1), (1,h), (w,1), (w,h)]
        my_c = sum(1 for c in corners if board.get(c) == maxL)
        op_c = sum(1 for c in corners if board.get(c) == minL)

        # Bordes (todas las casillas del perímetro)
        edge_coords = (
            [(1, y) for y in range(1, h+1)] + [(w, y) for y in range(1, h+1)] +
            [(x, 1) for x in range(1, w+1)] + [(x, h) for x in range(1, w+1)]
        )
        edge_set = set(edge_coords)
        my_e = sum(1 for p in edge_set if board.get(p) == maxL)
        op_e = sum(1 for p in edge_set if board.get(p) == minL)

        # Centro 4x4 (si cabe), útil en early/mid
        cx0, cx1 = (h//2 - 1), (h//2 + 2)
        cy0, cy1 = (w//2 - 1), (w//2 + 2)
        center = [(x,y) for x in range(max(1,cx0), min(h+1,cx1))
                         for y in range(max(1,cy0), min(w+1,cy1))]
        my_ctr = sum(1 for p in center if board.get(p) == maxL)
        op_ctr = sum(1 for p in center if board.get(p) == minL)

        # Movilidad
        my_m = _mobility_for_label(state, maxL)
        op_m = _mobility_for_label(state, minL)

        return float(
            25 * (my_c - op_c) +    # Esquinas = clave
             5 * (my_e - op_e) +    # Bordes
             2 * (my_m - op_m) +    # Movilidad
             1 * (my_ctr - op_ctr)  # Centro
        )

# ===================================================================================
# Heurística 3 — Fase adaptativa + penalización X/C (casillas peligrosas)
# ===================================================================================
class Solution3(StudentHeuristic):
    def get_name(self) -> str:
        return "sol3_phase+corner_safety"

    def evaluation_function(self, state: TwoPlayerGameState) -> float:
        board = state.board
        h, w = _dims(state)
        maxL, minL = _labels(state)

        # Material y fase
        my = _count_label(board, maxL)
        op = _count_label(board, minL)
        area = h * w
        phase = (my + op) / max(1.0, float(area))  # 0..1

        # Pesos por fase
        if phase < 0.33:         # early: movilidad y evitar X/C
            W_MOB, W_MAT, W_EDGE, W_CORN, W_CTR = 3.0, 0.5, 2.0, 25.0, 1.5
            PEN_X, PEN_C = 8.0, 4.0
        elif phase < 0.66:       # mid: equilibrio
            W_MOB, W_MAT, W_EDGE, W_CORN, W_CTR = 2.0, 1.0, 3.0, 30.0, 1.0
            PEN_X, PEN_C = 6.0, 3.0
        else:                    # late: material + estabilidad
            W_MOB, W_MAT, W_EDGE, W_CORN, W_CTR = 1.0, 3.0, 4.0, 35.0, 0.5
            PEN_X, PEN_C = 2.0, 1.0

        # Esquinas
        corners = [(1,1), (1,h), (w,1), (w,h)]
        my_c = sum(1 for c in corners if board.get(c) == maxL)
        op_c = sum(1 for c in corners if board.get(c) == minL)

        # X-squares (diagonales a la esquina) y C-squares (adyacentes por borde), 1-index
        Xs = [(2,2), (2,h-1), (w-1,2), (w-1,h-1)]
        Cs = [(1,2),(2,1),(1,h-1),(2,h), (w-1,1),(w,2),(w,h-1),(w-1,h)]

        # Penaliza X/C si NO posees la esquina asociada
        pen_my = pen_op = 0.0
        groups = [
            ((1,1),     [(2,2)],     [(1,2),(2,1)]),
            ((1,h),     [(2,h-1)],   [(1,h-1),(2,h)]),
            ((w,1),     [(w-1,2)],   [(w-1,1),(w,2)]),
            ((w,h),     [(w-1,h-1)], [(w,h-1),(w-1,h)]),
        ]
        for corner, xs, cs in groups:
            owner = board.get(corner, None)
            corner_my = (owner == maxL)
            corner_op = (owner == minL)
            if not corner_my:
                pen_my += PEN_X * sum(1 for p in xs if board.get(p) == maxL)
                pen_my += PEN_C * sum(1 for p in cs if board.get(p) == maxL)
            if not corner_op:
                pen_op += PEN_X * sum(1 for p in xs if board.get(p) == minL)
                pen_op += PEN_C * sum(1 for p in cs if board.get(p) == minL)

        # Bordes (perímetro)
        edge_coords = (
            [(1, y) for y in range(1, h+1)] + [(w, y) for y in range(1, h+1)] +
            [(x, 1) for x in range(1, w+1)] + [(x, h) for x in range(1, w+1)]
        )
        edge_set = set(edge_coords)
        my_e = sum(1 for p in edge_set if board.get(p) == maxL)
        op_e = sum(1 for p in edge_set if board.get(p) == minL)

        # Centro (4x4 si cabe)
        cx0, cx1 = (h//2 - 1), (h//2 + 2)
        cy0, cy1 = (w//2 - 1), (w//2 + 2)
        center = [(x,y) for x in range(max(1,cx0), min(h+1,cx1))
                         for y in range(max(1,cy0), min(w+1,cy1))]
        my_ctr = sum(1 for p in center if board.get(p) == maxL)
        op_ctr = sum(1 for p in center if board.get(p) == minL)

        # Movilidad
        my_m = _mobility_for_label(state, maxL)
        op_m = _mobility_for_label(state, minL)

        score = (
            W_CORN * (my_c - op_c) +
            W_EDGE * (my_e - op_e) +
            W_MOB  * (my_m - op_m) +
            W_MAT  * (my - op)     +
            W_CTR  * (my_ctr - op_ctr) -
            (pen_my - pen_op)
        )
        return float(score)