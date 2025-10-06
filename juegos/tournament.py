"""Infrastructure for tournament.

   Author:
        Alejandro Bellogin <alejandro.bellogin@uam.es>
"""

from __future__ import annotations  # For Python 3.7

import p1_1311_11_Palanco_Larrondo as p
import inspect  # for dynamic members of a module
import os
import sys
import time
from abc import ABC
from importlib import util
import traceback
from typing import Callable, Tuple
import numpy as np

from game import Player, TwoPlayerGameState, TwoPlayerMatch
from heuristic import Heuristic
from strategy import MinimaxStrategy
"""
NOTE: When MinimaxAlphaBetaStrategy has been implemented
replace MinimaxAlphaBetaStrategy for MinimaxStrategy,
so that the tournament runs faster.
"""
from strategy import MinimaxAlphaBetaStrategy


class StudentHeuristic(ABC):
    def __init__(self):
        pass

    def evaluation_function(self, state: TwoPlayerGameState) -> float:
        pass

    def get_name(self) -> str:
        pass


class Tournament(object):
    def __init__(self, max_depth: int,
                 init_match: Callable[[Player, Player], TwoPlayerMatch],
                 max_evaluation_time: float):
        self.__max_depth = max_depth
        self.__init_match = init_match
        self.__max_eval_time = max_evaluation_time
        self.h1_time = None
        self.reference_measured = False

    def _measure_reference_time(self, depth: int):
        """Mide el tiempo de una partida completa con Heuristic1 como referencia"""
        try:
            from demo_tournament import Heuristic1
            from game import Player
            from strategy import MinimaxAlphaBetaStrategy
            from heuristic import Heuristic
            
            # Crear dos jugadores con Heuristic1 usando EXACTAMENTE los mismos parámetros
            ref_heuristic = Heuristic1()
            pl1 = Player(
                name="ref1",
                strategy=MinimaxAlphaBetaStrategy(
                    heuristic=Heuristic(
                        name=ref_heuristic.get_name(),
                        evaluation_function=ref_heuristic.evaluation_function),
                    max_depth_minimax=depth,  # ← MISMO DEPTH que las partidas reales
                    max_sec_per_evaluation=self.__max_eval_time,
                    verbose=0,
                ),
            )
            pl2 = Player(
                name="ref2", 
                strategy=MinimaxAlphaBetaStrategy(
                    heuristic=Heuristic(
                        name=ref_heuristic.get_name(),
                        evaluation_function=ref_heuristic.evaluation_function),
                    max_depth_minimax=depth,  # ← MISMO DEPTH que las partidas reales
                    max_sec_per_evaluation=self.__max_eval_time,
                    verbose=0,
                ),
            )
            
            # Medir tiempo de partida completa (promedio de 3 partidas)
            # Usar EXACTAMENTE el mismo tablero que las partidas normales
            times = []
            for _ in range(3):
                start = time.perf_counter()
                # Usar el mismo __single_run que las partidas normales
                # Esto garantiza que use el MISMO tablero inicial
                self.__single_run(True, pl1, "ref1", pl2, "ref2", {}, {})
                end = time.perf_counter()
                times.append(end - start)
            
            self.h1_time = sum(times) / len(times)
            self.reference_measured = True
            print(f"Tiempo de referencia (Heuristic1, depth={depth}): {self.h1_time:.4f}s")
            
        except Exception as e:
            print(f"Error midiendo tiempo de referencia: {e}")
            self.h1_time = 0.1  # Fallback a valor estimado
            self.reference_measured = True

    def __get_function_from_str(self, name: str, definition: str, max_strat: int) -> list:
        # write content in file with new name
        newfile = "playermodule__" + name
        with open(newfile, 'w') as fp:
            print(definition, file=fp)
        student_classes = list()
        n_strat = 0
        # not needed, but this hack somehow fixes some files not being loaded
        time.sleep(1)
        sp = util.find_spec(newfile.replace(".py", ""))
        if sp:
            m = sp.loader.load_module()
            # return all the objects that satisfy the function signature
            for name, obj in inspect.getmembers(m, inspect.isclass):
                if name != "StudentHeuristic":
                    for name2, obj2 in inspect.getmembers(obj, inspect.isfunction):
                        if name2 == "evaluation_function" and n_strat < max_strat:
                            student_classes.append(obj)
                            n_strat += 1
                        elif name2 == "evaluation_function":
                            print("Ignoring evaluation function in %s because limit of submissions was reached (%d)" % (
                                name, max_strat), file=sys.stderr)
                    # end for
            # end for
        # remove file
        os.remove(newfile)
        return student_classes

    #   we assume there is one file for each student/pair
    def load_strategies_from_folder(self, folder: str, max_strat: int = 3) -> dict:
        student_strategies = dict()
        for f in os.listdir(folder):
            p = os.path.join(folder, f)
            if os.path.isfile(p):
                with open(p, 'r') as fp:
                    s = fp.read()
                    name = f
                    strategies = self.__get_function_from_str(
                        name, s, max_strat)
                    student_strategies[f] = strategies
        return student_strategies

    def run(self, student_strategies: dict, increasing_depth: bool = True,
            n_pairs: int = 1, allow_selfmatch: bool = False) -> Tuple[dict, dict, dict]:
        """
        Play a tournament among the strategies.
        n_pairs = games each strategy plays as each color against
        each opponent. So with N strategies, a total of
        N*(N-1)*n_pairs games are played.
        """
        time_min = np.inf
        time_max = 0
        scores = dict()
        totals = dict()
        name_mapping = dict()
        for student1 in student_strategies:
            strats1 = student_strategies[student1]
            for student2 in student_strategies:
                if student1 > student2:
                    continue
                if student1 == student2 and not allow_selfmatch:
                    continue
                strats2 = student_strategies[student2]
                for player1 in strats1:
                    for player2 in strats2:
                        # we now instantiate the players
                        for pair in range(2*n_pairs):
                            player1_first = (pair % 2) == 1
                            sh1 = player1()
                            name1 = student1 + "_" + sh1.get_name()
                            name_mapping[name1] = sh1.get_name()
                            sh2 = player2()
                            name2 = student2 + "_" + sh2.get_name()
                            name_mapping[name2] = sh2.get_name()
                            if increasing_depth:
                                for depth in range(1, self.__max_depth):
                                    pl1 = Player(
                                        name=name1,
                                        strategy=MinimaxAlphaBetaStrategy(  # MinimaxStrategy(
                                            heuristic=Heuristic(
                                                name=sh1.get_name(),
                                                evaluation_function=sh1.evaluation_function),
                                            max_depth_minimax=depth,
                                            max_sec_per_evaluation=self.__max_eval_time,
                                            verbose=0,
                                        ),
                                    )
                                    pl2 = Player(
                                        name=name2,
                                        strategy=MinimaxAlphaBetaStrategy(  # MinimaxStrategy(
                                            heuristic=Heuristic(
                                                name=sh2.get_name(),
                                                evaluation_function=sh2.evaluation_function),
                                            max_depth_minimax=depth,
                                            max_sec_per_evaluation=self.__max_eval_time,
                                            verbose=0,
                                        ),
                                    )

                                    self.__single_run(
                                        player1_first, pl1, name1, pl2, name2, scores, totals)
                            else:
                                depth = self.__max_depth
                                pl1 = Player(
                                    name=name1,
                                    strategy=MinimaxAlphaBetaStrategy(  # MinimaxStrategy(
                                        heuristic=Heuristic(
                                            name=sh1.get_name(),
                                            evaluation_function=sh1.evaluation_function),
                                        max_depth_minimax=depth,
                                        max_sec_per_evaluation=self.__max_eval_time,
                                        verbose=0,
                                    ),
                                )
                                pl2 = Player(
                                    name=name2,
                                    strategy=MinimaxAlphaBetaStrategy(  # MinimaxStrategy(
                                        heuristic=Heuristic(
                                            name=sh2.get_name(),
                                            evaluation_function=sh2.evaluation_function),
                                        max_depth_minimax=depth,
                                        max_sec_per_evaluation=self.__max_eval_time,
                                        verbose=0,
                                    ),
                                )
                                # Medir tiempo de referencia si no se ha hecho (con el mismo depth)
