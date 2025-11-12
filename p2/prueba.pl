consult('prueba.pl').
consult('p27.pl').
%# cargar la base de conocimiento

%# ver cómo se va ejecutando
%trace.
%# cómo quitarlo
%notrace.
%nodebug.

%# ejecutar la consulta
%prod([1,2,3,4,5], X).
%write(X).

%# cerrar swipl
%halt.

prod([],1) :- !.
prod([X|Y], Z) :- prod(Y,K), Z is X*K.

%Ej1
my_last(X, [X|[]]) :- !.
my_last(X, [_|T]) :- my_last(X,T).

%Ej2
my_pre_last(X, [X|[]]) :- print('Error'), !, fail.
my_pre_last(X, [X|[_|[]]]) :- !.
my_pre_last(X, [_|T]) :- my_pre_last(X,T).
%my_pre_last(X, [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]).
%my_pre_last(X, [1]).

%Ej3
k_element(K, [K|_], 1) :- !.
k_element(K, [_|B], N) :- M is N-1, k_element(K,B,M).
%k_element(X, [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19], 7).

%Ej4: Find the number of elements of a list.
n_elements(0, []) :- !.
n_elements(X, [_|T]) :- n_elements(N, T), X is N+1.
%n_elements(X, [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]).

%Ej5: Reverse a list.
my_reverse(L1,L2) :- my_rev(L1,L2,[]).

my_rev([],L2,L2) :- !.
my_rev([X|Xs],L2,Acc) :- my_rev(Xs,L2,[X|Acc]).

%my_reverse([1,2,3,4,5,6,7,8,9], X).

%Ej6: Palyndrome
igual(A, A).

pal(L1) :- my_reverse(L1, L2), igual(L1, L2).
%pal([1,2,2,1]).

%Ej7: Flatten a nested list structure.
my_flatten(L, X) :- my_flatten_r(L, [], [], X).

my_flatten_r([H|T], Lf, [], X) :- my_flatten_r(T, Lf, H, X).
my_flatten_r([], Lf, [], Lf) :- !.

my_flatten_r(Lo, Lf, E, X) :- 
    is_list(E), 
    my_flatten_r(E, Lf, [], Lf1),
    my_flatten_r(Lo, Lf1, [], X).

my_flatten_r(Lo, Lf, E, X) :- 
    not(is_list(E)), 
    append(Lf, [E], Lf2),
    my_flatten_r(Lo, Lf2, [], X).

%my_flatten([a, [b, [c, d], e]], X).

%Ej8: Compress a list.
compress(L, X) :- compress(L, [], X).
compress([H|[]], L, X) :- append(L, [H], X).
compress([H|[H|T]], L, X) :- compress([H|T], L, X).
compress([H|[H1|T]], L, X) :- append(L, [H], L1), compress([H1|T], L1, X).
%compress([a,a,a,a,b,c,c,a,a,d,e,e,e,e],X).

%Ej9: Pack consecutive duplicates of list elements into sublists.
pack(L, X) :- my_pack(L, [], [], X).

my_pack([H|[]], L, L1, X) :- 
    append(L1, [H], L2), 
    append(L, [L2], X).

my_pack([H|[H|T]], L, L1, X) :- 
    append(L1, [H], L2), 
    my_pack([H|T], L, L2, X).

my_pack([H|[H1|T]], L, L1, X) :- 
    append(L1, [H], L2), 
    append(L, [L2], L3), 
    my_pack([H1|T], L3, [], X).
%pack([a,a,a,a,b,c,c,a,a,d,e,e,e,e],X).

%Ej10:
encode(L, X) :- my_encode(L, [], 1, X).

my_encode([H|[]], L, N, X) :- 
    append(L, [[N, H]], X).

my_encode([H|[H|T]], L, N, X) :- 
    M is N+1, 
    my_encode([H|T], L, M, X).

my_encode([H|[H1|T]], L, N, X) :- 
    append(L, [[N, H]], L1), 
    my_encode([H1|T], L1, 1, X).
    
%encode([a,a,a,a,b,c,c,a,a,d,e,e,e,e],X).

%Ej11:
encode_modified(L, X) :- my_encode_modified(L, [], 1, X).

my_encode_modified([H|[]], L, 1, X) :- 
    append(L, [H], X).

my_encode_modified([H|[]], L, N, X) :- 
    append(L, [[N, H]], X).

my_encode_modified([H|[H|T]], L, N, X) :- 
    M is N+1, 
    my_encode_modified([H|T], L, M, X).

my_encode_modified([H|[H1|T]], L, 1, X) :- 
    append(L, [H], L1), 
    my_encode_modified([H1|T], L1, 1, X).

my_encode_modified([H|[H1|T]], L, N, X) :- 
    append(L, [[N, H]], L1), 
    my_encode_modified([H1|T], L1, 1, X).
    
%encode_modified([a,a,a,a,b,c,c,a,a,d,e,e,e,e],X).

%Ej12:
decode(Lo, X) :- my_decode(Lo, [], 0, _, X).

my_decode([], Lf, 0, _, Lf) :- !.
my_decode([[N,E]|T], Lf, 0, _, X) :- my_decode(T, Lf, N, E, X).
my_decode([E|T], Lf, 0, _, X) :- my_decode(T, Lf, 1, E, X).
my_decode(Lo, Lf, N, E, X) :- M is N-1, append(Lf, [E], Lf2), my_decode(Lo, Lf2, M, E, X).

%decode([[4,a],b,[2,c],[2,a],d,[4,e]], X).

%Ej13: Es como hemos hecho el 10

%Ej14: Duplicate elements of list
my_dupli([], L, L) :- !.
my_dupli([H|T], X, L) :- append(L, [H,H], L1), my_dupli(T, X, L1).

