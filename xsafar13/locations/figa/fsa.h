/***	fsa.h		***/

/*	Copyright (C) Jan Daciuk, 1996-2004	*/

/* This structure describes a labelled arc in an automaton */

#ifndef		FSA_H
#define		FSA_H

#include	<iostream>
#include	<fstream>

#define		START_CHAR	'^'

inline int
bytes2int(const unsigned char *bytes, const int n)
{
  register int r = 0;
  register int i;
  for (i = n - 1; i >= 0; --i) {
    r <<= 8; r |= bytes[i];
  }
  return r;
}

/* This constant depends on the representation of the # of children per node.
 * It MUST BE a power of 2 minus 1.
 * If not compiled with STOPBIT, 127 is max, because there are 7 bits
 * for the number of children in that representation.
 * Otherwise it can perhaps be 255, because there is no counter of children,
 * but the labels must be different, and they have 8 bits. I have not tested
 * that.
 */
const int	MAX_ARCS_PER_NODE = 255;

typedef		unsigned long		fas_pointer;

typedef char		*mod_arc_ptr; /* modifiable arc pointer */
typedef	const char	*arc_pointer;

/*

FLEXIBLE, STOPBIT, NUMBERS, NEXTBIT, !TAILS, !WEIGHTED - version 5

First, cardinality of the right language

 Byte
       +-+-+-+-+-+-+-+-+\
     0 | | | | | | | | | \  LSB
       +-+-+-+-+-+-+-+-+  +
     1 | | | | | | | | |  |      number of strings recognized
       +-+-+-+-+-+-+-+-+  +----- by the automaton starting
       : : : : : : : : :  |      from this node.
       +-+-+-+-+-+-+-+-+  +
 ctl-1 | | | | | | | | | /  MSB
       +-+-+-+-+-+-+-+-+/

Then, a vector of arcs

       +-+-+-+-+-+-+-+-+\
    0  | | | | | | | | | +------ label
       +-+-+-+-+-+-+-+-+/

                  +------------- node pointed to is next
                  | +----------- the last arc of the node
                  | | +--------- the arc is final
                  | | |
            +------------+
            |     | | |  |
         ___+___  | | |  |
        /       \ | | |  |
       MSB           LSB |
    	7 6 5 4 3 2 1 0  |
       +-+-+-+-+-+-+-+-+ |
     1 | | | | | | | | | \ \
       +-+-+-+-+-+-+-+-+  \ \  LSB
       +-+-+-+-+-+-+-+-+     +
     2 | | | | | | | | |     |
       +-+-+-+-+-+-+-+-+     |
     3 | | | | | | | | |     +----- target node address (in bytes)
       +-+-+-+-+-+-+-+-+     |      (not present except for the byte
       : : : : : : : : :     |       with flags if the node pointed to
       +-+-+-+-+-+-+-+-+     +       is next)
  gtl  | | | | | | | | |    /  MSB
       +-+-+-+-+-+-+-+-+   /
gtl+1


*/

  const int goto_offset = 1;

/* Class name:	fsa_arc_ptr
 * Purpose:	Provide a structure for an arc (a transition)
 *		of a finite-state automaton. This representation
 *		is used by application programs.
 * Remarks:	None.
 */
class fsa_arc_ptr {
public:
  arc_pointer	arc;		/* the arc itself */
  static int	gtl;		/* length of go_to field */
  static int	size;		/* size of the arc */
  static int	entryl;		/* size of number of entries field */
  static int	aunit;		/* how many bytes arc number represents */

  fsa_arc_ptr(void) { arc = NULL; } /* constructor */
  fsa_arc_ptr(const arc_pointer a) { arc = a; } /* constructor */
  fsa_arc_ptr & operator=(arc_pointer a) { arc = a; return *this;}

  int is_last(void) const { /* returns TRUE if the arc is the last in node */
    return ((arc[goto_offset] & 2) == 2);
  }

  int tail_present(void) const { /* returns TRUE if the next arc is
				    at a location pointed to by additional
				    pointer following the arc */
    return ((arc[goto_offset] & 8) == 8);
  }

  int is_final(void) const {	/* return TRUE iff the arc is final */
    return (arc[goto_offset] & 1);
  }

  char get_letter(void) const {	/* return arc label */
    return (*arc);
  }

  fas_pointer get_goto(void) const { /* get number of the target node */
    /* FLEXIBLE, STOPBIT, NEXTBIT, !TAILS */
    return bytes2int((const unsigned char *)arc + goto_offset, gtl) >> 3;
  }

  arc_pointer set_next_node(const arc_pointer curr_dict) { /* get address
							      of  target
							      node */
    /* NEXTBIT,FLEXIBLE,STOPBIT */
  return (arc[goto_offset] & 4) ? arc + goto_offset + 1
    /* NEXTBIT,FLEXIBLE */
    /* NEXTBIT,FLEXIBLE,NUMBERS */
    + entryl
    /* NEXTBIT,FLEXIBLE */
     : curr_dict + 
    /* NEXTBIT,FLEXIBLE,NUMBERS */
    entryl +
    /* NEXTBIT,FLEXIBLE */
    get_goto();
}


  fsa_arc_ptr & operator++(void) { /* get next arc */
    arc += size;
    return *this;
  }

  arc_pointer first_node(arc_pointer curr_dict) { /* get address of first arc*/
    return (curr_dict
	    + entryl * 2
	    + size);
  }

};/* class fsa_arc_ptr */



inline int
fsa_set_last(mod_arc_ptr arc, const int whether_last) {	/* set last arc */
  return (whether_last ? (arc[goto_offset] |= 2) : (arc[goto_offset] &= 0xfd));
}


inline void
fsa_set_final(mod_arc_ptr arc, const int f) { /* set final attribute */
  if (f) arc[goto_offset] |= 1; else arc[goto_offset] &= 0xfe;
}


inline void
fsa_set_next(mod_arc_ptr arc, const int f) {/* set next flag */
  if (f) arc[goto_offset] |= 4; else arc[goto_offset] &= 0xfb;
}

#define	forallnodes(i) \
          for (int i##nlast = 1;\
		 i##nlast;\
		 i##nlast = !(next_node.is_last()), ++next_node)

struct signature {		/* dictionary file signature */
  char          sig[4];         /* automaton identifier (magic number) */
  char          ver;            /* automaton type number */
  char          filler;         /* char used as filler */
  char          annot_sep;      /* char that separates annotations from lex */
  char          gtl;            /* length of go_to field */
};/*struct signature */

#endif
/***	EOF fsa.h	***/