#                                if not self.reference_measured:
#                                    self._measure_reference_time(depth)
                                
                                # Medir tiempo de la partida
#                                start_time = time.perf_counter()
                                self.__single_run(
                                    player1_first,
                                    pl1, name1,
                                    pl2, name2,
                                    scores, totals)
#                                end_time = time.perf_counter()
#                                game_time = end_time - start_time
#                                
#                                if self.h1_time is not None:
#                                    if game_time > self.h1_time * 10:
#                                        print(f"DESCALIFICADO: {game_time:.4f}s > {self.h1_time*10:.4f}s")
#                                    else:
#                                        print(f"OK: {game_time:.4f}s <= {self.h1_time*10:.4f}s")

        return scores, totals, name_mapping

    def __single_run(self, player1_first: bool, pl1: Player, name1: str,
                     pl2: Player, name2: str, scores: dict, totals: dict):
        players = []
        if player1_first:
            players = [pl1, pl2]
        else:
            players = [pl2, pl1]
        game = self.__init_match(players[0], players[1])
        try:
            game_scores = game.play_match()
            # let's get the scores (do not assume they will always be binary)
            # we assume a higher score is better
            if player1_first:
                score1, score2 = game_scores[0], game_scores[1]
            else:
                score1, score2 = game_scores[1], game_scores[0]
            wins = loses = 0
            if score1 > score2:
                wins, loses = 1, 0
            elif score2 > score1:
                wins, loses = 0, 1
        except Warning:
            wins = loses = 0
        # store the 1-to-1 numbers
        if name1 not in scores:
            scores[name1] = dict()
        if name2 not in scores:
            scores[name2] = dict()
        scores[name1][name2] = wins if name2 not in scores[name1] else wins + \
            scores[name1][name2]
        scores[name2][name1] = loses if name1 not in scores[name2] else loses + \
            scores[name2][name1]
        # store the total values
        if name1 not in totals:
            totals[name1] = 0
        totals[name1] += wins
        if name2 not in totals:
            totals[name2] = 0
        totals[name2] += loses
        # end of function