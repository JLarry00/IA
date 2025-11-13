consult('a.pl').


%Base de conocimiento: Productos
precio(casa_museo_dali, 14).
precio(catedral_segovia, 8).
precio(cien_anios_soledad, 18).
precio(parque_retiro, 0).
precio(el_quijote, 12).

categoria(casa_museo_dali, museo).
categoria(catedral_segovia, monumento).
categoria(cien_anios_soledad, novela).
categoria(parque_retiro, madrid).
categoria(el_quijote, novela).

autor(casa_museo_dali, salvador_dali).
autor(catedral_segovia, anonimo).
autor(cien_anios_soledad, gabriel_garcia_marquez).
autor(parque_retiro, juan_de_herrera).
autor(el_quijote, miguel_de_cervantes).

%Preferencias de usuarios
pref_precio(paco, Precio) :- Precio < 20.
pref_precio(miguel, Precio) :- Precio < 12.
pref_precio(manuel, Precio) :- Precio < 10.

pref_categoria(paco, museo).
pref_categoria(juan, monumento).
pref_categoria(miguel, novela).
pref_categoria(manuel, madrid).

pref_autor(paco, gabriel_garcia_marquez).
pref_autor(miguel, miguel_de_cervantes).
pref_autor(juan, salvador_dali).
pref_autor(manuel, juan_de_herrera).

% Predicados a definir:
% recomienda_segun_atributo/2: es cierto si el producto tiene al menos un atributo
% (precio, categoria o autor) que coincide con las preferencias del usuario.
% Ejemplos:
% ?- recomienda_segun_atributo(paco, casa_museo_dali).  % true
% ?- recomienda_segun_atributo(miguel, casa_museo_dali).  % false

% recomienda_segun_atributos/2: es cierto si todos los atributos del producto 
% (precio, categoria y autor) cumplen las preferencias del usuario.
% Ejemplos:
% ?- recomienda_segun_atributos(manuel, parque_retiro).  % true
% ?- recomienda_segun_atributos(paco, casa_museo_dali).  % false

recomienda_segun_atributo(U,Prod) :- (precio(Prod,Precio), pref_precio(U,Precio), !);
                                    (categoria(Prod,C), pref_categoria(U,C), !);
                                    (autor(Prod,A), pref_autor(U,A), !).

recomienda_segun_atributos(U,Prod) :- precio(Prod,Precio), pref_precio(U,Precio),
                                        categoria(Prod,C), pref_categoria(U,C),
                                        autor(Prod,A), pref_autor(U,A).

%compress([], []).
%compress([H1], [H1]).
%compress([H1, H1|T], X) :- compress([H1|T], X).
%compress([H1, H2|T], [H1|Xs]) :- compress([H2|T], Xs).

%compress([a,c,c,b,d,d,e,e,e,e,a],X).

slice([], _, _, []).
slice([X|_], 1, 1, [X]).
slice([X|Xs], 1, K, [X|Ys]) :- K > 1, K1 is K-1, slice(Xs, 1, K1, Ys).
slice([_|Xs], I, K, Y) :- I > 1, I1 is I-1, K1 is K-1, slice(Xs, I1, K1, Y).

%slice([a,b,c,d,e,f,g,h,i,k],3,7,L).

range(I,I,[I]).
range(I,K,[I|Ls]) :- K > I, I1 is I+1, range(I1,K,Ls).

%range(4,9,L).

element_at(X,[X|_],1).
element_at(X,[_|L],K) :- K > 1, K1 is K-1, element_at(X,L,K1).

%element_at(X,[a,b,c,d,e],3).

%my_length([_],1).
%my_length([_|Xs],N) :- my_length(Xs,M), N is M+1.

%my_length([a,b,c,d], N).

insert_at(X,Ys,1,[X|Ys]).
insert_at(X,[Y|Ys],N,[Y|Ls]) :- N > 1, N1 is N-1, insert_at(X,Ys,N1,Ls).

%insert_at(alfa,[a,b,c,d],2,L).

dupli(L,1,L).
dupli(L,N,Lf) :- my_dupli(L,N,Lf,N).

my_dupli([],_,[],_).
my_dupli([X|Xs],N,[X|Ls],1) :- my_dupli(Xs,N,Ls,N).
my_dupli([X|Xs],N,[X|Ls],M) :- M > 1, M1 is M-1, my_dupli([X|Xs],N,Ls,M1).

%dupli([1,5,7],2,X).

split(Xs,0,[],Xs).
split([X|Xs],N,[X|L1s],L2) :- N > 0, M is N-1, split(Xs,M,L1s,L2).

%split([a,b,c,d,e,f,g,h,i,k],3,L1,L2).

remove_at(X,[X|Xs],1,Xs).
remove_at(X,[Y|Xs],N,[Y|Ys]) :- N > 1, N1 is N-1, remove_at(X,Xs,N1,Ys).

%remove_at(X,[1,2,3,4,5],2,Y).

my_last(X,[X]).
my_last(X,[_|Xs]) :- my_last(X,Xs).

%my_last(X,[a,b,c,d]).

my_reverse(X,L) :- my_rev(X,L,[]).

my_rev(X,[],X).
my_rev(X,[L|Ls],Rs) :- my_rev(X,Ls,[L|Rs]).

%my_reverse(X,[a,b,c]).

compress([], []).
compress([L],[L]).
compress([L,L|Ls],Xs) :- compress([L|Ls],Xs).
compress([L,L1|Ls],[L|Xs]) :- L \= L1, compress([L1|Ls],Xs).

%compress([a,c,c,b,d,d,e,e,e,e,a],X).

my_length([],0).
my_length([_|Ls],N) :- my_length(Ls,N1), N is N1+1.

%my_length([a,b,c],N).

is_prime(2).
is_prime(3).
is_prime(P) :- integer(P), P > 3, P mod 2 =\= 0, not(has_factor(P,3)).

has_factor(N,L) :- N mod L =:= 0.
has_factor(N,L) :- L * L < N, L2 is L + 2, has_factor(N,L2).



next_prime(Last,Next) :- NextAux is Last+2, is_prime(NextAux), Next is NextAux, !.
next_prime(Last,Next) :- Last mod 2 =\= 0, Last1 is Last+2, next_prime(Last1,Next).

my_first_n_primes(0,[],_) :- !.
my_first_n_primes(N,[P|Ps],LastP) :- N1 is N-1, next_prime(LastP,P), my_first_n_primes(N1,Ps,P).

first_n_primes(0,[]) :- !.
first_n_primes(1,[2]) :- !.
first_n_primes(2,[2,3]) :- !.
first_n_primes(N,[2,3|X]) :- N1 is N-2, my_first_n_primes(N1,X,3), print(X).

%is_prime(1019).
%first_n_primes(1,X).
%first_n_primes(2,X).
%first_n_primes(10,X).
%first_n_primes(100,X).
%first_n_primes(1000,X).