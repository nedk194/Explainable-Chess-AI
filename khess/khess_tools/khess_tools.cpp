#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <types.h>
#include "pst.h"

namespace py = pybind11;

// Surge move generator
#include "position.h"
#include "tables.h"
#include "types.h"

#include <iostream>
#include <string>
#include <sstream>
// #include <chrono>

void init()
{
    initialise_all_databases();
    zobrist::initialise_zobrist_keys();
}

inline Square move_to(const uint16_t move) { return Square(move & 0x3f); }
inline Square move_from(const uint16_t move) { return Square((move >> 6) & 0x3f); }
inline MoveFlags move_flags(const uint16_t move) { return MoveFlags((move >> 12) & 0xf); }
inline bool is_capture(const uint16_t move)
{
    return (bool)(move_flags(move) & CAPTURE);
}

const int PIECE_VALUES[] = {100, 280, 320, 479, 929, 100000, 0, 0, -100, -280, -320, -479, -929, -100000, 0};
const int PIECE_VALUES_ABS[] = {100, 280, 320, 479, 929, 100000, 0, 0, 100, 280, 320, 479, 929, 100000, 0};

inline int32_t move_with_order(const uint16_t move, const Position& pos)
{
    if (is_capture(move))
    {
	Piece piece_victim = pos.board[move_to(move)];
	Piece piece_attacker = pos.board[move_from(move)];
	return (abs(PIECE_VALUES_ABS[piece_victim] - PIECE_VALUES_ABS[piece_attacker]) << 16) | move;
    }
    else
	return move;
}

