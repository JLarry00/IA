consult('a.pl').

compress([], []) :- !.
compress([H1], [H1]) :- !.
compress([H1, H1|T], X) :- compress([H1|T], X).
compress([H1, H2|T], [H1|Xs]) :- compress([H2|T], Xs).

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

my_length([_],1).
my_length([_|Xs],N) :- my_length(Xs,M), N is M+1.

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