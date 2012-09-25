#!/usr/bin/perl
eval 'exec /usr/bin/perl -S $0 ${1+"$@"}'
    if $running_under_some_shell;
			# this emulates #! processing on NIH machines.
			# (remove #! line above if indigestible)

eval '$'.$1.'$2;' while $ARGV[0] =~ /^([A-Za-z_0-9]+=)(.*)/ && shift;
			# process any FOO=bar switches

# prep_gen.pl

# This script coverts data in the format:
#
# inflected_formHTlexemeHTtags
#
# (where HT is the horizontal tabulation, lexeme is the canonical form,
# and tags are annotations)
# into the form:
#
# lexeme+tags+Kending
#
# where '+' is a separator, K is a character that specifies how many characters
# should be deleted from the end of the canonical form (lexeme) to produce
# the inflected form the stripped string with the ending. K='A' means
# no deletion, 'B' - delete 1 character, 'C' - delete 2, and so on.
#
# Written by Jan Daciuk <jandac@eti.pg.gda.pl>, 2008
#

$separator = '+';

while (<>) {
    chop;	# strip record separator
    @Fld = split('\t', $_, 9999);

    $l1 = length($Fld[0]);
    if (($prefix = &common_prefix($Fld[0], $Fld[1], $l1))) {
	# The canonical and inflected form have a common prefix,
	# which has the length $prefix.
	# Print the canonical form, separator, tags, separator,
	# deletion code and canonical ending
	printf '%s%s%c%s%s%s', $Fld[1], $separator, $Fld[2], $separator,
	($l1 - $prefix + 65), substr($Fld[0], $prefix, 999999);
    }
    else {
	# The canonical form and the inflected form have no common prefix.
	# Print the canonical form, separator, tags, separator, 'A' 
	# and canonical ending
	printf '%s%s%s%sA%s', $Fld[1], $separator, $Fld[2],
	$separator, $Fld[0];
    }
    # Delete the following (1) line if your tags do not contain spaces
    # and you would like to append comments at the end of lines
    for ($i = 3; $i < $#Fld; $i++) {
	printf ' %s', $Fld[$i];
	# Do not delete this
	;
    }
    printf "\n";
}

# common_prefix finds the length of the longest common prefix
# of two strings that are its parameters.
# $1 - the first string
# $2 - the second string
# $3 - length of the first string
sub common_prefix {
    local($s1, $s2, $n, $i) = @_;
    for ($i = 0; $i < $n; $i++) {
	if (substr($s1, $i, 1) ne substr($s2, $i, 1)) {	#???
	    return $i;
	}
    }
    $n;
}