PYBIND11_MODULE(khess_tools, module) {
    init();
    module.doc() = "pybind11 example";

    py::class_<Position>(module, "Board")
        .def(py::init())
        .def("__str__",
             [](const Position &pos)
                 {
                     std::ostringstream stream;
                     stream << pos;
                     return stream.str();
                 }
            )
        .def("fen", &Position::fen)
        .def("set_fen",
             [](Position &pos, const std::string &fen)
                 {
                     Position::set(fen, pos);
                 }
            )
        .def("moves",           // List legal moves
             [](Position &pos, const int color)
                 {
                     std::vector<int32_t> moves;
		     		 py::list moves_list;
                     if (color)
                     {
                         MoveList<BLACK> list(pos);
                         for (Move move : list)
                             moves.push_back(move_with_order(move.move, pos));
                     }
                     else
                     {
                         MoveList<WHITE> list(pos);
                         for (Move move : list)
			     moves.push_back(move_with_order(move.move, pos));
                     }
		     // Sort moves by MVVLVA
		     std::sort(moves.begin(), moves.end());
		     // Add moves to list in reverse order
		     for (std::vector<int32_t>::reverse_iterator i = moves.rbegin(); i != moves.rend(); ++i)
			 moves_list.append((*i) & 0xFFFF);
		     return moves_list;
                 }
            )
	.def("entry",
             [](Position &pos)
		 {
		     return pos.history[pos.game_ply].entry;
		 }
	    )
	.def("play",
             [](Position &pos, const int side, const int move)
		 {
		     // printf("Playing %d for %d\n", move, pos.side_to_play);
		     if (side)//(pos.side_to_play)
			 pos.play<BLACK>(move);
		     else
			 pos.play<WHITE>(move);

		     // Bitboard e = pos.history[pos.game_ply].entry;
		     // printf("entry: %lu\n", e);
		 }
	    )
	.def("pop",
             [](Position &pos, const int side,  const int move)
		 {
		     if (side)//(pos.side_to_play)
			 pos.undo<BLACK>(move);
		     else
			 pos.undo<WHITE>(move);
		 }
	    )
	.def("in_check",
             [](Position &pos, const int color)
		 {
		     if (color)
			 return pos.in_check<BLACK>();
		     else
			 return pos.in_check<WHITE>();
		 }
	    )
	.def("at",
             [](Position &pos, const int square)
		 {
		     return (int)pos.board[square];
		 }
	    )
	.def("score_material",
             [](Position &pos)
                 {
		     int score = 0;
		     for (size_t square = 0; square < 64; ++square)
		     {
			 Piece piece = pos.board[square];
			 score += PIECE_VALUES[piece];
		     }
		     return score;
                 }
            )

	.def("king_safety",
		[](Position &pos, int color) -> int {
			Color C = (color == 0 ? WHITE : BLACK);
			Square king_sq = bsf(pos.bitboard_of(C, KING));
			Bitboard all = pos.all_pieces<WHITE>() | pos.all_pieces<BLACK>();
	
			// 8 surrounding squares
			Bitboard adjacent = attacks<KING>(king_sq, all);

			// Threat score count how many of those squares are attacked
			int threats = 0;
			Bitboard check_area = adjacent;
			int count = 0;
			while (check_area) {
				Square sq = pop_lsb(&check_area);
				Bitboard attackers;
				if (color == 0)
					attackers = pos.attackers_from<BLACK>(sq, all);  // Opponent = black
				else
					attackers = pos.attackers_from<WHITE>(sq, all);  // Opponent = white
	

				while (attackers) {
					Square attackSq = pop_lsb(&attackers);
					PieceType p = type_of(pos.at(attackSq));
					if (p == KNIGHT || p == BISHOP) {
						count += 2;
					} else if (p == ROOK) {
						count += 3;
					} else if (p == QUEEN) {
						count += 5;
					}
				}
			}
	
			return -safetyTable[count];
		}
	)
	.def("hello",
		[](const Position &pos) {
			return "Hi from C++ Board!";
		}
	)
	.def("pawn_front_span", [](const Position& pos, int color, int square) {
		Color c = (color == 0 ? WHITE : BLACK);
		Color other = ~c;
		Square sq = Square(square);
		Bitboard bb = WHITE_PAWN_ATTACKS[sq];
		int up = (c == WHITE ? 8 : -8);

		Square walk = Square(int(sq) + up);
		py::list squares;
		while (walk >= h1 && walk <= a8) {
			
			//squares.append(int(walk));
			if (pos.get_color(walk) == BLACK){
				squares.append("1");}
			if (pos.get_color(walk) == WHITE){
				squares.append("0");}
			if (pos.get_color(walk) == COLOR_NONE){
				squares.append("2");}
			
			walk = Square(int(walk) + up);
		}
	
		return squares;
	})

	
	.def("isolated_pawns",
		[](const Position& pos, int color) -> int {
			Color c = (color == 0 ? WHITE : BLACK);
			Bitboard pawns = pos.bitboard_of(c, PAWN);
			int count = 0;
	
			while (pawns) {
				Square sq = pop_lsb(&pawns);
				int file = sq & 7;
	
				Bitboard friendly_pawns = pos.bitboard_of(c, PAWN);
	
				bool has_left = (file > 0) && (friendly_pawns & (0x0101010101010101ULL << (file - 1)));
				bool has_right = (file < 7) && (friendly_pawns & (0x0101010101010101ULL << (file + 1)));
	
				if (!has_left && !has_right)
					count++;
			}
	
			return count;
		}
	)
	.def("doubled_pawns",
		[](const Position& pos, int color) -> int {
			Color c = (color == 0 ? WHITE : BLACK);
			Bitboard pawns = pos.bitboard_of(c, PAWN);
	
			int count = 0;
			for (int file = 0; file < 8; ++file) {
				Bitboard file_mask = 0x0101010101010101ULL << file;
				int pawns_on_file = pop_count(file_mask & pawns);
	
				if (pawns_on_file > 1)
					count += (pawns_on_file - 1);
			}
	
			return count;
		}
	)
	.def("backward_pawns",
		[](const Position& pos, int color) -> int {
			Color C = (color == 0 ? WHITE : BLACK);
			Color Them = ~C;
	
			Bitboard pawns = pos.bitboard_of(C, PAWN);
			Bitboard other_pawns = pos.bitboard_of(Them, PAWN);
			Bitboard attack_span = 0;
	
			Bitboard pawns_copy = pawns;
			while (pawns_copy) {
				Square sq = pop_lsb(&pawns_copy);
				attack_span |= (PAWN_FRONT_SPAN[C][sq] & ~MASK_FILE[file_of(sq)]);
			}
	
			Bitboard enemy_attacks = (Them == WHITE)
				? pawn_attacks<WHITE>(other_pawns)
				: pawn_attacks<BLACK>(other_pawns);
	
			// Shift pawns forward by 8 (white) or back by 8 (black)
			Bitboard advanced_squares = (C == WHITE) ? (pawns << 8) : (pawns >> 8);
	
			// Backward pawns are those that:
			// - Move into a square attacked by the enemy
			// - Aren't covered by our own attack span
			Bitboard backward = advanced_squares & enemy_attacks & ~attack_span;
	
			return pop_count(backward);
		}
	)
	.def("is_passer",
		[](const Position& pos, int square_index) -> bool {
			Square sq = Square(square_index);
			if (pos.board[sq] != make_piece(WHITE, PAWN) &&
				pos.board[sq] != make_piece(BLACK, PAWN))
				return false;
	
			Color c = color_of(pos.board[sq]);
			Color other = ~c;
	
			if (!(PAWN_FRONT_SPAN[c][sq] & pos.bitboard_of(other, PAWN)))
				return true;
	
			if ((MASK_FILE[file_of(sq)] & PAWN_FRONT_SPAN[c][sq] &
				 pos.bitboard_of(other, PAWN))) {
				return false;
			}
			
			int up = (c == WHITE ? 8 : -8);
			Square forward1 = Square(int(sq) + up);
			if (forward1 >= a1 && forward1 <= h8) {
				Bitboard support, enemies;

				if (other == WHITE)
					support = pawn_attacks<WHITE>(BB_SQUARE[forward1]) & pos.bitboard_of(c, PAWN);
				else
					support = pawn_attacks<BLACK>(BB_SQUARE[forward1]) & pos.bitboard_of(c, PAWN);

				if (c == WHITE)
					enemies = pawn_attacks<WHITE>(BB_SQUARE[forward1]) & pos.bitboard_of(other, PAWN);
				else
					enemies = pawn_attacks<BLACK>(BB_SQUARE[forward1]) & pos.bitboard_of(other, PAWN);
	
				if (pop_count(support) >= pop_count(enemies)) {
					if (!(PAWN_FRONT_SPAN[c][forward1] &
						  pos.bitboard_of(other, PAWN))) {
						return true;
					}
				}
	
				Square forward2 = Square(int(forward1) + up);
				if (forward2 >= a1 && forward2 <= h8) {
					return !(PAWN_FRONT_SPAN[c][forward2] &
							 pos.bitboard_of(other, PAWN));
				}
			}
			return false;
		}
	)
	.def("passed_score",
		[](const Position& pos, int color) -> int {
			Color c = (color == 0 ? WHITE : BLACK);
			Color other = ~c;
			int up = (c == WHITE ? 8 : -8);
			Bitboard pawns = pos.bitboard_of(c, PAWN);
			int score = 0;
			int debug = 0;
	
			while (pawns) {
				Square sq = pop_lsb(&pawns);
				bool passer = false;
				if (!(PAWN_FRONT_SPAN[c][sq] & pos.bitboard_of(other, PAWN))) {
					passer = true;
					debug += 1;
				} else if (!(MASK_FILE[file_of(sq)] & PAWN_FRONT_SPAN[c][sq] &
							 pos.bitboard_of(other, PAWN))) {
					Square fwd1 = Square(int(sq) + up);
					if (fwd1 >= a1 && fwd1 <= h8) {
						Bitboard support, enemies;

						if(c == WHITE) {
							support = pop_count(BLACK_PAWN_ATTACKS[fwd1] & pos.bitboard_of(c, PAWN));
							enemies = pop_count(WHITE_PAWN_ATTACKS[fwd1] & pos.bitboard_of(other, PAWN));
						}
						else {
							support = pop_count(WHITE_PAWN_ATTACKS[fwd1] & pos.bitboard_of(c, PAWN));	
							enemies = pop_count(BLACK_PAWN_ATTACKS[fwd1] & pos.bitboard_of(other, PAWN));
						}
	
						if (pop_count(support) >= pop_count(enemies)) {
							Square fwd2 = Square(int(fwd1) + up);
							if (!(PAWN_FRONT_SPAN[c][fwd2] &  
								  pos.bitboard_of(other, PAWN))) {
									passer = true;
									debug += 3;
								}
						}
					}
				}
	
				if (passer) {
					int rank = rank_of(sq);
					if (c == BLACK) rank = 7 - rank;
					score += passedRank[rank];  // Must be defined somewhere
	
					Bitboard file_mask = MASK_FILE[file_of(sq)];
					Bitboard front_span = PAWN_FRONT_SPAN[c][sq];
	
					Bitboard friendly_rooks_queens =
						pos.bitboard_of(c, ROOK) | pos.bitboard_of(c, QUEEN);
					Bitboard enemy_rooks_queens =
						pos.bitboard_of(other, ROOK) | pos.bitboard_of(other, QUEEN);
	
					if (file_mask & friendly_rooks_queens & front_span)
						score += (passedRank[rank] * 2) /10;
					if (file_mask & enemy_rooks_queens & front_span)
						score -= (passedRank[rank] * 2) /10;
	
					Square walk = Square(int(sq) + up);
					while (walk >= h1 && walk <= a8) {
						if (pos.get_color(walk) == other)
							score -= 5;
						walk = Square(int(walk) + up);
					}
				}
			}
			return score;
		}
	)
	.def("score_pst",
             [](Position &pos)
                 {
		     int score = 0;
		     for (size_t square = 0; square < 64; ++square)
		     {
			 Piece piece = pos.board[square];
			 // printf("%d\n", piece);
			 score += PST[piece][square];
		     }
		     return score;
                 }
            );
        }
