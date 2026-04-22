#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from itertools import combinations
from typing import List, Tuple, Dict, Set, FrozenSet
import argparse


Party = str
TCombo = Tuple[Party, ...]
Subset = FrozenSet[Party]
LayoutEntry = Tuple[int, str, TCombo]  # (i, "cover"/"patch", payload)


def parties(n: int) -> List[Party]:
    """Return ordered party names: P1, P2, ..., Pn."""
    return [f"P{i}" for i in range(1, n + 1)]


def lex_combinations(items: List[Party], r: int) -> List[TCombo]:
    """Combinations are generated in lexicographic order by default."""
    return list(combinations(items, r))


def cov_of_G(G: TCombo, t: int) -> Set[Subset]:
    """cov(G) = all (t-1)-subsets of G."""
    return {frozenset(S) for S in combinations(G, t - 1)}


def subset_sort_key(fs: Subset) -> Tuple[int, ...]:
    """Sort subsets like {P2,P10} by numeric indices."""
    return tuple(sorted(int(p[1:]) for p in fs))


def ctp_layout(
    n: int, t: int
) -> Tuple[List[Party], Set[Subset], List[LayoutEntry], Set[Subset], Set[Subset]]:
    """
    Cover-then-Patch (CtP) layout generation.
    """
    if not (2 <= t <= n):
        raise ValueError("Require 2 <= t <= n.")

    P = parties(n)
    Q: Set[Subset] = {frozenset(S) for S in combinations(P, t - 1)}
    U: Set[Subset] = set()
    E: Set[Subset] = set()
    layout: List[LayoutEntry] = []

    i = 1

    # Cover phase
    for G in lex_combinations(P, t):
        covG = cov_of_G(G, t)
        if covG.isdisjoint(U):
            U |= covG
            layout.append((i, "cover", G))
            i += 1

    # Patch phase
    remaining = sorted(Q - U, key=subset_sort_key)
    for S in remaining:
        S_tuple = tuple(sorted(S, key=lambda x: int(x[1:])))
        E.add(S)
        U.add(S)
        layout.append((i, "patch", S_tuple))
        i += 1

    if U != Q:
        raise RuntimeError("Invariant failed: U must equal Q at the end.")

    return P, Q, layout, U, E


def share_table_from_layout(
    P: List[Party], t: int, layout: List[LayoutEntry]
) -> Dict[Party, Dict[int, str]]:
    """
    Generate the PUBLIC share-table schema v_{i,k}.
    """
    table: Dict[Party, Dict[int, str]] = {pk: {} for pk in P}

    for (i, typ, payload) in layout:
        v_i = f"v_{i}"

        if typ == "cover":
            G = list(payload)
            r = [None] + [f"r^({i})_{j}" for j in range(1, t + 1)]
            r_t_expr = "-(" + "+".join(r[j] for j in range(1, t)) + ")"

            for pk in P:
                if pk == G[0]:
                    table[pk][i] = f"{v_i} + {r[1]}"
                elif pk in G[1:]:
                    pos = G.index(pk) + 1
                    if pos == t:
                        table[pk][i] = f"{r[t]} = {r_t_expr}"
                    else:
                        table[pk][i] = r[pos]
                else:
                    table[pk][i] = v_i

        elif typ == "patch":
            S = set(payload)
            for pk in P:
                table[pk][i] = "⊥" if pk in S else v_i

        else:
            raise ValueError(f"Unknown column type: {typ}")

    return table


def print_layout_and_table(n: int, t: int) -> None:
    P, Q, layout, U, E = ctp_layout(n, t)

    cover_cols = [c for c in layout if c[1] == "cover"]
    patch_cols = [c for c in layout if c[1] == "patch"]

    print(f"(n,t)=({n},{t})")
    print(f"|Q| = C(n,t-1) = {len(Q)}")
    print(f"Cover columns C = {len(cover_cols)}")
    print(f"Patch columns = {len(patch_cols)}")
    print(f"Upper bound floor(|Q|/t) = {len(Q)//t}")

    print("\nLayout L:")
    for (i, typ, payload) in layout:
        print(f"  col {i:>2}: {typ:<5} payload={payload}")

    table = share_table_from_layout(P, t, layout)
    cols = [i for (i, _, _) in layout]

    print("\nPublic Share-Table Schema (entries v_{i,k}):")
    header = ["Party"] + [f"c{i}" for i in cols]
    print(" | ".join(header))
    print("-" * (len(" | ".join(header)) + 5))

    for pk in P:
        row = [pk] + [table[pk][i] for i in cols]
        print(" | ".join(row))


def main():
    parser = argparse.ArgumentParser(
        description="CtP public share-table generator (layout + schema)."
    )
    parser.add_argument("--n", type=int, default=6, help="Number of parties n")
    parser.add_argument("--t", type=int, default=3, help="Threshold t (2 <= t <= n)")
    args = parser.parse_args()

    if args.t < 2 or args.t > args.n:
        parser.error("Require 2 <= t <= n.")

    print_layout_and_table(n=args.n, t=args.t)


if __name__ == "__main__":
    main()

