// subor: figa_main.cc v0.35
// autor: Marek Visnovsky, xvisno00@stud.fit.vutbr.cz
// popis: znackovac vybranych nazvov v texte

#include <iostream>
#include <unistd.h>

#include "fsa.h"
#include "nstr.h"
#include "common.h"
#include "figa.h"

using namespace std;

// nazov: print_help
// popis: vytlaci napovedu na standardny vystup
void print_help () {
	cout << "FItGAzetteer v0.35, September 14th, 2010, Marek Visnovsky, xvisno00@stud.fit.vutbr.cz" << endl;
	cout << "based on: fsa Ver. 0.49, March 18th, 2009, (c) Jan Daciuk, jandac@eti.pg.gda.pl" << endl;
	cout << "usage:" << endl << "figav03 [options]..." << endl << "options" << endl;
	cout << "-d dictionary (automaton file)" << endl;
	cout << "-l list file" << endl;
	cout << "-m map file corresponding to specified list file" << endl;
	cout << "-h this help" << endl;
	return;			
}

// nazov: main
// popis: spusta program
int main (const int argc, char *argv[]) {
	word_list dict;
    const char *lang_file = NULL;
    char *fsa_name = NULL, *list_name = NULL, *map_name = NULL;
    int c, error = 3;
    
    // spracovanie argumentov
    while ((c = getopt(argc, argv, "d:l:m:h")) != -1) 
		switch (c) {
			case 'd':
				fsa_name = optarg;
				error --;
				break;
			case 'l':
				list_name = optarg;
				error --;
				break;
			case 'm':
				map_name = optarg;
				error --;
				break;
			case 'h':
				error = 4;
				break;
			default:
				cerr << "Unrecognized option" << endl;
				error = 4;
				break;
			}
	
	// osetrenie chybajucich argumentov		
	if (error > 0) {
		if (error != 4)
			cout << "One dictionary file, one list file and one map file must be specified" << endl;
		print_help();
		return 1;
	}
		
    dict.insert(fsa_name);
    marker seek_names(&dict, lang_file);
    
    seek_names.lookup(list_name,map_name);
     
    return 0;
}