dupli(L, X) :- my_dupli(L, X, []).
%dupli([a,b,c,c,d],X).

%Ej15: Duplicate n times
dupli(L, N, X) :- my_dupli(L, N, [], X).

my_dupli([], _, L, L) :- !.
my_dupli([H|T], N, L, X) :- n_times(H, N, [], L1), append(L, L1, L2), my_dupli(T, N, L2, X).

n_times(_, 0, L, L) :- !.
n_times(H, N, L, L1) :- append(L, [H], L3), M is N-1, n_times(H, M, L3, L1).
%

%Ej16: Drop every Nth item
drop(L, N, X) :- M is N-1, my_drop(L, M, [], M, X).

my_drop([], _, X, _, X) :- !.
my_drop([_|T], 0, L, M, X) :- my_drop(T, M, L, M, X).
my_drop([H|T], N, L, M, X) :- append(L, [H], L1), N1 is N-1, my_drop(T, N1, L1, M, X).
%drop([a,b,c,d,e,f,g,h,i,k],3,X).

%Ej17:
split(Lo, N, X1, X2) :- my_split(Lo, N, [], X1, X2).

my_split(L, 0, X1, X1, L) :- !.
my_split([H|T], N, L1, X1, X2) :- M is N-1, append(L1, [H], L3), my_split(T, M, L3, X1, X2).

%split([a,b,c,d,e,f,g,h,i,j,k],3,L1,L2).

%Ej18:
slice(Lo, I, K, X) :- I1 is I-1, split(Lo, I1, _, L), K1 is K-I1, split(L, K1, X, _).

%slice([a,b,c,d,e,f,g,h,i,k],3,7,L).

%Ej19:
rotate(L,N,X) :- N < 0, length(L, Len), M is Len+N, my_rotate(L,M,X).
rotate(L,N,X) :- my_rotate(L,N,X).

my_rotate(L, N, X) :- split(L, N, X1, X2), append(X2, X1, X).

%rotate([a,b,c,d,e,f,g,h],3,X).
%rotate([a,b,c,d,e,f,g,h],-2,X).

%Ej20:
remove_at(X, L, N, R) :- M is N-1, split(L, M, L1, [X|T]), append(L1, T, R).

%remove_at(X, [a,b,c,d,e,f,g,h], 3, R).

%Ej21:
insert_at(X, L, N, R) :- M is N-1, split(L, M, L1, L2), append(L1, [X|L2], R).

%insert_at(alfa, [a,b,c,d,e,f,g,h], 3, L).

%Ej22:
range(A, B, X) :- A =< B, my_range(A, B, [], X).

my_range(A, B, X, X) :- A > B.
my_range(A, B, L, X) :- append(L, [A], L1), A1 is A+1, my_range(A1, B, L1, X).

%range(4,9,L).

%Ej23:
rnd_select(L, N, X) :- is_list(L), not(is_list(N)), my_rnd_select(L, N, [], X).
my_rnd_select(_, 0, X, X).
my_rnd_select(Lo, N, L, X) :- length(Lo, Len), U is Len+1, random(1, U, Rand), M is N-1, remove_at(E, Lo, Rand, L1), append(L, [E], L2), my_rnd_select(L1, M, L2, X).

%rnd_select([a,b,c,d,e,f,g,h],3,L).

%Ej24:
rnd_select(N, M, X) :- not(is_list(N)), not(is_list(M)), range(1, M, L), rnd_select(L, N, X).

%rnd_select(6,49,L).

%Ej25:
rnd_permu(L, X) :- length(L, N), rnd_select(L, N, X).

%rnd_permu([a,b,c,d,e,f],L).

%Ej26: Generate the combinations of K distinct objects chosen from the N elements of a list
combination(0, _, []).
combination(N, Lo, [H|T]) :- N > 0, eliminar(Lo, Lo, 1, H, L1), M is N-1, combination(M, L1, T).

eliminar(Lo, [H|T], N, E, X) :- not(is_list(E)), igual(H,E), remove_at(E, Lo, N, X).
eliminar(Lo, [H|T], N, E, X) :- length(Lo, Len), N < Len, not(is_list(E)), M is N+1, eliminar(Lo, T, M, E, X).

%combination(2, [1,2,3], L).

%Ej27a: In how many ways can a group of 9 people work in 3 disjoint subgroups of 2, 3 and 4 persons?
%       Write a predicate that generates all the possibilities via backtracking.
group3(L,G1,G2,G3) :- my_combination(2, L, L, G1, L1), my_combination(3, L1, L1, G2, G3).

my_combination(0, Lf, _, [], Lf).
my_combination(N, Lo, LTo, [H|T], Lf) :- 
    N > 0, 
    length(Lo, N1), length(LTo, N2), N3 is N1-N2+1, 
    my_eliminar(Lo, LTo, N3, H, LTail, Lneta), 
    M is N-1, 
    my_combination(M, Lneta, LTail, T, Lf).

my_eliminar(Lo, [H|T], N, H, T, X) :- remove_at(_, Lo, N, X).
my_eliminar(Lo, [H|T], N, E, Y, X) :- length(Lo, Len), N < Len, M is N+1, my_eliminar(Lo, T, M, E, Y, X).

%group3([1,2,3,4,5,6,7,8,9],G1,G2,G3).
%my_eliminar([1,2,3,4,5], [3,4,5], 3, H, LTail, Lneta).

%Ej27b:

%Ej28:

%Ej29:

%Ej30:

%Ej31:

%Ej32:

%Ej33:

%Ej34:

%Ej35:

%Ej36:

%Ej37:

%Ej38:

%Ej39:

%Ej40:

%Ej41:

%Ej42:

%Ej43:

%Ej44:

%Ej45:

%Ej46:

%Ej47:

%Ej48:

%Ej49:

%Ej50: